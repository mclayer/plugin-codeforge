---
slug: test-failing-y-no-section
status: Active
authors: [test]
---

# Test failing fixture — CFP-47 §8.5 1+ Y but §8.5.1 본문 없음

### §1. 목적
fixture failing case — Y 1개 인데 §8.5.1 부재.

### §2. 현재 구조
N/A — fixture.

### §3. 도입할 설계
N/A — fixture.

### §4. API 계약
N/A — fixture.

### §7. 보안
N/A — fixture.

### §8. Test Contract

#### §8.5 Stateful / restart invariant tests (CONDITIONAL)

##### §8.5.0 Applicability decision

| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| Long-running connection | Y | WebSocket subscription 보유 |
| Stateful in-memory cache | N | cache 없음 |
| Background worker | N | worker 없음 |
| Process restart-aware system | N | 무관 |

(Y 1개 인데 §8.5.1 본문 부재 — lint FAIL 예상)

### §10. ADR 정합성
N/A — fixture.

### §11. 데이터 마이그레이션
N/A — fixture.
