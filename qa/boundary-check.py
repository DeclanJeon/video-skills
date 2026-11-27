# /// script
# requires-python = ">=3.12"
# dependencies = ["pytest", "pydantic>=2"]
# ///
# How to run: python3 -m pytest qa/boundary-check.py -q
# Uses installed dependencies only; never submits jobs or changes package sources.
"""Synthetic, agent-authored projection contract; not an automatic CSV adapter."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Final

import pytest

ROOT: Final = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "video-preproduction-skills/scripts"),
               str(ROOT / "video-production-skills")]

from cp2.ledger import Ledger
from production.adapters import resolve_legacy
from production.models import ContractError, Requirement
from production.upstream import (
    Artifact, Asset, AssetUse, Board, CoverageEnvelope, Panel, Project, Shot, Speech,
    derive_asset_uses, derive_coverage, export_coverage,
)


def test_projection_when_actual_legacy_ledger_and_board_csv(tmp_path: Path) -> None:
    # Given: actual Ledger tool plus preproduction-shaped CSV/header in a temp work.
    asset = tmp_path / "LOOK-01.md"
    asset.write_text("# Synthetic visual design\n", encoding="utf-8")
    Ledger.load(tmp_path).register("LOOK-01", asset, 1, [])
    pin = resolve_legacy(tmp_path / "ledger.json", "LOOK-01@v1")
    board = tmp_path / "04_board"
    board.mkdir()
    (board / "index-header.json").write_text(
        json.dumps({"LOOK": ["LOOK-01@v1"], "runtime_s": 2}), encoding="utf-8")
    row = {"cut": "S01-C01", "t_start": "0", "t_end": "2",
           "panels": "S01-C01-P1", "beats": "PLT@v1.B01", "dialogue": "D001",
           "dialogue_text": '{"D001":"잠깐."}', "look": "LOOK-01@v1"}
    with (board / "index.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    with (board / "index.csv").open(newline="", encoding="utf-8") as stream:
        source_row = next(csv.DictReader(stream))
    # When: an agent explicitly maps this fixture into the existing Project model.
    projection = Project(
        shots=(Shot(id=source_row["cut"], speech=(Speech(id=source_row["dialogue"]),),
                    asset_ids=(pin.id,), start_s=float(source_row["t_start"]),
                    end_s=float(source_row["t_end"])),),
        storyboard=Board(panels=(Panel(id=source_row["panels"],
                                       shot_id=source_row["cut"],
                                       beat_ids=(source_row["beats"],)),)),
        artifacts=(Artifact(id="LOOK-01", type="look", status="approved",
                            asset_ids=(pin.id,)),),
        asset_registry=(Asset(id=pin.id, version=pin.version, path=pin.path,
                              sha256=pin.sha256, status="available"),),
    )
    origin = tmp_path / "production-input-v1.json"
    origin.write_text(projection.model_dump_json(), encoding="utf-8")
    coverage = export_coverage(origin)
    # Then: actual downstream derivation preserves input IDs and exact design pin.
    assert {r.id for r in coverage.requirements} == {
        "shot:S01-C01", "panel:S01-C01-P1", "speech:D001",
        "beat:S01-C01:PLT@v1.B01",
    }
    assert derive_coverage(origin) == coverage.requirements
    assert derive_asset_uses(origin)[0].pin == pin
    assert coverage.origin is not None
    assert coverage.origin.sha256 == hashlib.sha256(origin.read_bytes()).hexdigest()
    assert json.loads((tmp_path / "ledger.json").read_bytes())["artifacts"]


def test_dependency_when_projection_drops_mandatory_asset(tmp_path: Path) -> None:
    # Given: a projection names a mandatory asset but no real registry entry.
    project = Project(shots=(Shot(id="S01-C01", asset_ids=("CHR-01",)),),
                      storyboard=Board(panels=(Panel(id="S01-C01-P1",
                                                    shot_id="S01-C01", beat_ids=()),)))
    path = tmp_path / "missing-asset.json"
    path.write_text(project.model_dump_json(), encoding="utf-8")
    # When / Then: existing production code blocks incomplete asset closure.
    with pytest.raises(ContractError, match="missing/current asset"):
        derive_asset_uses(path)


def test_coverage_when_dialogue_crosses_two_cuts(tmp_path: Path) -> None:
    # Given: canonical D001 spans both cut obligations and consumes the same audio.
    audio = tmp_path / "VOC-01.txt"
    audio.write_text("synthetic audio pin, not playable media", encoding="utf-8")
    Ledger.load(tmp_path).register("VOC-01", audio, 1, [])
    pin = resolve_legacy(tmp_path / "ledger.json", "VOC-01@v1")
    source = CoverageEnvelope(
        requirements=tuple(
            requirement
            for cut, panel, start, end in (
                ("S01-C01", "S01-C01-P1", "1.0", "2.0"),
                ("S01-C02", "S01-C02-P1", "2.0", "3.0"),
            )
            for requirement in (
                Requirement(id=f"shot:{cut}", shot=cut, panels=(panel,),
                            locator=f"04_board/index.csv#cut={cut}"),
                Requirement(id=f"panel:{panel}", shot=cut, panels=(panel,),
                            locator=f"04_board/index.csv#panels={panel}"),
                Requirement(id=f"speech:{cut}:D001", shot=cut, panels=(panel,),
                            modality="audio", locator=(
                                f"04_board/index.csv#cut={cut};dialogue=D001;"
                                f"L-cut;range={start}-{end}")),
            )
        ),
        asset_uses=tuple(AssetUse(shot=cut, pin=pin)
                         for cut in ("S01-C01", "S01-C02")),
    )
    path = tmp_path / "lcut-input-v1.json"
    path.write_text(source.model_dump_json(), encoding="utf-8")
    # When: the supported explicit envelope branch exports this cross-cut scope.
    exported = export_coverage(path)
    # Then: both scoped obligations survive with original D001 locators and pin.
    speech = tuple(r for r in exported.requirements if r.modality == "audio")
    assert {r.id for r in speech} == {
        "speech:S01-C01:D001", "speech:S01-C02:D001",
    }
    assert {r.shot for r in speech} == {"S01-C01", "S01-C02"}
    assert all("dialogue=D001" in r.locator for r in speech)
    assert {use.shot for use in exported.asset_uses} == {"S01-C01", "S01-C02"}
    assert all(use.pin == pin for use in exported.asset_uses)
    assert exported.origin is not None
    assert derive_coverage(tmp_path / exported.origin.path) == exported.requirements
    assert derive_asset_uses(tmp_path / exported.origin.path) == exported.asset_uses
