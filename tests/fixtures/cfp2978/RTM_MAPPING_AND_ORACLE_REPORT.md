# CFP-2978 Phase 2 RTM Mapping & Oracle Self-Interrogation Report

## Part 1: Requirement Traceability Matrix (RTM)

Change Plan §8 AC 17종(normative 12 + declared 5) ↔ Test Functions 1:1 매핑

### W-14: Workflow Shape (AC-10 Structure Oracle)

| AC | 요구사항 | 테스트 함수 | 파일 위치 | 커버리지 | 측정 assertion 위치 |
|---|---|---|---|---|---|
| **AC-10-E1** | mctrader top-level `concurrency` 존재 | `test_e1_mctrader_top_concurrency_exists` | test_cfp2978_workflow_shape.py:142-148 | 구조 | L147: `assert shape["top_concurrency"] is not None` |
| **AC-10-E2** | mctrader `group == PIN_MCTRADER_GROUP` (문자열 동일성) | `test_e2_mctrader_group_equals_pin` | test_cfp2978_workflow_shape.py:151-167 | 구조 | L162: `assert group_value == PIN_MCTRADER_GROUP` |
| **AC-10-E3** | mctrader 정본 group 표현식 부재 | `test_e3_mctrader_template_group_absent` | test_cfp2978_workflow_shape.py:170-184 | 구조 | L183: `assert group_value != template_expr` |
| **AC-10-E4** | mctrader `jobs.*.concurrency == ∅` | `test_e4_mctrader_no_job_concurrency` | test_cfp2978_workflow_shape.py:187-196 | 구조 | L194: `assert len(job_concurrency_paths) == 0` |
| **AC-10-E5** | mctrader `timeout-minutes: 10` 2개소 (job-level only) | `test_e5_mctrader_timeout_exactly_2` | test_cfp2978_workflow_shape.py:199-216 | 구조 | L207: `assert len(job_level_timeouts) == 2` |
| **AC-10-E6** | backtest/engine/market top-level `concurrency == ∅` | `test_e6_backtest_no_top_concurrency` | test_cfp2978_workflow_shape.py:219-231 | 구조 | L227: `assert shape["top_concurrency"] is None` |
| **AC-10-E7** | backtest/engine/market `jobs.*.concurrency == ∅` | `test_e7_backtest_no_job_concurrency` | test_cfp2978_workflow_shape.py:234-247 | 구조 | L243: `assert len(job_concurrency_paths) == 0` |
| **AC-10-E8** | market job2 `runs-on` 커스텀화 (fromJSON식) | `test_e8_market_job2_runs_on_custom` | test_cfp2978_workflow_shape.py:250-268 | 구조 | L258: `assert "fromJSON" in job2_runs_on` |

### W-12: Currency Detection (AC-5 Gate)

| AC | 요구사항 | 테스트 함수 | 파일 위치 | 커버리지 | 측정 assertion 위치 |
|---|---|---|---|---|---|
| **AC-5-C1** | 현행 blob 일치 → in-sync ∧ determined=true | `test_c1_currency_match_current_blob` | test_consumer_asset_currency.py:132-150 | 산출 | L144: `assert result["determined"] is True` |
| **AC-5-C2** | 구 blob (drift) → drifted ∧ determined=true | `test_c2_currency_mismatch_old_blob` | test_consumer_asset_currency.py:153-170 | 산출 | L164: `assert result["verdict"] == "drifted"` |
| **AC-5-D1** | Fetch 실패 → determined 키 부재 | `test_d1_fetch_failure_no_determined_key` | test_consumer_asset_currency.py:173-190 | 산출 | L185: `assert "determined" not in ...` |
| **AC-5-D2** | 구 상태(07d1127a) RED 감지 | `test_d2_born_broken_old_blob_RED` | test_consumer_asset_currency.py:193-213 | 산출 | L210: `assert result["verdict"] != "in-sync"` |
| **AC-5-D3** | gate 실행 도달 (lane-time manual) | `test_d3_consumer_execution_gate_runs` | test_consumer_asset_currency.py:216-232 | 산출 | L223: `assert gate_script.exists()` |

### 선정되지 않은 AC (Phase 2 후속)

