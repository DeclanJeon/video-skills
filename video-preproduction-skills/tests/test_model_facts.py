import pathlib, sys, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
from cp2.model_facts import submission_gate, initial_audio_path, effective_status
D = datetime.date(2026, 11, 25)
def reg(dur='verified', asp='verified', when='2026-11-20', audio=None):
    f = {'max_duration_s': {'value': 10, 'status': dur, 'verified_at': when, 'source': 'doc:fixture'}, 'aspects': {'value': ['9:16'], 'status': asp, 'verified_at': when, 'source': 'doc:fixture'}}
    if audio: f['native_audio'] = audio
    return {'facts': f, 'ttl_days': 30}
def test_verified_passes(): assert submission_gate(reg(), today=D) == (True, [])
def test_unverified_blocks():
    ok, why = submission_gate(reg(dur='unverified'), today=D); assert not ok and 'max_duration_s: unverified' in why
def test_expired_blocks():
    ok, why = submission_gate(reg(when='2026-09-01'), today=D); assert not ok and any('expired' in w for w in why)
def test_accepted_risk_allows_but_records():
    ok, why = submission_gate(reg(asp='unverified'), accepted_risk='사용자: 근사 비율 감수', today=D); assert ok and why[0].startswith('accepted_risk')
def test_missing_fact_is_unverified(): assert effective_status({}, 30, D) == 'unverified'
def test_audio_defaults_to_separate_when_unverified():
    assert initial_audio_path(reg(), D) == 'separate'
    assert initial_audio_path(reg(audio={'value': True, 'status': 'verified', 'verified_at': '2026-11-20', 'source': 'doc:fixture'}), D) == 'native'


def test_source_required_and_future_date_rejected():
    assert effective_status({'status': 'verified', 'verified_at': '2026-11-20'}, 30, D) == 'unverified'
    assert effective_status({'status': 'verified', 'verified_at': '2026-11-26', 'source': 'doc:fixture'}, 30, D) == 'unverified'


def test_unsupported_native_audio_not_inferred_from_string():
    audio = {'value': 'unsupported', 'status': 'verified', 'verified_at': '2026-11-20', 'source': 'doc:fixture'}
    assert initial_audio_path(reg(audio=audio), D) == 'separate'
