# codeforge 거버넌스 레드팀 결과 (RED-TEAM-FINDINGS)

> 방법: 검사망(evidence-checks-registry.yaml 147 entry)·결정기록(ADR 120)·계약(inter-plugin-contracts 33)·차단검사(branch protection)를 디스크 실측으로 공격. 4개 독립 감사 에이전트 병렬 + Orchestrator 직접 검증.
> 날짜: 2026-06-02 KST. 모든 수치는 실측(디스크 ground-truth), 추측 아님.

---

## 0. 한 줄 결론

**"강제 외형"의 상당 부분이 비어 있다.** 차단형이라 표기된 검사 10개 중 실제로 머지를 막는 건 2개, ADR 번호 체계의 backbone에 무결성 검사가 0개, 검사망 곳곳에 "검사하는 척하고 항상 통과"하는 CI job이 존재한다. 그리고 가장 깊은 문제: **시스템이 자기 거짓을 수정하기 어렵게 설계돼 있다** (정정 = "약화"로 간주돼 ratchet/provenance 의식에 묶임).

---

## 1. 배터리 1 — Phantom 검사 (선언만, 실체 없음)

| 발견 | 실측 |
|---|---|
| 총 entry | 147 |
| detect 스크립트가 디스크에 없음 | 14 (13개는 정직하게 `deferred-followup` 라벨) |
| 라이브 워크플로가 `if: false` no-op (항상 통과) | **4** (`backlog-issue-label-forbid`, `filesystem-worktree-pinned-check`, `fix-loop-reverify-check`, `retro-fact-verify-check`) |
| "경고 연극" — inline grep 후 무조건 `exit 0` (검사하는 척) | **3** (`deploy-lane-spawn-evidence`, `cross-layer-impact-check`, `dependency-order-check`) |
| 진짜 배선됨 | ~120 |

**교정**: 직전 분석(CHECK-VERDICT.md)의 "선언만 38개"는 과대계상. 대부분은 `deferred-followup`로 정직하게 표기됨(거짓 아님, 거버넌스 부채). 단 **7개(if:false 4 + echo연극 3)는 배포된 CI job이 enforcement처럼 보이면서 아무것도 안 함** = 가장 기만적 부분. CI 시간만 소모.

**좋은 소식**: 차단형(blocking-tier) entry 중 phantom 0개. 진짜 막는 게이트는 진짜다.

---

## 2. 배터리 2 — ADR 번호/상태 부기 붕괴

| 발견 | 실측 |
|---|---|
| 번호 충돌 (한 번호 = 2파일) | **4건 전부 확정** — 042·047·048·056 |
| 그중 양쪽 다 "살아있음(Accepted)" = 최악 | 042, 056 |
| 패딩 불일치 | `ADR-72`만 2자리 (나머지 119개 3자리), 예약 레지스트리에도 불일치 박힘 |
| 상태 drift (한 파일 안 상태시스템 2개 모순) | **ADR-076**(`status: Active` + `sunset_status: Sunsetted` + `superseded_by` 설정, 76개 파일이 살아있는 듯 참조), **ADR-083** 동일 |
| 죽음/삶 어휘 통제 부재 | "살아있음" = Accepted(87)/Active(9)/Adopted(5) 3종, "죽음" = Superseded/Deprecated/자유문장 혼재 |
| **번호 유일성·패딩 검사** | **0개** — 155개 검사망에서 backbone만 구멍 |

충돌·패딩이 안 잡힌 이유 = **아무도 안 본다.** 유일하게 번호를 파싱하는 스크립트는 `\d+`로 `ADR-72`/`ADR-072`를 같은 72로 읽어 패딩 drift가 애초에 안 보임.

---

## 3. 배터리 3 — "차단형 10개"의 실체

