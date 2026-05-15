---
adr_number: 12
title: Wrapper CLAUDE.md SSOT Boundary
status: Adopted
category: Team & Process
date: 2026-04-30
related_files:
  - CLAUDE.md (본 ADR 의 enforcement 대상 + 5-line summary inline)
  - docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md (parent CFP)
  - docs/adr/ADR-014-operational-risk-ssot-distribution.md (CFP-46 4번째 SSOT 예외 짝꿍)
  - docs/adr/ADR-051-ssot-skill-extraction-pattern.md (CFP-343 / CFP-506 — skill 추출 패턴, SSOT 예외 영역의 skill SSOT 인용)
  - docs/adr/ADR-060-evidence-enforceable-promotion-framework.md (CFP-506 Amendment 1 — mechanical lint forcing function carrier)
  - scripts/check-claude-md-line-cap.sh (CFP-506 Amendment 1 — line-count assertion)
  - templates/github-workflows/claude-md-line-cap.yml (CFP-506 Amendment 1 — warning-tier workflow)
related_stories:
  - CFP-44 (본 ADR 신설 시점 — wrapper CLAUDE.md 705→~330줄 압축)
  - CFP-43 (parent — X2 cleanup, 잔존 부속 사항 진단의 직전 상태)
  - ADR-009 (parent ζ arc decomposition — 6 lane plugin 추출)
  - CFP-506 (Amendment 1 — cap ≤380 → ≤320 ratchet + §3 scope 4-층 재해석)
related_adrs:
  - ADR-014  # 4번째 SSOT 예외 짝꿍 (operational risk SSOT)
  - ADR-051  # CFP-343 / CFP-506 — SSOT skill 추출 패턴
  - ADR-058  # ratchet 약화 차단 (sunset criteria mandate)
  - ADR-060  # CFP-506 Amendment 1 — mechanical lint framework carrier
  - ADR-064  # decision principle mandate (anchor 분류 source)
  - ADR-040  # Amendment 3 §결정 7.D self-application 패턴 reuse
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-506
    date: 2026-05-13
    summary: |
      cap ≤380 → ≤320 ratchet 강화 (ADR-058 §결정 5 정합, 강화 방향 — sunset_justification 면제) +
      §3 "4 SSOT 예외" 표현 재해석 — CFP-343 (ADR-051) + 본 CFP-506 결과 모두 skill SSOT 로 분리됨에 따라 wrapper CLAUDE.md scope 4-층 (identity / cross-cutting policy / anchor / skill pointer) 본문 재정의 +
      신설 §결정 5 (anchor 본문 inline 유지 / reference skill 추출 / "SSOT 예외" 표현 = "skill SSOT 로 인용" 재해석) +
      신설 §결정 6 (mechanical lint forcing function = scripts/check-claude-md-line-cap.sh + claude-md-line-cap.yml warning tier, ADR-060 4번째 entry carrier_adr cross-ref) +
      `is_transitional: false` 유지 (permanent policy, ratchet 약화 차단 정합).
mechanical_enforcement_actions:
  - name: claude-md-line-cap
    binding: 결정 6
    workflow: templates/github-workflows/claude-md-line-cap.yml
    detect_command: bash scripts/check-claude-md-line-cap.sh
    tier: warning
    bypass_label: hotfix-bypass:claude-md-line-cap
---

# ADR-012: Wrapper CLAUDE.md SSOT Boundary

## 상태

Adopted (2026-04-30) — CFP-44 PR-4 머지 시점.

## 컨텍스트

CFP-43 (X2 cleanup) 후 wrapper CLAUDE.md 가 705줄로 잔존. 사용자 진단:

> "분리를 수행했지만 부속 사항이 너무 많이 남아있는 것 같다."

증상: ζ arc decomposition (ADR-009) 으로 6 lane plugin 추출 완료됐지만, wrapper CLAUDE.md 에 lane 내부 디테일 (agent 역할 · spawn sequence · ideology · lifecycle · severity rule 등) 잔존. 의도된 SSOT 분업이 아니라 추출 시 미처 옮기지 못한 부속.

CFP-44 brainstorming 단계의 audit 결과:
- 1 MISSING (codeforge-test) + 2 PARTIAL critical (design, requirements) — backfill 의무
- 3 PARTIAL safe (review, pmo, develop) — wrapper 압축 무손실
- 3 wrapper-must-keep (cross-lane scope, single-plugin home 없음): 책임 매트릭스 + 원인 판정 decision table + FIX Ledger §10 schema

Codex (gpt-5.4) 두 번째 의견 — A1' (audit-driven minimum + explicit boundary statement) 권고: "process symmetry 만 사고 risk reduction 못 사는 거래" 회피.

## 결정

Wrapper plugin (codeforge) CLAUDE.md content scope 는 다음으로 strictly limited:

