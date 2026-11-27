from copy import deepcopy

import pytest
from e2e_grade import grade


@pytest.fixture
def packet(tmp_path):
    (tmp_path / 'evidence.md').write_text('fixture')
    rows = []
    for scenario in ('X-1','X-2','X-3'):
        for variant, count in [('v1', 11), ('v2', 12)]:
            rows.append(dict(scenario=scenario, variant=variant, run_id=f'{scenario}-{variant}', reviewer_id='reviewer',
                             model='fixed-model', reasoning='fixed-setting', brief_sha256='a'*64,
                             input_tokens=100, output_tokens=200, elapsed_s=2, conti_s=1,
                             checks={str(n):{'score':int(n <= count),'evidence':'evidence.md'} for n in range(1,14)}))
    return tmp_path, rows


def test_complete_comparable_packet_meets_threshold(packet):
    report = grade(*packet)
    assert report['status'] == 'threshold_met'
    assert report['scenarios']['X-1']['scores'] == {'v1':11,'v2':12}


@pytest.mark.parametrize('change', [
    lambda x: x.pop(), lambda x: x.append(deepcopy(x[0])), lambda x: x[0].update(model='other'),
    lambda x: x[0].update(brief_sha256='b'*64), lambda x: x[0].update(reviewer_id=x[0]['run_id']),
    lambda x: x[0]['checks']['1'].update(evidence='missing.md'),
    lambda x: x[0]['checks']['1'].update(evidence='../outside.md'), lambda x: x[0]['checks'].pop('13'),
    lambda x: x[0].update(elapsed_s=float('nan')),
])
def test_missing_or_noncomparable_evidence_never_passes(packet, change):
    root, rows = packet
    change(rows)
    assert grade(root, rows)['status'] == 'unverified'


def test_equal_scores_do_not_meet_superiority_requirement(packet):
    root, rows = packet
    rows[0]['checks']['12']['score'] = 1
    assert grade(root, rows)['status'] == 'threshold_not_met'
