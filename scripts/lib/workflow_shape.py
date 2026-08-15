#!/usr/bin/env python3
r"""workflow_shape.py — GitHub Actions workflow **구조 술어** (CFP-2978 W-13).

AC-10(consumer workflow 로컬 개조 양방향 보존) · AC-13(CI 배선 결과 흡수 금지) · D-3 공용.
입력 = workflow yml 파일 경로. 출력 = **경로 집합(path set) 반환형** (`WorkflowShape`).

────────────────────────────────────────────────────────────────────────────
표면 (S1 / S2 분할 — Change Plan §8.A)
────────────────────────────────────────────────────────────────────────────
본 모듈 = **S2 wrapper 검증면 전용**. 실행 러너 = wrapper CI `ubuntu-latest`
(+ lane-time 로컬), 런타임 전제 = `requirements.txt`(PyYAML) 가용.

★ `templates/consumer-scripts.manifest` **등재 금지**. consumer 배포면(S1)은
python3 stdlib only 러너라 PyYAML 이 부재하며, 배포되는 순간 파손된다.
(대조: `check_consumer_asset_currency.py`(W-4)는 S1 이라 stdlib only — 정의역이 다르다.)

────────────────────────────────────────────────────────────────────────────
전제 P-1~P-6 — 전부 fail-closed (`ShapeError` / CLI exit 2). GREEN 절대 금지
────────────────────────────────────────────────────────────────────────────
| #   | 전제                                    | error_kind              |
|-----|-----------------------------------------|-------------------------|
| P-1 | 대상 파일이 존재                        | `workflow_file_missing` |
| P-2 | `safe_load` 가 예외를 던지지 않음       | `workflow_parse_error`  |
| P-3 | `safe_load` 결과가 `dict`               | `workflow_not_mapping`  |
| P-4 | `jobs` 키 존재 ∧ non-empty dict         | `jobs_missing_or_empty` |
| P-5 | 질의 대상 job id 가 `job_ids` 에 실재   | `target_job_absent`     |
| P-6 | `import yaml` 성공                      | `pyyaml_missing` (meta) |

★ 순진한 `(d or {}).get("jobs") or {}` 는 **P-1~P-3 전건을 `{}` 로 흡수해
`(0, 0)` = GREEN 을 낸다**. 이 Story 가 막으려는 사고(전면 덮어쓰기 · surgical
patch 실패 · 파일 소실)가 정확히 그 입력을 만든다 — 그 형태로 쓰지 말 것.

★ INV-5: "게이트가 대조 대상을 **읽지 못한 상태**는 GREEN 이 아니다."
   그 상태의 종결은 **exit 2 이지 exit 0 이 아니다**.
   선례 = `scripts/check-workflow-yaml-parse.sh` L20-24 (`import yaml` 실패 → exit 2 meta-error).

────────────────────────────────────────────────────────────────────────────
비협상 계약 (1) — job 소속 판정. **bare `startswith` 금지**
────────────────────────────────────────────────────────────────────────────
정본 job id 는 `parallel-work-sentinel` 과 `parallel-work-sentinel-test` 이고
**전자가 후자의 진부분 문자열**이다. 순진한 `path.startswith("jobs." + jid)` 는
job2 경로를 job1 소속으로 **오분류**한다.
  실증: `"jobs.parallel-work-sentinel-test.steps[0].continue-on-error"
         .startswith("jobs.parallel-work-sentinel")` → `True` (오분류)

⇒ 소속 판정은 반드시 `_owned_by()` (아래 정의) 로만 한다.
   경계 구분자 `.` 누락 = **결격**.

────────────────────────────────────────────────────────────────────────────
비협상 계약 (2) — `DupSafeLoader` 의무 (중복 키 silent last-wins 차단)
────────────────────────────────────────────────────────────────────────────
PyYAML `safe_load` 는 같은 레벨에 같은 키가 2회면 **마지막 것만 남기고 에러 0**
(실측: `{'group': 'B'}` 반환). 이 처방 없이는 "top-level 개수 == 1" 류 leg 이
중복 주입에 눈먼다. ⇒ 본 모듈은 `DupSafeLoader` **만** 사용한다 (bare
`yaml.safe_load` 호출 금지).

────────────────────────────────────────────────────────────────────────────
카디널리티 파생 규칙 (§8.A — 전 leg 구속)
────────────────────────────────────────────────────────────────────────────
개수가 필요하면 **경로 집합의 파생값(`len(...)`)으로만** 계산하고, 원시 카운터를
술어의 1차 입력으로 삼지 않는다. 실패 보고는 항상 **위반 경로를 열거**한다 —
"2개여야 하는데 1개"가 아니라 "`jobs.parallel-work-sentinel.timeout-minutes` 소실".
이로써 같은 카디널리티를 유지하는 **relocation mutant 가 정의상 관측**된다.

────────────────────────────────────────────────────────────────────────────
알려진 실패 모드 (정직 declare)
────────────────────────────────────────────────────────────────────────────
* **B-F2**: YAML 1.1 이 `on:` 을 bool `True` **키**로 강제 coercion 한다
  (실측: 최상위 키 = `True`(bool) / `'jobs'`(str)). 본 술어는 `concurrency` ·
  `jobs` · `defaults` · `env` 만 질의하므로 무영향.
  ★ **키 경로 확장 시 `on` 을 문자열로 가정 금지** — 이 주석이 그 계약이다.
* **B-F3/B-F4**: anchor/alias(`concurrency: *ref`) · merge key(`<<: *ref`) 주입은
  파서가 해소하므로 **검출 성공**. 처방 불요.
* **B-F6**: GitHub Actions 실 파서 ↔ PyYAML 의미 차 = **[미실측]**,
  `[verification-out-of-scope]`. 본 술어가 *더 엄격한*(잡는) 쪽이라 판별력 손실
  방향은 아니다.
* **A6 (§8.B rc 흡수 표면)**: composite action 내부 `continue-on-error` 는
  **타 repo·파일 밖**이라 **원리적 미검출 잔여**다. `coe_paths` 가 비었다는 사실을
  "결과 흡수 없음"으로 인용하면 over-claim — 정적 층 단독 완결 주장 금지.
  leg ③ 의 완결 근거는 런타임 kill 관측(M-13a)이다.
* **`env_file_keys` 정의역**: **인라인 `$GITHUB_ENV` 기입 표기 한정 · 전수 아님**
  (§8.F C-3). 문서 계약이 정의하는 것은 *"`GITHUB_ENV` 가 가리키는 파일에 append"*
  이지 특정 표기가 아니므로 유효 표기 집합은 **셸이 파일에 쓸 수 있는 모든 방법**
  으로 열려 있다. 아래 `_scan_env_file_keys()` docstring 에 포섭/미포섭 축을 명시.

────────────────────────────────────────────────────────────────────────────
반환형 (`WorkflowShape`)
────────────────────────────────────────────────────────────────────────────
| 필드                     | 형                             | 의미 |
|--------------------------|--------------------------------|------|
| `job_ids`                | `list[str]`                    | 선언 순 job id |
| `top_concurrency`        | `dict \| None`                 | top-level `concurrency` 매핑 전문 |
| `concurrency_paths`      | `list[str]`                    | `concurrency` 전 출현 경로 |
| `coe_paths`              | `list[str]`                    | `continue-on-error` 전 출현 경로 |
| `timeout_paths`          | `dict[str, int]`               | `timeout-minutes` 경로 → 값 |
| `job_if`                 | `dict[str, str \| None]`       | job id → job-level `if` 원문 |
| `step_if`                | `dict[str, list[str \| None]]` | job id → step 순서별 `if` 원문 |
| `env_keys`               | `dict[str, list[str]]`         | `env` 키 목록 (3 레벨 전건) |
| `container_env_keys`     | `dict[str, list[str]]`         | job id → `container.env` 키 목록 |
| `env_file_keys`          | `dict[str, list[str]]`         | job id → 인라인 `$GITHUB_ENV` 기입 키 |
| `step_shell`             | `dict[str, list[str \| None]]` | job id → step 순서별 `shell:` 원문 |
| `defaults_run_shell`     | `str \| None`                  | workflow-level `defaults.run.shell` |
| `job_defaults_run_shell` | `dict[str, str \| None]`       | job id → `jobs.<id>.defaults.run.shell` |
| `runs_on`                | `dict[str, str]`               | job id → `runs-on` 원문 |

파생 접근자 `runs_on_local_delta(shape, canon)` = 정본 값과 **문자열 동일성**
비교로 실 로컬 개조만 남긴다. **E8 판정은 이 파생값 위에서만** 하고, 원시
`runs_on` 은 T-taut 항진 대조군 전용이다 (두 용도가 같은 필드를 공유하면
"무조건-참 assert" 가 판별력 0 인 채로 GREEN 을 낸다).

★ **원문 보존 원칙**: 표에 선언된 스칼라형(`int` / `str`)이 아닌 값(예:
`timeout-minutes: ${{ … }}` · `if: false`(bool) · `runs-on: [self-hosted, linux]`)
이 오면 **coerce·drop 하지 않고 원문을 그대로 보존**한다. 값 소실은 관측 손실이며
이 모듈의 목적(relocation·값 변조 관측)과 정면 충돌한다.

CLI:
    python scripts/lib/workflow_shape.py <workflow.yml> [--job <id> ...]
      exit 0 → stdout 에 shape JSON
      exit 2 → stderr 에 `{"error_kind": …}` (P-1~P-6 위반)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# P-6 — `import yaml` 실패는 침묵 PASS 로 흡수하지 않는다.
# 선례 답습: scripts/check-workflow-yaml-parse.sh L20-24 (exit 2 meta-error).
try:  # pragma: no cover - 환경 의존 분기
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


# ── 오류 계약 ────────────────────────────────────────────────────────────────
#  신규 어휘 발명 금지 — 아래 6종이 값 공간 전부다 (P-1~P-6 1:1 대응).
ERROR_KINDS = (
    "workflow_file_missing",   # P-1
    "workflow_parse_error",    # P-2 (중복 키 ConstructorError 포함)
    "workflow_not_mapping",    # P-3
    "jobs_missing_or_empty",   # P-4
    "target_job_absent",       # P-5
    "pyyaml_missing",          # P-6 (meta-error)
)


class ShapeError(Exception):
    """전제 P-1~P-6 위반. 라이브러리 경로의 fail-closed 종결자.

    CLI 경로에서는 exit 2 로 번역된다 (exit 0 절대 금지 — INV-5).
    """

    def __init__(self, error_kind: str, message: str, path: Optional[str] = None) -> None:
        super().__init__(message)
        if error_kind not in ERROR_KINDS:  # 어휘 발명 방지 self-guard
            raise ValueError(f"unknown error_kind: {error_kind!r}")
        self.error_kind = error_kind
        self.message = message
        self.path = path

    def to_payload(self) -> Dict[str, Any]:
        return {"error_kind": self.error_kind, "message": self.message, "path": self.path}


# ── 소속 판정 계약 (문면 고정 — bare startswith 금지) ────────────────────────
def _owned_by(path: str, jid: str) -> bool:
    """경로 `path` 가 job `jid` 소속인가.

    ★ 이 형태로만 구현한다. bare `path.startswith(f"jobs.{jid}")` 는
      job id prefix 충돌(`parallel-work-sentinel` ⊂ `parallel-work-sentinel-test`)로
      **오분류**하며 그 자체로 결격이다.
    """
    return path == f"jobs.{jid}" or path.startswith(f"jobs.{jid}.")


def paths_owned_by(paths, jid: str) -> List[str]:
    """경로 iterable 중 job `jid` 소속만 필터 (소속 판정 = `_owned_by`)."""
    return [p for p in paths if _owned_by(p, jid)]


# ── DupSafeLoader (중복 키 silent last-wins 차단) ────────────────────────────
_DUP_LOADER: Any = None


def _require_yaml():
    """P-6 — PyYAML 부재는 meta-error 로 종결한다 (침묵 GREEN 봉인)."""
    if yaml is None:
        raise ShapeError(
            "pyyaml_missing",
            "PyYAML not installed — meta-error. Run: python -m pip install pyyaml",
        )
    return yaml


def _dup_safe_loader():
    """중복 키를 `ConstructorError` 로 승격하는 SafeLoader 서브클래스 (lazy build).

    PyYAML `safe_load` 기본 동작 = **마지막 키만 남기고 에러 0** (silent last-wins).
    그 동작 아래서는 `concurrency:` 2회 주입이 "개수 1" 오라클을 통과한다.
    """
    global _DUP_LOADER
    if _DUP_LOADER is not None:
        return _DUP_LOADER
    y = _require_yaml()

    class DupSafeLoader(y.SafeLoader):  # type: ignore[misc,name-defined]
        def construct_mapping(self, node, deep=False):
            # ★ 스캔 대상 = **문면에 리터럴로 적힌 키**뿐이다.
            #   merge key(`<<: *ref`)는 여기서 건너뛴다 — B-F4 회귀 방지.
            #   (근거: SafeConstructor 는 `flatten_mapping()` 으로 merge 노드를 먼저
            #    제거한 뒤 키를 구성한다. 그 전에 `construct_object` 를 호출하면
            #    `tag:yaml.org,2002:merge` 에 constructor 가 없어 ConstructorError 가
            #    난다 — firsthand 실측. merge 로 들어온 키가 명시 키에 의해 override
            #    되는 것은 YAML 정상 의미론이므로 중복 판정 대상도 아니다.)
            seen = set()
            for key_node, _value_node in node.value:
                if getattr(key_node, "tag", None) == "tag:yaml.org,2002:merge":
                    continue
                try:
                    key = self.construct_object(key_node, deep=deep)
                except y.constructor.ConstructorError:
                    # 구성 불가 키는 중복 판정 대상 밖 — 삼키지 않고 super() 로 위임한다
                    # (super().construct_mapping 이 동일 노드에서 다시 raise 한다).
                    continue
                try:
                    duplicated = key in seen
                except TypeError:  # unhashable key — 중복 판정 대상 밖
                    continue
                if duplicated:
                    raise y.constructor.ConstructorError(
                        "while constructing a mapping",
                        node.start_mark,
                        f"duplicate key {key!r} (silent last-wins 차단 — DupSafeLoader)",
                        key_node.start_mark,
                    )
                seen.add(key)
            return super().construct_mapping(node, deep=deep)

    _DUP_LOADER = DupSafeLoader
    return _DUP_LOADER


def dup_safe_load(text: str) -> Any:
    """`DupSafeLoader` 로 파싱 (bare `yaml.safe_load` 대체 — 본 모듈 유일 파싱 진입점)."""
    y = _require_yaml()
    return y.load(text, Loader=_dup_safe_loader())


# ── 반환형 ───────────────────────────────────────────────────────────────────
@dataclass
class WorkflowShape:
    """workflow yml 의 구조 술어 산출 (경로 집합 반환형)."""

    path: str
    job_ids: List[str] = field(default_factory=list)
    top_concurrency: Optional[Dict[str, Any]] = None
    concurrency_paths: List[str] = field(default_factory=list)
    coe_paths: List[str] = field(default_factory=list)
    timeout_paths: Dict[str, Any] = field(default_factory=dict)
    job_if: Dict[str, Any] = field(default_factory=dict)
    step_if: Dict[str, List[Any]] = field(default_factory=dict)
    env_keys: Dict[str, List[str]] = field(default_factory=dict)
    container_env_keys: Dict[str, List[str]] = field(default_factory=dict)
    env_file_keys: Dict[str, List[str]] = field(default_factory=dict)
    step_shell: Dict[str, List[Any]] = field(default_factory=dict)
    defaults_run_shell: Optional[str] = None
    job_defaults_run_shell: Dict[str, Any] = field(default_factory=dict)
    runs_on: Dict[str, Any] = field(default_factory=dict)

    # ── P-5 결속 ────────────────────────────────────────────────────────────
    def require_job(self, jid: str) -> str:
        """P-5 — 질의 대상 job id 실재 확인.

        job id 오타·rename 이 "그 job 에 `continue-on-error` 없음" 을 **공허 참**으로
        만드는 경로를 차단한다.
        """
        if jid not in self.job_ids:
            raise ShapeError(
                "target_job_absent",
                f"target job id not present: {jid!r} (job_ids={self.job_ids})",
                self.path,
            )
        return jid

    # ── 소속 파생 접근자 (카디널리티 파생 규칙 — 경로 열거로만 보고) ────────
    def coe_paths_of(self, jid: str) -> List[str]:
        """job `jid` 소속 `continue-on-error` 경로 (P-5 강제)."""
        self.require_job(jid)
        return paths_owned_by(self.coe_paths, jid)

    def concurrency_paths_of(self, jid: str) -> List[str]:
        self.require_job(jid)
        return paths_owned_by(self.concurrency_paths, jid)

    def timeout_paths_of(self, jid: str) -> Dict[str, Any]:
        self.require_job(jid)
        return {p: v for p, v in self.timeout_paths.items() if _owned_by(p, jid)}

    def job_concurrency_paths(self) -> List[str]:
        """job 하위 `concurrency` 경로 전건 (top-level 제외)."""
        return [p for p in self.concurrency_paths if p != "concurrency"]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── 로딩 (P-1 ~ P-4) ─────────────────────────────────────────────────────────
def _load_mapping(path: str) -> Dict[str, Any]:
    y = _require_yaml()  # P-6

    if not os.path.isfile(path):  # P-1
        raise ShapeError(
            "workflow_file_missing",
            f"workflow file not found (or not a regular file): {path}",
            path,
        )
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:  # 읽기 불가도 "읽지 못한 상태" — GREEN 아님 (INV-5)
        raise ShapeError("workflow_file_missing", f"workflow file unreadable: {path} ({exc})", path)

    try:  # P-2 (중복 키 ConstructorError 포함)
        data = dup_safe_load(text)
    except y.YAMLError as exc:
        raise ShapeError("workflow_parse_error", f"YAML parse failed: {path} ({exc})", path)

    if not isinstance(data, dict):  # P-3
        # 실측: safe_load('') / ('   \n\n') / ('# 주석만\n') → 전건 None,
        #       ('hello') → str, ('- a\n- b') → list.
        raise ShapeError(
            "workflow_not_mapping",
            f"workflow root is not a mapping: {path} (type={type(data).__name__})",
            path,
        )
    return data


def _jobs_of(data: Dict[str, Any], path: str) -> Dict[str, Any]:
    jobs = data.get("jobs")  # B-F2 주의: `on` 은 bool 키지만 `jobs` 는 str 키
    if not isinstance(jobs, dict) or not jobs:  # P-4
        raise ShapeError(
            "jobs_missing_or_empty",
            f"`jobs` key missing or empty mapping: {path}",
            path,
        )
    return jobs


# ── 스캐너 ───────────────────────────────────────────────────────────────────
def _mapping_keys(value: Any) -> List[str]:
    """매핑의 키 목록 (str 화). 비-매핑이면 빈 목록 — 단 경로 자체는 호출측이 등재한다."""
    if not isinstance(value, dict):
        return []
    return [str(k) for k in value.keys()]


# `>> $GITHUB_ENV` / `>> "$GITHUB_ENV"` / `>> "${GITHUB_ENV}"` / `>>'$GITHUB_ENV'`
_GITHUB_ENV_REDIRECT_RE = re.compile(r""">>\s*["']?\$\{?GITHUB_ENV\}?["']?""")
# 리다이렉트 **앞** 구간의 `KEY=` / `KEY<<DELIM` 표기
_ENV_ASSIGN_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|<<)")


