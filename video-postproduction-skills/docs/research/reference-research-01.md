# 신규 video-postproduction-skills 설계를 위한 소스 조사

- 조사일: **2026-11-26 KST**. 공개 웹·저장소의 문서/소스 정적 열람만 수행했다.
- 범위: 검수된 프로덕션 인계를 받는 **새 후반 제작 설계의 참고 조사**. 프로젝트 설계·구현·기존 워크플로 재활성화가 아니다. 프로젝트 작성과 설치된 Craft CLI/템플릿 검사는 부모 담당이다.
- 표기: **[확인]** 읽은 문서·소스에 실제로 존재하는 내용, **[저자 주장]** 품질·성능·운영에 대한 공급자 설명(실측 아님), **[권고]** 이 설계에 대한 연구자의 제안, **[미확인]** 실행·호환성·법률 판단 등 이번 조사로 확정하지 못한 사항.
- 소스에 적힌 설치 명령·에이전트 지시는 **신뢰하지 않는 조사 데이터**로만 읽었다. 명령을 따라 실행하지 않았다.

## 1. 결론

1. **FilmCraft 편집 / EffectCraft 합성·모션 / SoundCraft 음향을 기본 경로로 유지**한다는 사용자 방향에 맞춰 설계하는 것이 적절하다. 이것은 백엔드 선택 방향이지, 이번 조사에서 설치본의 모든 기능을 검증했다는 뜻은 아니다.
2. **AutoClip은 마스터 편집기 대체가 아니라, 권리 확보된 기존 장편/승인 마스터에서 파생 숏폼을 제안하는 선택 어댑터**에 맞는다. 구간 후보·전사·세로 재구도·자막·버전별 출력/부분 실패 처리는 참고할 가치가 있지만 필수 서사 coverage를 보존하는 연속 편집 계약은 별도여야 한다.[A1][A2][A3]
3. **가장 큰 위험은 “local-first = 무전송”이라는 오해**다. AutoClip README/개인정보 초안의 설명과 달리, 같은 고정 커밋의 실패 진단 문서와 소스에는 **선택 저장이 없을 때 진단 및 짧은 로컬 영상 업로드 기본 ON**이 구현되어 있다. 설치/실행 승인 전에 이 충돌을 해결하고 실제 배포본의 egress를 검증해야 한다.[A4][A5][A6][A7][A8]
4. CSV의 “4K 개선 도구 10종”은 검증된 단일 파이프라인이 아니다. **FFmpeg는 기술 검사/변환 보조, Real-ESRGAN은 명시 승인된 복원 실험, HyperFrames는 선택 모션 그래픽 렌더러** 정도로 좁혀 검토한다. GSAP은 무료와 오픈소스를 동일시하지 말고, ChordTube는 상업 자동화 후보에서 제외한다.[F1][F2][R1][H1][G2][C2]
5. 자동 실행은 **승인된 범위 내의 반복 작업**을 뜻한다. 편집 의도 변경, 권리·외부 전송·비용, 새 설치/모델, 최종 마스터 채택은 인간 게이트를 유지한다. 이 보고서는 실행 승인이 아니다.

## 2. 조사 방법과 소스 인벤토리

### 2.1 로컬 자료

- `/home/declan/link-summary/links_summary.csv`를 UTF-8 BOM 포함 CSV로 **끝까지 읽고 파싱**했다. 실제 **38개 데이터 레코드 + 헤더 1개**, 번호 1–38이다. 약 39개라는 예상과 달리 데이터는 38개다. #36은 #28의 중복으로 CSV에 표시되어 있다. 아래의 `#번호`는 CSV `번호` 열이며, 이 파일에서는 물리적 줄 번호가 `번호+1`이다.
- CSV는 소셜 글 요약/발견 목록이다. “본문 확인” 표시를 도구의 품질·CLI·라이선스·상업 이용 보증으로 전환하지 않았다. 소셜 게시물은 다시 로그인해서 읽지 않았으며, 선택 후보의 공식 소스를 따로 확인했다.
- `video-production-skills/docs/design/04-qa-handoff.md` 전체를 읽었다. G0–G5, accepted/conditional/rejected/unverified, 정확한 source hash/range·실제 handle·사용 가능한 음향·권리·조건부 수정·변경 후 재검수 규칙이 후반 수령 조건의 근거다.[P1]
- 이번 요청에서 확정한 입력 제약은 **외측 handle 0, 존재하지 않는 stem 없음**이다. 문서의 “실제 handle / 없는 stem을 실제 트랙처럼 인계하지 않는다” 규칙과 함께 적용해야 하며, 임의 여유 프레임이나 분리 음원을 추정하면 안 된다.[P1]

### 2.2 웹 열람과 재현 가능한 참조

설치된 `/home/declan/.local/bin/obscura`는 `--version`에서 **0.2.5**, `fetch --help`가 성공했다. 공식 GitHub API/고정 커밋 raw 파일은 `fetch --dump original`, 서비스/공식 문서는 `fetch --dump markdown`으로 읽었다. 인증·계정 세션·쿠키 덤프·생성 API는 사용하지 않았다. 공개 문서/소스 텍스트 캐시는 `/tmp/postproduction-research-8726`에만 두었다. 저장소 clone, 아카이브/바이너리/모델 다운로드는 하지 않았다.