1. **Plugin identity** — 인트로, marketplace cross-repo sync 의무, 세션 개시 dependency check
2. **Cross-cutting policy** — dogfood Story 작성 의무, write boundary table (Lane plugin self-write boundary), inter-plugin contract index, ADR list
3. **4 named SSOT exceptions** (cross-lane scope, no single-plugin home):
   - Design / Code / Security 책임 매트릭스
   - 원인 판정 decision table
   - FIX Ledger §10 schema + Orchestrator monopoly + RESET 룰
   - **Cross-lane §7 운영 리스크 책임 매트릭스 행 + 원인 판정 §7.4 / §11 idempotency 행 + 6 deputy mandate 매트릭스** ([ADR-014](ADR-014-operational-risk-ssot-distribution.md) carrier — codeforge-design plugin SSOT 인 §7.4 schema 자체 와 분리되는 cross-lane disambiguation 영역)

**Excluded** (lane plugin SSOT 또는 playbook 으로 위임):
- per-lane spawn detail · agent role description
- lane-internal ideology · lifecycle · Freshness rule
- severity rule detail (codeforge-review templates SSOT)
- 병렬 스폰 권장 (spawn sequence 중복)
- GitHub workflow subsection 상세 (consumer-guide.md + label-registry-v1.md SSOT)

CLAUDE.md 본문 top (intro 직후) 에 본 ADR 의 5-line summary + ADR link inline 명시 — drift detection anchor.

## 결과

**달성**:
- CLAUDE.md 705 → 377줄 (47% 절감, 매 세션 ~7k tokens 절약). 첫 추정 330줄은 cross-cutting policy 잔류량 underestimate — bottom-up 재계산 후 ≤380 cap 내 377줄로 수렴
- "wrapper-only" 정체성 명확화 — composition + cross-cutting policy only
- 3 SSOT 예외 명시로 cross-lane 콘텐츠의 단일 출처 보장
- 미래 wrapper drift 의 anchor — boundary 위반 PR 의 review 시 ADR-012 reference

**비용**:
- 3 cross-repo backfill PR (codeforge-{test, design, requirements}) — audit gap 해소
- ADR-012 자동 강제 수단 부재 (linter 후속 CFP)
- documentation-quality asymmetry — lane plugin 별도 self-contained 깊이 차이 (review/pmo/develop 는 agent md 영역 의존)

**검증**:
- 압축 후 CLAUDE.md line count = 377 (target 330 미달, ≤ 380 cap 충족)
- §5.2 grep test (CFP-44 spec): 압축 대상 헤더 잔존 0
- ADR-012 frontmatter + section schema PASS

**2026-04-30 amendment (CFP-46)** — 4번째 SSOT 예외 추가. operational risk schema (§7.4) 가 codeforge-design plugin SSOT 라 wrapper 의 cross-lane 책임 매트릭스·decision table·deputy mandate matrix 만 wrapper 보유. 향후 §7.X / §11.X 추가 시 동일 패턴 (좁은 명명 + 짝꿍 ADR 개정) 의무 — H16 exception creep 차단.

### 결정 5: wrapper CLAUDE.md scope 4-층 재해석 (CFP-506 Amendment 1)

CFP-343 (ADR-051) 의 4 SSOT skill 분리 + 본 CFP-506 의 reference 4 블록 추가 skill 분리 결과, 위 "## 결정" 본문의 "4 SSOT 예외" 표현은 다음 4-층 분류로 재해석된다:

1. **identity** (Plugin intro / marketplace sync 의무 / 세션 개시 dependency check) — 매 turn unconditional 적용
2. **cross-cutting policy** (dogfood Story 작성 의무 / write boundary anchor / branch governance / inter-plugin contract anchor / ADR pointer 등) — 매 turn unconditional 적용
3. **anchor** (§결정 원칙 ADR-064 normative SSOT — forbid-list 8 어휘 / 4 normative anchor / sequential 3 사유 / Top-down ratchet) — 매 turn unconditional 자기검열 의무, skill 추출 거부 (ADR-051 Amendment 1 §결정 4 anchor vs reference 판정자 정합)
4. **skill pointer** (lane-conditional reference — `codeforge:review-responsibility` / `codeforge:root-cause-decision` / `codeforge:fix-ledger-schema` / `codeforge:deputy-mandate` / `codeforge:lane-self-write-boundary` / `codeforge:story-cutoff-classification` / `codeforge:inter-plugin-contract-registry` / `codeforge:story-epic-flow-preflight` — 총 8 wrapper-owned SSOT skill + `codeforge:codeforge-brainstorm` Stage 0) — lane 진입 / 이벤트 발화 시 lazy load

"SSOT 예외" 라는 표현 = "wrapper 가 본문 inline 으로 보유한 cross-lane SSOT" 의미가 아니라 "wrapper CLAUDE.md 본문 inline 으로 보유하지 않고 wrapper-owned skill 로 인용" 의미로 재해석한다.

