#!/usr/bin/env node
/**
 * CFP-2584 — phase-gate 형제 워크플로 parser-parity harness (extract-and-execute).
 *
 * ADR-136 hollow-gate 방어: 정규식/same-repo 가드를 테스트에 하드카피하지 않고, shipped
 *   .github/workflows/{auto-phase-label,phase-gate-auto-cleanup}.yml 을 파싱해 각 파서 블록을
 *   추출·eval 한다. shipped 파서가 drift 하면 본 harness 가 실패로 검출(GREEN=hollow 방지).
 *   본 파일에 파서 정규식 리터럴 없음(extract-only). CFP-2581 phase-gate-localrefs.test.js 구조 승계.
 *
 * Coverage (Change Plan §8 Test Contract — CFP-2584, AC-1~10):
 *   AC-1  same-repo owner/repo#N   → A=[123] / B=true    (확장판별: OLD bare-only 는 미매칭)
 *   AC-2  bare #N superset          → A=[123] / B=true    (회귀 witness)
 *   AC-3  foreign other/repo#N      → A=[]    / B=false   (same-repo 가드 mutant kill)
 *   AC-4  멀티라인 mix              → A=[10,30] / B=true  (확장+필터, ★멀티라인 필수)
 *   AC-8  same-repo owner/repo#N    → A=[123] Number-only (capture index / NaN 오취급 0)
 *   AC-9  story_uri 단독            → B marker=false + shipped OR 경로(hasAllowedStoryUri) 보존
 *   AC-10 full-URL foreign vs same  → A: foreign 미상속 / same-repo URL 상속 (fork① 가드)
 *   replacement-mutation: 구 파서 fragment shipped 잔존=0 (교체 실증)
 *
 * 실행: node .github/workflows/tests/phase-gate-sibling-parsers.test.js  (exit 0=GREEN, 1=RED)
 */
'use strict';
const fs = require('fs');
const path = require('path');
const assert = require('assert').strict;

const A_PATH = path.join(__dirname, '../auto-phase-label.yml');
const B_PATH = path.join(__dirname, '../phase-gate-auto-cleanup.yml');
const A_TEXT = fs.readFileSync(A_PATH, 'utf-8');
const B_TEXT = fs.readFileSync(B_PATH, 'utf-8');
const A_LINES = A_TEXT.split('\n');
const B_LINES = B_TEXT.split('\n');

// ─────────────────────────────────────────────────────────────────────────────
// EXTRACT A — auto-phase-label.yml tier-2 파서 블록 (selfRepo … uniqueRelated)
// ─────────────────────────────────────────────────────────────────────────────
function extractParserA() {
  let start = -1, end = -1;
  for (let i = 0; i < A_LINES.length; i++) {
    if (start === -1 && /const selfRepo = /.test(A_LINES[i])) start = i;
    if (start !== -1 && /const uniqueRelated = \[\.\.\.new Set\(relatedNumbers\)\];/.test(A_LINES[i])) { end = i; break; }
  }
  if (start === -1 || end === -1) {
    throw new Error('EXTRACT-FIDELITY FAIL (A): selfRepo … uniqueRelated 블록 미발견 — shipped auto-phase-label 파서가 예상 형태 아님(미이식 또는 drift)');
  }
  const block = A_LINES.slice(start, end + 1).map(l => l.replace(/^\s{12}/, '')).join('\n');
  assert(block.includes('(?:([\\w.-]+\\/[\\w.-]+))?#(\\d+)'),
    'EXTRACT-FIDELITY FAIL (A): shorthand owner/repo optional capture 부재 — parity 미이식');
  assert(block.includes('selfRepo'), 'EXTRACT-FIDELITY FAIL (A): selfRepo 가드 부재');
  return block;
}
const PARSER_A = extractParserA();
function parseA(body, context) {
  const fn = new Function('body', 'context', PARSER_A + '\nreturn uniqueRelated;');
  return fn(body, context);
}