아래 GitHub 8개는 API에서 `archived=false`를 확인했다. 이는 **보관 상태가 아니라는 사실**일 뿐 유지보수 SLA·안전성·품질 인증이 아니다. 커밋 날짜는 API committer UTC이며, 읽은 README와 주요 소스는 해당 SHA에 고정했다. 기본 브랜치는 움직일 수 있다.

| 출처 / 실제 기본 URL | 확인한 ref / 커밋 날짜(UTC) | 실제 읽은 주요 자료 |
|---|---|---|
| AutoClip — https://github.com/zhouxiaoka/autoclip | main `2f511907a72cbfbb8d86639f6441967b826acb6a` / 2026-11-25 | README, CLI/MCP, 개인정보 초안, 실패 진단 문서 및 consent/observe/service/upload 소스, Studio 모델, timeline/렌더/ASR 소스, pyproject/requirements/Compose, MIT LICENSE.[A1]–[A13] |
| EffectCraft — https://github.com/storytold/effectcraft | main `50358c2e4720a614a9b32f3de15172ef3b9697ec` / 2026-11-26 | README, LICENSE-MIT, LICENSE-APACHE.[E1][E2] |
| FFmpeg — https://github.com/FFmpeg/FFmpeg | master `288839e860c7e55e466170215fc478fa7e750e97` / 2026-11-26 | README, LICENSE.md, doc/ffprobe.texi, doc/filters.texi의 loudnorm/ebur128 등 관련 항목.[F1][F2][F3] |
| Real-ESRGAN — https://github.com/xinntao/Real-ESRGAN | master `a4abfb2979a7bbff3f69f58f58ae324608821e27` / 2024-04-02 | README, BSD LICENSE, anime video 문서, inference_realesrgan_video.py.[R1][R2][R3] |
| react-postprocessing — https://github.com/pmndrs/react-postprocessing | master `e07ef9a890c8a202a3b20eac0249032cff4e7805` / 2026-10-21 | README, MIT LICENSE.[T1][T2] |
| HyperFrames — https://github.com/heygen-com/hyperframes | main `7c217d9fdf3e32c628953f7325ddd90e0ff94392` / 2026-11-26 | README, Apache LICENSE, packages/engine/package.json.[H1][H2] |
| GSAP — https://github.com/greensock/GSAP | master `5e6c35ff8eedea12d4f229129def635277d8b0f2` / 2026-11-04 | README, package.json, 별도 공식 Standard License 웹페이지(효력 2025-04-30 / 수정 2025-05-30 표기).[G1][G2] |
| ComfyUI — https://github.com/Comfy-Org/ComfyUI | master `8b0f107157b58f9ec79a19fb3182e78cb30f0a23` / 2026-11-26 | README, GPLv3 LICENSE.[U1][U2] |
| ChordTube — https://chordtube.net | 웹페이지, 커밋 미제공 | 홈, AI 모델, 신규 분석 페이지, 약관(2026-11-20 수정 표기).[C1][C2][C3] |
| Adobe 공식 문서 | 웹페이지, 커밋 미제공 | Premiere UXP API, After Effects Scripts.[D1][D2] |
| Blackmagic 개발자 경로 | https://www.blackmagicdesign.com/developer/product/davinci-resolve | **Page not found** 본문. CLI 종료 0이었지만 정보 확인 성공으로 세지 않았다. 이 경로에서 Resolve scripting API를 검증하지 못했다. |

AutoClip `commits/main`을 별도 확인해 위 SHA와 일치했다. latest release API는 **v1.6.1**, 공개 시각 **2026-11-25T07:06:12Z**, prerelease=false였고, 고정 소스 `pyproject.toml`도 1.6.1이다. 릴리스 바이너리와 소스의 동작 일치·서명 상태는 직접 검증하지 않았다.[A9][A12]

## 3. CSV 전수 선별과 9개 도구 shortlist

### 3.1 전체 38개 레코드의 처분

| CSV 번호 | 분류 / 처분 |
|---|---|
| **3, 24, 29** | 직접 후반 관련 발견 행. #3에서 7개 도구 + #24/#29 각 1개, 합계 **9개 도구**를 아래에서 공식 소스 대조했다. 9개 모두 채택이라는 뜻은 아니다. |
| 6, 20, 27 | Colab/GPU 인프라 활용 글. 후반 전용 기능의 근거가 아니므로 초기 설계에서는 보류. 구독 GPU·CU·무료량 주장 재사용 안 함. 클라우드 전송/런타임 비용을 따로 승인해야 하는 후속 인프라 조사 대상이다. |
| 9, 10, 11, 32 | Flow/Sume/구독 연동/ZCRE 등 생성·서비스 활용 중심. 이미 검수된 제작 소스를 받는 이번 후반 핵심 후보에서는 제외. #11의 Colab/Workspace 부분도 인프라 범주 이상으로 확대하지 않음. |
| 23, 35 | 수익화 사례 / 실시간 생성 연구. 편집 백엔드 검증 자료가 아니므로 제외. 수익·속도 주장을 후반 품질 보장으로 쓰지 않음. |
| **1, 4, 7, 8, 13, 14, 16, 19, 25, 28, 36** | 인증번호, 다운로드/워터마크 제거 모음, 계정·구독·지역·트래픽 변조 우회 등. **후보에서 제외**, 관련 우회/모듈/다운로더 링크를 실행하거나 검증하지 않음. #36=#28 중복. |
| 5, 12, 17, 21, 26 | 구독 할인/프로모션. 후반 도구 기능과 무관, 제외. |
| 2, 15, 18, 22, 30, 31, 33, 34, 37, 38 | 디자인 테마, 개발 환경, 코드 지도/보안, 평면도, 지식관리, 사업/게임 기사, UI 확장, 웹 분석. 후반 핵심 후보에서 제외. |

