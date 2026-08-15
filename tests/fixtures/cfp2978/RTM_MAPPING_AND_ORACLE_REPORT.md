# CFP-2978 Phase 2 — QADev 매핑표 + 오라클 판별력 실측 보고

**보고자**: QADeveloperAgent
**대상**: W-14 `tests/scripts/test_cfp2978_workflow_shape.py` (AC-10 구조 오라클)
**측정 시각 앵커**: 2026-08-15 KST (본 판의 모든 수치는 실행 산출 인용)

> ★ 본 문서는 **전면 재작성본**이다. 구판은 존재하지 않는 줄번호를 인용하고
> ("test_c1 … L132-150" → 실측 L95-115), 이미 실행된 mutant 를 "미실측" 으로 적고,
> 아래 §5 에 기록된 **거짓 문장 1건**을 담고 있었다. 근거 없는 체크(✓)로 채운
> 6방향 자문표는 정작 사문 필드 10 종을 놓쳤으므로 재현하지 않는다.

---

## 0. 무엇이 고쳐졌나 (배선 결함)

구판 W-14 는 W-13(`scripts/lib/workflow_shape.py`)을 **import 하지 않고** 자체
`extract_workflow_shape()` + bare `yaml.safe_load()` 를 재구현했다. bare
`safe_load` 는 W-13 비협상 계약 (2)가 금지한 형태다(중복 키 silent last-wins).

⇒ 구판의 GREEN 은 **W-13 오라클이 아니라 그 흉내**를 검증했고, mutant 11 종이
pytest 면에서 조용히 통과했다.

| 구분 | 구판 | 현판 |
|---|---|---|
| 추출기 | 자체 재구현 (`extract_workflow_shape`) | W-13 `load_workflow_shape()` **호출** |
| 파서 | bare `yaml.safe_load` (계약 (2) 위반) | W-13 `DupSafeLoader` 단일 경로 |
| 전제 위반 처리 | 자체 `ValueError` / 일부 흡수 | `ShapeError` (P-1~P-6 fail-closed) |
| assert 되는 shape 필드 | 4 / 14 | **14 / 14** |
| 미검출 mutant (pytest 면) | 11 | **0** |
| 수집 테스트 수 | 10 | 61 |

**단일 근인**: shape 14 필드 중 **10 종이 사문**(계산만 되고 조회 0)이었고, 미검출
mutant 11 건이 그 사문 집합에 1:1 로 착지했다. 실측상 그 10 종은 정확히 **4 fixture
전건에서 값이 동일한 필드**(= backfill 보존 불변식)이고, assert 되던 4 종은 정확히
**repo 별로 값이 갈리는 필드**(= 로컬 개조)였다.

---

## 1. RTM — AC-10 요소 ↔ 테스트 함수 ↔ 측정 assertion 위치

파일: `tests/scripts/test_cfp2978_workflow_shape.py` (749 lines). 정의역 = **구조**
(W-13 `DupSafeLoader` 파싱 산출). 줄번호는 AST 실측값.

### (가) repo 별 차등 필드 — E1~E8 (로컬 개조 자체)

| §8 항목 | 테스트 함수 | 커버리지 | 측정 assertion 위치 |
|---|---|---|---|
| AC-10-E1 | `test_e1_mctrader_top_concurrency_exists` | 정상 경로 | L253 `assert shape.top_concurrency is not None` ∧ L254 경로 실재 |
| AC-10-E2 | `test_e2_mctrader_group_equals_pin` | 정상 경로 | L265 `assert group_value == PIN_MCTRADER_GROUP` |
| AC-10-E3 | `test_e3_mctrader_template_group_absent` | 엣지(부재) | L284 양성 앵커 ∧ **L288** `assert group_value != TEMPLATE_GROUP` |
| AC-10-E4 | `test_e4_mctrader_no_job_concurrency` | 엣지(공집합) | L298 양성 앵커 ∧ **L302** `assert job_paths == []` |
| AC-10-E5 | `test_e5_mctrader_timeout_paths_pinned` | 경계(경로집합) | **L325** `pytest.fail(...)` — 경로→값 매핑 전문 대조, 위반 경로 열거 |
| AC-10-E6 | `test_e6_backtest_no_top_concurrency` ×3 repo | 엣지(부재) | L339 `assert shape.top_concurrency is None` ∧ L342 |
| AC-10-E7 | `test_e7_backtest_no_job_concurrency` ×3 repo | 엣지(공집합) | **L354** `assert job_paths == []` |
| AC-10-E8 | `test_e8_market_job2_runs_on_custom` | 통합(파생접근자) | **L368** `assert JOB2 in delta` (`runs_on_local_delta`) ∧ L372 값 대조 |

