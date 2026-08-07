---
kind: runbook
title: CFP-2889 실시간 측정 실행 Runbook
owner_story: CFP-2889
related_adrs: [ADR-101, ADR-111, ADR-169]
status: Active
date: 2026-08-06
---

# CFP-2889 실시간 측정 실행 Runbook

**담당**: InfraEngineerAgent (operator = 로컬 개발자 셸)

**목적**: CFP-2829 설계 착지 후 실제 Confluence v2 API 측정 실행으로 AC-11/AC-12/AC-13 4건을 정산한다. 테스트 계약 용 captured-golden 증거 + empirical-source provenance 레코드를 생성한다.

---

## §1. 사전 점검 목록

### 1.0 테스트 실행 사전 요건 (suite-A/B 공통)

- `pip install --user -r requirements.txt` (hypothesis 포함 — §8.8 fuzz/property 의존. 미설치 시 test collection 이 fail-loud exit 2 로 명시 중단, FIX iter2 F-CL2-01)

### 1.1 자격증명 설정

- **파일 위치**: `~/.claude/codeforge-scratch/atlassian-creds.env` (ADR-169 scratch TTL purge 정의역)
- **내용**:
  ```
  ATLASSIAN_API_TOKEN=<token>
  ATLASSIAN_USER_EMAIL=<email>
  ```
- **검증**: `test -f ~/.claude/codeforge-scratch/atlassian-creds.env && echo "OK" || echo "MISSING"`
- 부재 시: 1Password `Automation` vault 에서 retrieval, 신규 token 으로 provisioning (K-7)

### 1.2 테스트 페이지 Provisioning

- **Page ID 출처**: shell env var `CFP2829_TEST_PAGE_ID` (env 주입 우선 — stale id 위험 완화)
- **생성**: MCP `createConfluencePage` 사용
  - 제목 sentinel: `CFP-2889-THROWAWAY-<YYYYMMDD>` (예: `CFP-2889-THROWAWAY-20260806`)
  - Ancestor: 지정하지 않음 — parentId 미지정 시 서버가 space homepage(1867943) 직속으로 자동배정. 이 space 는 homepage 가 곧 mirror IA tree 루트라 "mirror IA tree 밖" 배치는 **구조적 달성 불가** (CFP-2889 구현 C 실측 정정)
  - 실제 보장 = **deny-set 미소속 ∧ sentinel 제목 ∧ homepage 직속 형제** — 기계 게이트는 deny-set + sentinel 2축(조상 관계 미검사)
  - Standalone throwaway = 안전한 삭제 범위
- **보유 주의**: 테스트 페이지는 **영구 잔존** — 수동 UI 삭제만 가능 (MCP tool 부재)

### 1.3 환경 설정

실행 전 환경 설정:
```bash
export ATLASSIAN_API_TOKEN=<token>
export ATLASSIAN_USER_EMAIL=<email>
export CFP2829_TEST_PAGE_ID=<page-id>
```

**별도 준수 환경 변수** (승인 gate 와 별개):
```bash
export CBL_SKIP_ISSUE_CREATE=1  # 측정 중 Jira issue auto-creation 미실행
```

---

## §2. 계획 모드 → 승인 (필수 gate)

### 2.1 건조 회계 투영 (Dry Accounting Projection)

**live write flag 없음** — 사전 예측만:
```bash
python scripts/confluence_backward_measure.py --all
```

**출력**: 회계표 표시:
- 예상 POST/PUT 시도: 논리 카운트 10 (§3.10 표 W1–W5 기준)
- 재시도 contingency: +10 max (429 제한 write 당 1회 재시도)
- **총 write 예산**: ≤20 (cap 불변식)
- DELETE 개수: 전체 property 회수 (chunk 2 + manifest 1 + basis 2 + encoding 2 + control 1 = ~8 properties)
- 용량 여유: 논리 10 / 최악(전 write 429 1회 재시도) 20 ≤ cap 20 — 무-429 시 여유 10
- Page 신원 확인: deny-set 검증 (ia-tree roots + sentinel 양성 확인)

**plan 모드 회계표는 실행 전 ground-truth 재산출이다** — plan 변경 시 새로운 회계표 + 새로운 승인 필요.

### 2.2 승인 gate (1 run = 1 승인)

