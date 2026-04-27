# CFP-4: Self-application 메타 정합 — story-init.yml drift sync + CLAUDE.md self-app stage 정정 + plugin.json v0.9·20 정합

## §1. 사용자 요구사항 (verbatim)

CFP-3 PR #27 작업 직후 사용자 요청:

> "지금 이 Agents와 전체 구성에 대해 codex와 너의 리뷰를 받아보자"

종합 리뷰 결과 (Claude+Codex 양측) 발견 P1 4건 중 정합 chore 3건(P1 #1+#3+#4)이 본 Story scope. P1 #2 (`validate_config.py` `story_cutoff` 검증)는 invariant 자동화 본질이라 CFP-5로 분리. 사용자가 옵션 A 선택 ("a") — "즉시 PR #27 머지 → CFP-4 (P1 묶음) → CFP-5".

## §2. 도메인 해석

본 변경은 **plugin meta SSOT drift 정합 chore**. CFP-1/2/3 self-application 흐름의 즉시 후속:

- 도메인 제약: 3개 정합 영역(workflow drift / narrative stage drift / distribution metadata drift)이 모두 **"코드는 바뀌었는데 narrative SSOT는 stale"** 동일 패턴
- 암묵 가정: dogfooding 자체가 stale state 노출 메커니즘 — CFP-1이 정책 도입, CFP-2가 인프라, CFP-3이 migration guide gap, 본 CFP-4가 meta drift 정합. 점진적 SSOT 강화
- 범위 경계: 정합 chore 3건만. invariant 자동화(CFP-5) / README narrative(별개 chore) / phase-gate-mergeable PR-label fallback(별개 정책 결정) 모두 scope 외
- 우선순위: `plugin.json`은 marketplace user-facing 메타라 즉시 정합 가치 큼

지식 공백: 없음.

## §3. 관련 ADR

- **[ADR-001-review-agent-unification](../adr/ADR-001-review-agent-unification.md)** (active): `.claude-plugin/plugin.json` description에 인용 추가 (v0.9 lane-agnostic 통합 명시)
- 신규 ADR 필요 없음

## §4. 관련 코드 경로 + 책임

| 경로 | 변경 유형 | 현재 책임 | 변경 후 책임 |
|------|-----------|-----------|--------------|
| `.github/workflows/story-init.yml` | 수정 | 구 range parser + `main` hardcoded (drift) | template과 byte-identical: sentinel parser + 동적 `default_branch` |
| `CLAUDE.md` | 수정 | "Plugin 자체 적용" stage-1/2 향후로 stale | stage-1/2 완료 + stage-3·실증 향후 + Branch protection 가이드 명시 |
| `.claude-plugin/plugin.json` | 수정 | `version: 0.7.1` + "24 core 에이전트" stale | `version: 0.9.0` + "20 core 에이전트" + ADR-001 lane-agnostic 통합 + dogfooding 명시 |
| `docs/stories/CFP-4.md` | 신규 | (없음) | 본 Story file |
| `docs/change-plans/cfp-4-self-app-meta-sync.md` | 신규 | (없음) | 본 Story의 Change Plan |

## §5. 요구사항 확장 해석

### 유스케이스

1. **Plugin maintainer가 self Story Issue Form 제출**: `.github/workflows/story-init.yml`이 sentinel parser로 Optional 필드(Epic Milestone / Component) 비어있어도 EOF 흘러가지 않음. 동적 `default_branch` read로 main 외 default branch 환경에서도 동작
2. **Consumer가 plugin marketplace에서 codeforge 설치/업그레이드 결정**: `plugin.json`이 v0.9 + 20 agents + ADR-001 lane-agnostic 통합 + dogfooding 명시 → 호환성·기능 판단 정확
3. **신규 plugin 이해자가 CLAUDE.md "Plugin 자체 적용" 섹션 read**: stage-1/2 완료 + stage-3 향후 명시 → 현재 self-application 수준 정확 인지

### Acceptance Criteria

- `diff -q .github/workflows/story-init.yml templates/github-workflows/story-init.yml` 결과 0 (byte-identical)
- `plugin.json.version == "0.9.0"` AND description에 "20 core 에이전트", "ADR-001", "Plugin self-application dogfooding" 포함
- `CLAUDE.md` "Plugin 자체 적용" 섹션이 stage-1/2 완료 명시 + Branch protection 1인 maintainer 가이드 1줄 영속화
- 다른 5 workflow의 byte-identical 상태 보존 (`fix-ledger-sync`, `phase-gate-mergeable`, `phase-label-invariant`, `story-section-1-immutable`, `subissue-from-impl-manifest`)

### 엣지 케이스

- **`.github/workflows/story-init.yml` 동기화 후 `default_branch != "main"` 시나리오**: `yq '.github.default_branch' .claude/_overlay/project.yaml`이 main 반환 (현재 plugin overlay), 그러나 다른 default branch 명을 쓰는 사용자 환경에선 동적 read 동작 — 본 변경의 핵심 가치
- **`plugin.json.version` ↔ `CHANGELOG.md` 최상단 동기화**: CHANGELOG.md `[0.9.0]` 최상단, plugin.json `0.9.0` — 일치 ✓
- **CLAUDE.md narrative drift 재발 방지**: stage-3 (CFP-5)가 invariant 자동화로 이를 자동 점검할 예정. 본 PR은 정합만, 자동화는 별개

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] CFP-4 작업 진행 결정 ("a" — 옵션 A)
- [✓] P1 #2 (`validate_config.py` `story_cutoff`)는 CFP-5에 분리 — 본 PR scope 외
- [✓] README · plugin-design.md stale narrative (Codex P2)는 별개 chore — 본 PR scope 외