def _scan_env_file_keys(run_text: str) -> List[str]:
    """`run` 문면에서 **인라인 `$GITHUB_ENV` 기입** 키를 식별한다.

    ★ 정의역 = **인라인 표기 한정 · 전수 아님** (§8.F C-3). 문서 계약은
      *"`GITHUB_ENV` 가 가리키는 파일에 append"* 이지 특정 표기가 아니므로
      유효 표기 집합은 **셸이 파일에 쓸 수 있는 모든 방법**으로 열려 있다.

    포섭 = **같은 줄에 리다이렉트 ∧ 그 앞 구간에 키 표기** (이것이 정의역 전부):
      * `echo "K=V" >> "$GITHUB_ENV"`      ← 선례: .github/workflows/css-lint.yml L128-129
      * `echo K=V >> $GITHUB_ENV` · `>> "${GITHUB_ENV}"` · `>>'$GITHUB_ENV'`
      * `echo "K<<EOF" >> "$GITHUB_ENV"`   ← 공식 multiline 첫 줄 형태
      * `{ echo 'K=V'; } >> "$GITHUB_ENV"` ← **1줄 형**의 블록 리다이렉트 (firsthand 검출 확인)

    ★ 미포섭 (declared 잔여 — 이 목록이 비었다고 "주입 없음" 으로 인용 금지):
      * **여러 줄 블록 리다이렉트** — 키 줄과 `} >> "$GITHUB_ENV"` 줄이 분리된 형태.
        ★ 공식 문서 multiline 예제 자신이 이 형태다 (firsthand: 미검출 확인)
      * heredoc `cat >> "$GITHUB_ENV" <<'EOF'` (키가 리다이렉트 뒤 다른 줄, firsthand 확인)
      * 스트림 재지정 `exec >> "$GITHUB_ENV"` 이후 임의 stdout
      * 변수 간접화 `F="$GITHUB_ENV"; echo K=V >> "$F"` · `eval`
      * 타 언어 writer (`python -c "open(os.environ['GITHUB_ENV'],'a')"` 등)
      * 간접 호출 `run: ./scripts/setup.sh` (기입이 스크립트 안 — 파일에 0회 등장)
      * `pwsh` 의 `$env:GITHUB_ENV` 표기

    과잉 포착(예: `printf '%s=%s\\n' … >> "$GITHUB_ENV"` 의 `s`)은 **fail-closed
    방향**(과잉 RED)이라 수용한다 — 이 Story 가 겨냥하는 vacuous-pass 와 반대 방향.
    """
    keys: List[str] = []
    if not isinstance(run_text, str):
        return keys
    for line in run_text.splitlines():
        m = _GITHUB_ENV_REDIRECT_RE.search(line)
        if not m:
            continue
        prefix = line[: m.start()]
        for hit in _ENV_ASSIGN_RE.finditer(prefix):
            key = hit.group(1)
            if key not in keys:
                keys.append(key)
    return keys


