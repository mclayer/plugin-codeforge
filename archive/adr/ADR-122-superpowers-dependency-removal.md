---
adr_number: 122
title: superpowers 의존 완전 제거 — codeforge wrapper dogfood self-sufficiency
status: Accepted
category: Team & Process
date: 2026-06-15
carrier_story: CFP-2249
supersedes: [ADR-028]
amends: [ADR-034, ADR-064]
is_transitional: false
related_stories:
  - CFP-2249
related_adrs:
  - ADR-028 (superseded — superpowers integration policy)
  - ADR-017 (존속 — skill override path enforcement, skill-agnostic literal 경로)
  - ADR-064 (amend — §결정10 일반 external-skill 원칙 존속, superpowers 어구 cleanup)
  - ADR-034 (amend — Stage 0 brainstorming fallback 문구 제거)
  - ADR-013 (무손상 — dogfood-out policy, 경로 강제 정책 원천)
  - ADR-058 (sunset_justification 의무 — 약화 차단)
  - ADR-060 (evidence-enforceable promotion framework — registry entry 12·13 retired + 신규 entry)
related_files:
  - skills/codeforge-brainstorm/SKILL.md
  - skills/codeforge-writing-plans/SKILL.md
  - overlay/hooks/check_bootstrap.py
  - docs/superpowers-integration.md
  - templates/skill-prompt-helpers/
  - scripts/check-no-superpowers.sh
  - docs/architecture/codeforge-family.md
---

# ADR-122: superpowers 의존 완전 제거 (dogfood self-sufficiency)

## 상태

Accepted (2026-06-15) — CFP-2249 Epic carrier. 설계 리뷰 PASS (FIX 2회 — ground-truth 정확도 보정, 골격 무변경). ADR-028 supersede + ADR-034 / ADR-064 amend.

## 컨텍스트

codeforge wrapper(dogfood) 는 `superpowers@claude-plugins-official` 을 다수 지점에서 라이브 호출한다. 참조 surface 는 2축으로 측정된다:

- **24 = 논리 매핑 수** — `docs/superpowers-integration.md §2` 표의 (agent × skill × trigger) 호출 지점 수 (line 36 SSOT). 설계 카운트.
- **89 = 물리 텍스트 surface** — `superpowers:[a-z][a-z0-9-]+` 라이브 매치 (archive·CHANGELOG 제외, 29 파일). 회귀 gate 가 0 으로 만드는 대상. 그 중 `docs/superpowers-integration.md` 자체가 31건.

ADR-028 이 통합 정책을 SSOT 화했으나 dogfood 자립성 관점에서 외부 plugin 강결합은 3 결함을 노출한다:

1. **외부 plugin 버전 drift 위험** — superpowers 자체 schema 변경 시 codeforge 호출 지점이 silent break.
2. **brainstorm SKILL.md hard-dependency** — `skills/codeforge-brainstorm/SKILL.md` 의 Phase 1 대화 본체(line 126) + 종료 plan 작성(line 203) 이 `superpowers:brainstorming` / `superpowers:writing-plans` 를 실행엔진으로 hard-call. "fallback 문구 제거" 수준 처리 시 broken skill (빈 껍데기) 발생.
3. **정체성 긴장** — 외부 의존이 "0 core 에이전트 wrapper-only" 정체성과 충돌.

본 ADR 은 superpowers 의존을 완전 제거하고 discipline 을 codeforge native 로 흡수한다. 코드 아키텍처 변경 0 — skill/거버넌스 설계 Epic.

## 결정

### 결정 1 — superpowers 호출 완전 제거

모든 lane agent md(20 file) + wrapper Stage 0 + brainstorm SKILL.md + 4 fragment + playbook 의 `superpowers:<skill>` 라이브 호출 제거. 대체 = codeforge native skill/절차. 측정 기준 = `superpowers:[a-z][a-z0-9-]+` 물리 매치 89건 → 0 (EXEMPT 영역 제외).

### 결정 2 — brainstorming 자체 재구현 (단일 skill 내재화)

