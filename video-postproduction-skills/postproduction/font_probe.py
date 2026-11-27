"""Readonly exact existing font face/version/charset checks, never fc-match fallback or installation."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess

from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.style_models import ExistingFont


@dataclass(frozen=True,slots=True)
class FontFacts:
    family: str
    charset: tuple[tuple[int,int], ...]


def verify_font(font: ExistingFont, root: Path) -> FontFacts:
    """Physical exact font plus fontconfig face facts; license evidence is supplied/reported, not authenticated."""
    _ = verified_file(root,font.license_evidence)
    if (any(p.is_symlink() for p in (font.path,*font.path.parents)) or not font.path.is_file()
        or hashlib.sha256(font.path.read_bytes()).hexdigest() != font.sha256):
        raise ContractError("font", "existing actual font file/hash is missing/changed; ask before any new setup")
    try:
        result = subprocess.run(["fc-query","-i",str(font.face_index),"-f",
            "%{family}\n%{style}\n%{fontversion}\n%{charset}\n",str(font.path)],
            capture_output=True,check=True,text=True,timeout=10)
        family,style,version,charset = result.stdout.splitlines()
        if (font.family not in family.split(",") or font.style not in style.split(",")
            or int(version) != font.version):
            raise ContractError("font", "actual requested font face/style/version not present; fallback is not identical design")
        ranges: list[tuple[int,int]] = []
        for value in charset.split():
            endpoints = value.split("-")
            low,high = int(endpoints[0],16),int(endpoints[-1],16)
            if not 0 <= low <= high <= 0x10ffff:
                raise ContractError("font", "font charset returned invalid Unicode range")
            ranges.append((low,high))
    except (OSError,ValueError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("font", "actual font face/charset could not be inspected") from exc
    if hashlib.sha256(font.path.read_bytes()).hexdigest() != font.sha256:
        raise ContractError("font", "actual font changed while inspecting it")
    return FontFacts(font.family,tuple(ranges))