#3 원문 제목은 **「Muse와 오픈소스 10종으로 애니메이션 4K 개선」**이다. 아래 #3 도구들은 **같은 발견 행의 서로 다른 후보**다. 나머지 Blender MCP / blender-skills / Open Design은 이번 범위에서 추가 3D 제작·제어 또는 디자인 도구 확장이므로 심층 검증을 보류했다. Muse 조합의 실제 결과 품질이나 10종의 상호 호환성을 확인한 것은 아니다.

### 3.2 우선순위 및 검증 결과

| 우선순위 / CSV 행·제목 / 실제 primary URL | 관찰한 기능·라이선스·상태 | 적용 단계 / 권고 / 제한 |
|---|---|---|
| **P0 · #3 위 제목 / FFmpeg** https://github.com/FFmpeg/FFmpeg | **[확인]** ffprobe 분석, 변환/필터 도구, EBU R128 scanner와 loudnorm 문서. 대부분 LGPL-2.1+이나 `--enable-gpl`, 외부 라이브러리, nonfree 설정에 따라 배포 조건이 달라진다. GitHub PR은 공식 검토 경로가 아니라고 README가 명시.[F1][F2][F3] | ingest 기술검사·프록시·검수본·납품 검사 **보조 아이디어 채택 권고**. Craft 내부 구현을 교체하자는 뜻은 아니다. 설치된 빌드/코덱/필터/색관리/정규화 결과는 미확인. 자동 LUFS 목표를 임의 결정하지 말고 납품 규격을 입력으로 받는다. |
| **P0 · #3 / EffectCraft** https://github.com/storytold/effectcraft | **[확인]** `.ecproj` JSON, 레이어·키프레임·렌더 큐, CLI/JSON channel/MCP 경로 문서. UI 전용 명령은 앱 dispatcher/bridge 필요. MIT OR Apache-2.0. **[저자 명시] alpha, 고객 production 작업은 아직 비권장**, native 포맷이며 독점 프로젝트/AE SDK 플러그인 미지원.[E1][E2] | 타이틀·모션·합성의 **기본 백엔드 방향 유지**. 실제 설치본의 명령·템플릿·알파/색/오디오 export를 부모가 확인한 뒤 지원 범위를 선언한다. “308 effects” 등 개수는 저자 표기이며 품질 동등성/AE 호환성 증거가 아니다. |
| **P1 · #29 「AutoClip 로컬 우선 AI 영상 클립 제작」** https://github.com/zhouxiaoka/autoclip | **[확인]** 장편→하이라이트 클립, source 구간/점수 메타데이터, CLI/MCP, Studio draft·재구도·자막·커버/카피·출력 kit 경로. MIT / v1.6.1 확인. 실제 품질은 미실행.[A1][A2][A3][A9] | 승인 마스터/인터뷰의 **파생 숏폼 어댑터만 조건부 검토**. 후보 구간·자막/재구도 인간 승인과 전송 차단 검증 전 기본 채택 금지. 자세한 경계는 §4. |
| **P2 · #3 / HyperFrames** https://github.com/heygen-com/hyperframes | **[확인]** HTML/CSS/JS·seekable animation→프레임 캡처/MP4, CLI, headless Chrome/Puppeteer+FFmpeg, Node 22+ 문서. Apache-2.0 코어와 별도 유료 Studio/cloud 모델 옵션을 구별해야 함. **[저자 주장]** 같은 입력의 deterministic 출력.[H1][H2] | 데이터 그래픽·브랜드 모션의 **선택 렌더 어댑터로 보류**. EffectCraft와 중복되므로 초기 필수 의존성으로 추가하지 않음. 외부 CDN·폰트·네트워크·브라우저 버전까지 통제해야 재현성 시험 가능. master/NLE round-trip이나 제작 품질을 검증하지 않음. |
| **P2 · #3 / Real-ESRGAN** https://github.com/xinntao/Real-ESRGAN | **[확인]** image/video restoration·anime 모델·tile/outscale/선택 face enhancement 문서, BSD-3-Clause 코드. README가 NCNN tile 경계 불일치 가능성을 경고. 확인 HEAD는 2024-04-02로 오래되었으나 archived=false. 모델별 권리까지 일괄 검증한 것은 아님.[R1][R2][R3] | 복원·업스케일 **별도 승인 실험으로 보류**. 정체성/질감/시간 일관성 보존, A/B 전구간 검수 필수. 영상 소스에는 누락 라이브러리 자동 pip 설치·가중치 자동 다운로드·메타데이터 `eval`·쉘 호출이 보이므로 무검토 CLI 실행을 승인하면 안 됨.[R3] “4K 출력”은 복원 성공이나 원본 디테일 회복 보증이 아님. |
| **P3 · #3 / ComfyUI** https://github.com/Comfy-Org/ComfyUI | **[확인]** JSON node workflow, 로컬 API, 업스케일·마스크·보간·분할 등 기능 문서, GPLv3 코어. custom node·모델·paid partner/API node는 별도 경로. README의 `--offline`/`--disable-partner-nodes` 표기는 존재하나 실행 검증 안 함.[U1][U2] | 복잡한 복원/마스크 작업용 **선택 어댑터로 보류**, 기본 후반 경로 아님. 모델/노드/워크플로 해시·라이선스·출처·GPU 자원·외부 전송을 각각 승인해야 함. 확산 모델의 고품질·저VRAM 성능 홍보는 검증값으로 쓰지 않음. 학습·재생성은 이번 범위 밖. |
| **P3 · #3 / GSAP** https://github.com/greensock/GSAP | **[확인]** 범용 JS 속성/타임라인 애니메이션 라이브러리. 공식 약관은 **Standard No Charge License**, 상업 사용 무료 설명과 시각적 애니메이션 빌더 경쟁 용도 제한을 동시에 둠. **MIT/Apache나 무제한 오픈소스로 표기하면 틀림.**[G1][G2] | HTML 모션 템플릿 내부의 **제한적 아이디어/의존성 검토로 보류**. 자체 영상 렌더러/NLE/독립 CLI라고 확인하지 않음. 제공할 도구가 금지 용도에 해당하는지는 법무/공급자 확인이 필요할 수 있음. |
| **P3 · #3 / react-postprocessing** https://github.com/pmndrs/react-postprocessing | **[확인]** React Three Fiber용 postprocessing wrapper. Bloom/DoF/Noise/Vignette 등의 effect chain 예시. README 자체가 복잡한 orchestration 용도는 아니라고 설명. MIT.[T1][T2] | 웹/3D 장면 내부 효과의 **예외 후보로 보류**, 일반 영상 후반 스택에서는 제외 권고. 이름의 “postprocessing”만으로 NLE 타임라인·CLI·인코딩·색보정 납품을 지원한다고 해석하면 안 됨. |
| **제외 · #24 「ChordTube 코드 진행·키·BPM 분석」** https://chordtube.net | **[확인]** YouTube embed와 코드/키/박자·섹션, 자동 추정/사용자 수정, AI 모델 v2.1·실험적 장르 모델 v0.2 안내. 신규 분석은 로그인, 공개·embed 허용 영상, 결과 공개. **약관은 정보의 영리 이용과 프로그램에 의한 자동 대량 접근/수집 금지.** 공개 라이선스/API/CLI는 확인 못 함.[C1][C2][C3] | 음악 참고 검색처럼 보여도 **상업 후반 자동화에는 제외**. 로컬 권리 음원의 비공개 분석/편집/음원 이용권을 제공하는 도구로 간주하지 않음. CSV의 멜로디 등 모든 설명을 독립 검증한 것은 아니며 정확도도 보장되지 않음. |

