# 오프라인 계약 예제

모든 신원·계정·native ID·capability/authority는 **합성 테스트 자료**다. 실제 얼굴 이미지나 실제 사용 가능한 공급자 계약이 아니다. JSON의 upload/generation 플래그는 오프라인 상태 전이 fixture에만 쓰며 외부 전송/실제 생성 승인으로 사용할 수 없다.

패키지 루트에서 예제를 임시 작품 폴더로 복사하고 로컬 준비만 검사한다:

```bash
work=$(mktemp -d)
cp examples/*.json examples/*.txt "$work/"
python3 scripts/production.py init "$work/ledger.json" "$work/state.json"
python3 scripts/production.py validate "$work/ledger.json"
python3 scripts/production.py ready "$work/ledger.json"
python3 scripts/production.py prepare "$work/ledger.json" C01 "$work/capability.json" "$work/authority.json" "$work/bindings.json"
```

출력은 로컬 prepared packet이며 제출/결과가 아니다. 상태는 `$work/ledger.json`의 production namespace에 저장된다. 실제 작품에는 fixture를 가져가지 말고 검수된 프리프로덕션·실제 지원 역할·현재 실행 권한으로 새 입력을 작성한다.
