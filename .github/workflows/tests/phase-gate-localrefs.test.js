#!/usr/bin/env node
/**
 * CFP-2581 — phase-gate-mergeable localRefs binding parser — extract-and-execute harness.
 *
 * ADR-136 hollow-gate 방어: 정규식/same-repo 가드를 테스트에 하드카피하지 않고, shipped
 *   .github/workflows/phase-gate-mergeable.yml 을 파싱해 (1) localRefs 파서 블록(selfRepo + localRefs)
 *   과 (2) checkLabelMismatchOnly deadlock-resolver 함수를 추출·eval 한다.
 *   → shipped 파서/가드가 drift 하면 본 harness 가 실패로 검출(GREEN=hollow 방지). 정규식을 여기 복사하면
 *     shipped 가 바뀌어도 통과하는 hollow-gate 가 되므로 금지 — 본 파일에 정규식 리터럴은 없다(extract-only).
 *
 * Coverage (Change Plan §8 Test Contract — CFP-2581):
 *   AC-1          cross-repo same-repo `owner/repo#N` 직독            → localRefs=[123]
 *   AC-2a         bare `#N` (바인딩 존재)                              → localRefs=[123]
 *   AC-2b         ref 없음 → [] (PR-라벨 fallback 오차단 0)            → localRefs=[]
 *   AC-3          bare `#N` superset 무손상 (기존형)                   → localRefs=[2559]
 *   AC-3-neg      foreign `owner/repo#N` → skip (same-repo 가드)       → localRefs=[]
 *   AC-3-mix      키워드-반복형 (foreign 제외 + same-repo 포함)        → localRefs=[10,30]
 *   AC-3-resolver checkLabelMismatchOnly hasStoryIssue 전환 (오unblock 0)
 *   replacement   구 bare-only 파서(정규식 fragment) shipped 잔존=0    (교체 실증, new-alongside-old 방지)
 *
 * 실행: node .github/workflows/tests/phase-gate-localrefs.test.js  (exit 0 = GREEN, exit 1 = RED)
 */
'use strict';
const fs = require('fs');
const path = require('path');
const assert = require('assert').strict;

const WORKFLOW_PATH = path.join(__dirname, '../phase-gate-mergeable.yml');
const WORKFLOW_TEXT = fs.readFileSync(WORKFLOW_PATH, 'utf-8');
const LINES = WORKFLOW_TEXT.split('\n');

// ─────────────────────────────────────────────────────────────────────────────
// EXTRACT #1 — localRefs 파서 블록 (const selfRepo … .map(m => parseInt(m[2], 10));)
// ─────────────────────────────────────────────────────────────────────────────
function extractParserBlock() {
  let start = -1, end = -1;
  for (let i = 0; i < LINES.length; i++) {
    if (start === -1 && /const selfRepo = /.test(LINES[i])) start = i;
    if (start !== -1 && /\.map\(m => parseInt\(m\[2\], 10\)\);/.test(LINES[i])) { end = i; break; }
  }
  if (start === -1 || end === -1) {
    throw new Error('EXTRACT-FIDELITY FAIL: localRefs 파서 블록(selfRepo … parseInt(m[2])) 미발견 — shipped 파서가 예상 형태 아님');
  }
  return LINES.slice(start, end + 1).map(l => l.replace(/^\s{12}/, '')).join('\n');
}

