"""Bounded HTTPS GET inside exact declared host scope; called only after coordinator consent checks."""
import hashlib
from http.client import HTTPResponse, HTTPSConnection
import os
from pathlib import Path
import ssl
from urllib.parse import urljoin, urlsplit

from postproduction.environment.consent_models import InstallationPlan
from postproduction.errors import ContractError


def write_body(response: HTTPResponse, part: Path, plan: InstallationPlan) -> None:
    """Stream bounded bytes, checking exact expected digest before publishing any artifact."""
    total = 0
    digest = hashlib.sha256()
    with part.open("xb") as out:
        while chunk := response.read(min(1048576,plan.max_download_bytes+1)):
            total += len(chunk)
            if total > plan.max_download_bytes:
                raise ContractError("limit", "download exceeds exact plan byte limit")
            digest.update(chunk)
            _ = out.write(chunk)
        out.flush()
        os.fsync(out.fileno())
    if digest.hexdigest() != plan.source_sha256:
        raise ContractError("hash", "downloaded artifact differs from approved exact digest")


def fetch_artifact(plan: InstallationPlan, cache: Path) -> Path:
    """No cookies/credentials/proxy/media uploads; redirects require explicit host scope."""
    if cache.exists():
        raise ContractError("existing", "existing cache needs inspection/reconciliation")
    if not cache.parent.is_dir() or any(p.is_symlink() for p in (cache,*cache.parents)):
        raise ContractError("path", "cache parent must be existing, owned and nonsymlink")
    cache.mkdir(mode=0o700)
    part = cache/".download.part"
    target = cache/"artifact.tar"
    url = plan.source_url
    try:
        for _ in range(6):
            address = urlsplit(url)
            if (address.hostname is None or address.scheme != "https"
                or address.hostname not in plan.network_hosts or address.username or address.password
                or address.port not in {None,443}):
                raise ContractError("network", "download/redirect is outside exact HTTPS host scope")
            connection = HTTPSConnection(address.hostname,timeout=30,context=ssl.create_default_context())
            try:
                path = address.path or "/"
                if address.query:
                    path += "?"+address.query
                connection.request("GET",path,headers={"User-Agent":"video-postproduction-skills/0.1"})
                response = connection.getresponse()
                if response.status in {301,302,303,307,308}:
                    location = response.getheader("Location")
                    if location is None:
                        raise ContractError("network", "redirect has no explicit destination")
                    url = urljoin(url,location)
                    continue
                if response.status != 200:
                    raise ContractError("fetch", f"official artifact HTTP status {response.status}")
                write_body(response,part,plan)
                os.link(part,target)
                part.unlink()
                directory = os.open(cache,os.O_RDONLY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
                return target
            finally:
                connection.close()
        raise ContractError("network", "download exceeded bounded redirect count")
    except (OSError,ValueError) as exc:
        raise ContractError("fetch", "bounded artifact retrieval failed; inspect owned cache before retry") from exc
    finally:
        if part.exists():
            part.unlink()