### (나) 4 repo 불변 필드 — F1~F10 (backfill 보존 불변식, **신설**)

전 leg 이 `@parametrize` 로 4 fixture 각각 독립 verdict 를 낸다.

| 사문이던 필드 | 테스트 함수 | 커버리지 | 측정 assertion 위치 |
|---|---|---|---|
| `job_ids` | `test_f1_job_ids_pinned` | 정상 경로 | **L385** `assert shape.job_ids == PIN_JOB_IDS` |
| `coe_paths` | `test_f2a_coe_paths_pinned` | 경계(경로집합) | **L400** `assert shape.coe_paths == PIN_COE_PATHS` |
| `coe_paths` (소속축) | `test_f2b_coe_ownership_partition_pinned` | 경계(소속분할) | **L422** `assert owned == PIN_COE_OWNED` (`coe_paths_of`, P-5 강제) |
| — (계약 (1) 실증) | `test_f2c_ownership_is_not_bare_startswith` | invariant | L467 `owned_job1 == []` ∧ L469 bare 오분류 ∧ **L473** `owned_job1 != bare_job1` |
| `job_if` | `test_f3_job_if_pinned` | 정상 경로 | **L482** `assert dict(shape.job_if) == PIN_JOB_IF` |
| `step_if` | `test_f4_step_if_pinned` | 경계(순서) | **L495** `assert {...shape.step_if...} == PIN_STEP_IF` |
| `env_keys` | `test_f5_env_keys_pinned` | 주입채널 §8.F | **L518** `pytest.fail(...)` — 3 레벨 전건, 위반 경로 열거 |
| `container_env_keys` | `test_f6_container_env_keys_absent` | 주입채널 #6 | L533 양성 앵커 ∧ **L535** `== PIN_CONTAINER_ENV_KEYS` |
| `env_file_keys` | `test_f7_env_file_keys_absent` | 주입채널 #5 | L551 양성 앵커 ∧ **L553** `== PIN_ENV_FILE_KEYS` |
| `step_shell` | `test_f8_step_shell_pinned` | §8.B rc 흡수 | L568 양성 앵커 ∧ **L570** `assert actual == PIN_STEP_SHELL` |
| `defaults_run_shell` | `test_f9_defaults_run_shell_absent` | §8.B 원거리 우회 | L583 양성 앵커 ∧ **L585** `== PIN_DEFAULTS_RUN_SHELL` |
| `job_defaults_run_shell` | `test_f10_job_defaults_run_shell_absent` | §8.B 우회 | L595 양성 앵커 ∧ **L597** `== PIN_JOB_DEFAULTS_RUN_SHELL` |

### (다) 계약·판별력 leg

| §8 항목 | 테스트 함수 | 커버리지 | 측정 assertion 위치 |
|---|---|---|---|
| 배선 결속 (born-broken 가드) | `test_f0_oracle_bound_to_w13_not_reimplemented` | invariant | L212 모듈 동일성 ∧ **L216** `w13_file.parts[-3:] == ("scripts","lib","workflow_shape.py")` ∧ L237 로컬 재구현 부재 |
| 비협상 계약 (2) DupSafeLoader | `test_f11_duplicate_key_fail_closed` | 엣지(fail-closed) | L632 bare safe_load last-wins 대조 ∧ **L642** `assert exc.value.error_kind == "workflow_parse_error"` |
| R-1 (제거 mutant) | `test_oracle_mutation_r1_remove_mctrader_top_concurrency` | mutant | L688/L691 R-1 축 붕괴 ∧ **L695** 형제 축 독립(self-referential) |
| T-taut (항진 대조군) | `test_oracle_taut_template_vs_mctrader_runs_on` | 대조군 | L731 밀짚 양쪽 GREEN ∧ **L741** `assert real_divergent` |

