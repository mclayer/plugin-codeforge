---
adr_number: 16
title: Marketplace registration policy for codeforge plugin family (narrow scope)
status: Accepted
category: Team & Process
date: 2026-05-01
related_files:
  - mclayer/marketplace/.claude-plugin/marketplace.json
  - mclayer/marketplace/README.md
  - .claude-plugin/plugin.json (codeforge wrapper + 6 lane plugins)
related_stories:
  - CFP-49
  - CFP-55
related_adrs:
  - ADR-008 (inter-plugin contract versioning)
  - ADR-010 (canonical / sibling sync within plugin repos)
  - ADR-013 (codeforge family dogfood-out policy)
is_transitional: false
---

# ADR-016: Marketplace registration policy for codeforge plugin family (narrow scope)

## 상태

Accepted (2026-05-01) — CFP-49 carrier. ADR-010 (canonical/sibling sync within plugin repos) 의 외부 marketplace 측 짝.

**Amendment 1 (2026-05-01) — CFP-55**: `.claude-plugin/plugin.json` 의 `dependencies` 필드 사용 정책 (결정 6) + Migration trigger (결정 7) 추가. Codex 2-round (gpt-5.5 high) 검증 후 D-A 채택 — Claude Code v2.1.110+ 가 표준 dep 필드 인식하지만 schema 미문서화 + first-adopter risk + malformed install fail reverse-risk 회피 우선. CLAUDE.md "필수 의존성 SSOT" + SessionStart hook 이 권위 SSOT 유지. ADR-013 amend (skill override path lane 의무) 는 concern 분리 위해 별도 ADR-017 (CFP-56) 로 deferred.

## 컨텍스트

CFP-31~40 (ζ arc) 에서 codeforge wrapper 가 wrapper-only 로 decomposition 되고 6 lane plugin (codeforge-{requirements, design, develop, test, review, pmo}) 이 별도 repo 로 spawn. 이후 각 plugin 의 `.claude-plugin/plugin.json` 변경이 `mclayer/marketplace/marketplace.json` 에 반영 안 되는 drift 누적 (CFP-46 / CFP-47 양쪽 모두). CLAUDE.md 의 "Marketplace cross-repo 동기화 의무" SSOT 는 sync 의무만 명시 — 등록 자격 / sync trigger / forward-looking 정책 / out-of-scope 가 모두 미정의.

ADR-010 은 inter-plugin contract canonical/sibling sync 만 cover (within plugin repos 끼리). `mclayer/marketplace` 는 별도 repo (3rd party 측) 라 ADR-010 scope 외.

CFP-49 가 즉시 drift 해소 sweep 진행 — 그 PR 의 carrier ADR 로 본 ADR-016 도입. **단, scope 를 narrow 하게 한정** — registration 자격 / mirrored field SSOT / sync trigger 만. 깊은 governance (parity audit 자동화 / unregister flow / lifecycle policy / cross-repo CI) 는 명시적으로 후속 CFP scope 로 deferred.

## 결정

### 결정 1: 등록 대상

codeforge family 7 plugin 모두 marketplace 등록 — wrapper (codeforge) + 6 lane plugin (codeforge-{requirements, design, develop, test, review, pmo}). 자격 기준:

- 각 plugin 의 `.claude-plugin/plugin.json` 존재
- repo public (`mclayer/plugin-codeforge-<name>` 또는 wrapper 의 경우 `mclayer/plugin-codeforge`)
- `/plugins install <name>@mclayer` 로 install 가능

신규 plugin 추가 시 본 자격 기준 충족 검증 후 등록. 자격 미충족 plugin (private / draft / 미공개) 등록 금지.

### 결정 2: Mirrored field SSOT

각 plugin 의 `.claude-plugin/plugin.json` 이 SSOT. `marketplace.json` 은 mirror only. 4 mirrored field:

- `name`
- `version`
- `description`
- `author`

