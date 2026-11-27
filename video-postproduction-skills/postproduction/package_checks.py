"""Executable package/source-schema/link/role permission checks; no claimed model-pressure test or skill installation."""
from pathlib import Path
import re
import sys

from pydantic import JsonValue, TypeAdapter, ValidationError

from postproduction.package_models import PackageCheck, PackageManifest, ROLE_IDS
from postproduction.schema_catalog import SCHEMAS

LINK = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)")


def check_package(root: Path) -> PackageCheck:
    issues: list[str] = []
    try:
        manifest = PackageManifest.model_validate_json((root/"manifest.json").read_bytes())
    except (OSError,ValidationError) as exc:
        return PackageCheck(ok=False,roles=0,issues=(f"manifest missing/invalid: {exc}",))
    if tuple(r.id for r in manifest.roles)!=ROLE_IDS:
        issues.append("exact eight role identities/order required")
    for role in manifest.roles:
        if role.id not in ROLE_IDS or role.path!=f"{role.id}/SKILL.md":
            issues.append(f"noncanonical/out-of-package role path: {role.id}")
            continue
        path = root/role.path
        if not path.is_file() or path.is_symlink() or path.parent.is_symlink():
            issues.append(f"missing actual role: {role.id}")
            continue
        text = path.read_text()
        header = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)",text,re.DOTALL)
        frontmatter = "" if header is None else header.group(1)
        if (re.search(rf"(?m)^name: {re.escape(role.id)}$",frontmatter) is None
            or re.search(r"(?m)^disable-model-invocation: true$",frontmatter) is None):
            issues.append(f"role invocation frontmatter incomplete: {role.id}")
        for match in LINK.finditer(text):
            link = match.group(1)
            if "://" not in link and not (path.parent/link).exists():
                issues.append(f"broken role link: {role.id}:{link}")
        if any(p.suffix.lower() in {".mogrt",".prgraphic",".ttf",".otf",".ttc"} for p in path.parent.rglob("*")):
            issues.append(f"raw template/font redistribution in role: {role.id}")
    entry = root/manifest.entry
    if not entry.is_file():
        issues.append("real local package entry missing")
    else:
        for match in LINK.finditer(entry.read_text()):
            link = match.group(1)
            if "://" not in link and not (entry.parent/link).exists():
                issues.append(f"broken entry link: {link}")
    if set(manifest.schemas)!={f"schemas/{name}" for name in SCHEMAS}:
        issues.append("schema inventory differs from runtime catalog")
    adapter = TypeAdapter(JsonValue)
    for name,model in SCHEMAS.items():
        try:
            actual = adapter.validate_json((root/"schemas"/name).read_bytes())
            expected = adapter.validate_python(model.model_json_schema())
            if actual!=expected:
                issues.append(f"runtime schema drift: {name}")
        except (OSError,ValidationError):
            issues.append(f"schema missing/invalid: {name}")
    for example in manifest.examples:
        if not (root/example).is_file():
            issues.append(f"example missing: {example}")
    return PackageCheck(ok=not issues,roles=len(manifest.roles),issues=tuple(issues))


def main() -> int:
    if any(a not in {"--json"} for a in sys.argv[1:]):
        print("usage: python3 scripts/check_package.py [--json]")
        return 2
    result = check_package(Path(__file__).resolve().parents[1])
    print(result.model_dump_json(indent=2))
    return 0 if result.ok else 1


if __name__=="__main__":
    raise SystemExit(main())
