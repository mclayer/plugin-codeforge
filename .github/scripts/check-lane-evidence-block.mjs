// check-lane-evidence-block.mjs
// CFP-490 Phase 2 — Lane Evidence block duplicate heading analyzer (extraction from lane-evidence-check.yml 5a guard)
//
// Purpose: PR body 안 `## Lane evidence` heading 의 collision (1회 초과 등장) 을 분석하고
//   tie-break case A / B / C 식별 + 어느 heading 이 valid 7-row format 인지 명시.
//
// Invariant (ADR-031 §결정 2 정합):
//   - heading 이 정확히 1회만 허용 (PASS path)
//   - heading 이 2회 이상 등장 시 항상 `action_required` (CFP-465 strict invariant 보존 — Option A)
//
// Tie-break cases:
//   - Case A: 1 valid heading (나머지는 mismatch) → valid heading 채택 + 나머지 삭제 권고
//   - Case B: 0 valid heading (모두 mismatch) → 1개만 남기고 valid 7-row 형식으로 정정 권고
//   - Case C: 2+ valid heading → ADR-031 invariant 위반 — 임의 1개 유지 + 나머지 삭제 권고
//
// Effective date: CFP-490 merge 이후 신규 Phase 2 PR 부터 (ADR-031 §결정 5 retroactive 미처리 정합).
//
// Self-application boundary (ADR-005 review 결과):
//   본 .mjs 는 .github/scripts/ 단방향 (templates 미러 없음) — yaml workflow 의 byte-identical
//   self-app invariant 와 별개 channel (Story §8.3 결정).

const HEADING_REGEX = /^## Lane evidence\s*$/gm;
const ROW_REGEX_SOURCE = /^-\s*([^:]+):\s*(PASS|SKIPPED|FIX|ESCALATED|BYPASS)/.source;
const REQUIRED_LANES = ['요구사항', '설계', '설계-리뷰', '구현', '구현-리뷰', '구현-테스트', '보안-테스트'];

/**
 * PR body 안 `## Lane evidence` heading collision 을 분석한다.
 *
 * @param {string} body  PR description (markdown)
 * @returns {null | {
 *   case: 'A' | 'B' | 'C',
 *   summary: string,            // GitHub Checks `output.summary` 용 markdown
 *   total: number,              // heading 등장 횟수
 *   valid_heading_idx: number | null,   // 1-indexed (Case A 만 단일 값, Case B null, Case C 첫 valid)
 *   valid_idx_list: number[],   // 1-indexed valid heading 목록
 *   invalid_idx_list: number[]  // 1-indexed invalid heading 목록
 * }}
 *   - duplicate 미발생 (heading 0 or 1회) → null (caller 가 다음 step 진입)
 *   - duplicate 발생 → tie-break 정보 객체
 */
export function analyzeDuplicateHeadings(body) {
  const matches = [...body.matchAll(HEADING_REGEX)];
  if (matches.length <= 1) return null;

  // 각 heading 의 content boundary 추출 — heading N 의 content = heading N 끝 ~ heading N+1 시작 (또는 body end)
  const contents = matches.map((m, i) => {
    const start = m.index + m[0].length;
    const end = (i + 1 < matches.length) ? matches[i + 1].index : body.length;
    return body.substring(start, end);
  });

  // 각 content 의 7-row 의무 lane 모두 capture 여부 분석
  const validResults = contents.map(c => {
    const found = new Set();
    const rowRegex = new RegExp(ROW_REGEX_SOURCE, 'gm');
    let row;
    while ((row = rowRegex.exec(c)) !== null) {
      found.add(row[1].trim());
    }
    return REQUIRED_LANES.every(l => found.has(l));
  });

  const validIdxList = validResults
    .map((v, i) => v ? i + 1 : null)
    .filter(x => x !== null);
  const invalidIdxList = validResults
    .map((v, i) => v ? null : i + 1)
    .filter(x => x !== null);

  let caseId;
  let summary;
  const validHeadingIdx = validIdxList[0] || null;

  if (validIdxList.length === 1) {
    caseId = 'A';
    const validIdx = validIdxList[0];
    const validHeadingLine = matches[validIdx - 1].index;
    summary =
      `## Lane evidence 블록 중복 감지 — body 에 ${matches.length} 회 등장 (1회만 허용, ADR-031 §결정 2).\n\n` +
      `**Case A**: heading ${validIdx} (1-indexed) 의 content 가 valid 7-row 형식. ` +
      `나머지 heading [${invalidIdxList.join(', ')}] 삭제 권고.\n\n` +
      `> ## Lane evidence (body offset 부근 ${validHeadingLine})\n\n` +
      `**Fix**: heading [${invalidIdxList.join(', ')}] 를 PR description 에서 삭제하고 push.\n\n` +
      `정책: ADR-031 §결정 2 — 1회 heading 의무. CFP-465 strict invariant 보존 (CFP-490).`;
  } else if (validIdxList.length === 0) {
    caseId = 'B';
    summary =
      `## Lane evidence 블록 중복 감지 — body 에 ${matches.length} 회 등장 (1회만 허용, ADR-031 §결정 2).\n\n` +
      `**Case B**: ${matches.length} heading 모두 7-row 형식 mismatch (table format / placeholder / empty 등). ` +
      `1개 heading 만 남기고 content 를 valid 7-row 형식으로 정정 후 push 권고.\n\n` +
      `valid 형식 (\`<lane>: <verdict>\`):\n` +
      '```\n' +
      '## Lane evidence\n' +
      REQUIRED_LANES.map(l => `- ${l}: PASS`).join('\n') + '\n' +
      '```\n\n' +
      `lane: ${REQUIRED_LANES.join(' / ')}. ` +
      `verdict: PASS / SKIPPED / FIX / ESCALATED / BYPASS.`;
  } else {
    caseId = 'C';
    summary =
      `## Lane evidence 블록 중복 감지 — body 에 ${matches.length} 회 등장 (1회만 허용, ADR-031 §결정 2).\n\n` +
      `**Case C**: ${matches.length} heading 중 ${validIdxList.length}개 (heading [${validIdxList.join(', ')}]) 모두 valid 7-row 형식. ` +
      `정책상 1개만 허용 — 임의 1개 유지 + 나머지 삭제 권고. ` +
      `(ADR-031 §결정 2 invariant — collision 자체가 위반)\n\n` +
      `**Fix**: heading [${validIdxList.slice(1).concat(invalidIdxList).join(', ')}] 를 PR description 에서 삭제하고 push.`;
  }

  return {
    case: caseId,
    summary,
    total: matches.length,
    valid_heading_idx: validHeadingIdx,
    valid_idx_list: validIdxList,
    invalid_idx_list: invalidIdxList
  };
}

// Re-export constants for test introspection
export const __TEST_INTERNALS__ = {
  HEADING_REGEX_SOURCE: HEADING_REGEX.source,
  ROW_REGEX_SOURCE,
  REQUIRED_LANES
};