Operator(사람)가 Orchestrator 경유 사용자 세션에서 명시적 승인을 얻는다:
- plan 모드 회계표 검토
- write 예산 수용 가능 확인
- **run 당 1회만 승인** (재사용 금지 — 재측정 = 새로운 승인 루프)
- 세션 중 plan 변경 시 → 새로운 승인 필요

---

## §3. 측정 실행 (`--confirm-live-write`)

### 3.1 실행 호출

```bash
python scripts/confluence_backward_measure.py --confirm-live-write --all
```

**필수 사전조건** (4-AND 전부):
- `--confirm-live-write` flag 존재
- `ATLASSIAN_API_TOKEN` + `ATLASSIAN_USER_EMAIL` creds 파일에 존재
- `CFP2829_TEST_PAGE_ID` env 주입 (creds 파일 stale id 아님)
- `¬CFP2829_MEASURE_SKIP_WRITE` (skip-write flag 부재)

**Fail-closed**: 어떤 사전조건도 부재 → write 전 hard abort.

### 3.2 Kill-Switch 7종 abort trigger (K-1 ~ K-7)

| ID | Trigger | Action | Event Log | Cap 영향 |
|---|---|---|---|---|
| K-1 | HTTP 401 Unauthorized | 즉시 전역 abort | `abort` 사유: K-1 + 인증 실패 상세 | 증가: 0 |
| K-2 | Write cap 20 초과 | 21번째 write 시도 hard stop | `abort` + orphan registry snapshot (NDJSON) | 이미 cap |
| K-3 | 3+ 연속 write 실패 (429 아님) | abort round | `abort` + retry backoff 소진 | per-attempt count |
| K-4 | 429 누적 ≥3 회 | 즉시 abort (rate-limit abort — 의도적 유발 회피) | `abort` + 429-상태 상세 (RateAbortError) | per write |
| K-5 | Page 신원 불일치 | `CFP2829_TEST_PAGE_ID` resolve ia-tree deny-set 실패 시 write 거부 | `abort` + 신원 drift 상세 | 0 |
| K-6 | Emit deny-scan 실패 | NDJSON 내 secret 감지 시 full record assembly abort | `abort` + deny-scan hit 상세 + field drop | attempt count |
| K-7 | Creds preflight 실패 | 파일/env 점검 실패 시 write 전 abort | `abort` + preflight 에러 (auth/파일 미발견) | 0 |

**Semantics**: `abort` event contains:
- Reason (K-1 through K-7)
- Last successful write details (if any)
- Orphan registry snapshot (property-id list, registry-independent fresh listing)
- Exit code: non-zero

### 3.3 재시도 정책

- **Write 범위화**: write 당 1회 재시도 (429 HTTP status 한정)
- **서버 Retry-After 헤더**: fixed backoff 보다 우선
  - 응답에서 `Retry-After` parse (초 또는 HTTP-date)
  - 기준: 응답 `Date` 헤더 (로컬 clock 아님)
  - Clamp: 단일 write 당 max 60초
  - 누적: 120초 total abort (2× 안전 margin)
  - Fallback: 헤더 부재 시 1초
- **Exception/timeout 재시도**: 금지 (도달 불확정 상태 = 오염 위험)
- **429 발생 post-retry**: abort (K-4)
- **HTTP-date 파싱 fallback** (RFC 9110 §10.2.3): `Retry-After` 가 date form 이면 → parse + clamp, numeric 형식 가정 금지

### 3.4 Write 회계

- **Counter 객체**: `WriteAccounting` (measure.py harness 소유)
- **증가 지점**: retry loop 내부, HTTP 송신 전 (retry 내부)
- **GET 요청**: 별도 집계 (rate-limit 추적, cap 범위 밖)
- **강제**: cap=20 POST+PUT 한정, DELETE = soft-ceiling 40 (orphan 회수, cap 면제)

---

## §4. 유령 Property 회수 (3-Step)

### 4.1 회수 사전조건

- Manifest 최우선 DELETE (reader fail-close 회복)
- Chunk DELETE **역순** (LIFO stack 의미론)
- Registry 독립 검증 step (Step 5, reconcile)

### 4.2 삭제 순서

