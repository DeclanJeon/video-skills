"""Compare complete GEN packets with the canonical cut-level allocation."""
from collections import Counter
import re

from timeline_check import DIALOGUE, seconds


def check_batch(board: list[dict], packets: list[dict], runtime: str) -> list[dict]:
    findings = []

    def add(code, message):
        findings.append(dict(code=code, message=message, severity='error'))

    duration = seconds(runtime)
    if not packets or not board or not duration:
        add('PBG01', 'nonempty board, packet list and positive runtime are required')
        return findings
    cursor = seconds(0)
    seen = set()
    actual = []
    for packet in packets:
        gen = packet['gen']
        offset = seconds(packet['global_offset_s'])
        span = seconds(packet['duration_s'])
        if not re.fullmatch(r'GEN-(?!00)[0-9]{2}', gen) or gen in seen or offset != cursor or not span:
            add('PBG01', f'{gen}: invalid/duplicate ID or expected global start {cursor} with positive duration')
        seen.add(gen)
        local = seconds(0)
        for shot in packet['shots']:
            left, right = map(seconds, shot['t'])
            if left != local or not left < right <= span:
                add('PBG02', f'{gen}/{shot["cut"]}: invalid local cut range')
            local = right
            dialogue = Counter(line for seg in shot['segments'] for line in seg.get('dialogue', []))
            actual.append((shot['cut'], left + offset, right + offset, dialogue))
        if local != span:
            add('PBG02', f'{gen}: cuts do not reach GEN end')
        cursor = offset + span
    if cursor != duration:
        add('PBG01', f'batch ends at {cursor}, required {duration}')
    wanted = [(row['cut'], seconds(row['t_start']), seconds(row['t_end'])) for row in board]
    if [item[:3] for item in actual] != wanted or len({item[0] for item in wanted}) != len(wanted):
        add('PBG02', 'global cut IDs, order or intervals differ from board')
    allocations = {row['cut']: Counter(DIALOGUE.findall(row.get('dialogue', ''))) for row in board}
    for cut, _, _, dialogue in actual:
        if dialogue != allocations.get(cut):
            add('PBG03', f'{cut}: dialogue allocation differs from board or contains duplicates')
    for key, syntax in (('screenplay', r'SCR@v[1-9][0-9]*'), ('fixed_block_baseline', r'GEN-01@v[1-9][0-9]*')):
        pin = packets[0].get(key, '')
        if not re.fullmatch(syntax, pin) or any(p.get(key) != pin for p in packets):
            add('PBG04', f'{key}: every packet must use the same valid version pin')
    return findings
