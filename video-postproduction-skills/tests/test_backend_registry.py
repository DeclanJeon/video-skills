"""Native dispatch consumes actual multi-route discovery; installed outside PATH is reused, not ignored for /usr/bin."""
from pathlib import Path
from conftest import require
from test_ledger import built,project,prepare
from test_revisions import order_for
from test_environment import host


def test_registry_when_same_program_is_discovered_at_existing_other_location_reuses_it(project,monkeypatch):
    path,store,state,production=prepare(project)
    import postproduction.backend_registry as registry
    snapshot=host(observation={"cli_path":"/opt/already-present/filmcraft-cli","known_app_locations":["/opt/already-present"]})
    monkeypatch.setattr(registry,"inspect_host",lambda reqs:snapshot,raising=False)
    backend=require('backend_registry','for_order')(store,order_for(state),path.parent/'owned-native')
    assert backend.binary==Path('/opt/already-present/filmcraft-cli')
