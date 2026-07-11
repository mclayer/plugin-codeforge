---
kind: contract
contract_version: "2.3"
status: Active
related_plugins:
  - codeforge (wrapper, consumer + IntegrationTestAgent spawn 주체)
  - codeforge-test (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008  # Inter-plugin Contract Versioning
  - ADR-010  # Inter-plugin Contract Sibling Sync
  - ADR-055  # Integration Test Lane Policy (본 v2 carrier)
  - ADR-048  # Amendment 1 — codeforge-test 통합테스트 전용 부활
  - ADR-148  # G2 지속-liveness soak 게이트 — soak_liveness_results additive v2.2→v2.3
authors:
  - CFP-367 (2026-05-10) — test-verdict v1 → v2 (integration lane 전용 패킷, ADR-055)
  - CFP-371 (2026-05-10) — v2 → v2.1: Epic-level 필드, story_attribution, env_missing, deployability_verified
  - CFP-373 (2026-05-10) — v2.1 → v2.2: story_key→story_keys[] 복수 attribution + attribution_confidence
  - CFP-2613 (2026-07-12) — v2.2 → v2.3: soak_liveness_results 독립 top-level optional object 추가 (지속-liveness soak verdict, ADR-148 §결정9). additive MINOR (기존 필드 무변경)
supersedes: test-verdict-v1.md
carrier_story: CFP-367
date: 2026-05-10
---

# test-verdict-v2 — Integration Lane 결과 패킷 (Canonical)

**CANONICAL SSOT**: 본 파일이 원본. wrapper sibling: `mclayer/plugin-codeforge:docs/inter-plugin-contracts/test-verdict-v2.md`

**상위 SSOT 위치**: 본 파일이 단일 원본 (canonical) — CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5 가 lane canonical ↔ wrapper mirror 이중체계를 폐지 (monorepo 통합 S1 후속). frontmatter 의 ADR-010 인용은 historical (sibling sync 정책 Superseded — ADR-010 Amendment 5). versioning 룰 = ADR-008 불변.

## 상태

Active — CFP-373 (2026-05-10)

test-verdict-v1 Archived. v1 → v2 이유: codeforge-test 통합테스트 전용 부활(ADR-048 Amendment 1)로 integration lane 전용 결과 패킷 스키마 신설.

v2 → v2.1 이유: CFP-371 / ADR-055 Amendment 2 — per-Story → Epic-level 실행 구조 전환. epic_key, stories_in_scope, responsible_stories, deployability_verified, suite_type, env_missing 필드 추가.

v2.1 → v2.2 이유: CFP-373 — `failures[].story_key: string|null` → `story_keys: list[string]` + `attribution_confidence` 추가. 단일 baseline failure가 복수 Story 변경에 기인할 수 있는 현실 반영. ADR-008 SemVer MINOR bump.

v2.2 → v2.3 이유: CFP-2613 (Epic CFP-2602 G2) / ADR-148 §결정9 — `soak_liveness_results` 독립 top-level optional object 추가. IntegrationTest Deployability soak step 이 `daemon_type: long_running_daemon` 데몬의 지속-liveness(프로세스 생존 ∧ terminal-sink monotone 전진)를 관측한 결과를 실어 반환. 기존 `deployability_verified` boolean 하위 nesting = type change = MAJOR → 회피(독립 top-level optional 로 편성). 기존 필드·의미 전원 무변경 = backward-compatible (soak 미적용 Epic 은 필드 자체 부재). ADR-008 SemVer MINOR bump.

## 스키마

```yaml
test_verdict:
  version: "2.3"
  epic_key: string              # "CFP-NNN" — Epic 단위 실행
  stories_in_scope: list        # ["CFP-NNN-S1", "CFP-NNN-S2"] — 이번 Epic 포함 Story key 목록
  lane: "integration"           # 고정값
  executed_at: ISO8601
  runner: "IntegrationTestAgent"
  trigger: "epic_complete"      # 고정값 — Epic 하위 전체 Story CI gate PASS 후 1회

  suite_summary:
    baseline_total: int         # Baseline Suite 전체 테스트 수 (이전 Epic까지 누적)
    baseline_passed: int
    baseline_failed: int
    story_total: int            # Story Suite 전체 테스트 수 (이번 Epic §8.6 기반 자동생성)
    story_passed: int
    story_failed: int
    skipped: int                # docker-compose 환경 미구성 or §8.6 면제 Story

  dynamic_test_compliance: boolean     # 내부 컴포넌트 정적 mock 미사용 여부
  docker_compose_used: boolean         # docker-compose.test.yml 실행 여부
  deployability_verified: boolean      # .env 키 + container 기동 + DB 연결 + health check 통과

  failures:                     # failed > 0 인 경우에만 존재
    - test_id: string
      test_path: string         # "tests/integration/stories/CFP-NNN/CFP-NNN-S1/test_order_flow.py::test_bithumb_order_create"
      suite_type: "baseline" | "story"
      story_keys: list[string]  # suite_type=story → [해당 Story key] (단일 항목)
                                # suite_type=baseline → blame 분석 결과 목록 (분석 전 [] 가능)
                                # 단일 baseline failure가 복수 Story 변경에 기인할 수 있으므로 list
      attribution_confidence: "definite" | "inferred" | "unknown"
                                # definite: STORY_KEY 메타데이터 or §8.6 related_components 직접 매핑
                                # inferred: static import 분석으로 추론
                                # unknown: blame 불가 (story_keys=[])
      failure_type: "regression" | "new_test" | "infra_setup" | "env_missing" | "soak_liveness"
      error_summary: string     # 500자 이내

  responsible_stories: list     # FIX 대상 Story key 목록 e.g. ["CFP-NNN-S1"] (failures story_keys 합집합)

  pl_recommendation: "PASS" | "FIX" | "ESCALATE_PACKET_INCOMPLETE"
  # PASS: 전체 suite green + deployability_verified true. responsible_stories: []
  # FIX: 실패 존재 → responsible_stories 목록 Story FIX loop
  # ESCALATE_PACKET_INCOMPLETE: docker-compose 미실행 or §8.6 누락

  notes: string | null

  soak_liveness_results:            # optional — soak 미적용 Epic 은 필드 부재 (v2.3, ADR-148 §결정9)
    survival: bool                  # exit==0 ∧ RestartCount==0 (boot-grace 경과 후)
    sink_monotone_progressed: bool  # terminal-sink net non-decreasing ∧ net 순증
    soak_verified: bool             # survival ∧ sink_monotone_progressed (merge-block key)
    liveness_declared: bool         # 표면 A 선언 존재 여부
    soak_duration_s: int
    soak_duration_basis: manifestation | floor
    boot_grace_s: int | null
    honest_ceiling_ack: bool        # "완전 봉인 아님" 정직 명시 (INV-D6/AC-9)
    # perf 필드(p50/p95/p99/throughput/rss) 물리 배제 — F2/§결정10
```

## FIX 루프 연동

`pl_recommendation: FIX` 시 `responsible_stories` 의 각 Story에 대해 FIX loop 진입:

| failure_type | 1차 가정 | FIX 담당 |
|---|---|---|
| `regression` | 구현 원인 (기존 코드 regression) | DeveloperPL → ArchitectPL 판정 |
| `new_test` | 구현 원인 (신규 시나리오 미구현) | DeveloperPL → ArchitectPL 판정 |
| `infra_setup` | 인프라 원인 (docker-compose 누락/오류) | InfraEngineerAgent 직접 수정 |
| `env_missing` | 환경 설정 누락 (.env 키 / 컨테이너 설정) | InfraEngineerAgent or 사용자 action |
| `soak_liveness` | 데몬 지속-liveness 실패 (지연 크래시 / terminal-sink 동결 — soak step, ADR-148 §결정5) | DeveloperPL → ArchitectPL 판정 |

### Baseline 실패 시 story_keys blame 절차

`suite_type: "baseline"` 이고 `story_keys: []` (빈 목록) 인 경우 3-tier 순서로 컴포넌트 경로 추출:

**Tier 1 (§8.6 related_components)**:
- 실패 테스트 `test_path` → 해당 scenario → `coverage_targets[].related_components[]` 조회
- related_components 존재 시 해당 경로 목록을 blame 대상으로 사용

**Tier 2 (static import 분석)**:
- related_components 미제공 시 실패 테스트 파일의 import 구문 정적 분석
- `from src.XXX import ...` / `import src.XXX` 패턴에서 실제 파일 경로 추출

**Tier 3 (ESCALATE)**:
- Tier 1·2 모두 실패 시 `story_keys: []`, `attribution_confidence: "unknown"` + ArchitectPL 에스컬레이션 메모

컴포넌트 경로 확정 후:
```bash
git log --oneline --follow -- <컴포넌트 경로>
```
가장 최근 변경 commit의 Story key들 → `story_keys` 목록에 추가 → `responsible_stories` union 갱신

### ESCALATE_PACKET_INCOMPLETE 처리

- `docker_compose_used: false` → InfraEngineerAgent에게 `docker-compose.test.yml` 작성 의뢰 후 재실행
- `stories_in_scope` 내 §8.6 없는 Story → TestContractArchitectAgent에게 §8.6 작성 의뢰 후 재실행
- `deployability_verified: false` (docker-compose 실행됐으나 health check 실패) → `failure_type: infra_setup` 으로 FIX 분기 (ESCALATE 아님)

## soak_liveness_results (v2.3 — 지속-liveness soak, ADR-148)

`daemon_type: long_running_daemon` 데몬 Story 에 대해 IntegrationTest Deployability soak step 이 실행됐을 때만 존재하는 **독립 top-level optional object** (soak 미적용 Epic 은 필드 자체 부재 = backward-compatible). 판정 축:

| 필드 | 의미 |
|---|---|
| `survival` | `exit==0 ∧ RestartCount==0` (boot-grace 경과 후 관측) |
| `sink_monotone_progressed` | terminal-sink net non-decreasing ∧ net 순증 (flat/역행 = false) |
| `soak_verified` | `survival ∧ sink_monotone_progressed` (양축 AND) |
| `liveness_declared` | 표면 A 선언(daemon_type + sink_probes[]) 존재 여부 |
| `soak_duration_s` | soak 구동 시간(초) |
| `soak_duration_basis` | `manifestation`(발현조건 임계 도달) \| `floor`(duration floor fallback) |
| `boot_grace_s` | exit/restart 카운트 시작 유예(초) — nullable |
| `honest_ceiling_ack` | "N분 관측 = 증명, 완전 봉인 아님" 정직 명시 (INV-D6/AC-9) |

- **merge-block key = `soak_verified == false`** (= `survival == false ∨ sink_monotone_progressed == false`) — 양축 AND 정합. 생존만 block key 로 삼으면 sink-freeze(생존 ∧ flat, AC-7) block 누락 → 생존·sink 양축 모두 gate. `soak_verified == false` 시 producer 는 `failure_type: soak_liveness` 로 FIX 분기.
- **perf 필드 물리 배제**: p50/p95/p99/throughput/rss 등 성능 metric 은 schema 에 부재 — soak verdict = liveness 스코프 고정(성능 metric = deploy-review 부활선, ADR-121 §결정10 금지).
- **정직 천장(`honest_ceiling_ack`)**: soak PASS = N분 생존·sink 전진 관측 증명일 뿐 무한 미래·모든 크래시 모드 봉인 아님. 잔여 catch-owner = post-deploy consumer 실-의존성 smoke (ADR-121 §결정8 기존 smoke cross-ref).
- **필드 정의는 additive-only**: 기존 v2.2 consumer 는 `soak_liveness_results` 부재 = soak 미적용으로 해석(무해). daemon_type/sink_probes[] 실 값 schema = `docs/project-config-schema.md` `integration_test` SSOT.

## Wrapper sibling 동기화

wrapper sibling(`mclayer/plugin-codeforge:docs/inter-plugin-contracts/test-verdict-v2.md`) 이 ADR-010 wrapper-first 패턴에 따라 먼저 갱신됨. 본 파일은 canonical sync PR (CFP-373, ADR-010 §4 sibling sync policy 이행).

이전 sync: CFP-371 (v2.0 → v2.1).
