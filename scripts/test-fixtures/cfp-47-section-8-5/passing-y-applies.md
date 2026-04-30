---
slug: test-passing-y-applies
status: Active
authors: [test]
---

# Test passing fixture — CFP-47 §8.5 1+ Y + §8.5.1 본문

### §1. 목적
fixture passing case — applicability 1+ Y + §8.5.1 본문 충족.

### §2. 현재 구조
N/A — fixture 단순화.

### §3. 도입할 설계
N/A — fixture 단순화.

### §4. API 계약
N/A — fixture 단순화.

### §7. 보안
N/A — fixture 비대상.

### §8. Test Contract

#### §8.1 커버리지 계획
N/A — fixture.

#### §8.2 경계 조건
N/A — fixture.

#### §8.3 Perf Baseline
N/A — 성능 영향 없음.

#### §8.4 N/A 권한
applicable — §8 본문 작성됨.

#### §8.5 Stateful / restart invariant tests (CONDITIONAL — CFP-47 / ADR-015)

##### §8.5.0 Applicability decision (필수)

| 적용 조건 | Y/N | 근거 1줄 (substantive) |
|---|:-:|---|
| Long-running connection | Y | WebSocket subscription 으로 6시간 sustained reception |
| Stateful in-memory cache | N | 본 Story 는 cache touch 없음 — read-only API |
| Background worker | N | 본 Story 는 sync request handler 만 — async worker 없음 |
| Process restart-aware system | N | 본 Story 는 stateless handler — in-flight 작업 없음 |

##### §8.5.1 Long-running invariant tests

- 테스트 대상 invariant: WebSocket sequence number 정합성 (cumulative gap detection)
- 부하 시나리오: 6시간 sustained subscription, 1Hz heartbeat
- assertion 주기: 매 60초
- tolerance: gap 0
- framework: pytest-anyio + asyncio long-running fixture

### §10. ADR 정합성
N/A — fixture.

### §11. 데이터 마이그레이션
N/A — fixture.