### invariant 커버

| invariant | 근거 | 측정 assertion 위치 |
|---|---|---|
| INV-5 "읽지 못한 상태 ≠ GREEN" | W-13 P-1~P-6 | `ShapeError` 전파 — M-13e-empty/malformed/delete 3종 전건 RED (§3) |
| 비협상 계약 (1) 소속 판정 ≠ bare `startswith` | W-13 docstring | `test_f2c` **L473** (두 판정형이 실제로 갈리는 입력에서 대조) |
| 비협상 계약 (2) DupSafeLoader 의무 | W-13 docstring | `test_f11` **L642** + M-dup-same RED |
| §8.D rule 1 카디널리티 = 경로집합 파생 | Change Plan §8.D | E5 L325 / F2a L400 (개수 아닌 경로 집합 동일성, 위반 경로 열거) |
| §8.D rule 2 부재-assert = 양성 앵커 AND | Change Plan §8.D | `_anchor_jobs` / `_anchor_steps` / `_anchor_run_step` — E3/E4/E6/F6/F7/F8/F9/F10 전건 |

---

## 2. 회귀 대조군 (측정 assertion 위치 = N/A 인 항목)

없음. 본 파일의 61 개 수집 테스트 전건이 실행 assertion 을 보유한다
(`manual:reviewer note` 영역 0).

---

## 3. Mutant 실행 관측표 (전/후) — 27 종 전건 실측

하네스 = `tests/scripts/cfp2978-mutant-lab/mutant_harness.py`,
산출 = `tests/scripts/cfp2978-mutant-lab/logs/*.json`.
**전(前)** = 배선 결함 상태(HEAD `9b7155a3c`) 실측치, **후(後)** = 본 수리 후 실측치.

### 3.1 미검출 → 검출 전환 11 종 (수리 목표)

| mutant | pytest 전 → 후 | W-13 면 | 후: 귀속 leg |
|---|---|---|---|
| M-envfile | GREEN → **RED** | RED | f2a, f2b, f4, f5, f7, f8 |
| M-envfile-inplace | GREEN → **RED** | RED | **f7 단독** (축 격리) |
| M-envfile-blk | GREEN → **RED** | RED | f2a, f2b, f4, f5, f7, f8 |
| M-envkey | GREEN → **RED** | RED | **f5 단독** |
| M-envctr | GREEN → **RED** | RED | **f6 단독** |
| M-own1 | GREEN → **RED** | RED | f2a, f2b |
| M-own2 | GREEN → **RED** | RED | f2a, f2b |
| R-7 | GREEN → **RED** | RED | f2a, f2b |
| M-dup-same | GREEN → **RED** | RED | 19 leg 전면 (`ShapeError[workflow_parse_error]`) |
| M-13k | GREEN → **RED** | RED | **f8 단독** |
| M-13l | GREEN → **RED** | RED | **f9 단독** |

소속축 3 종은 `f2b` 문면이 서로 다른 분할을 보고한다 (실행 산출 인용):

```
M-own1  실측: {'parallel-work-sentinel': ['jobs.parallel-work-sentinel.continue-on-error',
                                          'jobs.parallel-work-sentinel.steps[2].continue-on-error'],
               'parallel-work-sentinel-test': []}
M-own2  실측: {'parallel-work-sentinel': ['jobs.parallel-work-sentinel.steps[2].continue-on-error'],
               'parallel-work-sentinel-test': ['jobs.parallel-work-sentinel-test.continue-on-error']}
R-7     실측: {'parallel-work-sentinel': [],
               'parallel-work-sentinel-test': ['jobs.parallel-work-sentinel-test.continue-on-error']}
```

### 3.2 declared GREEN 4 종 (정직 천장 — 유지되어야 함)