**Step 1: Manifest Property 삭제** (resolve by property-id)
```bash
# 실제 코드에서 manifest_property_id 는 GET /?key=codeforge.sync.canonical.__manifest 로 resolve
curl -X DELETE \
  "https://mclayer.atlassian.net/wiki/api/v2/pages/<page-id>/properties/<manifest-property-id>" \
  -H "Authorization: Basic <base64-auth>"
# 예상: 200, 204, 또는 404 (멱등)
```

**Step 2: Chunk Property 삭제 (역순)**
```bash
# 각 chunk 키 `codeforge.sync.canonical.__chunk_k` (k = N-1, N-2, ..., 0) 에 대해:
curl -X DELETE \
  "https://mclayer.atlassian.net/wiki/api/v2/pages/<page-id>/properties/<chunk-property-id>" \
  -H "Authorization: Basic <base64-auth>"
```

**Step 3: 측정 기초 Property 삭제**
```bash
# basis_property_id 는 GET 으로 resolve 후 id 기반 DELETE
```

### 4.3 Registry 독립 검증

**전체 property 열거** (no-filter) 실행으로 잔존 0 확인:
```bash
curl -X GET \
  "https://mclayer.atlassian.net/wiki/api/v2/pages/<page-id>/properties" \
  -H "Authorization: Basic <base64-auth>"
```

- 열거: no-filter 전량 (필터는 `codeforge.sync.canonical.*` 키 prefix 로 식별)
- 예상: empty result set
- pagination 존재 시: 모든 페이지 반복 (설계 시점 cap 미지수)
- 기록: `reconcile_unknown` (열거 실패) 또는 `RECONCILED` (청결 확인)

---

## §5. 정산 확인 (Step R)

### 5.1 기준선 열거 (Baseline Enumeration)

**write 전**: property-id 목록 capture (live API):
```
S_baseline = set of 전체 page 의 (key, property-id) — no-filter 전량
```

### 5.2 실제 열거 (Actual Enumeration)

**cleanup 완료 후**: 재열거:
```
S_actual = set of 전체 page 의 (key, property-id) — no-filter 전량
```

### 5.3 정산 판정 (Reconciliation Verdict)

- **RECONCILED**: `S_actual ∖ S_baseline == ∅` (신규 property 전부 회수됨)
- **DRIFT**: `S_actual ∖ S_baseline ≠ ∅` (유령 잔존 — 조사 필요)
- **reconcile_unknown**: 열거 실패 (재시도 listing, 에러 검사)

**불변식**: cleanup 이 orphan-잔존을 성공으로 인정하지 않음 (reconcile_unknown ≠ "OK").

---

## §6. 산출물

### 6.1 Captured Evidence (Deny-Scan 게이트)

**위치**: `~/.claude/codeforge-scratch/` (run 중)

**파일** (3+1):
1. **property_envelope_shape_golden.json**: 단건 PropertyEnvelope template (upsert 용)
2. **property_list_shape_golden.json**: list 응답 wrapper (resolve `?key=` + no-filter 열거 골격, pagination 필드 유무)
3. **basis-golden.json**: 수치만 (utf8_bytes, ascii_bytes, delta bytes, status, 헤더명 세트, 경계 probe 결과)
4. **run-events.ndjson**: Write 시도 + abort 이벤트 + cleanup 레코드 + 정산 결과

### 6.2 Provenance 주석

captured 파일마다 반드시 포함:
```
[empirical-source: <KST ISO8601 timestamp>, <method+endpoint>, <http_status>, tenant=redacted, run_id=<uuid>]
```

**예**:
```
[empirical-source: 2026-08-06T05:00:00+09:00, PUT /wiki/api/v2/pages/123456/properties, 200, tenant=redacted, run_id=abc-def-123]
```

### 6.3 Deny-Scan Gateway

`tests/fixtures/cfp_2889/` 에 golden 커밋 전:
1. 전체 NDJSON 파일에 deny-scan 실행
2. hit 시: **abort**, secret 누출 조사
3. clear 시: commit 진행

### 6.4 Post-Run Archive

deny-scan gate 통과 후:
- cleared 파일을 **`tests/fixtures/cfp_2889/`** 로 복사 (persisted golden)
- `~/.claude/codeforge-scratch/` 사본 폐기 (ADR-169 TTL purge, commit 후 적격)

---

## §7. 정직 선언

### 7.1 테스트 페이지 영구 잔존