def _steps_of(job_body: Any) -> List[Any]:
    """job 의 steps 목록. 비-list 는 빈 목록 (reusable workflow `uses:` job 은 steps 부재).

    ★ 원소가 dict 가 아니어도 **인덱스는 소비**한다 — step 인덱스 정렬이 어긋나면
      경로 문자열(`steps[<i>]`)이 실물과 괴리돼 relocation 관측이 무너진다.
    """
    steps = job_body.get("steps") if isinstance(job_body, dict) else None
    return list(steps) if isinstance(steps, list) else []


def _defaults_run_shell(container: Any) -> Optional[Any]:
    """`<container>.defaults.run.shell` 원문 (부재 시 None)."""
    if not isinstance(container, dict):
        return None
    defaults = container.get("defaults")
    if not isinstance(defaults, dict):
        return None
    run = defaults.get("run")
    if not isinstance(run, dict):
        return None
    return run.get("shell")


def load_workflow_shape(path: str) -> WorkflowShape:
    """workflow yml 경로 → `WorkflowShape`. 전제 위반 시 `ShapeError` (P-1~P-6)."""
    data = _load_mapping(path)          # P-1 · P-2 · P-3 · P-6
    jobs = _jobs_of(data, path)         # P-4

    shape = WorkflowShape(path=path, job_ids=[str(j) for j in jobs.keys()])

    # workflow 레벨 ---------------------------------------------------------
    if "concurrency" in data:
        shape.concurrency_paths.append("concurrency")
        raw_top = data.get("concurrency")
        # 비-매핑(`concurrency: some-group` 축약형)은 매핑 전문이 아니므로 None.
        # 경로는 위에서 이미 등재됐다 ⇒ 존재 leg(E1)는 살고 값 leg(E2)만 RED = fail-closed.
        shape.top_concurrency = raw_top if isinstance(raw_top, dict) else None
    if "env" in data:
        shape.env_keys["workflow"] = _mapping_keys(data.get("env"))
    shape.defaults_run_shell = _defaults_run_shell(data)  # A4 — 원거리 1줄 우회 표면

    # job 레벨 --------------------------------------------------------------
    for jid_raw, body in jobs.items():
        jid = str(jid_raw)
        jpath = f"jobs.{jid}"

        if isinstance(body, dict):
            if "concurrency" in body:
                shape.concurrency_paths.append(f"{jpath}.concurrency")
            if "continue-on-error" in body:  # A2
                shape.coe_paths.append(f"{jpath}.continue-on-error")
            if "timeout-minutes" in body:
                shape.timeout_paths[f"{jpath}.timeout-minutes"] = body.get("timeout-minutes")
            if "env" in body:
                shape.env_keys[jpath] = _mapping_keys(body.get("env"))
            if "runs-on" in body:
                shape.runs_on[jid] = body.get("runs-on")
            container = body.get("container")
            if isinstance(container, dict) and "env" in container:  # §8.F 채널 #6
                shape.container_env_keys[jid] = _mapping_keys(container.get("env"))
            shape.job_if[jid] = body.get("if")
            shape.job_defaults_run_shell[jid] = _defaults_run_shell(body)  # A5
        else:
            # job body 가 매핑이 아님 — 값을 만들어내지 않고 부재로 남긴다.
            shape.job_if[jid] = None
            shape.job_defaults_run_shell[jid] = None

        # step 레벨 ---------------------------------------------------------
        step_ifs: List[Any] = []
        step_shells: List[Any] = []
        env_file_keys: List[str] = []
        for idx, step in enumerate(_steps_of(body)):
            spath = f"{jpath}.steps[{idx}]"
            if not isinstance(step, dict):
                step_ifs.append(None)
                step_shells.append(None)
                continue
            if "continue-on-error" in step:  # A1
                shape.coe_paths.append(f"{spath}.continue-on-error")
            if "timeout-minutes" in step:
                shape.timeout_paths[f"{spath}.timeout-minutes"] = step.get("timeout-minutes")
            if "env" in step:
                shape.env_keys[spath] = _mapping_keys(step.get("env"))
            step_ifs.append(step.get("if"))
            step_shells.append(step.get("shell"))  # A3 · A7
            for key in _scan_env_file_keys(step.get("run")):  # §8.F 채널 #5
                if key not in env_file_keys:
                    env_file_keys.append(key)

        shape.step_if[jid] = step_ifs
        shape.step_shell[jid] = step_shells
        if env_file_keys:
            shape.env_file_keys[jid] = env_file_keys

    return shape