## §6. 외부 지식 배경

본 변경은 plugin 내부 정합. 외부 지식 의존 없음.

> "외부 지식 보강 불필요" 판정 사유: drift 정합 chore + 인용 메타 갱신. ADR-001은 plugin 내부 결정.

ADR 정합성: ADR-001 active, plugin.json description에 인용 신설 — 정합.

## §7. 설계 서사

Change Plan: [`docs/change-plans/cfp-4-self-app-meta-sync.md`](../change-plans/cfp-4-self-app-meta-sync.md)

### 핵심 설계 (Change Plan §1·§3·§4·§9 미러링)

**§1 목적**: Claude+Codex 종합 리뷰에서 식별된 SSOT drift 3건 일괄 정합. P1 #1+#3+#4 묶음.

**§3 도입할 설계**:
- A: `.github/workflows/story-init.yml` ↔ template byte-identical sync
- B: `CLAUDE.md` "Plugin 자체 적용" 섹션 stage-1/2 완료 + stage-3·실증 향후 명시 + Branch protection 1줄 영속화
- C: `.claude-plugin/plugin.json` `version: 0.9.0` + description의 agent 수·ADR-001·dogfooding 명시

**§4 API 계약**: schema 변경 없음. metadata 갱신 + workflow 동작 동일성(template SSOT).

**§9 분기 선택**: 단일 PR + 4 commits 분할 (story-init / CLAUDE.md / plugin.json / Story+Change Plan).

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "stage-1/2 narrative는 CFP-1 시점 정확. plugin.json 0.7.1도 그 시점 정확. 변경 시 historical accuracy 훼손."
- **Refactor(혁신)**: "활성 narrative SSOT가 stale인 게 historical 회고성보다 비용 큼. 특히 plugin.json은 user-facing 메타라 marketplace 표시 즉시 영향."
- **채택: Refactor**. Mapper 우려는 §3.5 정정 narrative에 "CFP-2 머지로 stage-2 완료" 이력 명시 + plugin.json description에 "v0.9 lane-agnostic review 통합" 명시로 흡수.

## §8. 개발 서사

### §8.1-8.4 Backend / Frontend / DataEng / InfraEng 산출물

**N/A — Plugin meta 변경, 코드 산출물 없음**.

### §8.5 Impl Manifest (파일 단위 매핑표)

