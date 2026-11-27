"""모델 사실 레지스트리 읽기와 제출 차단 판정 (RR-6)."""
import json, datetime, pathlib
REQUIRED = ('max_duration_s', 'aspects')
def load(path): return json.loads(pathlib.Path(path).read_text())
def effective_status(fact, ttl_days, today=None):
    today = today or datetime.date.today()
    source = fact.get('source')
    if fact.get('status') != 'verified' or not isinstance(source, str) or not source.strip():
        return 'unverified'
    try:
        age = (today - datetime.date.fromisoformat(fact.get('verified_at'))).days
    except (TypeError, ValueError):
        return 'unverified'
    if age < 0:
        return 'unverified'
    return 'expired' if age > ttl_days else 'verified'
def submission_gate(registry, accepted_risk=None, today=None):
    """-> (allowed, reasons). max_duration_s·aspects 가 verified 가 아니면 차단, accepted_risk 가 있으면 허용(사유 기록)."""
    ttl = registry.get('ttl_days', 30); reasons = []
    for k in REQUIRED:
        st = effective_status(registry.get('facts', {}).get(k, {}), ttl, today)
        if st != 'verified': reasons.append(f'{k}: {st}')
    if not reasons: return True, []
    if accepted_risk: return True, [f'accepted_risk="{accepted_risk}"'] + reasons
    return False, reasons
def initial_audio_path(registry, today=None):
    f = registry.get('facts', {}).get('native_audio', {})
    ok = effective_status(f, registry.get('ttl_days', 30), today) == 'verified' and f.get('value') is True
    return 'native' if ok else 'separate'