| 검사 | 진짜 막나 |
|---|---|
| `invariant-check` | ✅ 진짜 차단 (required + exit 1 + continue-on-error 없음) |
| `phase-gate-mergeable` | ✅ 진짜 차단 (dynamic check) |
| `per-plugin-cumulative-counter` | ❌ **레지스트리는 "PR 차단형"이라 적었지만 워크플로가 continue-on-error + PR 트리거 자체 없음 → 영원히 못 막음.** entry 주석이 자백("Wave 2 = 별 sub-CFP") |
| `marketplace-description-verbatim`, `version-3way-atomic`, `wrapper-managed-block`, worktree-first 4종 | ❌ 워크플로는 제대로 실패하지만 **required context에 없음 + 라벨 한 장으로 우회** → 사실상 권고 |

추가:
- `deploy-lane-presence` — required 슬롯을 차지하는데 본문이 `echo PASS` no-op = **빈 게이트**.
- `check-gate` — required인데 job이 절대 실패 안 함(실제 게이트는 sibling dynamic check). 오해 소지.

**순효과: 차단형 10개 주장 중 실제 머지 차단 = 2개.**

---

## 4. 배터리 4 — 계약 버전 drift

| 발견 | 실측 |
|---|---|
| 죽은 버전 파일 잔존 (repo 내 운영 의존 0) | **8개** — review-verdict v1·v2·v3, design-output v1, test-verdict v1, label-registry v1, decision-packet v1·v2 |
| `decision-packet` = Active 버전 자체 없음 (v1 Archived + v2 Deprecated)인데 라이브 템플릿이 v2 가리킴 | 고아 |
| MANIFEST↔본문 drift | design-output-v2 본문 예시 `2.0` (frontmatter는 2.4); review-verdict v4.9→v4.11 drift는 이미 수정됨 |
| 가드 부재 | "패밀리당 Active 1개"·죽은버전·MANIFEST 고아 탐지 검사 전무 |

삭제는 **외부 consumer(mctrader 등) 참조 가능성** 때문에 cross-repo 확인 필요 (repo 내 죽음 ≠ 외부 안전).

---

## 5. 운영 발견 (직접)

- **worktree 168개 누적** — `git worktree list` 168 (전부 디스크 존재). SessionStart stale-check가 `pruned=0` 보고 = GC 판정이 실효 없음(병합 브랜치를 stale로 못 잡음). 디스크 누적 + `git worktree` 명령 저속화.

---

## 6. 가장 깊은 메타 발견 — 시스템이 자기를 못 고친다

거짓 주장 정정(거짓 차단형 강등 / phantom 정직화 / 죽은 ADR 은퇴)은 구조적으로 **"약화(weakening)" 또는 "결정 되돌림"**이라 anti-weakening ratchet + provenance(promoted_by/promoted_date) 의식에 걸린다. 즉 **과거버넌스를 만든 바로 그 절차가 그것을 치우는 것도 막는다.** 

→ 1순위 개선점: **"정정/축소 전용 경로"** (ratchet 면제 + 가벼운 승인) 신설. 이게 없으면 de-bloat 자체가 매번 풀 의식을 치른다.

### 6-bis. 실증 — tier 강등 PR(#1930)로 ratchet 테스트한 결과 (신규 발견)

거짓 차단형 `per-plugin-cumulative-counter`를 `blocking-on-pr`→`warning`으로 강등하는 PR을 올려 anti-weakening 검사가 막는지 시험. 결과:

- **막히지 않음. 단, "허용해서"가 아니라 anti-weakening 검사들이 레지스트리 tier 필드를 *아예 안 본다*.**
- `sunset-weakening-evidence` / `adr-077-ratchet` / `adr-sunset-criteria` 전부 `paths:` 필터가 `docs/adr/ADR-*.md`에만 걸려 있음 → 레지스트리 변경은 시야 밖. 게다가 전부 warning-mode.
- `evidence-registry` 검사는 스키마만 보고 **tier 방향 가드 없음**.

