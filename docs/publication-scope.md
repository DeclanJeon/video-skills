# 공개 저장소 범위

## 공개하는 것
- 세 제작 패키지의 현재 작업 트리 소스, 스킬 문서, 스키마, 예제와 테스트.
- 설계·운영 문서 및 로컬 기술 시험의 검증 기록. 기록된 테스트 통과는 GitHub CI나 다른 호스트에서의 실행 보증이 아니다.
- postproduction의 승인된242-file source scope와 공개 검수 보고서는 수정하지 않는다.

## 로컬에 보존하고 게시하지 않는 것
- 기존 `video-preproduction-skills/.git` 이력과 인덱스. 루트 저장소는 현재 파일의 일반 tree snapshot을 추적하며 submodule/gitlink를 만들지 않는다. 내부 저장소의 과거 커밋을 루트의 과거 이력으로 이식하지 않는다.
- `.ultragoal/`, `.superpowers/`, Python/pytest 캐시, 환경 파일과 credentials, 임시 lock 파일.
- 외부 절대경로를 가리키는 `compat/video-production-assets/scripts` 심볼릭 링크. 외부 자원 파일은 읽거나 복사해 게시하지 않는다.
- `video-preproduction-skills/docs/examples/ref-prompt-01/`의 원문 레퍼런스·동반 분석 자료, `*.tar.gz` 등의 scratch 아카이브. 이들에 의존하는 프리프로덕션 레퍼런스 검사는 공개 clone에서 자료를 별도로 준비해야 한다.

`.gitignore`는 게시 제외이지 로컬 원본 삭제가 아니다. 과거 문서의 머신별 절대경로나 제외한 로컬 기록 링크는 이력·운영 문맥이며 새 clone에 그 경로나 환경이 자동 생성되지 않는다.

## 검증·권리 경계
코드·문서 게시만 수행한다. 실제 사용자 미디어 생성·공급자 업로드·유료 실행·도구 설치·전역 스킬 등록은 수행하지 않는다. synthetic native 시험 자료는 기술 검증용이며 사용자 작품이나 인간 시청·청취 인증이 아니다. 라이선스를 임의로 추가하지 않으며 외부 폰트·템플릿·프로그램의 권리는 별도다.
