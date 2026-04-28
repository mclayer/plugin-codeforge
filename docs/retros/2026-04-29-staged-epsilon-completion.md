---
title: Staged ε Completion 회고 (CFP-25 Path A 설계 → CFP-26/27/28 Phase 0a/0b/0c + CFP-29 Phase 1)
date: 2026-04-29
sprint_period: "2026-04-28 ~ 2026-04-29"
cfp_keys: [CFP-25, CFP-26, CFP-27, CFP-28, CFP-29]
authors: [PMOAgent]
related_stories: [CFP-26, CFP-27, CFP-28, CFP-29]
sentinel_refs:
  - docs/retros/2026-04-28-marketplace-bootstrap-sprint.md
---

# Staged ε Completion 회고

기간: 2026-04-28 ~ 2026-04-29
범위: CFP-25 parent design + CFP-26/27/28/29 4 PR + 3 marketplace sync PR + 1 핸드오프 spec
선행 retro: [2026-04-28-marketplace-bootstrap-sprint.md](2026-04-28-marketplace-bootstrap-sprint.md)

---

## §1 결과 (closure)

### 1.1 commit·PR

| Story / 작업 | repo | PR | merge commit | 버전 | 비고 |
|---|---|---|---|---|---|
| **CFP-25** parent design (staged ε strategy + Path A) | plugin-codeforge | (in CFP-26 PR) | (`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md` commit) | — | 4-round Codex GPT-5.4 협업 spec, Path A 채택 |
| **CFP-26** Phase 0a · write 권한 재분배 (BREAKING) | plugin-codeforge | [#66](https://github.com/mclayer/plugin-codeforge/pull/66) | `e4bd1cd` | v0.15.0 | DocsAgent → 3 owner agent direct write |
| **CFP-27** Phase 0b · lint 강화 (Non-BREAKING) | plugin-codeforge | [#67](https://github.com/mclayer/plugin-codeforge/pull/67) | `1e75442` | v0.16.0 | warning 모드 lint + retro/domain-knowledge templates |
| **CFP-29** Phase 1 · codeforge-review 추출 (BREAKING) | plugin-codeforge | [#68](https://github.com/mclayer/plugin-codeforge/pull/68) | `81a4ad1` | v0.17.0 | 5 review agent + base + 3 checklist 별도 plugin |
| **CFP-28** Phase 0c · lint strict 전환 (Non-BREAKING) | plugin-codeforge | [#69](https://github.com/mclayer/plugin-codeforge/pull/69) | `7b4bff2` | v0.18.0 | warning → strict + retro frontmatter backfill |
| codeforge-review v0.1.0 initial release | plugin-codeforge-review | (initial commit) | `eb63780` | v0.1.0 | 5 review agent + base + 3 checklist + ADR-001 |
| codeforge-review own lint workflow handoff spec | plugin-codeforge-review | (direct push) | `21075d2` | — | CFP-9/13/16 carryover 후속 spec |
| marketplace: codeforge-review entry add | marketplace | [#5](https://github.com/mclayer/marketplace/pull/5) | `bf2bcf9` | — | 신규 plugin 등재 |
| marketplace: codeforge 0.16.0 → 0.17.0 sync | marketplace | [#6](https://github.com/mclayer/marketplace/pull/6) | `362f6a2` | — | CFP-24 의무 |
| marketplace: codeforge 0.17.0 → 0.18.0 sync | marketplace | [#7](https://github.com/mclayer/marketplace/pull/7) | `e681e93` | — | CFP-24 의무 |

**총 4 codeforge core PR + 3 marketplace sync PR + 1 codeforge-review 핸드오프 spec / sprint_period 단일 burst (2일)**.

### 1.2 lint·invariant 상태

| Lint / Invariant | 도입 | 상태 (CFP-28 머지 후) |
|---|---|---|
| `check-doc-frontmatter.sh` (4 owner path × frontmatter schema) | CFP-27 (warning) → CFP-28 (strict) | ✅ 0 warning |
| `check-doc-section-schema.sh` (4 owner path × 본문 섹션 schema) | CFP-27 (warning) → CFP-28 (strict) | ✅ 0 warning (legacy 16 change-plan allowlist + 회고 §1 regex 완화) |
| `check-write-permission-redistribution.sh` (CFP-26 invariant) | CFP-26 | ✅ 자동 |
| `invariant-check.yml` 7 step (workflow parity / version match / agent count / Write queue / ADR-002 footer / migration-guide BREAKING) | CFP-5 ~ CFP-10 (review-specific 2 step은 CFP-29에서 codeforge-review로 이관) | ✅ 자동 |
| `phase-gate-mergeable.yml` | CFP-2 | ✅ 자동 |

### 1.3 영구 산출물

- 새 plugin: [`mclayer/plugin-codeforge-review`](https://github.com/mclayer/plugin-codeforge-review) v0.1.0 (5 review agent + base + 3 checklist)
- 새 인터페이스: `review_verdict v1` Inter-plugin Contract ([`docs/inter-plugin-contracts/review-verdict-v1.md`](../inter-plugin-contracts/review-verdict-v1.md))
- 새 ADR: [ADR-008 — Inter-plugin Contract Versioning](../adr/ADR-008-inter-plugin-contract-versioning.md)
- 새 templates: [`templates/retro.md`](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/templates/retro.md), [`templates/domain-knowledge.md`](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/templates/domain-knowledge.md)
- 새 owner direct-write paths: ArchitectAgent → `docs/{change-plans,adr}/**`, DomainAgent → `docs/domain-knowledge/**`, PMOAgent → `docs/retros/**`
- 새 lint enforce mode: strict (warning 발견 시 PR 차단)

### 1.4 미머지 / 휘발 없음

모든 PR merged. 핸드오프 spec(`mclayer/plugin-codeforge-review:docs/superpowers/specs/2026-04-28-own-lint-workflow-design.md`)은 그쪽 repo의 future Claude 세션이 picking 대상으로 의도적 미실행 (codeforge-review 자체 cadence).

---

## §2 무엇이 잘 갔나 (kept)

- **CFP-25 4-round Codex 협업 → Path A 채택**의 신호품질 강함. Path B(eliminate)·Path C(skill downgrade)는 Codex가 "DocsAgent는 실제 failure mode(queue/manifest discipline + phase prefix 표준)를 위해 도입됐다" evidence로 일축. 4 라운드를 통해 옵션을 살아남게 함.
- **Staged ε path를 4 sprint(0a/0b/0c/1)로 분해**한 결정이 BREAKING 폭발 회피. CFP-26 BREAKING + CFP-29 BREAKING이 같은 PR이었다면 single-PR migration 부담 + risk 합산. Phase 분리로 각 PR의 migration impact를 isolated하게 검증·기록.
- **Phase 1(CFP-29) 직후 Phase 0c(CFP-28)** 실행이 자연스러웠음. CFP-29 BREAKING 후 strict lint 전환은 새 plugin boundary를 추가 invariant로 보호 (review_verdict v1 contract 안정화 효과).
- **CFP-24 marketplace cross-repo sync 의무**를 CFP-23 직후 정식 잠금. CFP-29/CFP-28 merge 직후 즉시 sync PR open + merge → 3건 모두 author 기억 기반 1-shot 성공. 자동화 부재에도 운영 무사고.
- **`check-doc-frontmatter.sh` + `check-doc-section-schema.sh`의 warning → strict 단계적 전환**이 매우 부드러웠음. CFP-27 도입 시점에 explicit "CFP-28 strict 전환" 약속 → 약속 이행 시점에 baseline 재확인(0 warning) → strict 모드로 single edit 전환. 동일 패턴 향후 다른 lint 도입에도 재사용 가능.
- **codeforge-review 핸드오프 spec 작성 + commit + push**으로 그쪽 repo의 future Claude가 자율 착수 가능한 형태로 마무리. 두 repo 간 책임 경계가 명확.

---

## §3 무엇이 막혔나 (problem)

- **CFP-26 Phase 0a 후 stale 잔재** 3건이 CFP-29까지 누적되어 발견됐음 (PMOAgent.md §4 ADR drain 주체 / ArchitectPLAgent.md Phase 2 Synthesis "DocsAgent 경유" / CLAUDE.md ## 레인 7개 §"설계" 줄). 본 retro PR에 bundle하여 정리. **근본 원인**: CFP-26 PR 작성 시점에 변경 영향을 모든 `DocsAgent.*docs/{change-plans,adr,domain-knowledge,retros}` 패턴으로 grep해 일괄 정리하지 않음. **재발 방지**: §4 try의 grep checklist 항목 참조.
- **`phase-gate-mergeable.yml` 첫 실행 fail (라벨 부재)** 패턴이 CFP-26/29/28 모든 PR에서 반복. plugin-meta-na 1-PR 패턴은 라벨 자동 부착 메커니즘이 없어 매번 수동 `gh pr edit --add-label "phase:설계-리뷰" --add-label "gate:design-review-pass"` 필요. **개선 후보**: §4 try 참조.
- **Local Windows 환경에서 lint 스크립트의 cp949 UnicodeEncodeError**가 첫 실행 시 발생. PYTHONIOENCODING=utf-8 PYTHONUTF8=1 강제로 해결. CI Linux는 영향 없음. **재발 방지**: 스크립트 자체에 `# -*- coding: utf-8 -*-` 또는 print 단계 wrapping 검토 (낮은 우선).
- **CFP-29 Phase 1 PR #68에서 `agents/CodexReviewAgent.md` FileNotFoundError로 invariant-check fail**. review-specific 2 step이 codeforge-review로 이동된 file을 참조했음. fix commit 하나로 즉시 해결. **재발 방지**: 향후 plugin 추출 시 추출 대상 file을 참조하는 invariant-check step도 함께 옮기거나 제거하는 체크리스트 의무화.
- **CFP-26 PR #66 ADR-002 footer pattern (CFP-8 invariant) 위반** 1건. final polish 시점에 footer 본문에 2번째 줄을 추가하여 violation. fix commit 하나로 1줄 footer + schema 참조 inline 통합으로 복원. **근본 원인**: CFP-8 invariant 인지 부족. **재발 방지**: 본 invariant는 자동 검증되므로 추가 룰 불요 — fail-fast가 작동.

---

## §4 다음에 할 일 (try)

- **CFP-26-style write 권한 재분배 같은 cross-cutting refactor 시 grep checklist 의무화**: refactor PR 작성 시 변경 영향을 받는 SSOT path/owner 표현을 모든 agent md + CLAUDE.md + orchestrator-playbook + 모든 templates에 대해 explicit grep으로 audit. CFP-26 시점에 했더라면 본 retro의 §3 잔재 3건이 즉시 정리됐을 것.
- **plugin-meta-na 라벨 자동 부착 메커니즘**: PR title 또는 body에 `plugin-meta-na` 토큰 인식 시 phase-gate-mergeable workflow가 자동으로 `phase:설계-리뷰` + `gate:design-review-pass`를 부착하는 sub-workflow 추가. 또는 PR open hook에서 PR body의 `## Story` 섹션이 plugin-meta-na 패턴이면 자동 라벨링. 별도 CFP로 발의 가능 (예: CFP-31 plugin-meta-na auto-labeling — 1 day 작업).
- **Strict lint 전환 패턴을 ADR로 정식화**: §6 ADR-009 후보 발의 (warning → strict staged transition pattern, 다른 lint 도입 시에도 동일 패턴 재사용).
- **codeforge-review own invariant-check 후속 모니터링**: 핸드오프 spec이 그쪽 main에 있음. 그쪽 Claude 세션이 picking할 때까지 기다리고, 머지되면 codeforge core에서 review category enum / severity overrides drift 위험이 그쪽으로 정식 이전됐는지 sanity check.
- **Cross-repo 동기화의 fail-fast 자동화 후속**: CFP-24 의무가 author 기억에 의존. cross-repo parity GitHub Action을 별도 CFP로 발의 (예: CFP-32 marketplace sync invariant-check). 각 plugin repo의 PR이 mirrored field 변경 시 marketplace repo의 일치 여부를 PR check로 강제.

---

## §5 cross-Story 패턴

본 5 CFP arc에서 반복 관측된 패턴:

1. **"warning → strict 단계적 전환" 메타-패턴**: CFP-27이 lint 도입을 warning 모드로 시작 → CFP-28이 strict 전환. 각 단계에서 baseline 검증 → 다음 단계 진입. 향후 invariant 추가 시(예: Story file schema, contract validation) 동일 패턴 재사용 가치 큼. **§6 ADR-009 후보**.
2. **"plugin-meta-na 1-PR 패턴" (ADR-005)의 5회 누적 활용**: CFP-23/24/26/27/28 모두 plugin-meta-na 1-PR. §8 Test Contract / §9 리뷰 lane / §11 데이터 마이그레이션을 N/A로 명시 + GitHub 라벨은 `phase:설계-리뷰` + `gate:design-review-pass` 합성 부착. 이 메타-패턴이 self-CFP work에서 사실상 default가 됐음. ADR-005 §3 결정 재확인 — 옳았음.
3. **"4-round Codex 협업 → 옵션 일축 → spec 단일화" 메타-패턴 (CFP-25)**: 사람이 5 옵션 중 무엇이 best인지 알기 어려운 상황에서, 외부 모델(Codex)과의 정형 라운드 진행으로 옵션 공간 가지치기. 향후 CFP 설계 시점에 이 패턴을 의식적으로 도입할 가치. ADR 정식화는 시기상조(아직 데이터 부족) — 추가 1-2 사례 누적 시 검토.

---

## §6 ADR 후보 발의

### ADR-009 후보: Lint warning → strict staged transition pattern

**status**: Proposed
**category**: Team & Process
**근거**: §5 패턴 1 + §3 problem (cf. legacy change-plan allowlist 결정의 신중함이 strict 진입을 가능하게 함). 사례 2건 누적 (CFP-7 invariant-check Step 4 → Step 6/7/8 추가도 staged였으나 explicit 패턴화 안 됨).

**제안 결정 요지**:
- 신규 invariant·schema lint 도입 시 default = warning 모드(`exit 0` + 명시 console message)로 시작
- 1 sprint 또는 minor version 사이에 baseline drift 정리(legacy backfill 또는 allowlist 결정)
- 그 후 별도 CFP로 strict 모드(`exit 1`) 전환
- 전환 시점에 `lint.yml` 또는 `invariant-check.yml` job 이름에 `(CFP-NN — strict)` 표시 + CHANGELOG entry
- consumer 영향 평가(BREAKING vs Non-BREAKING)는 lint 강제 시점이 아니라 lint 동작 결과에 따름. 일반적으로 Non-BREAKING (스키마 위반 시 PR 차단만, runtime 영향 무)

**예상 결과**: 향후 Story file schema lint(CFP-27.5), contract validation lint(CFP-30+) 도입 시 동일 패턴 재사용 → 도입 cost 하락 + 충돌 위험 하락.

ADR draft를 ArchitectAgent에 의뢰하기 위해 write queue에 제출해야 하나, 본 retro에서는 발의(propose)까지만. ArchitectAgent direct write trigger는 다음 CFP(CFP-31 또는 CFP-32) 시점에 자연스럽게.

---

## §7 토큰 예산 vs 실제

본 sprint는 단일 사용자 + 단일 Claude 세션으로 진행됐고, agent spawn 분포는 다음과 같음 (대략치 — playbook §8.3 정량은 실제 progress trace 부재로 사후 추정):

| 레인 / 작업 | 추정 토큰 | 비고 |
|---|---|---|
| CFP-25 4-round Codex 협업 | ~100k | 4 라운드 × Codex 응답 통합 |
| CFP-26 Phase 0a 구현 + review fix loop | ~80k | 8 follow-up commits |
| CFP-27 Phase 0b 구현 + final polish | ~50k | footer pattern fix 1회 |
| CFP-29 Phase 1 추출 + cross-repo coordination | ~120k | 3 repo (codeforge / codeforge-review / marketplace) |
| CFP-28 Phase 0c 구현 + sync | ~40k | 단일 PR + sync |
| 본 retro 작성 + cleanups | ~30k | (현재 진행) |
| **누적** | ~420k | 단일 세션 burst, 컨텍스트 압축 1회 발생 (CFP-29 → CFP-28 사이) |

**해석**: BREAKING + 다중 repo + 4 PR이 단일 세션 420k에 들어간 것은 효율 지표 우수. 컨텍스트 압축이 한 번 발생했으나 작업 손실 없음 (요약본 충실). 향후 5 CFP arc 같은 burst는 사전에 압축 시점을 의식하고 chunk 분할 가능.

---

## §8 개선 제안 (3건)

1. **plugin-meta-na 라벨 자동 부착 sub-workflow** — phase-gate-mergeable의 첫 실행 fail 패턴 제거. 별도 CFP 발의(추정 1 day).
2. **Cross-repo mirrored field parity invariant check** — CFP-24 의무를 author 기억에서 CI 강제로 격상. 별도 CFP 발의(추정 1-2 days, marketplace repo 측 GitHub Action).
3. **ADR-009 (warning → strict staged transition pattern) 정식 발의** — 본 retro §6 후보를 ArchitectAgent에 의뢰. 다음 자연스러운 CFP 시점에 ArchitectAgent direct write로 status=Proposed → Accepted 전환.

(4건 이상 작성 금지 룰 준수)
