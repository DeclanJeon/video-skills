import pathlib, sys, random
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
from cp2.speech import count_units, rate_verdict, rate
from calibrate_speech_rate import calibrate

def test_ex02_defect_timetable_matches_doc():           # EX-02 §3 표의 값을 코드로 재검증
    cases = [("다음 달부터 보증금 올린대. 더는 못 버틴다니까.", 2.0, 0, 'block'),
             ("못 버틴다고? 오빠가 언제 버텼는데. 버틴 건 매일 문 연 나야.", 2.5, 0, 'block'),
             ("새벽 여섯 시에 셔터 올리고 밤 열한 시에 내렸어. 이십 년을.", 3.5, 0, 'ok')]
    for text, sec, pz, want in cases:
        u, ok = count_units(text, 'ko'); assert rate_verdict(u, sec, 'ko', 'normal', pz, ok) == want, text
def test_ex02_numbers():
    assert round(rate(19, 2.0), 2) == 9.5 and round(rate(23, 2.5), 2) == 9.2 and round(rate(26, 4.0, 1), 2) == 7.03
    assert round(rate(26, 4.5, 1), 2) == 6.19
def test_pause_subtracted_makes_it_worse():
    assert rate(5, 1.0, 1) > rate(5, 1.0, 0)
def test_heated_mode_widens_limit():
    u, ok = count_units("one two three four five six seven eight nine ten eleven twelve", 'en')   # 12 words / 3.3 s = 3.64
    assert rate_verdict(u, 3.3, 'en', 'normal', 0, ok) == 'warn' and rate_verdict(u, 3.3, 'en', 'heated', 0, ok) == 'ok'
def test_mixed_japanese_kanji_unverified():
    u, ok = count_units("今日は雨です", 'ja'); assert ok is False and rate_verdict(u, 1.0, 'ja', trusted=ok) == 'unverified'
def test_calibration_needs_enough_samples():
    rows = [{'lang': 'ko', 'text': '가나다라마바사', 'seconds': '1.0', 'pauses': '0'}] * 5
    assert calibrate(rows)['ko']['status'] == 'insufficient'
def test_calibration_proposes_ordered_limits():
    random.seed(1); rows = [{'lang': 'en', 'text': ' '.join(['w'] * 10), 'seconds': str(10 / random.uniform(2.0, 4.0)), 'pauses': '0'} for _ in range(60)]
    c = calibrate(rows)['en']; assert c['status'] == 'proposed' and c['normal'] <= c['heated'] < c['block']