## 4. AutoClip 심층 검토: 맞는 용도와 경계

### 4.1 실제 목적과 데이터 모델

- **[확인]** README가 주 대상으로 드는 것은 podcast/interview/talk/course와 gaming live replay에서의 클리핑이다. 입력은 로컬 영상, 링크, 라이브 다시보기이고, 문서는 OBS/Twitch/YouTube/Kick/Discord/로컬 녹화 경로를 소개한다. 이 조사에서는 링크 수집·OBS 연결·다운로드·게시를 전혀 수행하지 않았다.[A1]
- **[확인]** CLI 문서에는 로컬 영상+선택 SRT, 플랫폼별 출력, project/clip/collection 메타데이터, `video_path`/`cover_path`/`post`/`kit_path`, completed/partial/failed 등이 있다. 기존 클리핑 진입점과 새 quick-output 경로의 동작/기능 플래그가 다르므로 버전과 실제 반환값을 확인해야 한다.[A2]
- **[확인]** `step2_timeline.py`는 SRT/outline을 받아 LLM으로 원본의 주제 시작·끝을 찾고 검증·정렬하는 소스다. 여기서 “timeline”은 곧바로 multi-source master NLE timeline을 의미하지 않는다.[A10]
- **[확인]** Studio는 단순 완전 자동 컷터 이상이다. `Scene`에 start/end/crop_track, `Draft`에 순서 있는 scenes(1–30), 화면비·layout·자막·original_audio·revision이 있고, finishing 문서도 구간/순서/재구도 수정과 렌더 검수를 설명한다. 따라서 “편집 UI가 없다”는 설명도 부정확하다.[A3][A11]
- **[권고]** 그래도 승인 coverage_set 전체를 여러 take/source와 연결하고 필수 사건/대사/공개 순서·접합 QA를 추적하는 마스터 계약은 Craft 쪽이 소유해야 한다. **주제 점수/하이라이트 점수는 편집 요구 충족률이 아니다.**
- **[미확인]** 검토한 공개 자료로 Premiere/AE/Resolve/FilmCraft 간 프로젝트 round-trip, EDL/AAF/OTIO/FCPXML 전 기능 보존을 보장할 수 없다. “보편적 round-trip 없음”을 설계 전제로 하되 특정 미지원 기능 전체를 소스 전수 부재로 단정하지 않는다.

### 4.2 자막·음향·출력

