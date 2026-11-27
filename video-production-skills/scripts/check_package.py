#!/usr/bin/env python3
"""Check local role packaging and schema drift; not agent behavior or provider QA."""
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import TypeAdapter, ValidationError
from production.models import Authority, Binding, Capability, Frozen, Prepared, State, Take, Review, JoinReview, FlowReview, Handoff
from production.scope import ScopeGrant
from production.upstream import CoverageEnvelope


class Package(Frozen):
    name: str
    version: str
    status: str
    entry_skill: str
    automatic_invocation: bool
    skills: tuple[str, ...]
    runtime: str
    external_execution: bool


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings: list[str] = []
    try:
        package = Package.model_validate_json((root/"manifest.json").read_bytes())
        if len(package.skills) != 5 or len(set(package.skills)) != 5 or package.entry_skill not in package.skills:
            findings.append("invalid role set/entry")
        if package.automatic_invocation or package.external_execution:
            findings.append("unreleased package cannot enable execution/auto invocation")
        for role in package.skills:
            if re.fullmatch(r"[a-z][a-z0-9-]+", role) is None:
                findings.append("unsafe role name")
                continue
            file = root/role/"SKILL.md"
            text = file.read_text()
            if not text.startswith("---\n") or text.count("\n---\n") < 1:
                findings.append(f"{role}: missing frontmatter")
                continue
            front = text.split("---", 2)[1]
            fields = dict(line.split(":", 1) for line in front.strip().splitlines())
            if fields.get("name", "").strip() != role or fields.get("disable-model-invocation", "").strip() != "true":
                findings.append(f"{role}: identity/invocation mismatch")
            if not fields.get("description", "").strip(' \"').startswith("Use when"):
                findings.append(f"{role}: missing routing description")
            for link in re.findall(r"\]\(([^)]+)\)", text):
                path = (file.parent/link.split("#")[0]).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    findings.append(f"{role}: invalid resource {link}")
        for name, model in (("state",State),("prepared",Prepared),("take",Take),("review",Review),("join",JoinReview),("flow",FlowReview),("handoff",Handoff),("authority",Authority),("capability",Capability),("scope-grant",ScopeGrant),("coverage",CoverageEnvelope)):
            if json.loads((root/f"schemas/{name}.schema.json").read_text()) != model.model_json_schema():
                findings.append(f"{name}: schema drift")
        if json.loads((root/"schemas/bindings.schema.json").read_text()) != TypeAdapter(tuple[Binding,...]).json_schema():
            findings.append("bindings: schema drift")
        result = {"skills": len(package.skills), "findings": findings, "scope": "metadata, linked files and boundary schemas only"}
    except (OSError, ValidationError, json.JSONDecodeError) as exc:
        result = {"skills": 0, "findings": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["findings"]))


if __name__ == "__main__":
    raise SystemExit(main())