**테스트 페이지는 자동화로 삭제되지 않는다.**
- MCP `deleteConfluencePage` tool 부재 (Atlassian API 한계)
- **수동 삭제 필요**: operator 가 measurement 완료 후 Confluence UI 로 삭제
- 추적: runbook 사후평가에 test page ID 기록 (이력 추적용)

### 7.2 Property 완전 회수 가능

**예상**: harness 가 생성한 모든 property 는 cleanup phase 에 삭제된다.
- **예외**: K-series abort 가 cleanup 중 발생 시 orphan registry snapshot 이 emitted (step R re-lists via API)
- **보증**: step R registry 독립 열거 = orphan 잔존 0 (API state = source of truth)

### 7.3 Token 전권 blast radius

**Creds token scope**: `mclayer.atlassian.net` 전체 Confluence write 권한
- **위험 수용**: 1회성 run, 단일 throwaway page, 즉시 cleanup
- **완화**: deny-scan + 수동 page ID 확인 + cap 불변식

### 7.4 터미널 출력 게이트 (emit choke-point 경유)

**Stdout 채널 제약**: 모든 터미널 출력은 deny-scan choke-point(T-12 제어) 를 경유한다.
- 구체적 의미: stdout 자체는 emit choke-point 로 게이트됨
- **Operator 주의**: 터미널 출력을 다른 채널(Slack, email, PR 댓글)에 복붙할 때는 deny-scan 재스캔 없이 복붙하지 말 것 (사람 경로 = choke-point 미경유)
- 안전 신호: stdout "deny-scan OK" = 공유 안전

---

## §8. Infra-D1 적용가능성 (설계리뷰 정산)

**판정**: `CFP2829_TEST_PAGE_ID` env-var 은 **N/A** (infra-resource-baseline.yaml 선언 불필요)

**근거** (3-AND):
1. Infra-signal 스캐너 suffix enum (`scripts/lib/check_infra_resource_drift.py` L39-40) 은 `_ID` suffix 를 drift scope 에서 제외
2. Consumer (wrapper-self) infra-resources baseline = main 기존재 (신규 infra entrypoint 0)
3. Baseline YAML 관련 entry = 0 (선언할 resource 없음)

**처분**: baseline 편집 action 불필요 — N/A 판정 은 설계리뷰 iter1 준수로 문서화 (P3 gate 해소)

---

## §9. 컨테이너 배포 N/A

**실행 환경**: 로컬 개발자 셸 (고정)
- CFP-2829 change-plan §7.4.6 조건: "container N/A" 는 **self-hosted runner 통합 미적용** 시 유지
- 상태: runner 통합 범위 밖
- **재평가 trigger**: 측정이 CI/self-hosted runner 로 이전 시 본 절 재검토 (신규 적용가능성 판정)

---

## 부록: 문제해결

| 문제 | 진단 | 조치 |
|---|---|---|
| K-1 (401) | Token 만료 또는 email 불일치 | 1Password 에서 PAT 갱신, creds 파일 재provision |
| K-2 (write 21 에서 cap hit) | 예산 초과 시나리오 | write probe 축소 또는 새로운 승인 루프로 2번째 run |
| K-4 (429 반복) | 속도 제한 소진 | Retry-After 대기, 내일 staggered re-run 고려 |
| K-5 (page-id 불일치) | Test page deny-set 미포함 | page ID 확인 + 필요 시 재생성, ia-tree roots 열거 |
| K-6 (deny-scan 실패) | NDJSON 내 secret 감지 | token scope 감사, 파일 단독 deny-scan 실행 |
| K-7 (creds 파일 미발견) | Preflight gate | `~/.claude/codeforge-scratch/atlassian-creds.env` provision |
| Reconcile drift | Cleanup 미완료 또는 중단 | no-filter 열거로 수동 재확인; error log 검사 |

---

## 참고자료

- **Change Plan**: `wrapper/change-plans/2026-08-04-cfp-2889-live-measurement-settlement.md` §3.10 (결정 13 — 운영 규율)
- **부모 Story**: `wrapper/stories/CFP-2829.md` (backward-sync 엔진 검증)
- **Golden 표준**: `tests/fixtures/cfp_2889/` (captured evidence archive)
- **기존 Runbook**: `scripts/CONFLUENCE_BACKWARD_MEASURE_RUNBOOK.md` (보완 offline 가이드)
- **Atlassian API**: developer.atlassian.com/cloud/confluence/rest (v2 properties CRUD, list pagination)
