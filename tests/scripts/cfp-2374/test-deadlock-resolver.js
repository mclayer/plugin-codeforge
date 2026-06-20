// CFP-2374 / ADR-127 §K — phase-gate-mergeable.yml deadlock-resolver anti-theater test.
//
// 목적: isDocOnly/isChoreOnly process-derived fast-pass 폐지 + isLabelMismatchOnly deadlock-resolver
//       신설을 4-case 행동 assert + 구조 assert 로 검증 (missing-case + 차단 assert 양면).
//
// 실행: node tests/scripts/cfp-2374/test-deadlock-resolver.js
//       exit 0 = PASS / exit 1 = FAIL (anti-theater — 실제 함수 추출 후 behavioral assert).
//
// anti-theater 설계:
//   1. checkLabelMismatchOnly 를 workflow yml 에서 실제 추출해 실행 (grep-only 연극 회피).
//   2. 4 case 모두 "기대값 ≠ 실제값" 시 즉시 FAIL (missing-case 검출).
//   3. 차단 case(②③④)는 false 를, unblock case(①)는 true 를 양면 assert.
//   4. 구조 assert: isChoreOnly/isDocOnly live 코드 잔존 0 (dead path 제거 확인).

'use strict';
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const repoRoot = path.resolve(__dirname, '..', '..', '..');
const wfPath = path.join(repoRoot, '.github', 'workflows', 'phase-gate-mergeable.yml');
const tmplPath = path.join(repoRoot, 'templates', 'github-workflows', 'phase-gate-mergeable.yml');

let failures = 0;
function check(name, fn) {
  try { fn(); console.log(`  PASS  ${name}`); }
  catch (e) { failures++; console.error(`  FAIL  ${name}\n        ${e.message}`); }
}

const wf = fs.readFileSync(wfPath, 'utf-8');
const tmpl = fs.readFileSync(tmplPath, 'utf-8');

// ── 구조 assert: byte-identical mirror (ADR-005) ──
check('mirror byte-identical (.github == templates)', () => {
  assert.strictEqual(wf, tmpl, 'two phase-gate-mergeable.yml must be byte-identical');
});

// ── 구조 assert: isChoreOnly/isDocOnly live 코드 잔존 0 ──
check('no live isDocOnly fast-pass (assignment 잔존 0)', () => {
  assert.ok(!/let\s+isDocOnly\s*=/.test(wf), 'let isDocOnly = ... must be removed');
});
check('no live isChoreOnly fast-pass (assignment 잔존 0)', () => {
  assert.ok(!/let\s+isChoreOnly\s*=/.test(wf), 'let isChoreOnly = ... must be removed');
});
check('checkNoStoryBinding helper 제거', () => {
  assert.ok(!/function\s+checkNoStoryBinding/.test(wf), 'checkNoStoryBinding helper must be removed');
});
check('OR-gate 가 isLabelMismatchOnly 사용 (isDocOnly/isChoreOnly 미사용)', () => {
  const m = wf.match(/if \(isEpicLabel \|\| isSiblingPr \|\| isPostMergeFix \|\| isLabelMismatchOnly\)/);
  assert.ok(m, 'OR-gate must read: isEpicLabel || isSiblingPr || isPostMergeFix || isLabelMismatchOnly');
  assert.ok(!/isDocOnly \|\| isPostMergeFix \|\| isChoreOnly/.test(wf), 'old 5-way OR-gate must be gone');
});

// ── 실제 함수 추출 후 behavioral assert ──
function extractFn() {
  const start = wf.indexOf('async function checkLabelMismatchOnly');
  assert.ok(start >= 0, 'checkLabelMismatchOnly must exist');
  // brace-match from the first '{' after the signature
  const braceStart = wf.indexOf('{', start);
  let depth = 0, i = braceStart;
  for (; i < wf.length; i++) {
    if (wf[i] === '{') depth++;
    else if (wf[i] === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  let src = wf.slice(start, i);
  // de-indent (12-space leading inside script block)
  src = src.split('\n').map(l => l.replace(/^ {12}/, '')).join('\n');
  // eslint-disable-next-line no-new-func
  return new Function('return (' + src.replace('async function checkLabelMismatchOnly', 'async function') + ')')();
}
const checkLabelMismatchOnly = extractFn();

// mock github — type:story Issue 보유 여부를 issueNum 으로 제어
function makeGithub(storyIssueNums) {
  return {
    rest: { issues: { get: async ({ issue_number }) => {
      if (storyIssueNums.includes(issue_number)) return { data: { labels: [{ name: 'type:story' }] } };
      const e = new Error('Not Found'); e.status = 404; throw e;
    } } }
  };
}
const ctx = { repo: { owner: 'mclayer', repo: 'plugin-codeforge' } };

// Case ① — full-flow 증거(Story binding ∧ gate 라벨) 충족 ∧ phase 라벨 존재 → unblock(true)
check('case ① full-flow 증거 + phase mismatch → unblock(true)', () => {
  const body = 'story_uri: https://github.com/mclayer/codeforge-internal-docs/blob/main/x/stories/CFP-2374.md';
  return checkLabelMismatchOnly(body, [], 'phase:구현', ['gate:design-review-pass'], makeGithub([]), ctx)
    .then(r => assert.strictEqual(r, true, 'expected true'));
});

// Case ② — Story 없음 → 차단(false)
check('case ② Story 미연결 → 차단(false)', () => {
  return checkLabelMismatchOnly('no story marker', [], 'phase:구현', ['gate:design-review-pass'], makeGithub([]), ctx)
    .then(r => assert.strictEqual(r, false, 'expected false (no Story binding)'));
});

// Case ③ — gate 라벨 0건 → 차단(false)
check('case ③ gate 라벨 0건 → 차단(false)', () => {
  const body = 'story_uri: https://github.com/mclayer/codeforge-internal-docs/blob/main/x/stories/CFP-2374.md';
  return checkLabelMismatchOnly(body, [], 'phase:구현', [], makeGithub([]), ctx)
    .then(r => assert.strictEqual(r, false, 'expected false (no gate label)'));
});

// Case ④ — phaseLabel 부재 → 차단(false)
check('case ④ phaseLabel 부재 → 차단(false)', () => {
  const body = 'story_uri: https://github.com/mclayer/codeforge-internal-docs/blob/main/x/stories/CFP-2374.md';
  return checkLabelMismatchOnly(body, [], null, ['gate:design-review-pass'], makeGithub([]), ctx)
    .then(r => assert.strictEqual(r, false, 'expected false (no phase label)'));
});

// linked type:story Issue 경로도 Story binding 으로 인정 (story_uri 부재여도)
check('case ①b linked type:story Issue → unblock(true)', () => {
  return checkLabelMismatchOnly('Related: #42', [42], 'phase:구현', ['gate:design-review-pass'], makeGithub([42]), ctx)
    .then(r => assert.strictEqual(r, true, 'expected true (linked type:story binding)'));
});

// 비동기 assert 들이 microtask 로 끝난 뒤 종료 코드 결정
setTimeout(() => {
  if (failures > 0) { console.error(`\nCFP-2374 deadlock-resolver test: ${failures} FAIL`); process.exit(1); }
  console.log('\nCFP-2374 deadlock-resolver test: ALL PASS'); process.exit(0);
}, 200);
