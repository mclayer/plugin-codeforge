---
title: Inter-plugin contract sibling backfill (5 lane output + MANIFEST + lint 확장)
slug: cfp-42-inter-plugin-contract-sibling-backfill
status: Phase-1-Design
author: Claude (Opus 4.7) — CFP-42 Phase 1 author
created: 2026-04-29
story: CFP-42
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only Decomposition)
  - ADR-010 (Inter-plugin Contract Sibling Sync — 본 CFP author)
---

### §1. 목적

ζ arc 가 도입한 5 lane plugin canonical `kind: contract` 의 wrapper sibling reference backfill + MANIFEST.yaml registry SSOT 신설 + lint 4 신규 검사로 향후 sibling 누락 차단.

### §2. 현재 구조 (As-is)

- `docs/inter-plugin-contracts/`: 5 파일 (3 kind:registry + 2 kind:contract — review-verdict v1+v2)
- `scripts/check-inter-plugin-contracts.sh`: kind:contract frontmatter+본문 sanity 검증 (manifest completeness 검증 없음)
- 5 lane plugin 의 canonical contract 는 각 plugin repo 의 `docs/inter-plugin-contracts/` 에 존재 — 각 plugin CLAUDE.md 가 자기 lane self-write 책임 명시

### §3. 도입할 설계 (To-be)

- `MANIFEST.yaml`: kind:contract registry SSOT (6 entry / 7 file — review_verdict v1+v2 + 5 신규)
- 5 신규 sibling file: review-verdict-v2 패턴 (frontmatter + "상위 SSOT 위치" 섹션 + canonical 본문 verbatim mirror)
- 기존 review-verdict v1+v2 frontmatter `related_adrs` 에 ADR-010 추가
- `check-inter-plugin-contracts.sh` 에 4 신규 검사 (manifest completeness · orphan · ADR-010 reference · sibling marker)
- `scripts/test-check-inter-plugin-contracts.sh` 신규 — lint 회귀 테스트 harness
- `CLAUDE.md` "Inter-plugin Contract" 섹션 — kind:contract 6 / kind:registry 3 분리 명시 + ADR-010 인용

### §4. API 계약 (영향받는 컴포넌트)

- wrapper repo `docs/inter-plugin-contracts/` 표면 (file 7 추가/갱신)
- wrapper repo `scripts/` (lint 1 갱신, harness 1 신규)
- consumer 사용 표면: lint 인터페이스 변경 없음 — 내부 검증 강화만

### §5. 마이그레이션 경로

본 CFP 는 wrapper repo 자체 self-application. 다른 plugin 또는 consumer 에 BREAKING 영향 없음. 선언:
- 5 lane plugin canonical 은 변경 없음
- review-verdict v1+v2 frontmatter 의 `related_adrs` array 에 항목 추가만 (consumer 로 노출되는 schema 의미 변경 없음)

### §6. 리팩터링 선행 항목

없음. 본 CFP 는 신규 file 추가 + 기존 lint 확장 + 메타데이터 갱신만.

### §7. 보안 설계

#### §7.1 Trust boundary

- canonical 본문 verbatim mirror 의 supply-chain 영향: lane plugin canonical 이 손상되면 sibling 도 손상 가능. 다만 wrapper-only 모델에서 sibling 은 reference 문서 (실행 코드 아님) 라 직접 실행 영향 없음
- mirror 시점: Phase 2 PR 작성 시 1회 — `mcp__github__get_file_contents` 로 fetch, sha 기록은 본 CFP 시점에는 보존 안 함 (drift detection 후속 CFP 의 영역)

#### §7.2 Threat model (STRIDE-LITE)

- Spoofing: lane plugin canonical 이 적대적으로 변경된 경우 → wrapper sibling sync PR 시 review 의 책임. 본 CFP 자동 검출 안 함
- Tampering: wrapper sibling file 이 변경된 경우 → wrapper repo CODEOWNERS + PR review 가 1차 방어
- Repudiation: N/A
- Information disclosure: contract 표면은 모두 public. 민감 데이터 부재
- Denial of service: lint 가 외부 API 호출 0 → DoS 표면 없음
- Elevation of privilege: N/A

#### §7.3 Auth/authz

N/A — 본 CFP 는 문서·lint 만.

#### §7.4 민감 데이터 분류·흐름

N/A.

#### §7.5 위협↔완화 매핑

| 위협 | 완화 |
|---|---|
| canonical 손상 후 sibling 자동 mirror | 본 CFP 시점은 author 의무 (수동 PR 작성). 후속 CFP 에서 drift detection 도입 |
| sibling 누락 (sync PR 깜빡) | lint manifest mismatch 로 다음 wrapper PR 가 차단 (간접 강제) |

### §8. Test Contract

§8 의 자세한 케이스는 spec [§8 Test contract preview](../superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md) 참조. 6 케이스 (T1-T6) 가 `scripts/test-check-inter-plugin-contracts.sh` 에 구현됨.

#### §8.1 기능 테스트

- T1 manifest mismatch (negative)
- T2 orphan (negative)
- T3 frontmatter ADR-010 누락 (negative)
- T4 sibling marker section 누락 (negative)
- T5 정합 상태 (positive)
- T6 review-verdict v1+v2 + 3 kind:registry 회귀 (positive)

#### §8.2 성능 테스트

N/A — 순수 shell+python lint, baseline 무관.

#### §8.3 통합 테스트

`bash scripts/check-inter-plugin-contracts.sh` 가 wrapper main branch 상태에서 exit 0 반환.

### §9. 리뷰 결과

(Phase 1 설계 리뷰 시 채움)

### §10. ADR 정합성

관련 ADR:
- ADR-008 (Inter-plugin Contract Versioning): 본 CFP 는 backward-compat 추가 (sibling 신설 + frontmatter 항목 추가) — ADR-008 위반 없음
- ADR-009 (Wrapper-only Decomposition): sibling reference 문서 추가는 wrapper-only 모델 강화 — ADR-009 정합
- ADR-010 (Inter-plugin Contract Sibling Sync): 본 CFP 가 author — 신규 ADR 필요, Phase 1 산출물로 포함

### §11. 데이터 마이그레이션

N/A — schema 변경 없음. 기존 review-verdict v1+v2 frontmatter `related_adrs` array 에 ADR-010 항목 추가만 (additive, lossless). Migration / rollback / integrity invariant 모두 N/A.
