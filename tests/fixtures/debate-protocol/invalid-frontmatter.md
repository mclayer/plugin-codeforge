---
kind: registry
registry: debate-protocol
# version 필드 누락 → check-doc-frontmatter.sh registry kind 검증 FAIL 의무
status: Active
# canonical_repo / canonical_path / date 필드 누락
---

# debate-protocol-v1 invalid fixture (CFP-391 TDD)

본 fixture 는 `check-doc-frontmatter.sh` 가 registry kind 의 필수 필드 (version + canonical_repo + canonical_path + date) 누락을 검출하는지 검증하기 위한 negative fixture.
