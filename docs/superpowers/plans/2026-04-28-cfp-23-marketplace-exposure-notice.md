# CFP-23 plan — `mclayer` marketplace 노출 사실 README/CHANGELOG 명시

[spec](../specs/2026-04-28-cfp-23-marketplace-exposure-notice-design.md) 참조. plugin-meta-na 패턴 (ADR-005).

## 작업 단계

### 1. plugin.json version bump
- [x] `.claude-plugin/plugin.json` `version`: 0.14.1 → 0.14.2

### 2. CHANGELOG.md 최상단 entry
- [x] `## [0.14.2] - 2026-04-28` prepend
- [x] `### CFP-23 — mclayer marketplace 노출` heading
- [x] **Non-BREAKING** 명시
- [x] `### Added` / `### Why` / `### Migration` 3 섹션 (CFP-22 패턴 준수)

### 3. README.md install 섹션
- [x] `<marketplace>` placeholder → `mclayer` 구체화
- [x] `/plugins marketplace add mclayer/marketplace` 명령 추가
- [x] `~/.claude/settings.json` 영구 등록 예시 추가

### 4. Story doc
- [x] `docs/stories/CFP-23.md` — §1 verbatim 4건 사용자 결정 + plugin-meta-na §8/§9 N/A

### 5. spec/plan
- [x] `docs/superpowers/specs/2026-04-28-cfp-23-marketplace-exposure-notice-design.md`
- [x] `docs/superpowers/plans/2026-04-28-cfp-23-marketplace-exposure-notice.md` (본 파일)

### 6. 자가 검증 (playbook §3B.5 pre-push)
- [ ] `python3 -m json.tool .claude-plugin/plugin.json` 통과
- [ ] Step 5 dry-run: `jq -r '.version' .claude-plugin/plugin.json` ↔ `grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1` 일치 확인
- [ ] Step 3 dry-run: `ls agents/*.md | wc -l` ↔ `grep -oE '[0-9]+ core 에이전트' CLAUDE.md | head -1` 일치 (본 PR 미변경이지만 sanity)
- [ ] Step 7 dry-run: 본 release Non-BREAKING 확인 (CHANGELOG header에 "BREAKING" 없음)

### 7. Commit + push + PR
- [ ] feature branch `feat/cfp-23-marketplace-exposure-notice` (이미 생성)
- [ ] commit message: `feat(cfp-23): mclayer marketplace 노출 — README/CHANGELOG/plugin.json + v0.14.2`
- [ ] PR open: title prefix 없이 (story-init.yml `[STORY]` strip 정책 준수). plugin-meta-na 패턴 명시
- [ ] phase-gate-mergeable fail 시 admin override merge (plugin-meta-na 정책)

### 8. 후속 (본 PR 비포함)
- [ ] `mclayer/marketplace` 리포 측 marketplace.json `plugins[name=codeforge].version`을 0.14.2로 동기화 (별도 PR)
- [ ] cross-repo version parity CI 후속 CFP
- [ ] README 잔여 stale cleanup CFP

## 검증 기준 (PR mergeable)

- invariant-check Step 1-8 모두 PASS
- phase-gate-mergeable: plugin-meta-na 패턴 → fail 시 admin override

## 추정 비용

- 토큰: ~5k (단일 세션 내 처리)
- 인적: PR 작성 + 리뷰 (plugin-meta-na는 lane 게이트 면제이므로 self-review 충분)