# ── 파생 접근자 ──────────────────────────────────────────────────────────────
_MISSING = object()


def runs_on_local_delta(shape: WorkflowShape, canon: Dict[str, Any]) -> Dict[str, Any]:
    """정본 `runs-on` 대비 **실 로컬 개조**만 남긴 파생값.

    `{jid: v for jid, v in runs_on.items() if v != CANON_RUNS_ON[jid]}` — 정본 값과
    **문자열 동일성** 비교.

    ★ E8 판정은 **이 파생값 위에서만** 한다. 원시 `shape.runs_on` 은 정본 상속값을
      포함하므로 그 위의 assert 는 **항진(무조건-참) = 판별력 0** 이다 (T-taut 대조군 전용).

    `canon` 에 없는 job id 는 정본 대비 신규이므로 **delta 로 계상**한다(fail-closed).
    `canon` 핀 리터럴의 SSOT = W-14 fixture (본 모듈은 정본 값을 내장하지 않는다).
    """
    return {jid: v for jid, v in shape.runs_on.items() if v != canon.get(jid, _MISSING)}


# ── CLI ──────────────────────────────────────────────────────────────────────
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workflow_shape.py",
        description="GitHub Actions workflow 구조 술어 (CFP-2978 W-13, S2 wrapper 검증면 전용)",
    )
    parser.add_argument("workflow", help="대상 workflow yml 경로")
    parser.add_argument(
        "--job",
        action="append",
        default=[],
        metavar="JOB_ID",
        help="P-5 강제 — 해당 job id 실재 확인 (반복 지정 가능)",
    )
    args = parser.parse_args(argv)

    try:
        shape = load_workflow_shape(args.workflow)
        for jid in args.job:
            shape.require_job(jid)  # P-5
    except ShapeError as exc:
        # INV-5 — 읽지 못한 상태의 종결은 exit 2 이지 exit 0 이 아니다.
        print(json.dumps(exc.to_payload(), ensure_ascii=False), file=sys.stderr)
        return 2

    print(json.dumps(shape.to_dict(), ensure_ascii=False, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