const PARSER_BLOCK = extractParserBlock();
// 추출된 블록이 실제 정규식+가드를 담고 있는지(빈 추출 방지)
assert(/matchAll\(/.test(PARSER_BLOCK) && /\.filter\(/.test(PARSER_BLOCK),
  'EXTRACT-FIDELITY FAIL: 추출 블록에 matchAll/filter 부재 — 파서 추출 손상');

function parseLocalRefs(body, context) {
  // shipped 블록을 eval — body/context 만 주입, localRefs 반환
  const fn = new Function('body', 'context', PARSER_BLOCK + '\nreturn localRefs;');
  return fn(body, context);
}

// ─────────────────────────────────────────────────────────────────────────────
// EXTRACT #2 — checkLabelMismatchOnly deadlock-resolver (localRefs 2nd 소비자, F2/AC-3-resolver)
// ─────────────────────────────────────────────────────────────────────────────
function extractResolverFn() {
  let start = -1, end = -1;
  for (let i = 0; i < LINES.length; i++) {
    if (/async function checkLabelMismatchOnly\(/.test(LINES[i])) { start = i; break; }
  }
  if (start === -1) throw new Error('EXTRACT-FIDELITY FAIL: checkLabelMismatchOnly 미발견');
  for (let i = start + 1; i < LINES.length; i++) {
    if (/^\s{12}\}\s*$/.test(LINES[i])) { end = i; break; }   // 12-space 들여쓰기 함수 닫는 중괄호
  }
  if (end === -1) throw new Error('EXTRACT-FIDELITY FAIL: checkLabelMismatchOnly 종료 브레이스 미발견');
  return LINES.slice(start, end + 1).map(l => l.replace(/^\s{12}/, '')).join('\n');
}

const RESOLVER_SRC = extractResolverFn();
const checkLabelMismatchOnly = new Function(RESOLVER_SRC + '\nreturn checkLabelMismatchOnly;')();

// ─────────────────────────────────────────────────────────────────────────────
// FIXTURES
// ─────────────────────────────────────────────────────────────────────────────
const CTX = { repo: { owner: 'mclayer', repo: 'plugin-codeforge' } };
// canonical Story issue 를 type:story 로 리턴하는 stub (resolver hasStoryIssue 경로용)
const storyGitHub = {
  rest: { issues: { get: async () => ({ data: { labels: [{ name: 'type:story' }] } }) } }
};

// ─────────────────────────────────────────────────────────────────────────────
// TEST RUNNER
// ─────────────────────────────────────────────────────────────────────────────
const tests = [];
let pass = 0, fail = 0;
function testCase(name, fn) { tests.push({ name, fn }); }

// ── 파서 ACs (extract #1) ──
testCase('AC-1 cross-repo same-repo owner/repo#N 직독 → [123]', () => {
  assert.deepEqual(parseLocalRefs('Related: mclayer/plugin-codeforge#123', CTX), [123]);
});
testCase('AC-1b case-insensitive owner/repo → [77]', () => {
  assert.deepEqual(parseLocalRefs('Related: MClayer/Plugin-Codeforge#77', CTX), [77]);
});
testCase('AC-2a bare #N (바인딩 존재) → [123]', () => {
  assert.deepEqual(parseLocalRefs('Related: #123', CTX), [123]);
});
testCase('AC-2b no-ref → [] (PR-라벨 fallback 오차단 0)', () => {
  assert.deepEqual(parseLocalRefs('본문에 issue ref 없음', CTX), []);
});
testCase('AC-3 bare #N superset 무손상 (기존형 #2559) → [2559]', () => {
  assert.deepEqual(parseLocalRefs('Related: #2559', CTX), [2559]);
});
testCase('AC-3-neg foreign owner/repo#N → [] (same-repo 가드)', () => {
  assert.deepEqual(parseLocalRefs('Related: other/repo#123', CTX), []);
});
testCase('AC-3-mix 키워드-반복형 → [10,30] (foreign other/x#20 제외 + same-repo #30 포함)', () => {
  assert.deepEqual(
    parseLocalRefs('Related: #10, Related: other/x#20, Related: mclayer/plugin-codeforge#30', CTX),
    [10, 30]);
});
testCase('parser keyword coverage: Closes/Fixes/Resolves 도 same-repo 가드 적용', () => {
  assert.deepEqual(parseLocalRefs('Closes: mclayer/plugin-codeforge#5\nFixes: other/x#6\nResolves: #7', CTX), [5, 7]);
});

// ── resolver ACs (extract #2, F2) ──
testCase('AC-3-resolver cross-repo ref + gate + phaseLabel → hasStoryIssue true → unblock(true)', async () => {
  const body = 'Related: mclayer/plugin-codeforge#123';
  const refs = parseLocalRefs(body, CTX);
  const out = await checkLabelMismatchOnly(body, refs, 'phase:구현', ['gate:design-review-pass'], storyGitHub, CTX);
  assert.equal(out, true, 'cross-repo 표기 PR 이 resolver 에서 Story-binding 으로 인식(F2 intended)');
});
testCase('AC-3-resolver 오unblock 0: gate 라벨 부재 → Story binding 인식돼도 unblock false', async () => {
  const body = 'Related: mclayer/plugin-codeforge#123';
  const refs = parseLocalRefs(body, CTX);
  const out = await checkLabelMismatchOnly(body, refs, 'phase:구현', [], storyGitHub, CTX);
  assert.equal(out, false, 'gate 라벨 없으면 unblock 안 함(오unblock 0)');
});
testCase('AC-3-resolver foreign ref → localRefs=[] → hasStoryIssue false → unblock false', async () => {
  const body = 'Related: other/repo#123';
  const refs = parseLocalRefs(body, CTX);
  const out = await checkLabelMismatchOnly(body, refs, 'phase:구현', ['gate:design-review-pass'], storyGitHub, CTX);
  assert.equal(out, false, 'foreign ref 는 Story binding 미인식 → 정식 차단(fail-closed)');
});

// ── replacement-mutation (ADR-136): 구 파서 grep=0 (shipped 텍스트 대상) ──
testCase('replacement-mutation: 구 bare-only 파서 fragment shipped 잔존=0 (교체 실증)', () => {
  const OLD_FRAGMENT = ':?\\s+#(\\d+)';                 // 구 정규식 distinctive fragment(\s+ 직후 #)
  assert.ok(!WORKFLOW_TEXT.includes(OLD_FRAGMENT),
    `구 파서 fragment '${OLD_FRAGMENT}' 잔존 — 정규식 미교체 또는 new-alongside-old(hollow)`);
  const NEW_FRAGMENT = '(?:([\\w.-]+\\/[\\w.-]+))?#(\\d+)'; // 새 파서 owner/repo optional capture
  assert.ok(WORKFLOW_TEXT.includes(NEW_FRAGMENT), '새 파서 fragment 부재 — shipped 파서 미확인');
});

// ─────────────────────────────────────────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────────────────────────────────────────
(async () => {
  console.log('='.repeat(78));
  console.log('CFP-2581 phase-gate-mergeable localRefs 파서 — extract-and-execute harness');
  console.log('  (parser block + checkLabelMismatchOnly = shipped .yml 에서 추출·eval, 하드카피 0)');
  console.log('='.repeat(78));
  for (const t of tests) {
    try { await t.fn(); console.log('✓ ' + t.name); pass++; }
    catch (e) { console.log('✗ ' + t.name); console.log('  ' + (e && e.message ? e.message : e)); fail++; }
  }
  console.log('='.repeat(78));
  console.log(`Results: ${pass} PASS, ${fail} FAIL`);
  if (fail === 0) { console.log('✓ ALL GREEN — localRefs 바인딩 파서 shipped-bound 검증 완료'); process.exit(0); }
  console.log('✗ RED'); process.exit(1);
})();