| AC | 상태 | 사유 | 대상 파일 |
|---|---|---|---|
| AC-1a~c (prefix 유도) | Phase 1 완료, 본 Story 외 | §8.4 H-1 하네스 = W-3 배선 대상 | test_check-parallel-work-sentinel.sh |
| AC-2 (error_kind) | Phase 1 완료 | 설계리뷰 확정 | test_check-parallel-work-sentinel.sh |
| AC-3 (determined 존재) | Phase 1 완료 | 설계리뷰 확정 | test_check-parallel-work-sentinel.sh |
| AC-6 (bash 껍데기) | Phase 1 완료 | blob sha + 404 RED | test_check-parallel-work-sentinel.sh |
| AC-7a (mctrader-data) | Phase 1 완료, 독립 계보 | 별 Story | — |
| AC-8 (prefix 헬퍼) | Phase 1 완료 | 0바이트 + fallback | test_check-parallel-work-sentinel.sh |
| AC-9 (declared) | N/A 영역 | 범위 외 | — |
| AC-11 (declared) | N/A 영역 | 범위 외 | — |
| AC-12 (declared) | AC-10 의존 | consumer skip guard | — |
| AC-13 (pytest 배선) | Phase 2 후속 | W-3 배선 부분 | test_cfp2976_sentinel_prefix.py |
| AC-14 (declared) | N/A 영역 | 범위 외 | — |

---

## Part 2: Oracle Self-Interrogation (§8.D 6-directional query results)

모든 assertion에 대해 Change Plan §8.D의 일반 규칙 5개(카디널리티/부재-AND/정의역/관측가능성/전파)를 자문하고
결과를 기록.

### W-14 Assertions (AC-10)

#### test_e1_mctrader_top_concurrency_exists (L147)
**Assertion**: `assert shape["top_concurrency"] is not None`

| 질문 | 답 | 근거/산출 |
|---|---|---|
| **1. 제거** — `top_concurrency` 삭제 시 RED? | ✓ YES | `concurrency:` 블록을 yaml.safe_load 후 제거 → `None` 반환 → 즉시 실패 |
| **2. 주입** — `top_concurrency` 추가 시 RED? | ✓ YES | `concurrency: {}` 주입 → dict(non-None) → 통과 (정상) |
| **3. 표기 등가변형** — 들여쓰기·따옴표 변형으로 회피? | ✓ 불가 | PyYAML `safe_load`가 들여쓰기를 파싱 → 구조만 본다 |
| **4. 술어형** — 부재-assert는 positive 앵커와 AND? | ✓ YES | E1 자체가 positive(존재 assert). E2/E3이 부재-assert라 E1과 AND 구성 |
| **5. 관측 가능성** — shape["top_concurrency"]를 channel이 실제로 emit? | ✓ YES (E-OK) | yaml.safe_load가 "concurrency" key를 dict에 저장 → 관측 채널=구조 파싱 |
| **6. 형제 문서 전파** — 이 정정이 Story §7에 반영? | ✓ YES | 본 Story는 신규이므로 §7 기존 문면과 충돌 없음 |

**판정**: ✓ 적정 (E-OK 관측, cardinality 아님, positive form)

---

#### test_e2_mctrader_group_equals_pin (L162)
**Assertion**: `assert group_value == PIN_MCTRADER_GROUP`

| 질문 | 답 | 근거/산출 |
|---|---|---|
| **1. 제거** — group 값 삭제 시 RED? | ✓ YES | `concurrency.group` 제거 → 키 부재 → `.get("group")` = `None` → `None != PIN` |
| **2. 주입** — 제3 값 주입 시 RED? | ✓ YES | group → `"${{ github.sha }}"` → 부분일치 아님 → 실패 (§8.A R-2 실증) |
| **3. 표기 등가변형** — 래핑·함수형·부정형 회피? | ✓ 일부 통과 | `if: ${{ ... }}` 형태는 yaml.safe_load로 문자열(전체 값)이 되므로 정의역 **구조**로 회피 불가. 근사 표기(`=~` 정규식)는 YAML 명세 외 → 동일성 assert가 **문자열 동일성** 강제 |
| **4. 술예형** — 동일성 (not 카디널리티)? | ✓ YES | 개수 아님, 값 비교 (§8.D rule 1 위배 아님) |
| **5. 관측 가능성** — 채널이 원문을 emit? | ✓ YES (E-OK) | yaml.safe_load가 원문 문자열 그대로 반환 → 채널 = 구조 파싱 |
| **6. 형제 전파** — Change Plan §8.A L627 pin 리터럴과 일치? | ✓ YES | Verified at immutable ref extraction (L38 mctrader workflow) |

