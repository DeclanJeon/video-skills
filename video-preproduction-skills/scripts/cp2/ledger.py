"""Single-writer, versioned artifact registry."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from cp2.ids import parse_ref


def artifact_key(ref: str) -> str:
    return ref.split('@', 1)[0].split('#', 1)[0].split('.', 1)[0]


class Ledger:
    def __init__(self, root: Path, artifacts: dict):
        self.root = root
        self.artifacts = artifacts

    @classmethod
    def load(cls, root: Path) -> 'Ledger':
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError('project root must be a directory')
        path = root / 'ledger.json'
        if not path.exists():
            return cls(root, {})
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('schema_version') != 1 or not isinstance(data.get('artifacts'), dict):
            raise ValueError('invalid ledger schema')
        return cls(root, data['artifacts'])

    def _save(self, artifacts: dict) -> None:
        path = self.root / 'ledger.json'
        with NamedTemporaryFile(dir=self.root, mode='w', encoding='utf-8', delete=False) as out:
            temp = Path(out.name)
            try:
                json.dump({'schema_version': 1, 'artifacts': artifacts}, out, ensure_ascii=False, indent=2)
                out.write('\n')
                out.flush()
                os.fsync(out.fileno())
            except BaseException:
                temp.unlink(missing_ok=True)
                raise
        try:
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)
        self.artifacts = artifacts

    def status(self, artifact_id: str) -> str:
        versions = self.artifacts.get(artifact_id)
        return versions[-1]['status'] if versions else 'missing'

    def resolve(self, value: str) -> dict | None:
        pin = parse_ref(value)
        if pin.version is None:
            return None
        return next((v for v in self.artifacts.get(artifact_key(value), [])
                     if v['version'] == pin.version), None)

    def register(self, artifact_id: str, path: Path | str, version: int, consumes: list[str]) -> None:
        parse_ref(artifact_id)
        if artifact_id != artifact_key(artifact_id) or type(version) is not int or version < 1:
            raise ValueError('registration needs a bare artifact ID and a positive version')
        initial = self.artifacts.get(artifact_id, [])
        if version != (initial[-1]['version'] + 1 if initial else 1):
            raise ValueError('version must be the next monotonic version')
        for ref in consumes:
            item = self.resolve(ref)
            if artifact_key(ref) == artifact_id or not item or item['status'] != 'current':
                raise ValueError(f'dependency must be a different current pinned artifact: {ref}')
        file = (self.root / path).resolve(strict=True)
        relative = file.relative_to(self.root)
        if file == self.root / 'ledger.json':
            raise ValueError('ledger cannot register itself')
        updated = deepcopy(self.artifacts)
        history = updated.setdefault(artifact_id, [])
        if history:
            previous = history[-1]
            self._propagate(updated, f'{artifact_id}@v{previous["version"]}')
            previous['status'] = 'superseded'
        history.append(dict(version=version, path=relative.as_posix(), sha256=sha256(file.read_bytes()).hexdigest(),
                            consumes=list(dict.fromkeys(consumes)), status='current'))
        self._save(updated)

    @staticmethod
    def _propagate(artifacts: dict, changed: str) -> list[str]:
        queue, visited, stale = [changed], set(), []
        while queue:
            value = queue.pop(0)
            if value in visited:
                continue
            visited.add(value)
            pin = parse_ref(value)
            for artifact_id, history in sorted(artifacts.items()):
                current = history[-1]
                if current['status'] != 'current':
                    continue
                for ref in current['consumes']:
                    other = parse_ref(ref)
                    if (artifact_key(ref) != artifact_key(value)
                            or (pin.version is not None and pin.version != other.version)
                            or (pin.anchor and other.anchor and pin.anchor != other.anchor)
                            or (pin.item and other.item and pin.item != other.item)):
                        continue
                    current['status'] = 'stale'
                    stale.append(artifact_id)
                    queue.append(f'{artifact_id}@v{current["version"]}')
                    break
        return sorted(stale)

    def mark_stale(self, changed_ref: str) -> list[str]:
        if parse_ref(changed_ref).draft:
            return []
        updated = deepcopy(self.artifacts)
        result = self._propagate(updated, changed_ref)
        if result:
            self._save(updated)
        return result
