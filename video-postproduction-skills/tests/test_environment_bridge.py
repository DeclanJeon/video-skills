"""Host installation facts mirrored narrowly to one canonical project namespace, before mutable readiness diagnostics."""
import json
import pytest
from conftest import require
from test_ledger import built,project,prepare
from test_installers import prepared
from test_install_consent import authority


def context(h,p):
    return require("environment.observation_models","InstallContext")(id="INSTALL-RUN-1",host_id=h.host_id,
        tool=p.tool,plan_digest=require("environment.consent","plan_digest")(p),evidence_kind="contract_fixture")


def test_environment_bridge_when_fixture_installer_facts_preserve_other_namespaces(project):
    path,store,state,production=prepare(project);store.initialize(state)
    root=path.parent/"owned-installer";root.mkdir()
    h,p,driver,events,runner=prepared(root)
    bridge=require("environment.project_bridge","InstallProjectBridge")(store,context(h,p))
    result=require("environment.provision","Provisioner")(driver,bridge.record).execute(p,h,authority(p,h))
    records=store.read_recorded().environment_events
    assert result.status=="ready"
    assert records[-1].event.phase=="ready"
    assert records[-1].evidence_kind=="contract_fixture"
    assert records[-1].real_media_ready is False
    assert json.loads(path.read_text())["production"]==production
    assert json.loads(path.read_text())["foreign"]["owner"]=="other-terminal"


def event():
    return require("environment.install_models","InstallEvent")(
        phase=require("environment.models","EnvStatus").INSTALLED,installed=True,detail="known actual fixture effect; not readiness")


def prepared_observation():
    from test_install_consent import missing_host,plan
    h=missing_host();p=plan(h)
    return require("environment.observation_models","EnvironmentObservation")(
        context=context(h,p),sequence=1,event=event())


def test_environment_when_source_lost_installed_fact_still_commits(project):
    path,store,state,production=prepare(project);store.initialize(state)
    (path.parent/"source1.mp4").unlink()
    result=store.record_environment(prepared_observation(),0)
    assert result.inputs_ready is False
    assert store.read_recorded().environment_events[-1].event.installed is True


def test_environment_when_diagnostic_crashes_installed_fact_is_already_durable(project,monkeypatch):
    path,store,state,production=prepare(project);store.initialize(state)
    monkeypatch.setattr(store,"input_issues",lambda state:(_ for _ in ()).throw(RuntimeError("diagnostic crash")))
    with pytest.raises(RuntimeError):store.record_environment(prepared_observation(),0)
    assert store.read_recorded().environment_events[-1].event.installed is True


def test_environment_when_generic_transaction_cannot_forge_ready_history(project):
    path,store,state,production=prepare(project);store.initialize(state)
    with pytest.raises(require("errors","ContractError")):
        with store.transaction(0) as tx:
            tx.state=tx.state.model_copy(update={"environment_events":(prepared_observation(),)})


def test_environment_when_initial_state_cannot_invent_installed_history(project):
    path,store,state,production=prepare(project)
    state=state.model_copy(update={"environment_events":(prepared_observation(),)})
    with pytest.raises(require("errors","ContractError")):store.initialize(state)
