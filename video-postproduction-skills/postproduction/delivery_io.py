"""Owned bundle bytes and privacy scan; no uploads, credentials, silent overwrite or implicit source redistribution."""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import shutil

from postproduction.common import Pin
from postproduction.delivery_models import DeliveryContract, DeliveryFile
from postproduction.errors import ContractError
from postproduction.files import verified_file


@dataclass(frozen=True,slots=True)
class BundleWriter:
    stage: Path
    root: Path
    contract: DeliveryContract

    def copy(self, pin: Pin, destination: str) -> DeliveryFile:
        if pin not in self.contract.rights.permitted:
            raise ContractError("rights", "exact native/media/output bytes are not in the receiver distribution grant")
        source = verified_file(self.root,pin)
        target = self.stage/Pin.relative_path(destination)
        target.parent.mkdir(parents=True,exist_ok=True)
        with source.open("rb") as incoming,target.open("xb") as outgoing:
            shutil.copyfileobj(incoming,outgoing)
            outgoing.flush()
            os.fsync(outgoing.fileno())
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual!=pin.sha256:
            raise ContractError("hash", "source changed while copying; incomplete bundle is not published")
        return DeliveryFile(path=destination,sha256=actual,source_sha256=pin.sha256,role="media")

    def metadata(self, destination: str, data: bytes) -> DeliveryFile:
        text = data.decode()
        if ("/home/" in text or "/tmp/" in text or "signed_url" in text.lower()
            or "access_token" in text.lower() or "api_key" in text.lower() or "bearer " in text.lower()):
            raise ContractError("privacy", "delivery metadata contains private absolute path/credential/signed URL field")
        target = self.stage/Pin.relative_path(destination)
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("xb") as stream:
            _ = stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return DeliveryFile(path=destination,sha256=hashlib.sha256(data).hexdigest(),source_sha256=None,role="metadata")
