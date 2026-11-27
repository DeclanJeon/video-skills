# GitHub 공개 저장소·README 설계

사용자 요청: `video-skills`를 저장소로 만들고 GitHub 형식의 아이콘 포함 README를 꾸며 push. 후속 답변으로 public을 명시했다.

## 접근
- 선택: 루트 단일 저장소에 현재 세 패키지 파일을 일반 파일로 추적. 기존 내부 `.git`은 로컬에 보존하며 submodule로 게시하지 않는다.
- 대안: 세 저장소의 submodule 구성은 추가 remote/게시 권한과 사용 절차가 필요하여 이번 요청 범위에서 제외한다. 기존 이력 삭제·이동은 하지 않는다.
- README: 🎬 소개 → Mermaid 3단계 흐름 → 역할/진입점 표 → 기존 환경 CLI → 근거가 있는 검증·지원 한계 → 문서 지도.
- 비밀정보·로컬 상태·외부 symlink·원문 레퍼런스·scratch archive는 게시하지 않는다. native source bytes와 기존 패키지는 바꾸지 않는다.
- remote: `DeclanJeon/video-skills`, public, 기본 브랜치 main. 강제 push·추가 라이선스·설치·스킬 등록 없음.

## 수락
로컬 링크 및 구조 검사, staged file/secret/gitlink 점검, 기존 내부 HEAD/index 보존, 승인된 post source scope 불변을 확인한다. 원격 public 속성과 HEAD가 로컬 main과 일치하고 GitHub README가 반환되는 것을 확인한다. 실제 GitHub UI 화면 검수나 전체 suite 재실행을 가장하지 않는다.
