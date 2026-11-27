"""Package checks target machine-consumed metadata, not prose wording."""
import json
from pathlib import Path
import subprocess
import sys


def test_package_checker_when_roles_and_links_are_valid():
    # Given: a repository-local skill pack.
    root = Path(__file__).resolve().parents[1]
    script = root/"scripts/check_package.py"
    assert script.exists(), "package checker not implemented"
    # When: invoking its public check command.
    result = subprocess.run([sys.executable,str(script),"--json"],capture_output=True,text=True)
    # Then: five roles and their linked resources exist.
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["skills"] == 5


def test_acceptance_map_when_nodes_resolve():
    # Given: named executable acceptance bindings, not prose snapshots.
    root = Path(__file__).resolve().parents[1]
    path = root/"docs/acceptance-map.json"
    assert path.exists(), "acceptance map not implemented"
    # When: reading machine-consumed case IDs and pytest nodes.
    data = json.loads(path.read_text())
    # Then: all design cases have concrete executable targets.
    assert set(data) == {f"T{i:02}" for i in range(1,35)}
    assert all("::test_" in node for nodes in data.values() for node in nodes)


def test_templates_when_json_schema_matches_runtime():
    # Given: public boundary schemas checked into package resources.
    root = Path(__file__).resolve().parents[1]
    schema = root/"schemas/state.schema.json"
    assert schema.exists(), "state JSON Schema not implemented"
    from production.models import State
    # When: loading the machine-consumed schema.
    actual = json.loads(schema.read_text())
    # Then: it matches the parser actually used by CLI.
    assert actual == State.model_json_schema()
