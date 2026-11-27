# 로컬 실행자·템플릿 조사 01

확인일 2026-11-26. 부모가 직접 실행한 help/명령 목록·패키지 조회와 로컬 자료 관찰이다. 실제 편집/렌더·설치/업데이트는 하지 않았다.

## 1. 실제 설치 경로

`/usr/bin/filmcraft`, `/usr/bin/effectcraft`, `/usr/bin/soundcraft` 및 **별도의** `/usr/bin/filmcraft-cli`, `/usr/bin/effectcraft-cli`, `/usr/bin/soundcraft-cli`를 확인했다. dpkg 소유 패키지는 각각 filmcraft/effectcraft/soundcraft다.

| 도구 | dpkg version | 실제 응답 |
|---|---|---|
| FilmCraft | 0.20.1-1 | app `--help/--version` 성공, version0.20.1. CLI `--help/commands --json` 성공, 718 IDs. |
| EffectCraft | 0.25.1-1 | app `--help` unknown option/exit1. 별도 CLI `--help/commands --json` 성공, 766 IDs. |
| SoundCraft | 0.20.1-1 | app `--help/--version` 성공, version0.20.1 (linux x86_64). CLI `--help/commands --json` 성공, 483 IDs. |

명령 목록의 enabled 표시는 조회 시 빈/default engine의 상태이지 실제 작품에서 모든 명령이 유효하거나 headless로 실행된다는 보증이 아니다. 특히 effect app help 오류를 CLI 미설치로 잘못 해석하지 않는다.

설치본 문서는 `/usr/share/doc/filmcraft/README.md`(492 lines), `/usr/share/doc/effectcraft/README.md`(399), `/usr/share/doc/soundcraft/README.md`(409)다. agents/status/interchange/license를 읽었다. 프로그램 문서는 원격 최신 README와 분리한다.

- FilmCraft 문서: integer ticks254016000000/s, CLI/JSON control/MCP 경로, OTIO/FCPXML/AAF 등의 교환 설명. `.prproj` 직접 import 미지원, alpha·실제 미디어/Linux 시험 제한 표기.
- EffectCraft 문서: native ecproj/CLI/template/render·bridge, UI-only와 headless 차이, 독점 프로젝트/AE plug-in 미지원, alpha/production-client 비권장 표기.
- SoundCraft 문서: headless session/commands/script/bounce·control, 표준 meter 설명. pre-alpha와 AAF/OMF interchange 미구현 표기.
- dual MIT OR Apache-2.0은 각 Craft 코드에 대한 문서 설명이다. bundled fonts/assets/상표·외부 plugins/모델까지 같은 조건이라는 뜻이 아니다.

근거: [discovery](../../qa/design/discovery.json), [FilmCraft help](../../qa/design/filmcraft-cli-help.txt), [EffectCraft help](../../qa/design/effectcraft-cli-help.txt), [SoundCraft help](../../qa/design/soundcraft-cli-help.txt). binary SHA와 command ID inventory도 같은 QA 폴더에 있다. 현재 버전의 native 편집·export·교환·품질은 **UNVERIFIED**다.

## 2. 템플릿 관찰

루트 `/home/declan/Documents/쇼츠템플릿` 전수 inventory는 139 files/27개 정의다. [inventory](../../qa/design/template-inventory.json)는 path/hash·정의 이름·원 앱/폰트·frame size·duration metadata만 보관한다. 빈 licenseID를 허락으로 처리하지 않았다.

직접 시각 확인한 대표 자료:
- Web Browser `_Freeticon license Guide.jpg` — 구독+출처 표시 조건/재배포 금지.
- Web Browser `A1.jpg` — 상단 UI·정보 줄·본문 창, preview용 조회수/반응 수치.
- Film Strip `A.png` — 종이 질감/film edge와 투명 가운데 창.
- 지수튜디오 safe PNG — 반투명 상/하·오른쪽 UI 가림 참고.
- pink00 thumb — serif/분홍 glow 문장.
- basic scale-up thumb — 흰 bold text의 단순 강조 외형.

실제 pixel alpha 측정은 [safe-area observation](../../qa/design/safe-area-observation.json)에 있다. 이미지 뷰어의 검은 투명 배경을 불투명 검정으로 오인하지 않았다. 모든 preview MP4의 전구간·easing/정확한 motion curve는 미검수다.

`fc-match`는 두 요청 폰트 대신 Noto Sans CJK KR을 반환했고 `fc-list`에서 요청 family/PostScript 이름을 찾지 못했다. 그 결과는 현재 OS 검색 범위이며 native embedded font의 전수 검증이 아니다. 폰트 설치/템플릿 변환/모델 훈련은 하지 않았다.

## 3. 외부 연구와 부모 확인

[소스 조사 보고서](reference-research-01.md)는 승인한 연구자 1명이 CSV 38개 레코드와 선택한 9개 도구를 공식 자료로 대조한 결과다. 그 연구자는 설계 문서의 독립 builder 검수자가 아니며 이 문서가 별도 독립 검수를 통과한 것은 아니다.

부모는 고정 AutoClip commit `2f511907a72cbfbb8d86639f6441967b826acb6a`의 diagnostics consent/service/upload 소스를 Obscura0.2.5로 다시 정적 열람했다. consent의 ‘Unset defaults on’/‘Diagnostics and excerpts upload by default’ 명시, background wake 경로, upload의 내장 Worker endpoint fallback을 확인했다. 실제 업로드/네트워크 격리 시험은 하지 않았다. [부모 정적 확인](../../qa/design/autoclip-parent-source-check.json).

AutoClip의 local-first 설명을 개인정보/무전송 인증으로 사용하지 않는다. 구체 release binary의 동작/설정·차단/서버 보존은 여전히 미확인이다. 이번에는 AutoClip을 설치/clone/import/run하지 않았다.

## 4. 보호·권한

원본 템플릿139 + CSV1 + 기존 production의 검수된 source/spec76, 합계216개 file SHA를 baseline으로 보관했다. [보호 입력](../../qa/design/protected-inputs.json). 최종 검증에서 동일성을 대조한다. 이 대상 파일 밖의 전체 시스템을 변경하지 않았다는 전면 감사를 의미하지 않는다.

설계 폴더에는 원본 이미지/비디오/MOGRT/prgraphic/font를 복사하지 않았다. 설치한 패키지/모델/폰트 없음, 실제 native 편집·렌더 없음, 미디어 외부 전송·생성·게시/구매 없음. CLI metadata용 실행과 공개 문서 GET은 수행했다. 구현 계획/코드·새 SKILL·실행 manifest·Git 초기화/커밋은 수행하지 않았다.
