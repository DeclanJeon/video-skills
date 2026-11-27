"""Owned headless process boundary: minimal environment, readonly sources, network namespace and limits."""
from dataclasses import dataclass
from pathlib import Path
import subprocess

from postproduction.common import Frozen, Nonempty
from postproduction.errors import ContractError


@dataclass(frozen=True, slots=True)
class SandboxScope:
    workspace: Path
    owner: str
    read_roots: tuple[Path, ...] = ()
    cpu_seconds: int = 60
    memory_bytes: int = 4294967296
    file_bytes: int = 536870912


@dataclass(frozen=True, slots=True)
class ProcessResult:
    pid: int
    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool
    network_denied: bool = True


class Owner(Frozen):
    owner: Nonempty


@dataclass(frozen=True, slots=True)
class IsolatedProcess:
    scope: SandboxScope

    def prepare(self) -> tuple[Path,Path]:
        """An unowned/nonempty workspace or symlink cannot be taken over by this process."""
        root = self.scope.workspace.absolute()
        for path in (root,*root.parents):
            if path.is_symlink():
                raise ContractError("owner", "symlink workspace refused")
        if not root.parent.is_dir() or not self.scope.owner.strip():
            raise ContractError("owner", "existing parent and explicit owner required")
        if not root.exists():
            root.mkdir(mode=0o700)
        marker = root/".postproduction-owner.json"
        if marker.is_symlink():
            raise ContractError("owner", "symlink owner marker refused")
        if marker.exists():
            actual = Owner.model_validate_json(marker.read_bytes())
            if actual.owner != self.scope.owner:
                raise ContractError("owner", "workspace belongs to another job")
        else:
            if any(root.iterdir()):
                raise ContractError("owner", "nonempty workspace has no matching owner receipt")
            with marker.open("x") as stream:
                _ = stream.write(Owner(owner=self.scope.owner).model_dump_json())
        home = root/".home"
        for name in ("config","cache","data","run"):
            target = home/name
            if target.is_symlink() or home.is_symlink():
                raise ContractError("owner", "private preference path is a symlink")
            target.mkdir(parents=True,exist_ok=True,mode=0o700)
        limits = (self.scope.cpu_seconds,self.scope.memory_bytes,self.scope.file_bytes)
        if any(value <= 0 for value in limits):
            raise ContractError("limits", "positive process resource bounds required")
        helper = root/".owned-limits.py"
        if helper.is_symlink():
            raise ContractError("owner", "resource helper is a symlink")
        code = (
            "# /// script\n# requires-python = \">=3.14\"\n# dependencies = []\n# ///\n"
            "import os,resource,sys\n"
            f"resource.setrlimit(resource.RLIMIT_CPU,({limits[0]},{limits[0]+2}))\n"
            f"resource.setrlimit(resource.RLIMIT_AS,({limits[1]},{limits[1]}))\n"
            f"resource.setrlimit(resource.RLIMIT_FSIZE,({limits[2]},{limits[2]}))\n"
            "os.execv(sys.argv[1],sys.argv[1:])\n"
        )
        _ = helper.write_text(code)
        return root,helper

    def run(self, argv: tuple[str, ...], *, stdin: bytes | None = None, timeout: int = 60) -> ProcessResult:
        """Run only a new owned process; timeout kills this wrapper/namespace, never a user app."""
        if not argv or not Path(argv[0]).is_absolute():
            raise ContractError("process", "explicit absolute executable required")
        root,helper = self.prepare()
        command = ["bwrap","--unshare-net","--unshare-pid","--unshare-ipc","--new-session","--die-with-parent"]
        for path in ("/usr","/lib","/lib64","/etc"):
            if Path(path).exists():
                command += ["--ro-bind",path,path]
        command += ["--proc","/proc","--dev","/dev","--tmpfs","/tmp"]
        executable = Path(argv[0]).absolute()
        visible = (*self.scope.read_roots,root,*(Path(p) for p in ("/usr","/lib","/lib64","/etc")))
        # Explicit command authority admits only this executable, never its unrelated parent directory.
        reads = self.scope.read_roots if any(executable.is_relative_to(p.absolute()) for p in visible) else (*self.scope.read_roots,executable)
        for source in reads:
            if any(p.is_symlink() for p in (source,*source.parents)) or not source.exists():
                raise ContractError("path", "readonly source root must exist without symlinks")
            command += ["--ro-bind",str(source.absolute()),str(source.absolute())]
        command += ["--bind",str(root),str(root),"--ro-bind",str(helper),str(helper),"--chdir",str(root),
                    "--","/usr/bin/python3",str(helper),*argv]
        home = root/".home"
        environment = {
            "PATH":"/usr/bin:/bin","LANG":"C.UTF-8","LC_ALL":"C.UTF-8","HOME":str(home),
            "XDG_CONFIG_HOME":str(home/"config"),"XDG_CACHE_HOME":str(home/"cache"),
            "XDG_DATA_HOME":str(home/"data"),"XDG_RUNTIME_DIR":str(home/"run"),
            "SOUNDCRAFT_NO_PREFS":"1",
        }
        try:
            with subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                  env=environment,close_fds=True) as process:
                timed_out = False
                try:
                    stdout,stderr = process.communicate(stdin,timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    process.kill()
                    stdout,stderr = process.communicate()
                return ProcessResult(process.pid,process.returncode,stdout,stderr,timed_out)
        except OSError as exc:
            raise ContractError("process", "existing sandbox/executable unavailable; inspect before any installation") from exc