| mutant | pytest 전 → 후 | W-13 면 | 근거 |
|---|---|---|---|
| M-envfile-blk-inplace | GREEN → **GREEN** | GREEN | §8.F C-3 declared 미포섭(여러 줄 블록 리다이렉트), 축 격리 |
| M-13h | GREEN → **GREEN** | GREEN | §8.B declared — 정적 층 rc 흡수 미검출, 완결 근거 = M-13a 런타임 kill |
| M-13i | GREEN → **GREEN** | GREEN | 동상 |
| M-13j | GREEN → **GREEN** | GREEN | 동상 |

### 3.3 기존 RED 유지 12 종

M-13e-empty / M-13e-malformed / M-13e-delete / M-dup / M-quot / M-job4 /
R-1 / R-2 / R-4 / R-5 / R-6 / T-taut — 전건 RED → RED. **역행(RED→GREEN) 0 건.**

### 3.4 두 오라클 면 verdict 일치

수리 전 11 종 불일치 → 수리 후 **27/27 일치**. 두 면이 갈리는 mutant 가 없다는 것은
"W-13 이 보는 것을 pytest 면도 본다" 는 뜻이다 (leg 부재 잔여 0).

---

## 4. RED 진정성 (본 파일이 무엇으로 falsify 되었나)

본 수리는 GREEN 구현이 먼저 도착한 cross-layer 상황이므로, RED 진정성은
**mutant 하네스 재실행**으로 사후 입증했다 (§3).

* **discriminating case (전 GREEN → 후 RED)**: 11 종. 신설 leg 이 없었다면 통과했을
  입력이 이제 실패한다 — vacuous 아님의 직접 증거.
* **regression-guard case (양 regime GREEN)**: 4 종(§3.2) + baseline 61/61.
  선언된 천장이 천장인 채로 남았음을 확인.

추가로, 수리 과정 자체에서 **자기 결함 2 건을 실행 산출로 falsify** 했다:

1. **F0 자기참조 함정** — 금지 패턴을 리터럴로 적었더니 F0 자신의 소스를 검출해
   baseline 이 RED(1 failed, 55 passed). needle 조립형으로 교정 + 술어 비공허 통제 추가(L233).
2. **F2 장식 assert** — 소속 assert 를 경로집합 assert 와 한 함수에 두었더니
   M-own1/M-own2/R-7 셋 다 **경로집합 assert 에서 종결**(분리 전 판 기준 L403)해 `coe_paths_of()` 가
   RED 방향으로 한 번도 구동되지 않았다. 즉 소속 축은 assert 는 있으나 판별에
   기여하지 않는 **장식**이었다 — 본 Story 가 겨냥하는 결함 class 의 재발.
   F2a/F2b 분리로 교정(§3.1 이 분리 후 관측치).

---

## 5. 구판 거짓 문장 정정

**구판 L151**:

> "정리하면, **W-14의 E5 assertion이 §8.D rule 1을 위반**하고 있으므로 파일을
> 수정해야 합니다. 이는 relocation mutant(R-6) 감지 불가를 의미합니다."

**판정: 실측 반증됨.** R-6(job-level timeout → step-level 이동, 카디널리티 불변)은
구판 E5 에서도 **검출되었다**.

* 근거: `tests/scripts/cfp2978-mutant-lab/logs/R-6.json` — 구판 pytest 면
  `failed_legs=['test_e5_mctrader_timeout_exactly_2']`, verdict RED.
* 기전: 구판 E5 는 `"[" not in k` 로 job-level 경로만 거른 뒤 개수를 봤는데,
  step-level 로 옮겨가면 경로 키에 `[` 가 붙어 필터에서 빠진다 → 2 ≠ 1 로 RED.
  즉 "카디널리티만 센다" 는 서술 자체가 부정확했다(경로 문면에 의존하고 있었다).
* 현판은 그와 무관하게 경로→값 매핑 전문 동일성으로 강화했고, R-6 은 여전히 RED다.

**구판이 놓친 것**: E5 의 rule 1 준수 여부가 아니라 **사문 필드 10 종에 leg 이
아예 없다**는 사실이었다. 구판 §Part 2 의 6방향 자문표는 8/8 ✓ 로 채워져 있었으나
그 표가 정작 이 결함을 지나쳤다 — 근거 없는 체크가 결함을 은폐한 사례로 기록한다.