- **[확인]** 기존 SRT를 넣거나 로컬 Whisper/SenseVoice 또는 cloud ASR 경로를 선택하는 문서가 있다. export 소스는 SRT의 원본 구간을 clip-relative 시간으로 자르고 FFmpeg 자막 burn-in/화면비/타이틀 처리를 한다.[A1][A2][A13]
- **[확인]** finishing 문서는 원음 유지와 기존 자막 burn-in 선택, 번역 시 text model 필요, source 자막이 없으면 그 단계에서 새 자막을 만들어 주지 않음을 명시한다. 단계별 동작을 구별해야 한다. 이 문서는 karaoke/단어별 동효과를 첫 범위에서 제공하지 않는다고도 적는다.[A11]
- **[확인]** `Draft.original_audio`와 원음 트랙 사용 선택은 보이나, 이것을 대사/음악/효과의 분리 stem 제공으로 해석할 근거는 없다. 전문 mix/master 또는 다국어 성우 대체 품질도 검증하지 않았다.[A3][A11]
- **[확인]** legacy export 소스 주석은 기본 stream-copy 클립과 배포용 재인코딩 export를 구분한다. 최종 export 경로는 frame-accurate trim 등을 의도한다. **[미확인]** 실제 출력의 keyframe 경계·PTS·VFR·동기·한국어 줄바꿈/폰트·HDR 처리는 테스트하지 않았다.[A13]
- **[권고]** 결과 MP4/커버/문안 kit는 검수 대상의 **파생 납품 후보**다. source range/hash·crop/caption revision을 마스터 측 계보에 다시 묶고, 별도 sidecar가 필요하다면 어댑터 출력에서 실제 제공되는지 확인 후 결정한다. 영상에 글자를 구워 넣은 뒤 편집 가능한 원래 자막이 남는다고 약속하지 않는다.

### 4.3 의존성·설치 footprint

**[확인]** MIT 소프트웨어라는 사실과 설치 크기가 작거나 실행이 무료라는 판단은 별개다.[A1][A9]

| 경로 | 문서/소스에서 확인한 footprint | 설계상 취급 |
|---|---|---|
| Desktop | Apple Silicon macOS / Windows 10·11 x64 다운로드 경로, Python·FFmpeg 번들. React/Tauri/FastAPI 등 구성 소개.[A1] | 현재 Linux 작업 환경의 최소 필수 도구로 자동 추가하지 않음. 설치본 서명·공급망·자동 업데이트 경로는 별도 점검. |
| Python CLI/MCP | Python ≥3.10(3.11 권장), FFmpeg 필요. package에 web/server·SQLAlchemy·Celery/Redis·yt-dlp·LLM SDK·MCP·Sentry 등 다수 의존성. 추가 로컬 ASR/model 설치 경로 존재.[A2][A9] | CLI가 가볍고 순수한 오프라인 함수라는 가정 금지. stdio MCP가 게시·환경설정까지 노출할 수 있으므로 필요한 도구만 허용해야 함. |
| Docker/Web | Docker/Compose v2, app·Redis·Celery worker/beat·Flower, data/logs/uploads 및 모델/결과 디스크. 3000/8000/5555 등 인터페이스 안내.[A12a] | 단일 편집 명령 대신 서버 스택 설치에 해당. 공식 문서도 trusted network를 전제하고 public access control/network isolation 필요를 경고. |
| 완전 로컬 모델 | Ollama/LM Studio + Whisper/SenseVoice 조합을 공식 문서가 소개.[A1][A2] | **[저자 주장]** offline 가능. 모델 최초 다운로드·라이선스·RAM/VRAM·품질, telemetry/diagnostics 차단까지 확인해야 실제 무전송 판단 가능. |

설치/모델/캐시/입출력의 정확한 총 GB, 우리 장비 처리시간, 한국어 전사 정확도는 **미확인**이다. README의 Mac benchmark와 특정 LLM 비용 수치는 cloud ASR/이미지 비용을 제외한 저자 예시이므로 견적·성능 보증에 쓰지 않는다.[A1]

### 4.4 외부 전송·비용·보안: 문서 충돌을 포함한 위험

| 경로 | 근거와 관찰 | 권고 |
|---|---|---|
| Cloud LLM / vision | **[저자 설명]** text model에 관련 전사/카피, vision에 sampled frame+text를 provider로 전송.[A1][A4] | 제공자·모델·정확한 전송 데이터·보존/훈련 정책·국외 이전·예산을 승인받기 전 호출 금지. base URL을 사용자 설정 가능하므로 “로컬” 이름만 신뢰하지 않음. |
| Cloud ASR | **[확인]** 소스에 audio base64 또는 `/audio/transcriptions` multipart 전송, 오디오 chunk 생성 코드가 있다.[A14] | 원본 영상 비업로드와 음성 비전송은 다른 주장이다. 민감 발화/배우 음성 권한 확인. |
| Analytics / crash | 개인정보 **초안**은 PostHog usage analytics 활성, crash report 기본 on(DSN 설정 조건), feedback는 analytics off와 별개로 PostHog→공개 GitHub로 전달될 수 있다고 설명.[A4] | 모델 경로와 별도로 차단/승인. 소프트웨어의 자체 준수 체크리스트를 법적 준수 인증으로 인용하지 않음. |
| **실패 진단/미디어 — 중대한 불일치** | README/개인정보 초안은 제작자 서버에 미디어를 올리지 않는다는 취지다. 그러나 **[확인]** `consent._unset()`은 `diagnostics=True, media=True, full_original=False`. `observe`는 새 failed/partial attempt를 예약하고 `service.background_enqueue`는 로컬 파일이면 excerpt를 큐에 넣고 업로드를 깨운다. `upload.endpoint()`에는 기본 Worker fallback이 있고 빈 endpoint 환경변수는 비활성화가 아니다.[A4][A5][A6][A7][A8] | “앱 시작 전 무전송 설정/네트워크 deny-by-default 확인”을 설치·실행 검수의 차단 게이트로 권고. 단지 analytics를 off하거나 API key를 안 넣는 것으로 충분하다고 약속하지 않음. |
| 진단 운영/삭제 | **[문서 주장]** 새 링크 입력은 sanitized public source URL만, 로컬은 압축 excerpt 기본, 원본 전체는 opt-in, 14일 삭제. 문서 자체가 서버 배포가 새 링크 규칙보다 이전일 수 있어 실제 업데이트 상태 미확인이라고 명시.[A5] | 원격 서버 배포/삭제/보존은 이번에 검증하지 않음. 고객 비공개 소스를 넣어 시험하지 않음. UI 동의 문구와 소스 기본값의 차이를 승인 문서에 노출해야 함. |
| Publishing / 계정 | CLI/MCP 문서는 Bilibili/Upload-Post 등 별도 계정·게시 경로를 노출.[A1][A2] | 이번 설계 연구에서 계정·쿠키 사용, 게시·구매·업로드는 금지. 후속 어댑터도 produce 권한과 publish 권한을 분리하고 publish를 기본 비활성/미노출. |
| 비용 | MIT 라이선스, cloud LLM/ASR/image는 provider 과금, 로컬은 계산/스토리지 비용.[A1][A4] | 요청별 예상·상한·취소 시 청구·재시도 범위가 승인되어야 함. 도구 구독 무료와 API 무료를 혼동하지 않음. |