drift 발생 시 plugin.json 측 진실 — `marketplace.json` 측이 plugin.json 을 따라 update.

`source` 필드 (`source.source` + `source.repo`) 는 marketplace.json 자체 가 SSOT (mirror 대상 아님 — repo 위치는 marketplace 가 결정).

`keywords` 필드 등 비-mirrored 필드는 marketplace.json 자체에서 선택적으로 유지 가능 (plugin.json 과 sync 의무 없음).

### 결정 3: Sync trigger

mirrored field 4종 중 하나라도 변경 시 즉시 sync PR (`mclayer/marketplace` 에). codeforge family plugin PR 머지 직후 sync PR open·merge 의무 — drift 누적 차단.

비-mirrored field (예: `keywords`) 만 변경 시 sync 면제 (CFP-49 spec §1.3 + CLAUDE.md "Marketplace cross-repo 동기화 의무" 의 narrow boundary).

### 결정 4: 신규 lane plugin 발생 시 (forward-looking)

codeforge family 에 신규 lane plugin spawn 시 — 해당 lane 신설 Story (CFP) 내 marketplace 등록 의무 포함. 별도 follow-up Story 분리 안 함. 등록은 spawn Story 의 Phase 2 PR 에 포함되거나 직후 sync PR 로.

본 CFP-49 시점에는 해당 사항 없음 (모든 6 lane 등록 완료) — forward-looking 정책으로만 enshrine.

### 결정 5: 명시 out-of-scope

다음 governance 항목은 본 ADR-016 scope 외 — 후속 CFP 후보:

- **Parity audit 자동화** — CI / scheduled job 으로 marketplace.json ↔ plugin.json mirrored field drift 자동 검출 (CFP-50 후보)
- **Unregister flow** — lane plugin deprecation / archival 시 marketplace 제거 절차 (CFP-51 후보)
- **Lifecycle policy** — version range / minimum version / breaking change marketplace 알림 정책
- **Cross-repo CI** — Branch protection / required check 로 sync PR 강제

위 항목들은 발생 시 별도 CFP 발의.

### 결정 6: `dependencies` 필드 사용 정책

`.claude-plugin/plugin.json` 의 `dependencies` 필드는 현 시점에서 사용하지 않는다. codeforge wrapper의 필수 의존성 표명과 복구 책임은 `CLAUDE.md` 의 `## 세션 개시 의무` 섹션 (필수 의존성 SSOT 정책 본문) 과 SessionStart hook을 권위 SSOT로 유지한다.

per Amendment 1 summary 기준 Claude Code v2.1.110+ 가 표준 dep 필드를 인식하지만, 해당 필드의 plugin schema / marketplace contract / 실패 동작은 본 ADR 작성 시점에 문서화된 계약으로 확인하지 않았다. 따라서 wrapper plugin이 first adopter로 `dependencies` 를 선언하면, 의존성 자동 설치 이득보다 malformed manifest 또는 schema 해석 차이로 install 자체가 실패하는 reverse-risk가 더 크다.

현재 wrapper `.claude-plugin/plugin.json` 에도 `dependencies` 필드는 없다. 본 결정은 현행 manifest surface를 보존하고, 필수 의존성은 세션 시작 직후 노출·설치·인증 상태 확인 대상으로 둔다. 자동 복구 가능한 항목은 hook/세션 절차에서 즉시 복구하고, 불가능한 항목은 사용자에게 요구한다. `plugin.json` 은 marketplace mirrored field와 plugin identity 중심의 좁은 계약으로 유지한다.

### 결정 7: Migration trigger

`dependencies` 필드 사용 금지는 영구 정책이 아니라 보수적 대기 상태다. D-A 에서 D-B 로 전환하려면 Claude Code 공식 plugin schema가 `dependencies` 형식, required/optional 의미, version range 의미, 실패 동작을 문서화해야 한다. 이후 codeforge wrapper + 6 lane plugin 조합에서 install smoke test, marketplace ingestion, 재설치/idempotency test가 모두 통과해야 한다.

