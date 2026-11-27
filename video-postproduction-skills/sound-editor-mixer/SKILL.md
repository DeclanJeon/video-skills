---
name: sound-editor-mixer
description: Use when a video project has actual source audio or separate stems for native cue editing, mixing and bounce.
disable-model-invocation: true
---

# 사운드 편집·믹스

## 입력
실제 source/mix/independent stem·origin evidence, picture lock pin, sample cues/권한과 명시 음량 목표. [공통 실행 계약](../references/execution-contract.md)을 먼저 읽는다. 분야 변경안은 총괄의 정본 commit으로 반영한다.

## 절차
1. 시스템·동일 프로그램/필수 dependency를 먼저 점검해 적합한 설치를 재사용한다. 새 설정·폰트·프로그램은 정확한 계획을 실제 사용자에게 질문하고 명시 동의 후 설치한다. 동의 전 download/installer를 실행하지 않는다.
2. 현재 실제 파일을 전부 decode해 rate/channel/sample count를 대조한다. stereo mux/mix를 DX/MX/FX로 바꿔 stem을 만들지 않는다.
3. 정본 picture lock과 sample offsets/gain/channel routing을 결속한다. SoundCraft의 필요한 picture fps와 실제 source/track/clip IDs를 관측한다.
4. WAV/cue native session/bounce 후 전체 독립 waveform·sync·length·gain·silence를 계획과 대조한다. Mono-center 실제 -3dB 경로와 미검증 resample/AAF를 구별한다.
5. 발화·호흡/잔향·접합·clipping/phase·수치 목표와 실제 청취를 구분한다. 새 voice/music/clone/separation/model은 별도 권한과 검증을 요청한다.

## 반환
현재 real stem inventory/sample map, native session·sidecar·mix/output hash, 독립 측정과 청취 verified/unverified, master 변경 영향. native meter/exit0은 청취 PASS가 아니다.