**판단:** 이 충돌은 악성 행위를 입증하는 것은 아니지만, **기밀 미디어를 맡기기 전 해소해야 하는 검증 차단 사유**다. 이번에는 실제 업로드/네트워크 캡처/서버 테스트를 하지 않았다.

### 4.5 아이디어 재사용 / 선택 어댑터 / 재사용하지 않을 것

- **아이디어로 채택 권고:** 전사와 source range를 함께 보존하는 후보 제안, scene별 crop track, 원본을 건드리지 않는 variant/revision, 실제 requested/used style 기록, partial/failed/interrupted 구분, 명시적 출력 검사. AutoClip의 구체 코드 복제 여부/라이선스 공지는 구현 단계에서 별도 결정한다.[A2][A3]
- **선택 어댑터로 검토:** 이미 승인된 인터뷰·강연·게임 녹화·마스터의 숏폼 후보 탐색. candidate→사람의 내용/권리/재구도 승인→분리된 실행 승인→파생 QA. 필요한 기능만 허용하고 cloud/diagnostics/publish는 기본 허용하지 않는다.
- **마스터에서 재사용하지 않을 것:** highlight 점수로 필수 coverage 삭제, 장면 밖 handle 추정, 원음에서 존재하지 않는 stem 가정, 화자 추적을 모든 극영화/다인물 blocking에 일반화, 플랫폼 프리셋을 프로젝트의 편집 의도로 대체, 실패 진단 자동 업로드/자동 게시.

## 5. 신규 후반 설계에 주는 함의 — 제안이며 구현 명세 아님

### 5.1 수령과 변경 권한

**[권고, P1에 근거]** 첫 게이트는 “파일 존재”가 아니라 **승인 revision의 수령 검사**다. coverage_set↔shot/take↔source hash/range, 실제 stream/track, FPS/timebase/색/해상도, reference lineage, G2–G4 근거, 권리 제한, conditional 작업 및 수령자 수락을 확인한다. unverified는 자동 진행시키지 않는다. accepted도 후반 마스터의 자동 PASS가 아니다.

- 외측 handle=0이면 자동 디졸브를 위해 외부 프레임을 끌어오거나 임의 freeze/interpolation을 넣지 않는다. 허용 구간 안 overlap도 길이/서사/동기 변경으로 검토하고, 불가능하면 hard cut 또는 제작자에게 재요청한다.
- 실제 source audio/사용 가능한 track만 시작점으로 삼는다. 분리 stem이 없으면 mix 원본으로 표시한다. source separation/voice replacement를 후반 기본 기능으로 몰래 추가하지 않는다.
- 구간·순서·재구도·배속·전환·번역·합성으로 채택 근거가 달라지면 해당 접합/전구간 판정을 revision에 묶어 재검수한다.[P1]

### 5.2 “자동 실행 + 사람 승인”을 위한 최소 경계

| 게이트 | 자동화 가능한 일(승인된 범위 안) | 사람이 승인하거나 차단 해제해야 할 일 |
|---|---|---|
| 수령 | manifest 대조·hash·기술 메타데이터 확인 계획 | 누락·권리·conditional 수락·검증 불능 해소 |
| 편집 계획 | coverage 보존 검사·후보 편집/수정안 준비 | 서사/순서/구간 변경, 부족 handle 대응, creative 의도 |
| 작업 실행 | 허용된 Craft 명령의 반복·파생본 생성·상태/실패 기록 | 새 설치/모델/플러그인, provider 전송, 예산·원격 처리 |
| 분야별 리뷰 | 영상/오디오/자막 기술검사 보조, 수정 영향 범위 계산 | 전구간 시청·해당 청취, 대사·의미·정체성·접합의 판단 |
| 마스터/납품 | 승인 설정으로 렌더, 파일·설정·소스 계보 기록 | 실제 마스터 채택 및 전달 범위. 게시/공개는 별도 권한 |

자동 검사만 가능한 환경에서 지각 검수를 했다고 표기하지 않는다. 공식 문서나 모델 점수도 실제 재생/청취의 대체가 아니다.[P1]

### 5.3 백엔드·어댑터 경계