**새 개선점: 검사망의 "강제 강도" SSOT인 tier 필드 자체가 무단 하향에 무방비.** 누구든 blocking→warning으로 조용히 낮춰도 어떤 검사도 안 본다. (역설: 정정엔 편하지만, 악의적 약화에도 무방비. 정정/축소 전용 경로 + tier 변경 감지 가드가 같이 필요.)

---

## 7. 개선점 — 우선순위/위험도

### A. 즉시 (무판단·무위험, 이번 PR) ✅
1. 라이브 템플릿이 Archived된 review-verdict-v3 가리킴 → v4(현행)로 (3곳). v4에 동일 필드 존재 확인됨.
2. design-output-v2 본문 예시 `contract_version: 2.0` → `2.4` (frontmatter 일치).

### B. 정직성 정정 (소유자 승인 후 — 거버넌스 의미 있음)
3. `per-plugin-cumulative-counter` tier `blocking-on-pr`→`warning` (레지스트리가 실체와 일치). 또는 반대로 진짜 차단 배선.
4. ADR-076/083 `status`를 자체 `sunset_status: Sunsetted`와 일치시킴 (단 76개 참조 영향 검토).
5. `if:false` no-op 워크플로 4개 + echo연극 3개 제거 또는 정직 표기 (deferred 작업 포기 결정).

### C. 가드 신설 (net-add — 축소 철학과 긴장)
6. ADR 번호 유일성+패딩 lint (warning). 현 충돌 4건+패딩 1건을 표면화.
7. 계약 "패밀리당 Active 1개" + MANIFEST 고아 탐지 invariant.

### D. 사람 판단 필수
8. 번호 충돌 4건 재번호 — 어느 파일이 canonical인지 결정 (042·056은 양쪽 살아있음, 참조 광범위).
9. `ADR-72`→`ADR-072` 리네임 + 이중표기 교차참조 정리.
10. 죽은 계약 버전 8개 물리 삭제 — cross-repo consumer 확인 선행.
11. worktree GC 기준 재정의 또는 일괄 prune.

### E. 구조 (가장 큰 효과)
12. §6 정정/축소 전용 경로 신설.

---

## 8. 확대 레드팀 (hooks / skills / consumer overlay)

