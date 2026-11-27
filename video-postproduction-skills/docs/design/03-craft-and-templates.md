# 03 — 자막·참고 템플릿·룩·음향

## 1. ‘학습’의 범위와 실제 inventory

참고 루트는 `/home/declan/Documents/쇼츠템플릿`이다. 이번에는 모델 훈련이 아니라 로컬 metadata/대표 이미지에서 컨셉·배치·모션 어휘를 추출했다. 원본 수정·자막 패키지 바이너리/이미지의 스킬 배포 폴더 복사는 하지 않는다.

직접 전수 확인: **139 files = PNG43 + JPG9 + MP4 27 + prgraphic27 + JSON27 + MOGRT6**. 27개 `definition.json`은 모두 `authorApp=ppro`, 원본 composition 1920×1080이다. 기본 모션군 21개, 핑크군 00–05의 6개(기본+변형)를 폴더 이름 ‘5종’만 보고 5개로 세지 않는다. frame/safe guide는 1080×1920 참고다. metadata composition과 세로 프레임은 같은 해상도가 아니다.

| 관측한 family/파일 | 추출할 제안 규칙 | 적용/제한 |
|---|---|---|
| 기본 scale up/down/pop, 퍼지는 fade, wiggle/wave/wriggle, neon/glitch | entrance/hold/exit 구분, 강조 강도/빈도, 단어/문장 단위 선택 | 원본 이름/정의와 대표 썸네일은 확인. 세부 easing/곡선·정확한 전구간 모션은 아직 관측/재현 검증하지 않음. |
| 핑크 기본+fade/blur/scale 변형 | 부드러운 serif·분홍 glow 강조, 문장 유지시간과 감정에 맞춘 등장 | 대표 이미지의 외형 관측. 모든 드라마 대사에 기본 적용하지 않음. |
| Web Browser Shorts | 상단/정보 strip/content window 분리, 역할별 제목/본문 배치 | preview에 든 조회수/좋아요 숫자를 실제 채널 성과처럼 복사하지 않음. 실데이터가 없으면 생략/명시적 가상 UI. |
| Film Strip Shorts | 질감 frame와 투명 content window, 상하 여백 | A.png center alpha=0 실제 확인. 검은 영상으로 오인하지 않고 실제 alpha metadata를 검사. |
| 지수튜디오 safe guide | 현재 참고 overlay의 occlusion mask를 기준으로 레이아웃 시험 | 플랫폼의 현재 보편 규격이나 출처 없는 ‘공식 안전영역’으로 승격하지 않음. 로고 포함 guide를 납품 영상에 그대로 얹지 않음. |

## 2. 폰트·라이선스

- 기본군은 `Paperlogy-6SemiBold`, 핑크군은 `HakgyoansimBareonbatangB`를 정의에 참조한다. `fc-match`는 Noto CJK로 fallback했고 `fc-list`에서 해당 이름을 찾지 못했다. **현재 OS에서 요청한 폰트가 해결되지 않음**을 기록하며 native 앱의 embedded fonts까지 전수 부재라고 단정하지 않는다.
- fallback을 같은 디자인이라고 숨기지 않는다. 원 폰트 합법 확보/설치·실제 glyph 확인은 [환경 준비](06-environment-and-installation.md)가 담당하고, 확보 불가 시 대체 폰트 승인을 받는다. 그 뒤 한국어 줄바꿈/폭/강조·safe area를 재검수한다. 이번 회차에 실제 폰트를 설치한 것은 아니다.
- Web Browser/Film Strip의 동일한 license Guide 이미지를 직접 읽었다. 구독+출처 표기를 개인/기업/상업 사용 조건으로 적고 공유·임의 판매·재배포를 금지한다. 표기 예시는 `[Video Source] Youtube channel "freeticon"`다. 현재 구독/별도 이용권 충족은 확인하지 않았고 자동 구독하지 않는다.
- 이 두 frame 패키지의 안내를 motion21/pink6·개별 폰트 전체에 자동 확장하지 않는다. 정의의 빈 licenseID는 이용 허락이 아니다. 패키지별 권리/수정/상업/재배포 조건을 별도 확인한다.
- 최종 납품의 attribution manifest에 실제 사용한 자산·권리·요구 표기를 결속한다. 미확인 asset 권리는 해당 사용을 차단한다. 설계 참고와 실제 픽셀/모션 자산 사용은 구별한다.