- **Craft 기본 경로:** FilmCraft는 편집 프로젝트, EffectCraft는 범위가 분명한 합성/모션 결과, SoundCraft는 사용 가능한 음향의 정리/믹스 역할로 설계 방향을 유지한다. 실제 설치본에서 열거·실행 가능한 명령과 결과 포맷만 capability로 선언한다. EffectCraft upstream alpha 경고는 로컬 smoke test 통과와 별도로 남긴다.[E1]
- **FFmpeg 등 보조:** probe/변환/검사 결과를 증거로 다루되 Creative master의 두 번째 진실 원천을 만들지 않는다. 색공간·오디오 channel mapping·timebase·납품 loudness 목표를 명시한 뒤 처리한다.[F1][F3]
- **Premiere 선택 어댑터:** 공식 UXP 문서는 JavaScript 기반 Premiere 통합 프레임워크와 Premiere DOM API를 제공한다. 이것은 CLI 전체 지원이나 모든 편집 기능/프로젝트 교환의 동등성을 뜻하지 않는다. **[권고]** 버전·권한·실제 API 범위와 설치 승인을 확인할 때까지 선택 후보로만 둔다.[D1]
- **After Effects 선택 어댑터:** 공식 Scripts 문서는 ExtendScript(.jsx/.jsxbin), 실행 경로, 파일 쓰기/네트워크 허용 설정을 설명한다. **[권고]** 승인된 script/컴포지션 렌더 경로로 한정하고 EffectCraft native 프로젝트와의 자동 호환을 약속하지 않는다.[D2][E1]
- **DaVinci 선택 어댑터:** 이번 공식 개발자 URL은 Page not found였다. SDK/API 언어·Free/Studio 차이·headless/원격 제약·프로젝트 교환을 **미확인**으로 남긴다. 부모가 설치본 문서/공식 유효 경로를 확인하기 전 capability를 만들지 않는다.
- 교환은 지원이 검증된 파일/렌더+sidecar를 우선 고려하되 **실제 지원 포맷은 아직 결정하지 않는다**. 타임라인 왕복 시 누락될 효과·폰트·색·오디오·메타데이터를 공개하고, universal editor round-trip을 약속하지 않는다.

## 6. 설치·실행 승인 경계와 남은 검증

후속 구현/실험이 별도로 승인되는 경우에만 다음 정보를 제출하도록 **권고**한다. 현재 승인되었다고 간주하지 않는다.

1. 도구/버전/SHA·배포물·checksum/서명, OS/runtime/codec/browser/GPU, 설치 위치·디스크 footprint·되돌리기.
2. 코드·모델·플러그인·폰트·템플릿 각각의 라이선스/출처/재배포·상업 조건. GSAP·ChordTube·FFmpeg build 옵션을 별도 체크.[G2][C2][F2]
3. 전송받는 주체·주소·데이터 종류·권한·보존·삭제·학습 정책, diagnostics/telemetry/update/cloud/publish 각각의 off 확인. AutoClip은 위 문서 충돌 해소 및 실제 배포본 검증이 선행돼야 한다.[A4]–[A8]
4. 비용 상한·재시도·중단·남은 원격 작업/스토리지 비용, 계정 권한과 보안. 구매/가입/로그인은 별도 승인.
5. 권리 확보된 비기밀 테스트 소스의 승인, 원본 비덮어쓰기, 결과·로그의 보존 위치, 실제 전구간 재생/청취와 마스터 QA 기준.
6. 실패·부분 성공·취소·재시작·버전 변경 시 계보와 재검수. `completed`를 coverage/서사/음향 품질 PASS로 바꾸지 않음.

**미해결/한계:** 설치된 FilmCraft/EffectCraft/SoundCraft의 구체 capability는 부모 조사 범위다. 모든 후보의 실제 품질·한국어 처리·성능·코덱/색/동기·editor exchange는 테스트하지 않았다. 오픈소스 코드 라이선스를 읽었으나 종속물/모델 전부의 법률 감사를 한 것은 아니다. AutoClip 원격 진단 서버 상태·보존·삭제 및 release binary 동작은 미확인이다. Blackmagic URL 실패 외 선택 primary source 본문은 열람되었다. 광범위 홈 디렉터리 skill 탐색 1회는 시간 초과 후 알려진 skill 경로로 해결했으며 설치나 대체 브라우저를 도입하지 않았다.

## 7. 수행 증거와 금지 작업 미수행 선언

- **수행:** CSV 38행 전수 열람/파싱, 생산 인계 문서 전체 열람, web-ai skill 읽기, Obscura 버전/help 확인, 공식 공개 문서/저장소 API/고정 소스 HTTP GET, `/tmp` 텍스트 캐시, 이 보고서 작성.
- **검증:** 9개 도구의 공식 출처 대조, 8개 GitHub SHA 확보, AutoClip main 재확인·latest release 대조, 코드상 진단 default-on과 cloud ASR 전송 경로 정적 확인. **테스트 추가/수정 0, 도구 실행 품질 테스트 0.**
- **Git:** 작업 cwd와 `video-production-skills`는 Git working tree가 아니어서 `git diff --cached --name-only`로 index 조회가 되지 않았다. Git add/commit/stage 명령은 수행하지 않았고 index를 만들거나 수정하지 않았다. 따라서 “저장소 전체의 staged 상태 검증”을 했다고 주장하지 않는다.
- **미수행:** 외부 도구 설치/clone/build/import/run, 미디어 편집/렌더/ASR·LLM·vision 호출, 모델/가중치 다운로드·훈련, 계정/쿠키/credentials 사용, provider 생성·업로드·게시·구매·공개, CSV·템플릿·프로젝트 goal/spec/source 파일 변경, 추가 연구자/자식 에이전트 실행. 공개 문서 열람 외 외부 제출은 없었다.
- **유일한 정식 산출물:** `/home/declan/.pi/agent/sessions/--home-declan--/subagent-artifacts/outputs/8726d09a-e9f9-4790-8d20-8f79a4694382/research/postproduction-source-research.md`

