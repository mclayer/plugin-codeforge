---
kind: contract
contract_version: "1.0"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-test (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
authors:
  - CFP-42 sibling backfill (2026-04-29) — wrapper sibling 첫 작성, canonical 본문 verbatim mirror
---

# test_verdict v1 — Inter-plugin Contract

`codeforge-test` plugin → `codeforge` core (Orchestrator) 단방향 schema.

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-test/docs/inter-plugin-contracts/test-verdict-v1.md`: **canonical** (codeforge-test repo)
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — ADR-010 + CFP-24 marketplace sync 정책 동질)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- ADR-010 (본 contract 의 sibling sync 정책): codeforge wrapper repo `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`

`codeforge-test` plugin → `codeforge` core (Orchestrator) 단방향 schema. TestAgent 가 functional + performance subset 병렬 실행 후 self-write (phase comment + label transition) + Orchestrator 가 §10 FIX Ledger append 결정 (FAIL 시).

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① test_packet (subset enum, baseline path, scope globs, Story §8 Test Contract slice)
        ▼
codeforge-test plugin
  └─ TestAgent
        │
        │ ② subset 병렬 실행 (한 메시지에 dispatch):
        │   ├─ TestAgent(subset: functional) — 단위/통합/인프라
        │   └─ TestAgent(subset: performance) — baseline 비교
        │
        │ ③ Self-write (PASS 시):
        │    - mcp__github__add_issue_comment ([구현-테스트] prefix + 결과 표)
        │    - mcp__github__issue_write (phase:구현-테스트 → phase:보안-테스트 transition)
        ▼
        │ ④ test_verdict v1 typed output
        ▼
codeforge core (Orchestrator)
        │
        │ ⑤ Output 처리:
        │    - status=PASS → 보안 테스트 lane 진입
        │    - status=FAIL → §10 FIX Ledger append (Orchestrator 단독, fix-event v1 schema)
        │      → DeveloperPL/ArchitectPL 병렬 진단 (CFP-19 R4)
```

## 2. test_packet (Orchestrator → TestAgent)

```yaml
test_packet:
  contract_version: "1.0"
  story_key: <STORY_KEY>
  subsets:                          # 필수 — array, 최소 1개
    - functional                    # 단위/통합/인프라 (consumer overlay 가 러너 지정)
    - performance                   # baseline 비교 (consumer overlay 가 baseline 위치 지정)
  test_contract:                    # 필수 — Story §8 Test Contract markdown
    section: <markdown>
  consumer_overlay:                 # 필수 — runner/baseline 경로 (project.yaml 에서 도출)
    test_runner: <command>          # 예: "pytest -v"
    performance_baseline: <path>    # 예: ".perf-baseline.json"
    sequential_fallback: <bool>     # tests.performance.depends_on_functional
```

## 3. test_verdict (TestAgent → Orchestrator)

```yaml
test_verdict:
  contract_version: "1.0"
  story_key: <STORY_KEY>

  status: PASS | FAIL | ESCALATE_PACKET_INCOMPLETE

  results:                          # 필수
    functional:
      executed: <bool>
      pass_count: <int>
      fail_count: <int>
      failures:                     # array — FAIL 시 details
        - test_id: <string>
          file: <path>
          line: <int>
          message: <markdown>
    performance:
      executed: <bool>
      mean_delta_pct: <float>       # baseline 대비 % 차이 (음수 = 빨라짐)
      threshold_pct: 10             # 기본 — consumer overlay 가 변경 가능
      regression: <bool>            # mean_delta_pct > threshold_pct → true

  # Self-write 결과 audit
  writes_completed:
    phase_comment: <bool>           # [구현-테스트] prefix comment 게시
    phase_label_transitioned: <bool> # PASS 만 — phase:구현-테스트 → phase:보안-테스트

  # Orchestrator FIX 라우팅 input (FAIL 시)
  fix_routing_hint:                 # 선택 — null on PASS
    primary_failure: functional | performance
    suggested_cause:                # ArchitectPL 최종 판정 input
      - 설계                         # 성능 회귀가 baseline 자체 갱신 필요한 경우
      - 구현                         # 구현 결함이 명백한 경우
```

## 4. ESCALATE 처리

- `ESCALATE_PACKET_INCOMPLETE`: test_runner 명령어 부재, baseline 파일 부재 등 packet 불완전
- TestAgent 가 self-write 실패 (예: GitHub MCP timeout) 시 verdict 에 writes_completed=false + Orchestrator 가 fallback (DocsAgent 경유 — 단 ζ arc 후 DocsAgent 부재 시 ESCALATE)

## 5. v1 → v2 변경 가능성

- 새 subset 추가 (예: integration, e2e) — minor (v1.1, enum 추가)
- threshold_pct 정책 변경 — minor
- fix_routing_hint schema 확장 — minor

## 6. 본 contract 시점 동결 ATTRIBUTION

- 동결 일시: 2026-04-29 (CFP-38)
- 협업: Claude (codification) · CFP-31 parent §5.8
