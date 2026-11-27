"""P01–P52 link to exact executed JUnit node IDs and current source bytes; never count prose or stale/missing runs as PASS."""
from pathlib import Path
from typing import Annotated
import xml.etree.ElementTree as ET

from pydantic import ValidationError
import typer

from postproduction.acceptance_models import AcceptanceCheck, AcceptanceMap, SourceSnapshot
from postproduction.source_scope import snapshot

DEFAULT_RESULTS = Path("qa/implementation/current-test-results.xml")
DEFAULT_SCOPE = Path("qa/implementation/current-test-scope.json")


def junit_nodes(root: Path, path: Path) -> dict[str,str]:
    tree = ET.fromstring(path.read_bytes())
    nodes: dict[str,str] = {}
    for case in tree.iter("testcase"):
        parts = case.get("classname","").split(".")
        name = case.get("name","")
        node = ""
        for end in range(len(parts),0,-1):
            module = Path(*parts[:end]).with_suffix(".py")
            if (root/module).is_file():
                node = module.as_posix()+"::"+"::".join((*parts[end:],name))
                break
        if not node or not name:
            raise ValueError("unresolvable actual JUnit testcase identity")
        if node in nodes:
            raise ValueError("duplicate actual JUnit testcase")
        status = "passed"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "failed"
        elif case.find("skipped") is not None:
            status = "skipped"
        nodes[node] = status
    if any(s.get("errors","0")!="0" or s.get("failures","0")!="0" for s in tree.iter("testsuite")):
        raise ValueError("JUnit run contains failures/errors")
    return nodes


def check_acceptance(root: Path, map_path: Path, results_path: Path, scope_path: Path) -> AcceptanceCheck:
    issues: list[str] = []
    try:
        mapping = AcceptanceMap.model_validate_json(map_path.read_bytes())
        original = SourceSnapshot.model_validate_json(scope_path.read_bytes())
        if not original.files or original!=snapshot(root):
            issues.append("source/spec/schema scope missing or changed since execution snapshot")
        ids = tuple(s.id for s in mapping.scenarios)
        if len(ids)!=52 or set(ids)!={f"P{i:02}" for i in range(1,53)}:
            issues.append("exact P01–P52 required, no duplicate/reduced denominator")
        nodes = junit_nodes(root,results_path)
    except (OSError,ValidationError,ValueError,ET.ParseError) as exc:
        return AcceptanceCheck(ok=False,mapped_scenarios=0,passed_cases=0,issues=(f"missing/invalid execution evidence: {exc}",))
    passed: set[str] = set()
    mapped = 0
    for scenario in mapping.scenarios:
        if not scenario.cases or not scenario.scopes or not scenario.purpose:
            issues.append(f"{scenario.id}: actual cases and evidence scope required")
            continue
        missing = tuple(node for node in scenario.cases if nodes.get(node)!="passed")
        if missing:
            issues.append(f"{scenario.id}: not executed and passed: {missing}")
        else:
            mapped += 1
            passed.update(scenario.cases)
    return AcceptanceCheck(ok=not issues,mapped_scenarios=mapped,passed_cases=len(passed),
                           issues=tuple(issues),scenarios=mapping.scenarios)


def main(
    results: Path = DEFAULT_RESULTS,
    scope: Path = DEFAULT_SCOPE,
    json_output: Annotated[bool,typer.Option("--json")] = False,
    capture: Annotated[bool,typer.Option("--snapshot")] = False,
) -> None:
    root = Path(__file__).resolve().parents[1]
    if capture:
        print(snapshot(root).model_dump_json(indent=2))
        return
    result = check_acceptance(root,root/"docs/acceptance-map.json",root/results,root/scope)
    print(result.model_dump_json(indent=2) if json_output else
          f"qualified automated trace ok={result.ok} scenarios={result.mapped_scenarios}/52; perceptual/vendor certification=False")
    raise typer.Exit(0 if result.ok else 1)


if __name__=="__main__":
    typer.run(main)