---

## 6. 정직 천장 (본 파일이 주장하지 **않는** 것)

* **`env_file_keys` 정의역 = 인라인 `$GITHUB_ENV` 기입 표기 한정 · 전수 아님**
  (§8.F C-3). F7 의 GREEN 을 "환경변수 주입 없음" 으로 인용하면 over-claim 이다.
  미포섭 축(여러 줄 블록 리다이렉트 · heredoc · `exec` 재지정 · 변수 간접화 ·
  타 언어 writer · 간접 스크립트 호출 · `pwsh $env:` 표기)의 SSOT =
  W-13 `_scan_env_file_keys()` docstring.
* **§8.B rc 흡수 정적 층은 단독 완결이 아니다.** `run` 문면의 rc 관용구
  (`|| :` · `; true` · `set +e; exit 0`)는 W-13 이 스캔하지 않는다 — M-13h/i/j 의
  GREEN 은 검출 성공이 아니라 **선언된 천장**이며, 완결 근거는 런타임 kill 관측(M-13a).
* **composite action 내부 `continue-on-error`** 는 타 repo·파일 밖이라 원리적 미검출
  잔여다. `coe_paths` 가 비었다는 사실을 "결과 흡수 없음" 으로 인용 금지 (W-13 A6).
* **GitHub Actions 실 파서 ↔ PyYAML 의미 차 = [미실측]** (`verification-out-of-scope`).
* **F0 의 소스 스캔은 자기 자신을 정의역에서 구조적으로 제외**한다(자기참조 회피).
  "재구현이 전혀 없다" 의 증명이 아니라 "구판 형태로의 회귀가 없다" 의 가드다.
* 본 파일은 **wrapper 검증면(S2) 전용**이다. W-13 은 PyYAML 의존이라
  `templates/consumer-scripts.manifest` 등재 대상이 아니다.

---

## 7. 실행 산출 (최종)

```
$ python -m pytest tests/scripts/test_cfp2978_workflow_shape.py -q
61 passed

$ python -m pytest tests/scripts/test_cfp2976_sentinel_prefix.py \
      tests/scripts/test_consumer_asset_currency.py \
      tests/scripts/test_cfp2978_workflow_shape.py -q     # CI workflow L127 과 동일 인자
75 passed     # = W-14 61 + W-12 11 + CFP-2976 3 (각 --collect-only 실측)

$ python tests/scripts/cfp2978-mutant-lab/mutant_harness.py --baseline
pytest face = GREEN (failed_legs=[]) ∧ W-13 face = GREEN (red_legs=[])

$ python tests/scripts/cfp2978-mutant-lab/mutant_harness.py --run-all
27/27 실행 — 두 면 verdict 일치 27/27, RED→GREEN 역행 0
```

**fixture blob 무변경** (`git hash-object` ↔ `HEAD:<path>` 대조, 4/4 일치):

| fixture | blob SHA |
|---|---|
| mctrader-sentinel.yml | `216e95f94450ee8e369e9bec50db6b7a893b7b47` |
| mctrader-backtest.yml | `cde6e59b15ce19428e49a002b526ececc891331d` |
| mctrader-market.yml | `f84fb3935975ac2ca3f71495076f87244ff4c47e` |
| mctrader-engine.yml | `cde6e59b15ce19428e49a002b526ececc891331d` |

---

## 8. 공백 / 질의

* **없음** — AC-10 E1~E8 및 shape 14 필드 전건에 측정 assertion 이 배치됐다.
* W-12(`test_consumer_asset_currency.py`, AC-5) 는 본 수리의 대상이 아니었고
  **무변경**이다. 구판 RTM 이 그 파일에 대해 적은 줄번호는 전부 부정확했으므로
  (예: `test_c1` 을 L132-150 으로 적었으나 실측 L95-115) 본 판에서는 재현하지 않는다.
  W-12 의 RTM 이 필요하면 별도 실측 후 작성해야 한다 — **[본 판 미작성]**.
