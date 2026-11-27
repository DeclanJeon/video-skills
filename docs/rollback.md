# Conflict-aware rollback

Snapshot: `/home/declan/.local/state/video-skills/20261126T235405/snapshot.json`.
Link changes: `../qa/migration.json`.

1. Compare current global settings/workflow with the migration and any later user edits. Preserve unrelated later changes. Do not copy whole stale settings over current work.
2. Remove only created symlinks whose current readlink exactly equals the recorded target. If a target changed, stop and resolve the conflict.
3. Restore each recorded removed registration symlink only if its path is empty. Resource-only video-production-assets aliases must first pass step 2; never recursively delete a real directory.
4. Restore the old shared Content production pointer from the unique canonical backup, and restore only the old skills-array delta in Pi settings. Other agent instruction paths are symlinks to the shared file; do not replace them with independent copies.
5. Leave this new source directory, original legacy source, phase sources and all concurrent edits intact.
6. Run skill discovery and reload/restart affected harness sessions.

The snapshot includes protected-file hashes for diagnosis, not permission to restore phase sources or the independently developed postproduction package.
