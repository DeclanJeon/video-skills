from cutover_preflight import preflight


def test_read_only_preflight_reports_collision_and_unsigned_release(tmp_path):
    source = tmp_path/'v2'; source.mkdir()
    (source/'manifest.json').write_text('{"version":"0.1.0","status":"scaffold","skills":["director"]}')
    target = tmp_path/'skills'; target.mkdir()
    (target/'director').symlink_to(tmp_path/'nonexistent')
    with (source/'director').open('w') as out:
        out.write('improper source')
    findings = preflight(source, target, ['equipment'])
    assert {x['code'] for x in findings} == {'package', 'source', 'collision', 'equipment'}
    assert (target/'director').is_symlink()
    assert len(list(target.iterdir())) == 1