### 8-1. hooks
- **"매 턴 배너 3회·대화규칙 2회" 전제 = main 기준 거짓** (배너는 heredoc 안, #1912가 per-turn 대화규칙 hook 실제 제거 — git 확인). 단 **이 세션은 여전히 주입** → 실행 설정이 main HEAD가 아님(stale 설치/overlay 드리프트).
- **worktree GC 결함(라이브 버그)**: `templates/scripts/check-worktree-stale.sh` — (B 주범) stale 기준이 "origin에 브랜치 없음"인데 머지 PR이 브랜치 안 지워 영원히 prune 안 함 → 171개 누적. (A) 경로 prefix 필터가 51개(30%) 못 봄. (C) `set -e`+`cd` 루프 취약. 올바른 기준 = PR merged/closed 판정.
- 모든 hook fail-open(exit 0) → 진짜 고장 침묵. `pretooluse-agent-spawn-gate` = Wave 1 warning-only(무강제).

### 8-2. skills (코퍼스 ~35K 토큰, deputy-mandate 혼자 31%)
- `deputy-mandate`: 충돌 번호 ADR-042 **bare 15회**(어느 042인지 모호) — 최우선 기계적 수정.
- `confluence-migration:181`: 죽은 ADR-022(폐기 decider)를 살아있는 retain 항목으로 인용 + ADR-083(sunsetted) 인용.
- `story-epic-flow-preflight:21`: 충돌 ADR-048 bare.
- `codeforge-brainstorm:130`: 슬림된 CLAUDE.md의 ADR-064 §결정 번호 가리킴 = dangling(슬림 부작용).
- CLAUDE.md 진입 스킬 표 불완전(4개 누락) + ADR-012/051 "스킬 8개"인데 실제 12개.
- 소유권 lore(pmo 오귀속) = 깨끗(확인).

### 8-3. consumer overlay (가장 심각)
- **[최상] validator가 문서화된 기능 5블록을 거부** — `validate_config.py` SCHEMA_RULES에 `aggregate_arch`/`deploy`/`atlassian`/`runtime`/`security` 없음 → 813줄 스키마 문서·consumer-guide 따라 deploy·Confluence·auto-resume 켜면 **exit 4 → SessionStart hook abort**. 문서는 자랐는데 validator 미확장.
- **lane 수 체계적 모순**: README/plugin-design = "6 lane / 7 레인 / 23 agent"(deploy 누락), CLAUDE.md = 8 lane. 신규 consumer가 deploy 레인 존재 여부 판단 불가.
- **"확장만 가능" 불변식 = 명예제** — validator는 unknown 키만 막고, ratchet 값 약화(`pl_autonomous_parallel_authority: disabled`)는 통과(실측 exit 0).
- `presets/` 참조하나 디렉토리 없음(죽은 `cp` 명령). `regen-agents.sh`는 wrapper-only consumer에서 즉시 exit 0 = 문서화된 단일 hook이 no-op. examples가 "조용히 무시되는" flat hook 스키마 사용 → 플러그인 자기 bootstrap 검사를 self-fail. README 버전 블록 stale(0.7.0/β).

### 8-4. 확대 개선점 우선순위
| # | 수정 | 위험 | 성격 |
|---|---|---|---|
| 13 | validator에 문서화된 5블록 추가(또는 unknown→WARN) | 중(스키마 정확성) | **consumer-깨짐 버그, 최상위** |
| 14 | lane 수 6/7→8 문서 일괄 정정 + org-chart에 deploy 추가 | 무 | 순수 doc |
| 15 | worktree GC 기준 merged-PR로 + 경로 broaden + 루프 hardening | 중 | 라이브 버그, 테스트 있음 |
| 16 | deputy-mandate ADR-042 bare 15회 → 풀네임 링크 | 무 | 순수 정정 |
| 17 | 스킬 죽은 참조(ADR-022/048) 정정 | 무 | 순수 정정 |
| 18 | extend-only ratchet 실제 강제 OR 문구를 "권장"으로 | — | 정책 판단 |
| 19 | regen-agents wiring 결정 / examples nested 스키마 통일 | — | 설계 |

### 8-5. 실증 — phase-gate가 코드 수정을 막음 (§6 forward 방향)

레드팀 5 PR을 올린 결과 phase-gate(병합 전 단계 게이트, 실제 차단검사 2개 중 하나)의 행동이 갈림:

| PR | 변경 종류 | phase-gate |
|---|---|---|
| #1929 stale 포인터 | docs | 통과 |
| #1930 tier 강등 | registry yaml | 통과 |
| #1931 가드+정책 | 새 script/workflow/doc | 통과 |
| #1933 정정 묶음 | docs+skills | 통과 |
| **#1932 validator 버그수정** | **.py 코드** | **BLOCKED** (`phase:unclassified`, `gate:design-review-pass` 부재) |

**검증된 consumer-깨짐 버그 수정(pytest 38 통과, RED→GREEN, 회귀 0)이 "코드라서" Story 바인딩 + 단계 진행 의식 없이는 머지 불가.** 문서 변경은 전부 fast-pass. 즉 **명백한 개선조차 forward 방향에서 ceremony에 막힘** — §6 메타발견의 반대 방향 실증. (부수: 새 파일 추가 #1931은 통과했는데 기존 .py 수정 #1932는 막힘 = phase-label 자동분류의 일관성 결여.)

→ 개선점 20: 검증된 소형 버그수정(테스트 동반 + diff 소형)에 대한 phase-gate fast-path (chore/hotfix 분류) — consumer-깨짐 hotfix가 design-review 전체 의식을 안 거치게.