| 파일 경로 | 변경 유형 | 담당 에이전트 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|---------------|-------------------|---------------|
| `.github/workflows/story-init.yml` | 수정 (template overwrite) | DocsAgent | +14 / -3 (sentinel parser + 동적 BASE) | Change Plan §3.2 A |
| `CLAUDE.md` | 수정 (Plugin 자체 적용 섹션) | DocsAgent | +5 / -2 | Change Plan §3.2 B |
| `.claude-plugin/plugin.json` | 수정 (version + description) | DocsAgent | +1 / -1 | Change Plan §3.2 C |
| `docs/stories/CFP-4.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-4-self-app-meta-sync.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## §9. 품질 게이트 이력

### §9.0 Clarification 재스폰 이력

해당 없음.

### §9.1 설계 리뷰

**N/A** — 종합 리뷰(Claude+Codex)가 본 변경의 발견 source. PR review에서 정합성 추가 확인.

### §9.2 구현 리뷰

**N/A** — 메타 정합 chore.

### §9.3 구현 테스트

**N/A** — workflow yaml syntax는 GitHub Actions가 push 시 자동 lint.

### §9.4 보안 테스트

**N/A** — 의존성·attack surface 변경 없음.

## §10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## §11. 참조

- **GitHub Issue URL**: 부재 (CFP-3와 동일하게 Issue Forms 미사용 — `.github/workflows/story-init.yml` 동기화 자체가 본 PR의 일부라 chicken-and-egg 살짝 잔존하지만, 다음 Story부터 sentinel parser 적용된 workflow로 정상 진행 가능)
- **PR URL**: 본 PR (작성 후 갱신)
- **Base PR (stack)**: 없음. main 기반 standalone (PR #27와 무관)
- **Change Plan**: [`docs/change-plans/cfp-4-self-app-meta-sync.md`](../change-plans/cfp-4-self-app-meta-sync.md)
- **CFP-1 Story**: [`docs/stories/CFP-1.md`](CFP-1.md) — Self-application 정책
- **CFP-2 Story**: [`docs/stories/CFP-2.md`](CFP-2.md) — 인프라 2단계
- **CFP-3**: deferred (audit Round 2 흡수, PR #27 close — story file 영속화 면제)
- **관련 ADR**: [`docs/adr/ADR-001-review-agent-unification.md`](../adr/ADR-001-review-agent-unification.md)

### 회고

**발견 1 — Self-application의 점진적 SSOT 강화 패턴**: CFP-1 정책 → CFP-2 인프라 → CFP-3 migration guide gap → CFP-4 meta drift. 매 Story마다 한 layer의 stale state가 노출. dogfooding이 SSOT 정합화의 자연스러운 ratchet으로 작동.

**발견 2 — Codex의 "drift 자동화 차단" 전략 통찰**: 종합 리뷰의 Codex executive summary verbatim — "다음 단계 우선순위는 새 기능 추가가 아니라 'SSOT를 SSOT답게 유지하는 자동 invariant'". Claude도 독립적으로 동일 결론 도달. 양측 합의가 CFP-5 (invariant 자동화) 우선순위를 강하게 정당화.

**발견 3 — `plugin.json` user-facing 메타의 visibility**: marketplace에서 plugin 설치 결정 시 가장 먼저 보이는 메타. v0.7.1 → v0.9.0 정합 + description의 ADR-001/dogfooding 명시는 consumer 신뢰 직접 영향. 이전엔 dogfooding 흐름에서 누락되어 있었는데 종합 리뷰가 노출.

**향후 작업 (별도 Story)**:
- **CFP-5 (다음)**: Invariant 자동화 — `templates/**` ↔ `.github/**` parity diff CI / frontmatter ↔ CLAUDE.md 표 정합 / `plugin.json.version` ↔ CHANGELOG 최상단 일치 / `validate_config.py` `story_cutoff` 검증 + unknown key reject. 본 CFP-4가 적용한 정합을 미래에도 자동으로 유지
- **CFP-6 (잠정)**: README · plugin-design.md stale narrative 정리 (Codex P2)
- **CFP-7 (잠정)**: phase-gate-mergeable.yml PR-label fallback SSOT 이중화 정책 결정
- **CFP-8 (잠정)**: End-to-end 실증 — 임의 plugin meta 변경을 GitHub Issue Form으로 시작해 workflow 자동 동작 첫 검증
- **ADR-002 (조건부)**: Process Decision의 ADR 격상 정량 trigger 결정