반대로 dependency 선언 실험 중 install fail, marketplace 등록 실패, 버전 범위 오해석, optional dependency의 hard-fail 처리, `CLAUDE.md` 필수 의존성 SSOT와 manifest drift가 관측되면 즉시 재검토한다. 이 경우 `dependencies` 선언은 rollback 후보이며, 권위 SSOT는 다시 `CLAUDE.md` + SessionStart hook으로 단일화한다.

D-B 전환 시 `dependencies` 필드의 marketplace.json mirroring 및 sync trigger 편입 여부도 결정해야 한다. 현 ADR-016 결정 2 의 mirrored field 4종 (`name`/`version`/`description`/`author`) 에 `dependencies` 를 추가할지, 또는 별도 sync 정책 제정할지는 D-B 전환 PR 내 결정 사항. CFP-55 시점에는 미결정 (D-A 유지 중이라 N/A). 이 결정도 forward trigger 충족 시 같은 Story 내 처리.

## 결과

### 긍정

- CFP-45 dogfood 정책 만족 — mirrored field 변경 = Story-mandated change 인 만큼 ADR carrier 동반
- Drift 즉시 차단 정책 enshrine — sync trigger (결정 3) 가 향후 CFP 의 marketplace 의무 명확
- Forward-looking 정책 (결정 4) 으로 신규 lane plugin spawn 시 누락 위험 차단
- Out-of-scope 명시 (결정 5) 로 governance 공백 인지 + 후속 CFP 후보 list
- (Amendment 1 / CFP-55) `dependencies` schema 미문서화 상태에서 first-adopter install fail risk를 회피하고, 필수 의존성 권위 SSOT를 `CLAUDE.md` + SessionStart hook으로 단일화
- (Amendment 1 / CFP-55) Migration trigger를 명시해 향후 공식 schema 문서화 시 D-B 전환 경로를 열어 둠

### 부정

- Parity audit 자동화 부재 — 본 ADR 후에도 sync PR open 누락 시 manual audit 만 가능. 후속 CFP 까지 risk 잔존
- Unregister flow 부재 — 미래에 lane plugin deprecate 시 별도 결정 필요
- Narrow scope 가 governance "spotty" 인상 줄 수 있음 (전체 lifecycle policy 부재)
- (Amendment 1 / CFP-55) 의존성이 `plugin.json` 에 machine-readable contract로 노출되지 않아 marketplace / installer 자동 검증 이득은 지연
- (Amendment 1 / CFP-55) 필수 의존성 확인은 계속 세션 절차와 hook 품질에 의존

### Trade-offs

- **본 ADR 의 narrow scope vs 깊은 governance ADR**: 솔로 dev + 트레이딩 dev 임박 상황에서 깊은 governance 작성 = scope creep. narrow ADR 이 즉시 closure + 후속 CFP 명시로 governance 공백 audit 가능
- **결정 4 forward-looking enshrine vs 발생 시 ADR**: 미래 lane spawn 시 누락 risk 차단을 위해 본 ADR 에 enshrine. 단, 정책 변경 (예: lane 등록 시 별도 Story 분리) 시 본 ADR supersede 필요
- **(Amendment 1 / CFP-55) manifest metadata 조기 채택 vs install 안정성**: 자동 의존성 표명 이득보다 schema 미문서화 상태의 malformed install fail reverse-risk를 더 크게 봄
- **(Amendment 1 / CFP-55) 단일 SSOT vs 중복 선언**: `CLAUDE.md` 와 `plugin.json` 중복을 피하고, 공식 schema 확인 전까지 운영 SSOT를 하나로 유지

## 거부된 대안

### 대안 A: Pure execution (no new ADR)