`codeforge-brainstorm` SKILL.md Phase 1(why-first 대화) + 종료(plan 작성) 를 본문 내재화. `codeforge:writing-plans` 신규 skill 추출 (0-context plan invariant 흡수처 + ArchitectAgent §3 작성 cross-agent 재사용). broken skill 차단 (컨텍스트 결함 #2 반영).

흡수 step:
- `superpowers:brainstorming` Phase 1 checklist 2~N → SKILL.md why-first 대화 규범 내재화 (checklist 1 = Phase 0 로 이미 대체, line 128-129).
- `superpowers:writing-plans` plan 작성 step(0-context 개발자 전제 / step 분해 / 검증 단계) → `codeforge:writing-plans` skill body.
- SKILL.md line 126 / 203 호출을 native 절차 호출로 치환.

거부: brainstorm dialog 를 별도 skill(`codeforge:brainstorm-dialog`)로 신설하는 안 — 단일 호출지점(brainstorm Phase 1) 이라 skill 추상화 이득 없음 + hot-path 토큰 부담. dialog 는 SKILL.md 내재화, writing-plans 만 cross-agent 재사용 근거로 skill 화.

### 결정 3 — discipline 3 invariant codeforge native 흡수

superpowers 제거로 사라지는 discipline 3건의 흡수처:

| invariant | 흡수처 | lint 가능성 |
|---|---|---|
| red-first TDD (실패 테스트 먼저) | `plugins/codeforge-develop/agents/QADeveloperAgent.md` (line 60-82 RED 확인 + git stash 진정성 = 이미 실질 SSOT) | 부분 (git stash 보고 presence-grep) |
| 0-context plan (처음 보는 개발자 실행 가능) | `skills/codeforge-writing-plans/SKILL.md` (신규, 결정 2 공유 carrier) | behavioral (DesignReview judgment) |
| iteration 가설 차별화 (매 iteration 다른 가설) | `skills/root-cause-decision/SKILL.md` + ADR-064 normative (이미 존재) | behavioral |

3건 모두 mechanical lint 100% 불가 — discipline 준수는 behavioral(review judgment), grep gate 는 호출 토큰 재유입만 차단. `tdd-discipline.md` fragment 는 접착제(superpowers↔§8)일 뿐 — 폐기 후 QADeveloperAgent.md 로 fold-up (drift 회피).

### 결정 4 — ADR-028 supersede + dead-file dangling 참조 cross-ADR 정리

ADR-028 status Accepted → **Superseded (by ADR-122)**. ADR-028 은 permanent(is_transitional: false) 이므로 물리 삭제 아닌 supersede Amendment + status 전환(이력 보존).

superpowers lint 6 파일 = 전부 repo 부재(실측 Glob 0건) → **삭제 action 0**:
- integration 계열: `check-superpowers-integration.sh` · `test-check-superpowers-integration.sh` · `superpowers-integration.yml`
- schema-drift 계열: `check-superpowers-schema-drift.sh` · `test-check-superpowers-schema-drift.sh` · `superpowers-schema-drift.yml`

dead 파일을 가리키는 dangling 경로 참조를 **3 ADR 에서 cross-ADR 정합 정리** (I-7):

| ADR | 위치 | 처리 |
|---|---|---|
| **ADR-017 (존속)** | line 87(검사 script) + 95/96/97(관련 파일 3) | dead 참조 4줄 `(CFP-113 lint — 후속 미구현/제거, dead reference)` 주석. §결정1 (literal 경로 lint) 본문 무손상. **존속 ADR 안 dead lint 참조 정리 = cross-ADR 정합 의무** |
| **ADR-028 (supersede)** | frontmatter 13-14 + 본문 90-92 | 경로 참조 dead 주석 (Superseded 전환 동반) |
| **ADR-060 (registry)** | entry 12 (line 1007 `superpowers-integration`) + entry 13 (line 1008 `superpowers-schema-drift`) + line 1246 | entry 12·13 둘 다 `~~취소선~~ (retired — dead file)` 표기 (line 1005 `marketplace-sync` retired 동형). line 1246 permissions 서술 schema-drift 부재 반영. **entry 11 `dogfood-artifact-paths` (line 1006) = 무손상** (ADR-013/017 존속, 본 결정 대상 아님) |

EXEMPT (정리 불요): `docs/superpowers-integration.md` 경로 참조 = 결정 6 sunset(파일 통째 제거)으로 자동 흡수. `archive/CHANGELOG-legacy.md` + `archive/prune-2026-06/CHECK-VERDICT.md` = 순수 이력, 양축(grep-gate EXEMPT + dangling 정리 EXEMPT) 모두 정리 불요.

### 결정 5 — ADR-017 존속 (근거 재기술)

`docs/superpowers/{specs,plans}/**` literal 경로 plugin-repo 금지 lint 는 **skill-agnostic dogfood 경로 정책** — `superpowers:<skill>` 호출과 무관한 디렉터리 경로 문자열. 근거 = ADR-013 (dogfood-out: spec/plan SSOT = internal-docs repo, plugin repo 금지). superpowers 의존 제거 후에도 이 literal 경로 규칙은 무손상 존속. 단 ADR-017 Amendment 1 의 dead lint 참조 4줄은 결정 4 로 정리.

### 결정 6 — ADR-064 §결정10 존속 vs integration SSOT §5.5 sunset 분리

ADR-064 §결정10(line 451-456) = **일반 external-skill priority 원칙** (CLAUDE.md normative > ADR > skill body > external skill). 적용 범위(line 458)가 `codeforge:*` / `claude-plugins-official:*` / 외부 plugin 까지 포함 — superpowers 는 instance 1개일 뿐. **일반형 존속**, 본문 superpowers 평문 어구만 "외부 plugin (일반)" 으로 wording 정규화 (referent 소멸 cleanup).

`docs/superpowers-integration.md` 전체 = **sunset (파일 통째 제거)**. 본 doc 은 "superpowers 사용 중 통합 정책" — referent 소멸 시 살아있는 SSOT 의미 상실. 이력은 ADR-028 supersede Amendment + 본 ADR 배경 절이 보존. SSOT §5.5(superpowers-specific application)의 행동규범은 §결정10 일반형에 이미 존재하므로 **fold-up (정보손실 0)** — 제거 전 byte-level 흡수 확인.

### 결정 7 — ADR-034 fallback 문구 제거 Amendment

ADR-034 Stage 0(pre-Issue brainstorming) 개념 존속. "조건 불충족 시 superpowers:brainstorming 으로 fallback" (SKILL.md line 16/26, ADR-034 Amendment 1 line 168 / Amendment 2 line 205/217) 문구만 제거 — codeforge:brainstorm 자립 후 fallback 대상 소멸.

### 결정 8 — architecture doc 영향 (interfaces:true 확정)

`docs/architecture/codeforge-family.md` (단일 architecture doc) 의 superpowers 서술 4지점 갱신 의무 — ADR-078 lane gate `architecture_doc_updated: true` 확정 (none_rationale 아님):
- line 130 — `Superpowers[superpowers / 17 lane skill]` mermaid node 제거
- line 144 — `Orchestrator -- "skill 호출 / parallel agent dispatch" --> Superpowers` 의존 edge 제거
- line 152 — Trust boundary 외부 입력 목록에서 `Superpowers skill body` 제거
- line 239 — `PluginCache` 다이어그램에서 `superpowers` 제거 (codex 는 잔존)

## 근거

- broken skill 차단: brainstorm SKILL.md line 126/203 = 실행엔진 hard-call (ArchitectAnalyst 발견). 내재화 필수.
- discipline 손실 0: 신규 skill/fragment 신설 = drift + hot-path 토큰 부담 (TestContractArch). 기존 SSOT(QADeveloperAgent.md / root-cause-decision) 흡수 우선.
- dead-declare 정합: ADR-028 §결정2/3 + ADR-017 Amd1 + ADR-060 entry 12·13 의 lint file 부재 → supersede/정리 시 명시 (CodebaseMapper 실측 Glob 0건).
- 회귀 방지: grep gate 가 토큰 재유입만 차단, discipline 준수는 흡수처 명문화 + review judgment.

## 거부된 대안

- **A — superpowers 유지, 문서만 정리.** 거부: dogfood 자립성 미달, broken skill 미해소, 버전 drift 위험 잔존.
- **B — 신규 skill 2종(brainstorm-dialog + writing-plans) 신설.** 부분 거부: dialog 단일 호출지점이라 drift 우려 > 추상화 이득. writing-plans 만 신설, dialog 는 SKILL.md 내재화.
- **C — ADR-028 물리 삭제.** 거부: status=Accepted permanent, 이력 보존(supersede 가 정본).
- **D — ADR-017/064 §결정10/013 동반 supersede.** 거부: 이 3개는 superpowers-agnostic — supersede 시 governance 약화(ADR-058 §결정5 위반). 존속.

## consumer 영향

- consumer 프로젝트는 여전히 superpowers 설치 가능(overlay 확장). 본 제거 = wrapper dogfood self 한정.
- consumer-guide / project-config-schema 의 "필수 4종" advertisement 에서 superpowers 강제성 제거 — consumer 는 opt-in. consumer 는 ADR-017 미적용이므로 `docs/superpowers/**` 경로 사용 가능 (brainstorming-path-override fragment 의 consumer 분기 정합).
- bootstrap WARN(check_bootstrap.py) 은 이미 non-blocking — consumer breaking 0.

## sunset_justification (ADR-058 §결정5 — 약화 차단)

본 supersede/sunset 은 **weaken 아닌 "referent 소멸 cleanup"**. 3축:

1. **referent 소멸** — superpowers 의존이 제거되어 ADR-028 / SSOT §5.5 / 4 fragment 의 referent(superpowers skill) 가 존재하지 않게 됨. governance 약화가 아니라 dead-referent 제거.
2. **discipline 흡수처 명시** — red-first TDD(QADev) / 0-context plan(codeforge:writing-plans) / iteration 가설차별화(root-cause-decision) 로 100% native 흡수.
3. **약화 0** — 회귀 gate(check-no-superpowers.sh) + evidence-registry warning entry + recurrence threshold 3 로 재유입 차단 = 오히려 ratchet 강화 (외부 의존 → 자립).

- **who**: PMOAgent (Epic close 후 retro — discipline 흡수 검증 + grep gate 0 실측).
- **how**: post-LAND repo-wide `superpowers:[a-z][a-z0-9-]+` grep 0줄 (EXEMPT 제외) + 흡수처 3곳 normative presence 확인.

## 회귀 방지 설계

신규 `scripts/check-no-superpowers.sh` (`check-no-atlassian.sh` 구조 모델 — 본체만 참조, fixture 는 신규 author):

| 요소 | 설계 |
|---|---|
| 정규식 | `superpowers:[a-z][a-z0-9-]+` (literal `docs/superpowers/**` 경로 미매칭 — 두 축 분리) |
| grep-gate EXEMPT | `archive/adr/**` + `archive/CHANGELOG-legacy.md` + `archive/prune-2026-06/**` (역사 보존) |
| EXEMPT 아님 (경고) | `docs/orchestrator-playbook.md`(9 호출) + `docs/superpowers-integration.md`(31, sunset 대상) — 라이브 호출, allowlist 금지 |
| tier | warning-first (전환 중간 PR 자기차단 deadlock 회피, ADR-060 framework). blocking 승격 = 별 follow-up |
| 재유입 차단 | `docs/evidence-checks-registry.yaml` warning entry (`check-atlassian-allow` 형식 모델) + recurrence threshold 3 |
| self-test | `scripts/test-check-no-superpowers.sh` 신규 author (`test-check-no-atlassian.sh` 부재 — 복제 원본 없음): (a) positive `superpowers:brainstorming` → exit 1 (b) negative `docs/superpowers/specs/x.md` literal → exit 0 (c) negative archive/adr/ → exit 0 (d) positive playbook 동형 → exit 1 |

## 인프라 sunset 순서 (leaf-first teardown — dangling 방지)

```
S1: codeforge-brainstorm SKILL.md internalize (Phase 1 + 종료) ← broken skill 차단, 최선행
    + codeforge:writing-plans 신규 + QADev/root-cause discipline 흡수
S3~S8 (병렬): lane별 agent md superpowers 호출 제거
S9 (sunset, 모든 호출 제거 후):
    ① 4 fragment 제거 (orphan — agent md Read() 역참조 0)
    ② docs/superpowers-integration.md 제거 (+§5.5 fold-up → ADR-064 §결정10 일반형, 정보손실 0 확인)
    ③ ADR-034 fallback 문구 제거 Amendment
    ④ ADR-064 superpowers 어구 cleanup (§결정10 일반형 존속)
    ⑤ ADR-028 supersede Amendment + dangling 3 ADR 정리 (017/028/060) + dead-file 6 삭제 action 0
    무손상: ADR-013 + ADR-017 §결정1
```

dangling 방지 invariant: ② SSOT 제거 전 ① 4 fragment(SSOT §4 link 보유) + SKILL.md reference 선제거. post-LAND repo-wide grep 0줄.

## 해소 기준

N/A — permanent policy (referent 소멸 cleanup 영구).

## 관련 파일

- `skills/codeforge-brainstorm/SKILL.md` (Phase 1 line 126 / 종료 line 203 internalize)
- `skills/codeforge-writing-plans/SKILL.md` (신규)
- `plugins/codeforge-develop/agents/QADeveloperAgent.md` (red-first 흡수)
- `skills/root-cause-decision/SKILL.md` (iteration 가설차별화 명문화)
- `overlay/hooks/check_bootstrap.py` (REQUIRED 4→3 + STRICT 8→7 + 산술 5곳)
- `docs/superpowers-integration.md` (sunset)
- `templates/skill-prompt-helpers/` (4 fragment sunset)
- `scripts/check-no-superpowers.sh` (신규 회귀 gate) + `scripts/test-check-no-superpowers.sh` (신규 fixture)
- `docs/evidence-checks-registry.yaml` (entry 12·13 retired + 신규 warning entry)
- `docs/architecture/codeforge-family.md` (superpowers 서술 4지점 line 130/144/152/239)
- `archive/adr/ADR-028-superpowers-integration-policy.md` (superseded)
- `archive/adr/ADR-017-skill-override-path-enforcement.md` (dead 참조 4줄 line 87/95/96/97)
- `archive/adr/ADR-034-pre-issue-brainstorming-stage.md` (fallback 문구 제거)
- `archive/adr/ADR-064-decision-principle-mandate.md` (§결정10 어구 cleanup)
- `archive/adr/ADR-060-evidence-enforceable-promotion-framework.md` (entry 12·13 line 1007/1008)