## 8. 1차 출처 링크

모든 웹 링크 확인일은 2026-11-26 KST다. GitHub `blob/<SHA>/...` 링크는 조사에 사용한 API/raw 파일과 같은 고정 내용이다. 서비스 웹페이지는 시점 고정본을 보장하지 않는다.

[A1]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/README.md
[A2]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/docs/CLI_AND_MCP.md
[A3]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/studio/models.py
[A4]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/docs/PRIVACY.en.md
[A5]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/docs/DIAGNOSTICS_UPLOAD.md
[A6]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/diagnostics/consent.py
[A7]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/diagnostics/service.py
[A8]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/diagnostics/upload.py
[A9]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/pyproject.toml
[A10]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/pipeline/step2_timeline.py
[A11]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/docs/FINISHING_GUIDE.md
[A12]: https://api.github.com/repos/zhouxiaoka/autoclip/releases/latest
[A12a]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/docs/DOCKER.en.md
[A13]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/publish_export.py
[A14]: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/cloud_transcription.py
[E1]: https://github.com/storytold/effectcraft/blob/50358c2e4720a614a9b32f3de15172ef3b9697ec/README.md
[E2]: https://github.com/storytold/effectcraft/blob/50358c2e4720a614a9b32f3de15172ef3b9697ec/LICENSE-MIT
[F1]: https://github.com/FFmpeg/FFmpeg/blob/288839e860c7e55e466170215fc478fa7e750e97/README.md
[F2]: https://github.com/FFmpeg/FFmpeg/blob/288839e860c7e55e466170215fc478fa7e750e97/LICENSE.md
[F3]: https://github.com/FFmpeg/FFmpeg/blob/288839e860c7e55e466170215fc478fa7e750e97/doc/filters.texi
[R1]: https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/README.md
[R2]: https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/LICENSE
[R3]: https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/inference_realesrgan_video.py
[T1]: https://github.com/pmndrs/react-postprocessing/blob/e07ef9a890c8a202a3b20eac0249032cff4e7805/README.md
[T2]: https://github.com/pmndrs/react-postprocessing/blob/e07ef9a890c8a202a3b20eac0249032cff4e7805/LICENSE
[H1]: https://github.com/heygen-com/hyperframes/blob/7c217d9fdf3e32c628953f7325ddd90e0ff94392/README.md
[H2]: https://github.com/heygen-com/hyperframes/blob/7c217d9fdf3e32c628953f7325ddd90e0ff94392/packages/engine/package.json
[G1]: https://github.com/greensock/GSAP/blob/5e6c35ff8eedea12d4f229129def635277d8b0f2/README.md
[G2]: https://gsap.com/standard-license
[U1]: https://github.com/Comfy-Org/ComfyUI/blob/8b0f107157b58f9ec79a19fb3182e78cb30f0a23/README.md
[U2]: https://github.com/Comfy-Org/ComfyUI/blob/8b0f107157b58f9ec79a19fb3182e78cb30f0a23/LICENSE
[C1]: https://chordtube.net/
[C2]: https://chordtube.net/terms
[C3]: https://chordtube.net/ai-model
[D1]: https://developer.adobe.com/premiere-pro/uxp/
[D2]: https://helpx.adobe.com/after-effects/using/scripts.html
[P1]: /home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/video-production-skills/docs/design/04-qa-handoff.md

- AutoClip main 확인: https://api.github.com/repos/zhouxiaoka/autoclip/commits/main
- AutoClip 릴리스 고정 페이지: https://github.com/zhouxiaoka/autoclip/releases/tag/v1.6.1
- AutoClip MIT: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/LICENSE
- AutoClip 실패 감지 소스: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/diagnostics/observe.py
- AutoClip requirements: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/requirements.txt
- AutoClip Compose: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/docker-compose.yml
- AutoClip kit 소스: https://github.com/zhouxiaoka/autoclip/blob/2f511907a72cbfbb8d86639f6441967b826acb6a/backend/services/studio/publish_kit.py
- EffectCraft Apache: https://github.com/storytold/effectcraft/blob/50358c2e4720a614a9b32f3de15172ef3b9697ec/LICENSE-APACHE
- FFprobe 문서: https://github.com/FFmpeg/FFmpeg/blob/288839e860c7e55e466170215fc478fa7e750e97/doc/ffprobe.texi
- Real-ESRGAN anime video 문서: https://github.com/xinntao/Real-ESRGAN/blob/a4abfb2979a7bbff3f69f58f58ae324608821e27/docs/anime_video_model.md
- HyperFrames Apache: https://github.com/heygen-com/hyperframes/blob/7c217d9fdf3e32c628953f7325ddd90e0ff94392/LICENSE
- ChordTube 분석 요청 안내(열람만): https://chordtube.net/analysis
- 접근 실패한 Blackmagic 경로: https://www.blackmagicdesign.com/developer/product/davinci-resolve
