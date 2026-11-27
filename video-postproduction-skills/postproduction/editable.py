"""Copy and relink only exact authorized known native/media bytes, with actual local three-app reopen proof."""
import hashlib
import json
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from postproduction.delivery_io import BundleWriter
from postproduction.delivery_models import DeliveryFile
from postproduction.delivery_scope import required_fonts
from postproduction.editable_inventory import editable_inventory
from postproduction.editable_verify import verify_relinked
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.relink import RelinkContext, relink_value
from postproduction.state_models import PostState


def copy_editable(state: PostState, writer: BundleWriter) -> tuple[DeliveryFile, ...]:
    inventory = editable_inventory(state,writer.contract,writer.root)
    destinations: dict[Path,Path] = {}
    files: list[DeliveryFile] = []
    for pin in inventory.media:
        destination = f"media/{pin.sha256[:16]}-{Path(pin.path).name}"
        if (writer.stage/destination).exists():
            destinations[(writer.root/pin.path).absolute()] = writer.stage/destination
            continue
        files.append(writer.copy(pin,destination))
        destinations[(writer.root/pin.path).absolute()] = writer.stage/destination
    for native in inventory.projects:
        destinations[(writer.root/native.source.path).absolute()] = writer.stage/native.destination
    for native in inventory.projects:
        if native.source not in writer.contract.rights.permitted:
            raise ContractError("rights", "native projection is not in exact receiver distribution scope")
        source = verified_file(writer.root,native.source)
        value = TypeAdapter(JsonValue).validate_json(source.read_bytes())
        relinked = relink_value(value,RelinkContext(source.parent,(writer.stage/native.destination).parent,destinations))
        file = writer.metadata(native.destination,TypeAdapter(JsonValue).dump_json(relinked,indent=2))
        files.append(file.model_copy(update={"source_sha256":native.source.sha256,"role":"native_relinked"}))
    font_records: list[dict[str,JsonValue]] = []
    for font in required_fonts(state,writer.contract,writer.root):
        permission = next(p for p in writer.contract.font_permissions if p.font_sha256==font.sha256)
        if permission.redistribute:
            data = font.path.read_bytes()
            if hashlib.sha256(data).hexdigest()!=font.sha256:
                raise ContractError("font", "font changed before approved redistribution")
            destination = f"fonts/{font.sha256[:16]}{font.path.suffix}"
            target = writer.stage/destination
            target.parent.mkdir(exist_ok=True)
            _ = target.write_bytes(data)
            files.append(DeliveryFile(path=destination,sha256=font.sha256,source_sha256=font.sha256,role="font"))
            files.append(writer.copy(font.license_evidence,f"fonts/{font.sha256[:16]}-license.json"))
        font_records.append({"family":font.family,"style":font.style,"version":font.version,"sha256":font.sha256,
                             "receiver_present_reported":permission.receiver_present,"supplied":permission.redistribute})
    files.append(writer.metadata("records/font-dependencies.json",json.dumps(font_records,indent=2).encode()))
    verify_relinked(inventory,writer.stage,writer.stage.parent/"private-reopen")
    return tuple(files)
