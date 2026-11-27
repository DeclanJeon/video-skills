from copy import deepcopy
from datetime import date, timedelta
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import pytest
from e2e_trace_check import check_traces


PACKAGE = Path(__file__).resolve().parents[1]


def put(root, path, data):
    (root / path).write_bytes(data)
    return {'path': path, 'sha256': sha256(data).hexdigest()}


@pytest.fixture
def synthetic_packet(tmp_path):
    """Invented sessions, timestamps, sources, provider facts and endpoints; not a formal evaluation."""
    sources = {v: put(tmp_path, f'{v}.snapshot', f'synthetic {v} source'.encode()) for v in ('v1', 'v2')}
    target = {'transport': 'synthetic-api', 'model': 'synthetic-media', 'endpoint': 'synthetic-generate'}
    receipt = dict(target, ttl_days=30, facts={
        name: dict(value=value, source='experiment:EXP-synthetic', status='verified',
                   verified_at=date.today().isoformat())
        for name, value in {'max_duration_s': 10, 'aspects': ['9:16', '16:9'], 'reference_images_max': 4,
                            'native_audio': True, 'dialogue_languages': ['ko']}.items()
    }, source_evidence=put(tmp_path, 'capabilities.txt', b'Synthetic archived provider response'))
    provider_receipt = put(tmp_path, 'provider.json', json.dumps(receipt).encode())
    rows = []
    for scenario in ('X-1', 'X-2', 'X-3'):
        brief = put(tmp_path, f'{scenario}.md', (PACKAGE / 'evals' / 'e2e' / f'{scenario}.md').read_bytes())
        for variant, gate in [('v1', 'S08'), ('v2', 'QA4')]:
            lane = f'{scenario}-{variant}'
            markers = ('wall_start', 'conti_start', 'conti_end', 'formal_endpoint')
            row = dict(
                scenario=scenario, variant=variant, session_id=lane, observer_id='synthetic-observer',
                model='synthetic-evaluator', reasoning='fixed', brief=brief.copy(), source=sources[variant].copy(),
                timing_protocol='wo13-preflight-v1', clock_id='synthetic-monotonic',
                events=[dict(event=name, tick_ns=index * 2_000_000_000, line=index + 1)
                        for index, name in enumerate(markers)],
                endpoint=dict(gate=gate, verdict='REVISE' if variant == 'v1' else 'PASS',
                              artifact=put(tmp_path, f'{lane}.snapshot', f'synthetic {gate} {lane}'.encode())),
                provider=target.copy(), provider_receipt=provider_receipt.copy(),
            )
            log = [dict(event=e['event'], tick_ns=e['tick_ns'], session_id=row['session_id'],
                        observer_id=row['observer_id'], clock_id=row['clock_id']) for e in row['events']]
            log[0].update(source_sha256=row['source']['sha256'], brief_sha256=row['brief']['sha256'])
            log[-1].update(gate=gate, verdict=row['endpoint']['verdict'],
                           artifact_sha256=row['endpoint']['artifact']['sha256'])
            row['event_log'] = put(tmp_path, f'{lane}.log', '\n'.join(map(json.dumps, log)).encode())
            rows.append(row)
    return tmp_path, rows


def test_synthetic_trace_packet_only_checks_claimed_evidence(synthetic_packet):
    result = check_traces(*synthetic_packet)
    assert result['status'] == 'trace_checked'
    assert result['lanes']['X-1/v1'] == dict(elapsed_s=6, conti_s=2, gate='S08', verdict='REVISE')
    assert result['lanes']['X-1/v2']['gate'] == 'QA4'
    assert len(result['lanes']) == 6


@pytest.mark.parametrize(('change', 'issue'), [
    (lambda r: r.pop(), 'missing lane'),
    (lambda r: r.append(deepcopy(r[0])), 'duplicate lane'),
    (lambda r: r[0].update(session_id=r[1]['session_id']), 'duplicate session_id'),
    (lambda r: r[0].update(observer_id=r[1]['session_id']), 'observer_id is an execution session'),
    (lambda r: r[0].update(observer_id=' '), 'observer_id'),
    (lambda r: r[0].pop('session_id'), 'session_id'),
    (lambda r: r[0].update(model='other'), 'evaluator settings'),
    (lambda r: r[0].update(reasoning='other'), 'evaluator settings'),
    (lambda r: r[0].update(timing_protocol='planned-runtime'), 'timing_protocol'),
    (lambda r: r[0].pop('clock_id'), 'clock_id'),
    (lambda r: r[0]['events'].pop(), 'event sequence'),
    (lambda r: r[0]['events'].reverse(), 'event sequence'),
    (lambda r: r[0]['events'][3].update(tick_ns=r[0]['events'][2]['tick_ns']), 'ticks'),
    (lambda r: r[0]['events'][2].update(tick_ns=r[0]['events'][1]['tick_ns']), 'ticks'),
    (lambda r: r[0]['events'][2].update(tick_ns=True), 'ticks'),
    (lambda r: r[0]['events'][2].update(tick_ns=float('nan')), 'ticks'),
    (lambda r: r[0]['events'][3].update(line=500), 'event log line'),
    (lambda r: r[0]['events'][3].update(line=r[0]['events'][2]['line']), 'event log line'),
    (lambda r: r[0]['endpoint'].update(gate='QA4'), 'expected S08'),
    (lambda r: r[1]['endpoint'].update(gate='QA2', verdict='BLOCKED'), 'expected QA4'),
    (lambda r: r[1]['endpoint'].update(verdict='UNVERIFIED'), 'reached verdict'),
    (lambda r: r[0].pop('provider_receipt'), 'provider_receipt'),
    (lambda r: r[0]['provider'].update(model='other'), 'provider target'),
    (lambda r: r[0].update(source=r[1]['source']), 'source differs within v1'),
    (lambda r: r[0].update(brief=r[2]['brief']), 'unchanged X-1 brief'),
])
def test_rejects_missing_or_incomparable_claims(synthetic_packet, change, issue):
    root, rows = synthetic_packet
    change(rows)
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert result['lanes'] == {}
    assert any(issue in message for message in result['issues']), result


