# CFP-24 plan — Marketplace cross-repo 동기화 의무 정식 잠금

[spec](../specs/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule-design.md) 참조. plugin-meta-na 패턴 (ADR-005).

## 작업 단계

### 1. CLAUDE.md SSOT 갱신
- [x] `## Plugin` 섹션 하위 `### Marketplace cross-repo 동기화 의무` 신규 subsection
- [x] subsection 본문: (a) mirrored 필드 4종 정의 (b) 의무 절차 4단계 (c) 면제 조건 (d) 자동화 후속 후보 + 근거(사용자 명시 인용)

### 2. plugin.json version bump
- [x] `version`: 0.14.2 → 0.14.3

### 3. CHANGELOG.md 최상단 entry
- [x] `## [0.14.3] - 2026-04-28` + `### CFP-24 — Marketplace cross-repo 동기화 의무 정식 잠금`
- [x] **Non-BREAKING** 명시
- [x] Added/Why/Migration 3 섹션

### 4. Story doc
- [x] `docs/stories/CFP-24.md` — §1 verbatim 사용자 메시지 + plugin-meta-na §8/§9 N/A + §11에 marketplace sync 의무 명시

### 5. spec/plan
- [x] `docs/superpowers/specs/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule-design.md`
- [x] `docs/superpowers/plans/2026-04-28-cfp-24-marketplace-cross-repo-sync-rule.md` (본 파일)

### 6. 자가 검증 (playbook §3B.5 pre-push)
- [ ] `python3 -m json.tool .claude-plugin/plugin.json` 통과
- [ ] Step 5: plugin.json `0.14.3` ↔ CHANGELOG `[0.14.3]` 일치
- [ ] Step 3: agent count 24 ↔ 24 (본 PR 미변경 sanity)
- [ ] Step 7: Non-BREAKING 확인
- [ ] markdown internal links: CLAUDE.md 신규 외부 https://link만 → 통과 예상

### 7. Codeforge commit + push + PR
- [ ] feature branch (이미 생성)
- [ ] commit message: `feat(cfp-24): marketplace cross-repo 동기화 의무 정식 잠금 — CLAUDE.md + v0.14.3`
- [ ] PR open (plugin-meta-na 패턴 명시)
- [ ] CI green (phase-gate-mergeable expected fail) → admin override merge
- [ ] local main sync

### 8. 본 규칙의 첫 self-실증 — Marketplace sync PR
- [ ] cd `mclayer/marketplace` workspace
- [ ] branch `chore/sync-codeforge-0.14.3`
- [ ] marketplace.json `plugins[name=codeforge].version`: 0.14.2 → 0.14.3
- [ ] gh API cross-check: codeforge plugin.json (main) `0.14.3` ↔ marketplace.json `0.14.3`
- [ ] commit + push + PR
- [ ] merge (no CI on marketplace repo, CLEAN)

### 9. 후속 (본 Story 비포함)
- [ ] cross-repo version parity CI 자동화 CFP (잠정 CFP-25)
- [ ] plugin manifest schema 확장 시 mirrored 필드 정의 갱신 절차

## 검증 기준

- CLAUDE.md `### Marketplace cross-repo 동기화 의무` subsection 존재 및 mirrored 필드 4종 명시
- 양쪽 main의 codeforge plugin.json `version` ↔ marketplace.json `plugins[codeforge].version` 모두 `0.14.3`
- invariant-check 1-8 PASS

## 추정 비용

- 토큰: ~6k (CLAUDE.md 편집 + 두 PR)
- 인적: 사용자 직접 작업 없음 (autonomous CFP series flow)