CFP-49 가 ADR 없이 ADR-008 / ADR-010 + CLAUDE.md 인용만으로 진행.

**거부 사유**: CFP-45 정책상 fragile — Story 가 ADR 기대하는데 부재 시 dogfood 위반 risk. "신규 ADR 결정 / 기존 ADR 변경" 강제 카테고리에 marketplace 정책이 들어가는지 모호 — 안전 측 = ADR 작성.

### 대안 B: Broader governance ADR

Registration + parity audit + unregister + lifecycle 통합 ADR.

**거부 사유**: yak-shaving — parity CI / unregister / lifecycle 가 명시 후속 CFP scope. 솔로 dev + 트레이딩 dev 임박 상황에서 깊은 governance 작성 = scope creep. 본 ADR 의 narrow scope 가 즉시 closure + governance 공백 audit 명확.

### 대안 C: Deferred ADR stub

최소 placeholder + 후속 CFP (parity CI / governance 분리) 로 deferred.

**거부 사유**: deferred = 후속 CFP 와 사실상 동일하면서 ADR overhead 추가. 가치 vs 비용 균형 안 맞음. narrow ADR 이 차라리 더 명확한 결정 enshrine.

### 대안 D-B: `plugin.json` dependencies 적극 선언

(Amendment 1 / CFP-55) wrapper `.claude-plugin/plugin.json` 에 codeforge lane plugin 및 필수 외부 plugin 의존성을 `dependencies` 로 선언한다. 장점은 의존성이 machine-readable manifest에 노출되고, 향후 installer / marketplace / runtime 자동 검증과 맞물릴 수 있다는 점이다.

**거부 사유**: per Amendment 1 summary 기준 Claude Code v2.1.110+ 가 표준 dep 필드를 인식하더라도 schema가 문서화된 계약으로 확인되지 않았다. first adopter로 선언할 경우 잘못된 field shape 또는 해석 차이로 install fail을 만들 수 있다. 현 시점의 더 안전한 정책은 `CLAUDE.md` 필수 의존성 SSOT + SessionStart hook 유지다.

### 대안 D-C: 일부 dependency만 선택 선언 + CLAUDE.md 중복

(Amendment 1 / CFP-55) 안정적으로 보이는 일부 의존성만 `plugin.json` 에 선언하고, 나머지는 `CLAUDE.md` 필수 의존성 SSOT에 남긴다. schema risk를 줄이면서 machine-readable metadata로 점진 이동하는 절충안이다.

**거부 사유**: partial declaration은 어떤 의존성이 authoritative한지 모호하게 만들고, manifest와 `CLAUDE.md` 사이 drift를 새로 만든다. optional/required 의미가 문서화되지 않은 상태에서는 "일부만 선언"이 오히려 운영자와 installer 모두에게 잘못된 신호가 될 수 있다.

## 후속 CFP 후보

본 ADR 결정 5 (out-of-scope) 에 명시된 항목들의 follow-up CFP:

- **CFP-50 (잠정)**: Cross-repo parity CI — marketplace.json ↔ plugin.json drift 자동 검증
- **CFP-51 (잠정)**: Lane plugin lifecycle / unregister flow governance ADR

본 CFP-49 머지 후 별도 issue 로 발의 (사용자 판단).

## 해소 기준

N/A — permanent policy

## 관련 파일

- 본 ADR
- [CFP-49 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-01-cfp-49-marketplace-resync-sweep.md) (internal-docs)
- [CFP-49 change-plan](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-49-marketplace-resync-sweep.md) (internal-docs)
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — inter-plugin contract versioning (mirrored field SemVer 룰의 inter-plugin 측 짝)
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — canonical / sibling sync (within plugin repos)
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — dogfood-out monorepo (spec/plan/change-plan 위치)
- `mclayer/marketplace/.claude-plugin/marketplace.json` — 정책 enforcement target
- `mclayer/marketplace/README.md` — 등재 플러그인 표 mirror