### 결정 6: cap ≤320 + mechanical lint forcing function (CFP-506 Amendment 1)

**cap ratchet**: `wc -l CLAUDE.md` ≤ **320** (이전 ≤ 380 으로부터 강화). ADR-058 §결정 5 정합 (강화 방향 — sunset_justification 면제). 본 amendment 이후 신규 CLAUDE.md 변경 PR 부터 발효.

cap declaration 자체로는 사후 감지만 가능 — CFP-44 이후 CFP-506 시점까지 434줄로 누적 (54줄 초과 지속) 이 작성 시점 enforce 필요성 입증.

**mechanical lint forcing function**:
- `scripts/check-claude-md-line-cap.sh` — line-count assertion (exit 0 PASS / exit 1 validation FAIL / exit 2 meta-error, ADR-060 §결정 15 3-tier semantic)
- `templates/github-workflows/claude-md-line-cap.yml` — warning-tier workflow (`continue-on-error: true`, ADR-060 §결정 5)
- `.github/workflows/claude-md-line-cap.yml` — byte-identical self-app mirror (CFP-449 sentinel 1 / ADR-005 invariant-check.sh)
- bypass channel = `hotfix-bypass:claude-md-line-cap` label (label-registry-v2 v2.4 8번째 hotfix-bypass family member, ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합) + `check-bypass-audit-comment.sh` reuse (audit comment 자동 발의)

framework carrier = [ADR-060 Amendment 5](ADR-060-evidence-enforceable-promotion-framework.md) — 4번째 warning-tier entry. declaration-only ADR mechanical enforcement 확장 (ADR-040 Amendment 3 §결정 7.D self-application 패턴 reuse — 1st adr-sunset-criteria / 2nd decision-principle-vocab / 3rd auto-phase-label / 4th claude-md-line-cap).

## 거부된 대안

- **A2 symmetric refresh** (CFP-43 패턴 답습, 6 cross-repo PR) — Codex 명시 reject: "process symmetry 만 사고 risk reduction 못 사는 거래"
- **A3 wrapper-only quick-win** (1 PR, lane plugin gap deferral) — ADR 급 결정 의도 (사용자 (2') 선택) 미달성, 결과 ~500줄 (target 미달)
- **Linter-first ratchet** (boundary 정의 없이 자동 강제만 도입) — 강제할 boundary 가 정의돼 있어야 lint rule 작성 가능. 후속 CFP 에서 도입 가능

## 해소 기준

N/A — permanent policy



```
Before (CFP-43 후, 본 ADR 결정 전):
codeforge wrapper CLAUDE.md (705 lines)
├── Plugin identity
├── 세션 개시 의무
├── Development Agent Team tree (52 lines, lane internal)
├── 레인 정의
├── 스폰 시퀀스 (91 lines, lane internal)
├── FIX 루프 + 원인 판정 table
├── 책임 매트릭스
├── 4-way 이념 (lane internal)
├── ArchitectPL 라이프사이클 (lane internal)
├── Deputy Freshness (lane internal)
├── Lane plugin self-write boundary
├── 병렬 스폰 권장 (duplicates spawn sequence)
├── Inter-plugin Contract index
├── ADR list
├── GitHub Workflow (89 lines, mostly in consumer-guide)
├── Story 작성 의무 (dogfood policy)
└── Domain Knowledge (lane internal)

After (CFP-44 머지 후):
codeforge wrapper CLAUDE.md (377 lines)
├── Plugin identity (KEEP)
├── ## SSOT Boundary (NEW — ADR-012 5-line + link)
├── 세션 개시 의무 (compressed — checklist 만)
├── Lane → plugin → agent count (10-line table, replaces 52-line tree)
├── 레인 정의 (compressed)
├── Spawn sequence pointer → playbook §3
├── FIX 루프 (trigger/counter/§10 schema only)
├── 원인 판정 decision table (KEEP — SSOT 예외 #2)
├── 책임 매트릭스 (KEEP — SSOT 예외 #1)
├── PMOAgent Cross-cutting trigger (compressed)
├── Lane plugin self-write boundary (KEEP)
├── Inter-plugin Contract index (KEEP)
├── ADR list (compressed)
├── GitHub Workflow (compressed listing only)
├── Story 작성 의무 (KEEP — dogfood policy)
└── docs/stories markdown 규약 (KEEP)
```

## 관련 파일

- 본 ADR
- [CFP-44 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md)
- CLAUDE.md (본 ADR 의 enforcement 대상)
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — parent ζ arc 결정
- [ADR-010 Inter-plugin Contract Sibling Sync](ADR-010-inter-plugin-contract-sibling-sync.md) — sibling cleanup arc
- [ADR-014 Operational Risk SSOT Distribution](ADR-014-operational-risk-ssot-distribution.md) — CFP-46 4번째 SSOT 예외 짝꿍
