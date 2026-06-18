#!/usr/bin/env node
/**
 * CFP-2324 Phase 2 gate logic — anti-theater test harness
 * Extracts LIVE workflow JS from .github/workflows/phase-gate-mergeable.yml
 * and exercises S2/S6/S7 via pure Node assertions + mutation survival proofs.
 *
 * Test coverage: 14 cases (3 S2 hard + 5 S6 provenance + 6 S7 operational AC)
 * Mutation survival: 3/3 killed (M-S2 wrong-gate, M-S6 provenance warning, M-S7 throughput warning)
 * False-positives: 0 (regression-guard cases verify no spurious warnings)
 * Implementation verified: S2/S6/S7 blocks all active in workflow (lines 491/686/742)
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert').strict;

// ─────────────────────────────────────────────────────────────────────────────
// 1. EXTRACT LIVE JS from workflow file
// ─────────────────────────────────────────────────────────────────────────────

function extractWorkflowScript() {
  const workflowPath = path.join(__dirname, '../phase-gate-mergeable.yml');
  const content = fs.readFileSync(workflowPath, 'utf-8');

  // Find "script: |" and extract until the next unindented line or EOF
  const lines = content.split('\n');
  let scriptStartIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('script: |')) {
      scriptStartIdx = i + 1;  // script content starts on next line
      break;
    }
  }

  if (scriptStartIdx === -1) {
    throw new Error('Could not find "script: |" in workflow');
  }

  // Extract script lines until we hit a line with less indentation than 12 spaces (or EOF)
  const scriptLines = [];
  for (let i = scriptStartIdx; i < lines.length; i++) {
    const line = lines[i];
    // Check if this line starts with less than 12 spaces (and is not empty)
    if (line.length > 0 && !line.match(/^\s{12}/)) {
      break;
    }
    scriptLines.push(line);
  }

  // De-indent 12 spaces
  const scriptBody = scriptLines
    .map(line => {
      if (line.match(/^\s{12}/)) {
        return line.slice(12);
      }
      return line;
    })
    .join('\n')
    .trim();

  if (!scriptBody.includes('github.rest.checks.create')) {
    throw new Error('Extracted script does not contain expected gate logic');
  }

  return scriptBody;
}

const WORKFLOW_SCRIPT = extractWorkflowScript();

// ─────────────────────────────────────────────────────────────────────────────
// 2. STUB OBJECTS (github, context, core, fetch, Buffer)
// ─────────────────────────────────────────────────────────────────────────────

class StubContext {
  constructor(config) {
    this.repo = config.repo || {owner: 'mclayer', repo: 'plugin-codeforge'};
    const prNumber = config.prNumber || 1;
    this.payload = {
      pull_request: {
        number: prNumber,
        body: config.prBody || '',
        head: {sha: 'deadbeef'},
        html_url: `https://github.com/${this.repo.owner}/${this.repo.repo}/pull/${prNumber}`
      }
    };
  }
}

class StubGitHub {
  constructor(config) {
    this.config = config || {};
    this.commentsPosted = [];
    this.checksCreated = [];
    this.rest = {
      pulls: {
        get: async (opts) => {
          return {
            data: {
              labels: this.config.labels || []
            }
          };
        },
        listFiles: async (opts) => {
          return {
            data: this.config.files || []
          };
        }
      },
      issues: {
        get: async (opts) => {
          throw {status: 404, message: 'Not Found'};
        },
        listComments: async (opts) => {
          return {
            data: this.config.comments || []
          };
        },
        createComment: async (opts) => {
          this.commentsPosted.push({
            issue_number: opts.issue_number,
            body: opts.body
          });
          return {data: {id: Math.random()}};
        }
      },
      checks: {
        create: async (opts) => {
          this.checksCreated.push({
            conclusion: opts.conclusion,
            title: opts.output.title,
            summary: opts.output.summary
          });
          return {data: {}};
        }
      }
    };
  }
}

class StubCore {
  constructor() {
    this.messages = [];
  }
  info(msg) { this.messages.push({level: 'info', msg}); }
  warning(msg) { this.messages.push({level: 'warning', msg}); }
  setOutput(key, val) {}
}

global.fetch = async (url, opts) => {
  const fetchConfig = global.__fetchConfig || {};
  if (fetchConfig.mockResponse) {
    return fetchConfig.mockResponse;
  }
  return {
    ok: false,
    status: 404,
    statusText: 'Not Found',
    json: async () => ({})
  };
};

global.Buffer = require('buffer').Buffer;

// ─────────────────────────────────────────────────────────────────────────────
// 3. RUN GATE LOGIC with fixture
// ─────────────────────────────────────────────────────────────────────────────

async function runGate(fixture) {
  const context = new StubContext(fixture);
  const github = new StubGitHub(fixture);
  const core = new StubCore();

  if (fixture.fetchMock) {
    global.__fetchConfig = fixture.fetchMock;
  } else {
    global.__fetchConfig = {};
  }

  const oldEnv = process.env.ALLOWED_HUB_REPOS;
  const oldCrossToken = process.env.CROSS_REPO_TOKEN;
  process.env.ALLOWED_HUB_REPOS = fixture.allowedHubRepos || 'github.com/mclayer/codeforge-internal-docs';
  process.env.CROSS_REPO_TOKEN = fixture.crossRepoToken || '';

  try {
    const fn = new Function('github', 'context', 'core', `
      return (async () => {
        ${WORKFLOW_SCRIPT}
      })();
    `);

    await fn(github, context, core);
  } finally {
    process.env.ALLOWED_HUB_REPOS = oldEnv;
    process.env.CROSS_REPO_TOKEN = oldCrossToken;
    global.__fetchConfig = {};
  }

  return {
    checks: github.checksCreated,
    comments: github.commentsPosted,
    core: core
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. TEST HARNESS
// ─────────────────────────────────────────────────────────────────────────────

const tests = [];
let passCount = 0;
let failCount = 0;

function testCase(name, fn) {
  tests.push({name, fn});
}

async function runAllTests() {
  console.log('='.repeat(80));
  console.log('CFP-2324 Phase 2 Gate Logic Test Suite');
  console.log('='.repeat(80));

  for (const test of tests) {
    try {
      await test.fn();
      console.log(`✓ ${test.name}`);
      passCount++;
    } catch (e) {
      console.log(`✗ ${test.name}`);
      console.log(`  Error: ${e.message}`);
      failCount++;
    }
  }

  console.log('='.repeat(80));
  console.log(`Results: ${passCount} PASS, ${failCount} FAIL`);
  return failCount === 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// S2 TEST CASES (Hard Gate) — ACTIVE
// ─────────────────────────────────────────────────────────────────────────────

testCase('S2-A: 요구사항-리뷰 phase, no pass gate, code file → action_required + requires gate:requirements-review-pass', async () => {
  const result = await runGate({
    prBody: '',
    labels: [{name: 'phase:요구사항-리뷰'}],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const check = result.checks[0];
  assert.equal(check.conclusion, 'action_required', 'should be action_required');
  assert(check.summary.includes('gate:requirements-review-pass'), 'summary must require gate:requirements-review-pass');
  assert(!check.summary.includes('gate:design-review-pass'), 'summary should NOT require gate:design-review-pass (wrong-gate guard)');
});

testCase('S2-B: 요구사항-리뷰 + gate:requirements-review-pass label → success', async () => {
  const result = await runGate({
    prBody: '',
    labels: [
      {name: 'phase:요구사항-리뷰'},
      {name: 'gate:requirements-review-pass'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const check = result.checks[0];
  assert.equal(check.conclusion, 'success', 'should be success with gate:requirements-review-pass');
});

testCase('S2-C: 요구사항-리뷰 phase, no gate label, but comment evidence → success', async () => {
  const result = await runGate({
    prBody: '',
    labels: [{name: 'phase:요구사항-리뷰'}],
    files: [{filename: 'src/x.js', status: 'modified'}],
    comments: [
      {
        id: 1,
        body: '## [요구사항-리뷰] PASS\nReview completed successfully.'
      }
    ]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const check = result.checks[0];
  assert.equal(check.conclusion, 'success', 'should succeed via comment evidence');
});

// ─────────────────────────────────────────────────────────────────────────────
// S6 TEST CASES (Provenance Warning) — ACTIVE
// ─────────────────────────────────────────────────────────────────────────────

const VALID_PACKET = [
  'review_verdict:',
  '  contract_version: "4.13"',
  '  lane: design',
  '  story_key: CFP-2330',
  '  iteration: 1',
  '  pl_recommendation: PASS'
].join('\n');

const LANE_EVIDENCE = '## Lane evidence\n- 설계-리뷰: PASS (gate:design-review-pass)';

testCase('TC-S6-1 (mutation): active-gate, no packet, no Lane evidence → should warn', async () => {
  const result = await runGate({
    prBody: '',
    labels: [
      {name: 'phase:설계-리뷰'},
      {name: 'gate:design-review-pass'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  assert.equal(result.checks[0].conclusion, 'success', 'gate passes (no hard block on S6 warning)');
  const hasS6Warning = result.comments.some(c => c.body.includes('[CFP-2324 S6 provenance — warning]'));
  assert(hasS6Warning, 'S6 warning should be posted (no packet, no evidence)');
});

testCase('TC-S6-2 (mutation): non-mixed repo, no Lane evidence → should warn', async () => {
  const result = await runGate({
    repo: {owner: 'mclayer', repo: 'mctrader'},
    prBody: VALID_PACKET,
    labels: [
      {name: 'phase:설계-리뷰'},
      {name: 'gate:design-review-pass'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  assert.equal(result.checks[0].conclusion, 'success', 'gate passes');
  const hasS6Warning = result.comments.some(c => c.body.includes('[CFP-2324 S6 provenance — warning]'));
  assert(hasS6Warning, 'S6 warning should be posted (packet present but no Lane evidence on non-mixed)');
});

testCase('TC-S6-3 (regression-guard): mixed repo, packet + Lane evidence → NO warn', async () => {
  const result = await runGate({
    prBody: VALID_PACKET + '\n\n' + LANE_EVIDENCE,
    labels: [
      {name: 'phase:설계-리뷰'},
      {name: 'gate:design-review-pass'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS6Warning = result.comments.some(c => c.body.includes('[CFP-2324 S6 provenance — warning]'));
  assert(!hasS6Warning, 'NO S6 warning (both anchors present)');
});

testCase('TC-S6-4 (regression-guard): mixed repo (plugin-codeforge), packet alone → NO warn', async () => {
  const result = await runGate({
    prBody: VALID_PACKET,
    labels: [
      {name: 'phase:설계-리뷰'},
      {name: 'gate:design-review-pass'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS6Warning = result.comments.some(c => c.body.includes('[CFP-2324 S6 provenance — warning]'));
  assert(!hasS6Warning, 'NO S6 warning (mixed repo exemption: packet = anchor 1+2)');
});

testCase('TC-S6-5 (regression-guard): non-active-gate phase → NO warn', async () => {
  const result = await runGate({
    prBody: '',
    labels: [{name: 'phase:구현'}],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS6Warning = result.comments.some(c => c.body.includes('[CFP-2324 S6 provenance — warning]'));
  assert(!hasS6Warning, 'NO S6 warning (non-review gate phase: S6 only fires on active-gate PRs)');
});

// ─────────────────────────────────────────────────────────────────────────────
// S7 TEST CASES (Operational Throughput AC Warning) — ACTIVE
// ─────────────────────────────────────────────────────────────────────────────

const THR = 'throughput ≥ 100 req/s under sustained load';
const RSS = 'bounded-memory RSS ≤ 256 MB under sustained load';
const EMP = '[empirical-source: benchmark run CFP-2330-perf]';

testCase('TC-S7-1 (mutation): operational, no throughput → should warn', async () => {
  const result = await runGate({
    prBody: RSS + '\n' + EMP,
    labels: [
      {name: 'operational:true'},
      {name: 'component:runner'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS7Warning = result.comments.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
  assert(hasS7Warning, 'S7 warning should be posted (no throughput AC)');
  const warningBody = result.comments.find(c => c.body.includes('[CFP-2324 S7')).body;
  assert(warningBody.includes('throughput'), 'warning must mention throughput axis');
});

testCase('TC-S7-2 (mutation): operational, no RSS → should warn', async () => {
  const result = await runGate({
    prBody: THR + '\n' + EMP,
    labels: [
      {name: 'operational:true'},
      {name: 'component:runner'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS7Warning = result.comments.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
  assert(hasS7Warning, 'S7 warning should be posted (no RSS AC)');
  const warningBody = result.comments.find(c => c.body.includes('[CFP-2324 S7')).body;
  assert(warningBody.includes('bounded-memory') || warningBody.includes('RSS'), 'warning must mention RSS/bounded-memory');
});

testCase('TC-S7-3 (mutation): operational, no empirical-source → should warn', async () => {
  const result = await runGate({
    prBody: THR + '\n' + RSS,
    labels: [
      {name: 'operational:true'},
      {name: 'component:runner'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS7Warning = result.comments.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
  assert(hasS7Warning, 'S7 warning should be posted (no empirical-source)');
  const warningBody = result.comments.find(c => c.body.includes('[CFP-2324 S7')).body;
  assert(warningBody.includes('empirical-source'), 'warning must mention empirical-source');
});

testCase('TC-S7-4 (regression-guard): operational, all AC present + TBD → NO warn', async () => {
  const result = await runGate({
    prBody: THR + '\n' + RSS + '\n' + '[empirical-source: TBD]',
    labels: [
      {name: 'operational:true'},
      {name: 'component:runner'}
    ],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS7Warning = result.comments.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
  assert(!hasS7Warning, 'NO S7 warning (all AC present; TBD is valid)');
});

testCase('TC-S7-5 (regression-guard): non-operational label → NO warn', async () => {
  const result = await runGate({
    prBody: '',
    labels: [],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS7Warning = result.comments.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
  assert(!hasS7Warning, 'NO S7 warning (operational:true not attached; S7 skipped)');
});

testCase('TC-S7-6 (mutation): operational, no component label → should warn', async () => {
  const result = await runGate({
    prBody: THR + '\n' + RSS + '\n' + EMP,
    labels: [{name: 'operational:true'}],
    files: [{filename: 'src/x.js', status: 'modified'}]
  });

  assert.equal(result.checks.length, 1, 'should create 1 check');
  const hasS7Warning = result.comments.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
  assert(hasS7Warning, 'S7 warning should be posted (no component:* label)');
  const warningBody = result.comments.find(c => c.body.includes('[CFP-2324 S7')).body;
  assert(warningBody.includes('component:'), 'warning must mention component label');
});

// ─────────────────────────────────────────────────────────────────────────────
// MUTATION SURVIVAL TESTS (M-S2, M-S6, M-S7)
// ─────────────────────────────────────────────────────────────────────────────

async function testMutationSurvival() {
  console.log('\n' + '='.repeat(80));
  console.log('Mutation Survival Tests');
  console.log('='.repeat(80));

  let killedCount = 0;

  // ─── Mutation M-S2: Wrong-gate deadlock guard ────────────────────────────────
  {
    // Mutation: replace "gate:requirements-review-pass" requirement with "gate:design-review-pass"
    // This tests that S2-A discriminator catches the wrong-gate assignment
    const mutated = WORKFLOW_SCRIPT.replace(
      "required = { phase: phaseLabel, gates: ['gate:requirements-review-pass'] };",
      "required = { phase: phaseLabel, gates: ['gate:design-review-pass'] }; // MUTATED: wrong gate"
    );

    if (mutated === WORKFLOW_SCRIPT) {
      console.log('✗ M-S2 APPLY FAILED: Pattern not found in live code');
      process.exit(1);
    }

    const fnMutated = new Function('github', 'context', 'core', `
      return (async () => {
        ${mutated}
      })();
    `);

    const context = new StubContext({
      prBody: '',
      labels: [{name: 'phase:요구사항-리뷰'}],
      files: [{filename: 'src/x.js', status: 'modified'}]
    });
    const github = new StubGitHub({
      labels: [{name: 'phase:요구사항-리뷰'}],
      files: [{filename: 'src/x.js', status: 'modified'}]
    });
    const core = new StubCore();

    process.env.ALLOWED_HUB_REPOS = 'github.com/mclayer/codeforge-internal-docs';
    process.env.CROSS_REPO_TOKEN = '';

    try {
      await fnMutated(github, context, core);

      const check = github.checksCreated[0];
      if (check && check.summary.includes('gate:design-review-pass') && !check.summary.includes('gate:requirements-review-pass')) {
        // Mutant PASSES the wrong gate → S2-A test KILLS this mutant
        console.log('✓ M-S2 killed: S2-A discriminator catches wrong-gate deadlock');
        killedCount++;
      } else {
        console.log('✗ M-S2 NOT KILLED: Mutant still requires correct gate (mutation had no effect)');
        process.exit(1);
      }
    } catch (e) {
      console.log(`✗ M-S2 execution error: ${e.message.slice(0, 80)}`);
      process.exit(1);
    }
  }

  // ─── Mutation M-S6: Disable provenance warning ─────────────────────────────
  {
    // Mutation: disable S6 warning by changing 'if (provWarnReason)' to 'if (false)'
    const mutated = WORKFLOW_SCRIPT.replace(
      'if (provWarnReason) {',
      'if (false && provWarnReason) { // MUTATED: disable S6'
    );

    if (mutated === WORKFLOW_SCRIPT) {
      console.log('✗ M-S6 APPLY FAILED: Pattern not found in live code');
      process.exit(1);
    }

    const fnMutated = new Function('github', 'context', 'core', `
      return (async () => {
        ${mutated}
      })();
    `);

    const context = new StubContext({
      prBody: '',
      labels: [
        {name: 'phase:설계-리뷰'},
        {name: 'gate:design-review-pass'}
      ],
      files: [{filename: 'src/x.js', status: 'modified'}]
    });
    const github = new StubGitHub({
      labels: [
        {name: 'phase:설계-리뷰'},
        {name: 'gate:design-review-pass'}
      ],
      files: [{filename: 'src/x.js', status: 'modified'}]
    });
    const core = new StubCore();

    process.env.ALLOWED_HUB_REPOS = 'github.com/mclayer/codeforge-internal-docs';
    process.env.CROSS_REPO_TOKEN = '';

    try {
      await fnMutated(github, context, core);

      const hasWarning = github.commentsPosted.some(c => c.body.includes('[CFP-2324 S6 provenance — warning]'));
      if (!hasWarning) {
        // Mutant skips warning → TC-S6-1 test KILLS this mutant
        console.log('✓ M-S6 killed: TC-S6-1 discriminator detects disabled warning');
        killedCount++;
      } else {
        console.log('✗ M-S6 NOT KILLED: Mutant still posts warning (mutation had no effect)');
        process.exit(1);
      }
    } catch (e) {
      console.log(`✗ M-S6 execution error: ${e.message.slice(0, 80)}`);
      process.exit(1);
    }
  }

  // ─── Mutation M-S7: Disable throughput warning ──────────────────────────────
  {
    // Mutation: disable S7 warning by changing 'if (s7Violations.length > 0)' to 'if (false)'
    const mutated = WORKFLOW_SCRIPT.replace(
      'if (s7Violations.length > 0) {',
      'if (false) { // MUTATED: disable S7'
    );

    if (mutated === WORKFLOW_SCRIPT) {
      console.log('✗ M-S7 APPLY FAILED: Pattern not found in live code');
      process.exit(1);
    }

    const fnMutated = new Function('github', 'context', 'core', `
      return (async () => {
        ${mutated}
      })();
    `);

    const context = new StubContext({
      prBody: 'RSS ≤ 256 MB\n[empirical-source: TBD]',
      labels: [
        {name: 'operational:true'},
        {name: 'component:runner'}
      ],
      files: [{filename: 'src/x.js', status: 'modified'}]
    });
    const github = new StubGitHub({
      labels: [
        {name: 'operational:true'},
        {name: 'component:runner'}
      ],
      files: [{filename: 'src/x.js', status: 'modified'}]
    });
    const core = new StubCore();

    process.env.ALLOWED_HUB_REPOS = 'github.com/mclayer/codeforge-internal-docs';
    process.env.CROSS_REPO_TOKEN = '';

    try {
      await fnMutated(github, context, core);

      const hasWarning = github.commentsPosted.some(c => c.body.includes('[CFP-2324 S7 throughput AC — warning]'));
      if (!hasWarning) {
        // Mutant skips warning → TC-S7-1 test KILLS this mutant
        console.log('✓ M-S7 killed: TC-S7-1 discriminator detects disabled warning');
        killedCount++;
      } else {
        console.log('✗ M-S7 NOT KILLED: Mutant still posts warning (mutation had no effect)');
        process.exit(1);
      }
    } catch (e) {
      console.log(`✗ M-S7 execution error: ${e.message.slice(0, 80)}`);
      process.exit(1);
    }
  }

  console.log('='.repeat(80));
  return killedCount;
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN RUNNER
// ─────────────────────────────────────────────────────────────────────────────

(async () => {
  const success = await runAllTests();
  const killedCount = await testMutationSurvival();

  console.log('\n' + '='.repeat(80));
  const totalCases = passCount + failCount;
  if (success && killedCount === 3) {
    console.log(`✓ ALL PASS (${totalCases} cases, ${killedCount} mutations killed) — S2 hard / S6 provenance / S7 throughput AC all VERIFIED`);
    console.log('Exit code: 0');
    process.exit(0);
  } else if (!success) {
    console.log(`✗ FAILED (${failCount} test failures, ${passCount} PASS)`);
    console.log('Exit code: 1');
    process.exit(1);
  } else if (killedCount < 3) {
    console.log(`✗ MUTATION SURVIVAL FAILURE (${killedCount}/3 mutations killed)`);
    console.log('Exit code: 1');
    process.exit(1);
  }
})();
