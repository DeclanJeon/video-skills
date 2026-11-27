import pathlib, sys, shutil
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import leak_scan
REF = leak_scan.load_ref(ROOT / 'docs/examples/ref-prompt-01')
def layers(text): return {l for l, _ in leak_scan.scan_text(text, REF)}

def test_real_tree_is_clean():
    assert leak_scan.scan_root(ROOT) == []
def test_term_layer_A():
    assert 'L-A' in layers('이 장면은 Troy 가 말한다')
def test_translated_concept_layer_B_korean():          # Q-21에서 단어 목록이 놓쳤던 번역 누출
    assert 'L-B' in layers('감정의 목적: 지워진 인생에 대한 저항')
def test_translated_concept_layer_B_other_language():
    assert 'L-B' in layers('他想知道谁牺牲得更多')
def test_paraphrase_shingle_layer_C():
    assert 'L-C' in layers("She said: I gave eighteen years of my life to stand in the same spot as you")
def test_structure_vocabulary_is_not_flagged():        # 구조 어휘는 통과해야 한다 (과탐 방지)
    ok = '눈썹 안쪽이 올라가고 아래 눈꺼풀이 긴장한다. 긴 테이크를 하위 구간으로 나눈다. AU4 AU7 AU23.'
    assert layers(ok) == set()
def test_synthetic_fixture_is_not_flagged():
    assert layers((ROOT / 'docs/examples/synthetic-laundromat-34s/fixture.md').read_text()) == set()
def test_planted_leak_in_tree_detected(tmp_path):
    shutil.copytree(ROOT / 'docs', tmp_path / 'docs'); (tmp_path / 'docs/design/x.md').write_text('예시: 부부 싸움 장면')
    assert any(f[1].endswith('x.md') for f in leak_scan.scan_root(tmp_path))

def test_masked_skeleton_has_no_leak():                # 폴더 안이지만 골격은 "내용 제거"가 계약이다
    assert layers((ROOT / 'docs/examples/ref-prompt-01/masked-skeleton.md').read_text()) == set()
