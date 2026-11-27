#!/usr/bin/env python3
"""Execute mapped contract tests. This is not real provider/perceptual QA."""
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from pydantic import TypeAdapter, ValidationError


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = root/"qa/implementation"
    report.mkdir(parents=True, exist_ok=True)
    try:
        mapping = TypeAdapter(dict[str, tuple[str, ...]]).validate_json((root/"docs/acceptance-map.json").read_bytes())
        if set(mapping) != {f"T{i:02}" for i in range(1,35)} or any(not nodes for nodes in mapping.values()):
            raise ValueError("all T01-T34 need nonempty executable node bindings")
        nodes = sorted({node for values in mapping.values() for node in values})
        if any(re.fullmatch(r"tests/test_[a-z_]+\.py::test_[a-z_]+(?:\[[^\]\n]+\])?", n) is None for n in nodes):
            raise ValueError("unsafe pytest node")
        completed = subprocess.run([sys.executable,"-m","pytest","-q",*nodes,"--junitxml",str(report/"acceptance-junit.xml")], cwd=root, capture_output=True, text=True, timeout=180)
        (report/"acceptance-pytest.txt").write_text(completed.stdout+completed.stderr)
        tree = ET.parse(report/"acceptance-junit.xml")
        cases = list(tree.iter("testcase"))
        passed = completed.returncode == 0 and len(cases) >= len(nodes) and not any(list(c) for c in cases if c.find("skipped") is not None or c.find("failure") is not None or c.find("error") is not None)
        reported_semantics = {"T04","T10","T12","T13","T15","T16","T22","T24","T31","T34"}
        result = {"valid": passed, "planned_cases":34,"executed_pytest_cases":len(cases),
                  "cases": {key:{"nodes":values,"status":"passed" if passed else "blocked",
                                  "evidence_kind":"reported-semantic-contract" if key in reported_semantics else "structural-contract"}
                            for key,values in sorted(mapping.items())},
                  "live_provider_verified":False,"perceptual_quality_verified":False,
                  "scope":"local contract scenarios; semantic reports are fixtures; technical decode/render are real local media checks, never provider/perceptual certification"}
    except (OSError, ValueError, ValidationError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        result = {"valid":False,"error":str(exc)}
    (report/"acceptance-results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return int(not result["valid"])


if __name__ == "__main__":
    raise SystemExit(main())