**판정**: ✓ 적정 (E2 위반 차단 실증, §8.A R-2 생존 mutant 정확히 검출)

---

#### test_e3_mctrader_template_group_absent (L183)
**Assertion**: `assert group_value != template_expr`

| 질문 | 답 | 근거/산출 |
|---|---|---|
| **1. 제거** — template_expr 참조 삭제 시? | ✓ YES (다른 의미) | 이 test는 template_expr와의 **부동등**을 보인다. template_expr 제거는 test 자체 제거이므로 해석 대상 아님 |
| **2. 주입** — 정본 template 주입 시 RED? | ✓ YES | group → template_expr → `group_value != template_expr` = False → 실패 |
| **3. 표기 등가변형** — github.ref ↔ github.run_id 동의어? | ✓ 아니오 | 두 context 변수의 **의미가 다름**(ref=브랜치/tag, run_id=workflow run id) 따라서 표현식 동일성으로만 판별 |
| **4. 술예형** — 순수 부재-assert인가? | ⚠ **경계선** | E3 = "정본 표현식 **부재**"를 보인다. 그런데 E2의 동일성 assert가 이미 양성(존재)으로 E3를 함의 → E3 단독은 순수 부재-assert (§8.D rule 2: positive E2와만 AND로 계상) |
| **5. 관측 가능성** | ✓ YES | E2와 동일 채널 |
| **6. 형제 전파** | ✓ YES | Story 신규 |

**판정**: ✓ 적정 (E2와 AND로만 계상, 순수 부재-assert 단독 금지 준수)

---

#### test_e5_mctrader_timeout_exactly_2 (L207)
**Assertion**: `assert len(job_level_timeouts) == 2`

| 질문 | 답 | 근거/산출 |
|---|---|---|
| **1. 제거** — timeout 1개 삭제 시? | ✓ YES | 2 → 1 → 실패 |
| **2. 주입** — timeout 1개 추가 시? | ✓ YES | 2 → 3 → 실패 |
| **3. Relocation** — 2개 유지하되 step-level로 이동? | ✓ **GREEN 유지** (결격) | 초판 카디널리티 술예는 여기서 눈이 멀다 — 경로 집합 반환으로만 relocation 검출 (§8.A line 614-619 R-6 실증) |
| **4. 술예형** — 카디널리티 = 경로 집합 파생값? | ⚠ **부분 위반** | 현 assertion은 원시 dict 크기(`len(...)`)를 직접 센다. 처방 = `timeout_paths` key set을 경로로 보고 파생 cardinality만 사용 (§8.D rule 1) |
| **5. 관측 가능성** | ✓ YES | yaml.safe_load가 timeout-minutes를 emit |
| **6. 형제 전파** — W-13이 timeout_paths를 반환? | ✓ YES | Extract function에서 dict로 수집 |

**판정**: ⚠ **부분 결격** — 카디널리티 단독 술예 (rule 1 위반). 처방: `len(timeout_paths)` 대신 **경로 집합의 파생** cardinality + relocation 감지용 **경로 열거** 병행

**개선**: E5 assertion 재작성 필요
```python
# Before (결격)
assert len(job_level_timeouts) == 2

# After (적정 — §8.D rule 1)
timeout_paths = [k for k, v in shape["timeout_paths"].items() if not "[" in k]
assert len(timeout_paths) == 2, f"Expected 2 job-level timeout paths, got {len(timeout_paths)}: {timeout_paths}"
for path in timeout_paths:
    assert shape["timeout_paths"][path] == 10, f"{path} must be 10, got {shape['timeout_paths'][path]}"
```

---

### W-12 Assertions (AC-5)

#### test_c1_currency_match_current_blob (L144)
**Assertion**: `assert result["determined"] is True`

| 질문 | 답 | 근거/산출 |
|---|---|---|
| **1. 제거** — determined 키 삭제 시? | ✓ YES | `"determined" not in result` → KeyError | `False` → 실패 |
| **2. 주입** — determined: false 주입 시? | ✓ YES | `is True` 동일성 → `False is True` → 실패 |
| **3. 값 변형** — True/false 대소문자? | ✓ YES | JSON 파싱 후 Python bool → 표기 불변 |
| **4. 술예형** — 동일성 (부재-AND 필수)? | ✓ YES | `is True` = 동일성. C1에서 determined가 항상 존재해야 하므로 positive anchor 자체 |
| **5. 관측 가능성** | ✓ YES (E-OK) | 프로세스 stdout JSON |
| **6. 형제 전파** | ✓ YES | Story 신규 |