// ─────────────────────────────────────────────────────────────────────────────
// EXTRACT B — phase-gate-auto-cleanup.yml marker 파서 블록 (selfRepo … hasRelatedMarker)
// ─────────────────────────────────────────────────────────────────────────────
function extractParserB() {
  let start = -1, end = -1;
  for (let i = 0; i < B_LINES.length; i++) {
    if (start === -1 && /const selfRepo = /.test(B_LINES[i])) start = i;
    if (start !== -1 && /const hasRelatedMarker = relatedRefs\.length > 0;/.test(B_LINES[i])) { end = i; break; }
  }
  if (start === -1 || end === -1) {
    throw new Error('EXTRACT-FIDELITY FAIL (B): selfRepo … hasRelatedMarker(relatedRefs.length) 블록 미발견 — shipped phase-gate-auto-cleanup 파서가 예상 형태 아님(미이식 또는 drift)');
  }
  const block = B_LINES.slice(start, end + 1).map(l => l.replace(/^\s{12}/, '')).join('\n');
  assert(block.includes('matchAll('), 'EXTRACT-FIDELITY FAIL (B): matchAll 부재 — boolean .test() 구조전환 미이행');
  assert(block.includes('.filter('), 'EXTRACT-FIDELITY FAIL (B): filter 부재 — same-repo 가드 미이식');
  assert(block.includes('(?:([\\w.-]+\\/[\\w.-]+))?#(\\d+)'), 'EXTRACT-FIDELITY FAIL (B): owner/repo optional capture 부재');
  return block;
}
const PARSER_B = extractParserB();
function markerB(body, owner, repo) {
  const fn = new Function('body', 'owner', 'repo', PARSER_B + '\nreturn hasRelatedMarker;');
  return fn(body, owner, repo);
}

// ─────────────────────────────────────────────────────────────────────────────
// FIXTURES + RUNNER
// ─────────────────────────────────────────────────────────────────────────────
const CTX = { repo: { owner: 'mclayer', repo: 'plugin-codeforge' } };
const OWNER = 'mclayer', REPO = 'plugin-codeforge';
const tests = [];
let pass = 0, fail = 0;
function testCase(name, fn) { tests.push({ name, fn }); }

testCase('AC-1 same-repo owner/repo#N → A=[123] / B=true (확장판별)', () => {
  assert.deepEqual(parseA('Related: mclayer/plugin-codeforge#123', CTX), [123]);
  assert.equal(markerB('Related: mclayer/plugin-codeforge#123', OWNER, REPO), true);
});
testCase('AC-1b case-insensitive owner/repo → A=[77] / B=true', () => {
  assert.deepEqual(parseA('Related: MClayer/Plugin-Codeforge#77', CTX), [77]);
  assert.equal(markerB('Closes: MClayer/Plugin-Codeforge#77', OWNER, REPO), true);
});
testCase('AC-2 bare #N superset 무손상 → A=[123] / B=true (회귀 witness)', () => {
  assert.deepEqual(parseA('Related: #123', CTX), [123]);
  assert.equal(markerB('Related: #123', OWNER, REPO), true);
});
testCase('AC-2b no-ref → A=[] / B=false (오차단/오인식 0)', () => {
  assert.deepEqual(parseA('본문에 issue ref 없음', CTX), []);
  assert.equal(markerB('본문에 issue ref 없음', OWNER, REPO), false);
});
testCase('AC-3 foreign other/repo#N → A=[] / B=false (same-repo 가드 mutant kill)', () => {
  assert.deepEqual(parseA('Related: other/repo#123', CTX), []);
  assert.equal(markerB('Related: other/repo#123', OWNER, REPO), false);
});
testCase('AC-4 ★멀티라인 mix → A=[10,30] / B=true (foreign other/x#20 제외)', () => {
  const body = 'Related: #10\nRelated: other/x#20\nRelated: mclayer/plugin-codeforge#30';
  assert.deepEqual(parseA(body, CTX), [10, 30]);
  assert.equal(markerB(body, OWNER, REPO), true);
});
testCase('AC-8 capture index 정합 → A=[123] Number-only (repo문자열/undefined→NaN 오취급 0)', () => {
  const out = parseA('Related: mclayer/plugin-codeforge#123', CTX);
  assert.deepEqual(out, [123]);
  assert.ok(out.every(n => Number.isInteger(n)), 'output NaN/문자열 혼입 → capture index 버그');
});
testCase('AC-9 B story_uri OR 경로 보존 (Related 없이 story_uri 만 → marker=false, OR 진입 유지)', () => {
  const body = 'story_uri: https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-2584.md';
  assert.equal(markerB(body, OWNER, REPO), false, 'Related 없음 → hasRelatedMarker=false');
  assert.ok(B_TEXT.includes('hasAllowedStoryUri'), 'story_uri OR 경로(hasAllowedStoryUri) 부재 — AC-9 회귀');
  assert.ok(B_TEXT.includes('!hasRelatedMarker && !hasAllowedStoryUri'), 'OR 결합 skip 로직 부재 — AC-9 회귀');
});
testCase('AC-10 full-URL foreign → A=[] / same-repo URL → A=[999] (fork① 가드 mutant kill)', () => {
  assert.deepEqual(parseA('https://github.com/other/repo/issues/999', CTX), []);
  assert.deepEqual(parseA('https://github.com/mclayer/plugin-codeforge/issues/999', CTX), [999]);
});

