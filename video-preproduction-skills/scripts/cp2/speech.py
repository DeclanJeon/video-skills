"""대사 말속도 계산 (DES-07 §3 규칙 7). 표준 라이브러리만."""
import json, re, pathlib
RATES = pathlib.Path(__file__).with_name('speech_rates.json')
def load_rates(path=RATES): return json.loads(pathlib.Path(path).read_text())
def count_units(text, lang):
    """(단위 수, 신뢰 여부). en=단어, ko=한글 음절, zh=CJK 글자, ja=가나 수(한자 섞이면 신뢰 False)."""
    if lang == 'en': return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", text)), True
    if lang == 'ko': return len(re.findall(r'[가-힣]', text)), True
    if lang == 'zh': return len(re.findall(r'[\u4e00-\u9fff]', text)), True
    if lang == 'ja':
        kana = len(re.findall(r'[\u3040-\u30ff]', text)); kanji = len(re.findall(r'[\u4e00-\u9fff]', text))
        return kana + kanji, kanji == 0
    raise ValueError(f'unsupported language: {lang}')
def rate(units, seconds, pauses=0, pause_s=0.3):
    eff = seconds - pause_s * pauses
    return float('inf') if eff <= 0 else units / eff
def rate_verdict(units, seconds, lang, mode='normal', pauses=0, trusted=True, rates=None):
    """ok / warn / block / unverified. mode=heated 는 연기 레이어에 '빠르게/격앙'이 있을 때만."""
    r = rates or load_rates(); lim = r['limits'][lang]
    if not trusted: return 'unverified'
    v = rate(units, seconds, pauses, r['pause_seconds'])
    if v > lim['block']: return 'block'
    if v > lim[mode]: return 'warn'
    return 'ok'