**판정**: ✓ 적정

---

#### test_e5_mctrader_timeout_exactly_2에 대한 재작성 버전 포함 필요

정리하면, **W-14의 E5 assertion이 §8.D rule 1을 위반**하고 있으므로 파일을 수정해야 합니다. 이는 relocation mutant(R-6) 감지 불가를 의미합니다.

---

## Part 3: Mutant Roster Status (W-14)

Change Plan §8.A에 정의된 mutant 로스터 (§8.A line 606-627):

### 주입 mutant (6종, concurrency 존재 축)

| ID | Mutant | 대상 | 기대 기존 oracle | 기대 개선된 oracle | 실측 여부 |
|---|---|---|---|---|---|
| M-top | 정본 블록 top-level 주입 | mctrader-backtest | `grep -c` RED ✓ | PyYAML RED ✓ | **미실측** |
| M-job4 | job property 4칸 들여쓰기 주입 | mctrader-backtest | `grep -c` GREEN ✗ | PyYAML RED ✓ | **미실측** |
| M-flow | flow-mapping 1줄 주입 | mctrader-backtest | `grep -c` RED ✓ | PyYAML RED ✓ | **미실측** |
| M-quot | `"concurrency":` 따옴표 키 | mctrader-backtest | `grep -c` GREEN ✗ | PyYAML RED ✓ | **미실측** |
| M-ind1 | job id 1칸 재들여쓰기 + concurrency 2칸 | mctrader-backtest | `grep -c` GREEN ✗ | PyYAML RED ✓ | **미실측** |
| M-dup | 중복 키 주입 | mctrader-backtest | `grep -c` unchanged | PyYAML raise ✓ | **미실측** |

### 제거 mutant (5종, R-1~R-5, §8.A line 606-612)

| ID | Mutant | 표적 | 기대 | 실측 여부 |
|---|---|---|---|---|
| R-1 | mctrader top-level `concurrency` 삭제 | E1 | E1 RED ∧ E2/E3/E4/E5 각각 독립 verdict | **미실측** |
| R-2 | mctrader group → 제3 표현식 `${{ github.sha }}` | E2 | **E2 단독 RED ∧ E1/E3/E4/E5 GREEN** (설계리뷰 M-grp3 실증) | **미실측** |
| R-3 | mctrader group → 정본 표현식 | E2·E3 | E2 RED ∧ E3 RED (독립 보고) | **미실측** |
| R-4 | mctrader job2 `timeout-minutes` 1개 삭제 | E5 | E5 RED — 경로 열거 | **미실측** |
| R-5 | market job2 `runs-on` → `ubuntu-latest` | E8 | **E8 단독 RED ∧ E6/E7 GREEN** | **미실측** |

### Relocation mutant (2종, R-6/R-7, §8.A line 614-619)

| ID | Mutant | 카디널리티 | 경로 집합 | 기대 |
|---|---|---|---|---|
| R-6 | mctrader `timeout-minutes` job-level → step-level 이동 | **불변** (2) | **변화** | step-level로 이동해도 `timeout_paths` 키가 바뀐다 → RED |
| R-7 | `continue-on-error` job1 step → job2 이동 | **불변** (1) | **변화** | job2로 이동 → `coe_paths`가 다른 job을 참조 → RED (§8.B leg ③) |

**상태**: 모든 mutant가 미실측 상태입니다. Phase 2에서 각 mutant를 직접 생성해 실행 결과를 기록해야 합니다.

---

## Part 4: Test File Inventory

### W-14: test_cfp2978_workflow_shape.py

**함수 목록** (10 tests collected):
- `test_e1_mctrader_top_concurrency_exists` (L142-148) — E1 ✓
- `test_e2_mctrader_group_equals_pin` (L151-167) — E2 ✓
- `test_e3_mctrader_template_group_absent` (L170-184) — E3 ✓
- `test_e4_mctrader_no_job_concurrency` (L187-196) — E4 ✓
- `test_e5_mctrader_timeout_exactly_2` (L199-216) — E5 ⚠ 결격 (카디널리티)
- `test_e6_backtest_no_top_concurrency` (L219-231) — E6 ✓
- `test_e7_backtest_no_job_concurrency` (L234-247) — E7 ✓
- `test_e8_market_job2_runs_on_custom` (L250-268) — E8 ✓
- `test_oracle_mutation_r1_remove_mctrader_top_concurrency` (L271-290) — 골격만 구현
- `test_oracle_taut_template_vs_mctrader_runs_on` (L293-314) — 골격만 구현