## 3. Recipe는 파일 변환 약속이 아니다

`CaptionStyleRecipe` 제안 필드: reference path/hash와 관측 범위, 사용 조건, 용도(대사/강조/제목/주석), 실제 font file/version/license, 크기/행간/정렬/outline/shadow/glow, 색·alpha·blend, 안전 mask/profile, entrance/hold/exit 및 keyframe/easing 단위, 최대 점멸/강조 빈도·reduced-motion 대안, 적용 backend와 검수 revision.

프리셋 이름을 복사한 것으로 `.mogrt → .ectemplate` 호환을 인증하지 않는다. 기본은 허용된 스타일 어휘를 native primitives로 새 구성하고 대표 문장·짧은/긴 한국어·복수 화자·최대 폭을 실제 render 후 비교한다. 검증 전 곡선을 ‘원본과 정확히 동일’이라고 쓰지 않는다.

safe guide의 alpha=0 row spans는 로컬 측정값으로 **[y0,y1), [x0,x1)**: y0–117 없음, y117–850 x0–1080, y850–1622 x0–924, y1622–1920 없음. 이는 이 파일의 투명 구간이며 여백 없는 글자 배치 허용선이 아니다. target별 추가 padding·현재 UI overlay·얼굴/행동 보호 영역과 교차해 caption bounds를 검사한다. [실측](../../qa/design/safe-area-observation.json).

## 4. 자막 원문과 시간

- 승인된 대사 원문/화자와 transcript를 기준으로 실제 발화를 대조한다. ASR는 위치/오탈자 후보 도구이고 내용/화자/번역을 자동 승인하지 않는다.
- source time→현재 edit map→timeline clock으로 cue를 옮긴다. cut/속도/음성 offset 수정은 자막 timing을 stale로 만든다. 단어 강조는 실제 word timestamp가 있을 때만 하고 문장 SRT에서 단어 시각을 꾸미지 않는다.
- 대사 자막, 편집 강조, 제목/정보, 번역을 구별한다. 축약/번역이 원래 인용이나 인물 대사처럼 오해되면 차단한다. 의미/반전 공개 순서를 새 자막으로 미리 누설하지 않는다.
- 정책별 최대 줄수/읽기 속도/행 길이/노출·간격·강조·safe bounds를 입력으로 받는다. ‘쇼츠는 무조건 빠른 자막’ 같은 고정 규칙은 없다. 실제 font shaping/glyph·장면 대비·가림·잘림을 확인한다.
- editable cue/source transcript, sidecar(SRT/VTT 등 실제 지원 포맷), burned-caption variant를 구별한다. 이미 자막이 구워진 source에 중복 burn-in하지 않는다.

## 5. 음향과 색의 작업 계약

SoundCraft 입력은 실제 원본/mix/stem과 sample/time offset·speaker/cue·권리다. 하나의 stereo mix를 dialogue/music/SFX stem 세 개로 이름만 바꾸지 않는다. 새 음성/음악/효과 생성·source separation·voice clone·모델 다운로드는 별도 권한/도구/품질 검증 대상이다. 기존 원음+허용된 정리로 가능한지 먼저 판정하고 부족하면 요청을 반환한다.

picture lock의 version/hash와 reference movie를 audio 세션에 결속하고 변경 시 cue/믹스/최종 sync를 재검수한다. 대사 앞뒤 호흡·잔향·ambience, 컷 접합, clipping·true peak·목표 LUFS·채널/위상·sample rate를 검사한다. LUFS/TP 목표는 delivery profile에 명시하고 하나의 숫자를 모든 플랫폼에 강제하지 않는다. native meter 설명은 독립 측정/실제 청취의 대체가 아니다.

색은 실제 source/sequence/output 색공간·transfer·range·bit depth와 LOOK pin을 보존한다. metadata가 없으면 unknown이며 승인된 ‘할당’과 실제 ‘검출’을 구별한다. 인접 컷·피부/의상·하이라이트/블랙, 알파 가장자리·blend/색 변환 순서를 확인한다. 룩 보정으로 무승인 얼굴 변형이나 인물/에셋 정체성 변경을 하지 않는다. motion plate·grade·mix 모두 source→transform→output 계보와 backend/recipe/version을 갖는다.
