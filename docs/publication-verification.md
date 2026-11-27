# GitHub 공개 검증 기록

- 요청에 따라 `https://github.com/DeclanJeon/video-skills`를 **public**, 기본 브랜치 `main`으로 생성하고 force 없이 push했다.
- `0c47a1e`: 세 패키지·스킬·계약·검증 자료의 현재 snapshot. `68ff543`: 아이콘/배지/Mermaid/문서 표 README 및 공개 범위.
- 게시 파일1,340개를 대상으로 credential 패턴과 제외 경로를 점검했다. 해당 패턴 일치0; 자격증명이 절대 없다는 보편 인증은 아니다.
- Git mode160000/120000 항목0. 기존 프리 내부 HEAD `98da7817e09e5a047ad82302dad2442e4c2fb217`과 staging 전후 내부 HEAD/index bytes 보존을 확인했다. 기존 이력은 로컬에 그대로 있고 루트는 파일 snapshot을 게시한다.
- 로컬 검사: 프리 `scripts/check_skills.py`20개/findings0, 프로 package5개/findings0, 포스트 package8개/issues0 및 acceptance52/52·334 PASS 매핑. 공용 boundary 테스트3 passed0.26s.
- 실제 staged tree를 별도 임시 디렉터리에 export하고 프로/포스트 package 검사와 포스트 승인 source scope/acceptance 검사를 통과했다. 내부 `.git`과 private archive 없음 확인. 제외한 레퍼런스 자료가 필요한 프리 검사를 clean clone 전체 PASS로 주장하지 않는다.
- GitHub API에서 public·main·remote HEAD=local HEAD 및 README bytes 일치를 확인했다. GFM 변환에서 heading13개/table3개/Mermaid markup을 확인했다. API는 heading ID를 제공하지 않으므로 API ID 확인 시도는 증거로 세지 않는다. 실제 브라우저의 Mermaid/레이아웃 visual QA는 수행하지 않았다.
- 기존 포스트438-case full suite는 source 불변의 기록이다. 이번 문서·Git 작업에서 전체 suite를 재실행하지 않았으며 새 CI 결과로 표시하지 않는다.
- 공개 정책은 [publication-scope.md](publication-scope.md). 외부 리소스 symlink·원문 레퍼런스·scratch archive·로컬 agent state·환경·캐시는 로컬 보존하고 게시하지 않았다. 도구 설치·글로벌 스킬 등록·미디어 생성/공급자 전송은 하지 않았다.