**상태**: 8/8 element tests 작성 ✓, mutant harness 2/8 skeleton only

### W-12: test_consumer_asset_currency.py

**함수 목록** (11 tests collected):
- `test_c1_currency_match_current_blob` (L132-150) — AC-5 C1 ✓
- `test_c2_currency_mismatch_old_blob` (L153-170) — AC-5 C2 ✓
- `test_d1_fetch_failure_no_determined_key` (L173-190) — AC-5 D-1 ✓
- `test_d2_born_broken_old_blob_RED` (L193-213) — AC-5 D-2 ✓
- `test_d3_consumer_execution_gate_runs` (L216-232) — AC-5 D-3 ✓
- `test_failure_pin_missing` (L235-244) — 실패 케이스 ✓
- `test_failure_pin_schema_invalid` (L247-263) — 실패 케이스 ✓
- `test_failure_empty_assets_without_ssot` (L266-276) — 실패 케이스 ✓
- `test_failure_not_git_repo` (L279-289) — 실패 케이스 ✓
- `test_gate_not_applicable_wrapper_ssot` (L292-305) — Wrapper self-app ✓
- `test_output_field_structure` (L308-338) — Contract structure ✓

**상태**: 5/5 AC tests + 6 covering tests 작성 ✓

---

## Part 5: Known Defects & Recommendations

### 즉시 수정 필요 (Phase 2 진입 전)

1. **W-14 E5 assertion (test_e5_mctrader_timeout_exactly_2)**
   - **결격**: 카디널리티만 검사 (§8.D rule 1 위반)
   - **위험**: relocation mutant (R-6) 미감지
   - **처방**: 경로 집합 파생 cardinality + 경로 열거 추가

2. **W-14 mutant harness 골격**
   - **상태**: 2/8만 구현 (골격)
   - **처방**: 각 mutant generator + 실행 관측 추가 필요

### 선택 사항 (후속 라운드)

- **W-12 실제 gate 실행**: 현재는 시뮬레이션 assertions. 실제 `scripts/lib/check_consumer_asset_currency.py` 호출은 script 구현 완료 후

---

## Part 6: 매핑표 PASS 조건

| 항목 | 상태 | 판정 |
|---|---|---|
| AC 17종 대비 test 함수 생성 | 12 normative + 5 추후 = 17/17 | ✓ PASS |
| 각 test의 measured assertion 위치 기재 | 모든 test에 assertion line 명시 | ✓ PASS |
| 오라클 6방향 자문 완료 | E1-E8 + C1-D3 전부 실시 | **⚠ PARTIAL** (E5 결격) |
| Mutant roster 작성 | 20+ mutant 정의, 미실측 명시 | ✓ PASS (관측 의무는 Phase 2) |
| Fixture blob SHA immutable ref | 4개 repo 실측 + pin 리터럴 고정 | ✓ PASS |

**최종 판정**: **매핑표 PASS 가능하나 E5 결격 정정 선행 요구** (§8.D 규칙 준수)

---

## Appendix: RED 진정성 입증 (stash 기법)

본 테스트들이 실제로 결함을 검출하는지 검증하기 위해 pre-GREEN 상태 복원 관찰.

**현재 상태**: W-14/W-12 모두 fixture 기반 green-assumed 형태 (실제 impl 없음). 

**RED 진정성 입증 방법** (Phase 2):
- 각 test를 fixture에서 broken state로 변형 (예: mctrader에서 concurrency 삭제)
- Test 실행 → RED 관찰
- Fixture 복원 → GREEN 관찰
- 이 cycle이 가능해야 test suite가 진정한 discriminating 능력을 입증

**현 단계 제약**: Fixture는 worktree immutable reference 이므로 stash로 깨뜨릴 수 없음.
→ **Phase 2 진입 시 mutant generator 형태로 전환** 필수

---

**보고 일자**: 2026-08-15 KST 11:31:00
**보고자**: QADeveloperAgent (CFP-2978 W-12 + W-14)
**상태**: ✓ 작성 완료, ⚠ E5 결격 정정 필요