@pytest.mark.parametrize(('change', 'field'), [
    (lambda root, row: row['events'][1].update(tick_ns=1), 'tick_ns'),
    (lambda root, row: row.update(session_id='other-session'), 'session_id'),
    (lambda root, row: row.update(observer_id='other-observer'), 'observer_id'),
    (lambda root, row: row.update(clock_id='different-clock'), 'clock_id'),
    (lambda root, row: row.update(source=put(root, 'other-source', b'replaced source')), 'source_sha256'),
    (lambda root, row: row['endpoint'].update(artifact=put(root, 'other-artifact', b'new bytes')), 'artifact_sha256'),
])
def test_claims_match_hashed_observer_event_log(synthetic_packet, change, field):
    root, rows = synthetic_packet
    change(root, rows[0])
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert any('event log line' in issue and field in issue for issue in result['issues'])


@pytest.mark.parametrize('artifact', ['source', 'brief', 'event_log', 'endpoint', 'provider_receipt'])
def test_rehashes_current_bytes_and_rejects_tampering(synthetic_packet, artifact):
    root, rows = synthetic_packet
    ref = rows[0]['endpoint']['artifact'] if artifact == 'endpoint' else rows[0][artifact]
    (root / ref['path']).write_bytes(b'tampered after capture')
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert any(f'{artifact}' in issue and 'SHA-256 mismatch' in issue for issue in result['issues'])


@pytest.mark.parametrize(('change', 'issue'), [
    (lambda p: p['facts']['aspects'].update(value=[]), 'aspects'),
    (lambda p: p['facts']['native_audio'].update(value='unknown'), 'native_audio'),
    (lambda p: p['facts'].pop('dialogue_languages'), 'dialogue_languages'),
    (lambda p: p['facts']['reference_images_max'].update(status='unverified'), 'reference_images_max'),
    (lambda p: p['facts']['max_duration_s'].update(source=' '), 'max_duration_s'),
    (lambda p: p['facts']['max_duration_s'].update(verified_at=(date.today() - timedelta(days=31)).isoformat()),
     'max_duration_s'),
    (lambda p: p['facts']['max_duration_s'].update(verified_at=(date.today() + timedelta(days=1)).isoformat()),
     'max_duration_s'),
    (lambda p: p.pop('source_evidence'), 'source_evidence'),
])
def test_hash_match_alone_does_not_make_a_provider_receipt_usable(synthetic_packet, change, issue):
    root, rows = synthetic_packet
    path = rows[0]['provider_receipt']['path']
    receipt = json.loads((root / path).read_text())
    change(receipt)
    rows[0]['provider_receipt'] = put(root, path, json.dumps(receipt).encode())
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert any(issue in message for message in result['issues']), result


def test_provider_targets_must_match_within_pair(synthetic_packet):
    root, rows = synthetic_packet
    receipt = json.loads((root / rows[0]['provider_receipt']['path']).read_text())
    receipt['endpoint'] = rows[0]['provider']['endpoint'] = 'other'
    rows[0]['provider_receipt'] = put(root, 'other-provider.json', json.dumps(receipt).encode())
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert any('provider target differs within pair' in issue for issue in result['issues'])


def test_provider_source_evidence_is_rehashed(synthetic_packet):
    root, rows = synthetic_packet
    (root / 'capabilities.txt').write_text('changed evidence')
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert any('source_evidence: SHA-256 mismatch' in issue for issue in result['issues'])


@pytest.mark.parametrize('kind', ['missing', 'empty', 'absolute', 'parent', 'symlink'])
def test_unusable_endpoint_artifacts_are_rejected(synthetic_packet, kind):
    root, rows = synthetic_packet
    ref = rows[0]['endpoint']['artifact']
    path = root / ref['path']
    if kind == 'missing':
        path.unlink()
    elif kind == 'empty':
        path.write_bytes(b'')
    elif kind == 'absolute':
        ref['path'] = str(path)
    elif kind == 'parent':
        ref['path'] = f'../{root.name}/{path.name}'
    elif kind == 'symlink':
        outside = root.parent / f'{root.name}-outside'
        path.rename(outside)
        path.symlink_to(outside)
    result = check_traces(root, rows)
    assert result['status'] == 'unverified'
    assert any('endpoint.artifact' in issue for issue in result['issues'])


def run_cli(root, traces):
    return subprocess.run([sys.executable, str(PACKAGE / 'scripts' / 'e2e_trace_check.py'),
                           '--project', str(root), '--traces', traces], capture_output=True, text=True)


def test_cli_rejects_archived_text_only_pilot():
    result = run_cli(PACKAGE, 'qa/wo-13/readonly-pilot.md')
    assert result.returncode == 2
    assert 'JSON trace array' in result.stderr


def test_cli_synthetic_packet_and_blocked_text_only_lane(synthetic_packet):
    root, rows = synthetic_packet
    path = root / 'traces.json'
    path.write_text(json.dumps(rows))
    result = run_cli(root, 'traces.json')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['status'] == 'trace_checked'

    rows[1]['endpoint'] = {'gate': 'QA2', 'verdict': 'BLOCKED'}
    rows[1]['events'].pop()  # A text-only stop has no formal endpoint event.
    path.write_text(json.dumps(rows))
    result = run_cli(root, 'traces.json')
    assert result.returncode == 3, result.stderr
    assert json.loads(result.stdout)['status'] == 'unverified'
