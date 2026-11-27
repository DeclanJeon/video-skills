"""Parse the artifact and cut identifiers defined in DES-03."""
from dataclasses import dataclass
import re


class RefError(ValueError):
    """An identifier does not conform to the document contract."""


@dataclass(frozen=True)
class Ref:
    prefix: str
    number: str | None
    suffix: str | None
    version: int | None
    anchor: str | None
    item: str | None
    draft: bool = False


_NUMBER = r'(?!00)[0-9]{2}'
_ATOM = r'[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*'
_SIMPLE = frozenset('BRF BOR SYN PLT SCR WLD SND DNT CNT CTY STB EDL'.split())
_NUMBERED = frozenset('BMK CHR LOC SET ENV PRP VOC AMB SFX MUS CAM LGT LOOK VFX SHT GEN VPR APR RUL'.split())
_REF = re.compile(rf'(?P<id>{_ATOM})(?:@(?P<version>v[1-9][0-9]*|draft))?(?:#(?P<anchor>{_ATOM}))?(?:\.(?P<item>{_ATOM}))?')
_CUT = re.compile(rf'S({_NUMBER})-C({_NUMBER})(?:\.b([1-9][0-9]*))?')


def parse_ref(ref: str) -> Ref:
    match = _REF.fullmatch(ref)
    if not match:
        raise RefError(ref)
    artifact, pin, anchor, item = match.groups()
    prefix, sep, tail = artifact.partition('-')
    number = suffix = None
    if prefix in _SIMPLE and not sep:
        pass
    elif prefix in _NUMBERED and re.fullmatch(_NUMBER, tail):
        number = tail
    elif prefix == 'WRD' and re.fullmatch(rf'{_NUMBER}[a-z]', tail):
        number, suffix = tail[:2], tail[2:]
    elif prefix == 'TAK' and re.fullmatch(rf'{_NUMBER}-[1-9][0-9]*', tail):
        number, suffix = tail[:2], tail[2:]
    elif prefix == 'QAR' and re.fullmatch(r'[1-5F]', tail):
        suffix = '-F' if tail == 'F' else None
        number = tail if tail != 'F' else None
    elif prefix in {'IMG', 'REF'} and tail:
        suffix = '-' + tail
    else:
        raise RefError(ref)
    return Ref(prefix, number, suffix, int(pin[1:]) if pin and pin != 'draft' else None,
               anchor, item, draft=pin == 'draft')


def parse_cut(value: str) -> tuple[int, int, int | None]:
    match = _CUT.fullmatch(value)
    if not match:
        raise RefError(value)
    scene, cut, segment = match.groups()
    return int(scene), int(cut), int(segment) if segment else None
