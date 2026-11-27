# 구현 독립 리뷰 01 보완

원본 판정과 재현 증거는 [implementation-review-01.md](implementation-review-01.md)에 불변 보존한다. 아래 체크는 코드 보완·회귀 확인이며 독립 재검수 PASS를 대신하지 않는다.

- [x] F1: checked build_handoff에 root 필수화, 납품 원본/현재 승인 핀을 재확인. 렌더 후 삭제·교체를 라이브러리/실제 CLI에서 각각 회귀 검사.
- [x] F2: upstream character→identity/SSOT·panel version/image/sheet·LOOK·voice/spatial·cue/caption·source/master·artifact closure 보존. exported coverage에 asset_uses/origin을 유지. dependencies는 로컬 계보이며 전부 업로드하지 않음. 실제 기존 project_index와 대표 closure 대조, 패널 버전 충돌 검사.
- [x] F3: ApprovedConfig로 클립별 scope/source hash/구성 hash·길이·크기·요청 음향을 명시. prepare와 reserve가 정확한 approval을 비교. 지원 capability를 승인으로 대체하지 않음.
- [x] F4: 최초 채택/재검수에 현재 승인 핀/설정 검사, Selection에 적용 approval 결속. 승인 증거 drift 시 차단. 새 scope 재검수는 새 approval을 명시적으로 받고 원래 request 핀은 유지.
- [x] F5: T05는 채택된 선행 영상이 있는 상태에서 실제 video role/modality 미지원을 검사. T10 time_elision의 승인/미승인 prop 변화, T22 보고된 반복 대사 결함, T27 실행 중 A→B 교체 후 늦은 성공, T29 range/imports/조건부 판정 변경을 각각 구체적 테스트에 매핑.
- [x] 추가 정책: invalid 필수 source를 후손 재검수로 우회 금지. imports에 영향 없는 conditional source의 유효 판정은 보존 가능함을 양성/음성 회귀로 고정.
- [x] R02 긍정 경로: 기존 로컬 소스는 exact reuse grant로 채택하고 remote job을 발명하지 않음. 필수 요구 제외는 ScopeGrant의 이전/새 source 및 정확한 요구·자산 차이 승인으로만 적용. historical attempts/unknown 예약 보존.
- [x] 동일 검수자의 후속 최종 [review 04](implementation-review-04.md)에서 현 스냅샷 F1–F5/N1–N3 해소와 scoped PASS 확인. 이전 REVISE 보고서는 불변 보존.

수락 사례 실행 결과는 structural-contract / reported-semantic-contract를 구분하고 live_provider_verified/perceptual_quality_verified는 false로 유지한다. 추가 기능도 이 목표의 로컬 계약 범위이며 실제 공급자 호출·설치·결제·Git 작업은 없다.