// ── replacement-mutation (ADR-136): 구 파서 fragment shipped 잔존=0 ──
testCase('replacement-mutation A: 구 bare-only relatedRegex/urlRegex fragment 잔존=0 + 신규 존재', () => {
  assert.ok(!A_TEXT.includes('related[ \\t]*:[ \\t]*#(\\d+)'), '구 A relatedRegex bare fragment 잔존 — 미교체/hollow');
  assert.ok(!A_TEXT.includes('github\\.com\\/[\\w.-]+\\/[\\w.-]+\\/issues\\/(\\d+)'), '구 A urlRegex non-capture fragment 잔존 — fork① 미이식');
  assert.ok(A_TEXT.includes('(?:([\\w.-]+\\/[\\w.-]+))?#(\\d+)'), '신규 A shorthand capture 부재');
  assert.ok(A_TEXT.includes('github\\.com\\/([\\w.-]+\\/[\\w.-]+)\\/issues\\/(\\d+)'), '신규 A urlRegex capture 부재');
});
testCase('replacement-mutation B: 구 boolean .test() fragment 잔존=0 + 신규 matchAll+filter 존재', () => {
  assert.ok(!B_TEXT.includes('/(?:Related|Closes|Fixes|Resolves):?\\s+#\\d+/i.test(body)'), '구 B boolean .test() fragment 잔존 — 미교체/hollow');
  assert.ok(B_TEXT.includes('matchAll('), '신규 B matchAll 부재');
  assert.ok(B_TEXT.includes('.filter(m => !m[1]'), '신규 B same-repo filter 부재');
});

(async () => {
  console.log('='.repeat(78));
  console.log('CFP-2584 phase-gate 형제 파서 parity — extract-and-execute harness');
  console.log('  (A=auto-phase-label / B=phase-gate-auto-cleanup, shipped .yml 추출·eval, 하드카피 0)');
  console.log('='.repeat(78));
  for (const t of tests) {
    try { await t.fn(); console.log('PASS ' + t.name); pass++; }
    catch (e) { console.log('FAIL ' + t.name); console.log('  ' + (e && e.message ? e.message : e)); fail++; }
  }
  console.log('='.repeat(78));
  console.log(`Results: ${pass} PASS, ${fail} FAIL`);
  if (fail === 0) { console.log('ALL GREEN — 형제 파서 parity shipped-bound 검증 완료'); process.exit(0); }
  console.log('RED'); process.exit(1);
})();
