#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_infra_resource_drift.py
CFP-2700 (Epic) G2 / ADR-157 §결정3(D3) + §결정6(D4) — infra-resource manifest drift scan
  (인프라 자원 선언 manifest ↔ 실 참조면 대조, census-floor oracle, warning tier / ADR-060 §결정5 3-tier).

대상 = wrapper-self(및 consumer 상속) 인프라 env-key 소비면. manifest(`.claude/_overlay/project.yaml`
  `infra_resources:` block)가 선언한 자원 카탈로그(canonical_env + accepted/deprecated alias)와, repo 안
  실 참조면(workflow `secrets.<KEY>` + project.yaml `<lower>_env: <KEY>` + scripts 정적 env-key 리터럴)을
  대조한다. 미선언 표면(참조되나 manifest 未등재 = drift 원천)을 각 참조면에서 loud 검출하고, 선언되었으나
  어디서도 참조되지 않는 자원(orphan = dead 선언)을 별도 tier 로 표면화한다. base scan 한정 —
  cross-repo 대조(G5) · startup fail-closed(D2/G3)는 본 스캐너 정의역 밖(ADR-157 §결정4/§결정7(e)).

★ live violation 대상 vs census inert (ADR-157 §결정9.1 / §결정9.2 — corpus 완전 열거):
  - LIVE(candidate, undeclared 판정 대상):
    · `.github/workflows/*.yml|*.yaml` — `secrets.<KEY>`(form=signal) + `<lower>_env: <KEY>`(form=signal).
    · `.claude/_overlay/project.yaml` — `<lower>_env: <KEY>`(form=signal). 단 `infra_resources:` block 은
      manifest 자체(소비면 아님)라 SELF_EXCLUDE(canonical_env: 선언을 소비로 오판 차단).
    · `scripts/**/*.py` — QUOTED uppercase 리터럴 중 infra-signal 매치(§결정7(b) 참조).
    · `scripts/**/*.sh` — env-passthrough 자기참조형 `VAR="${VAR}" <cmd>` 만(§결정8(vi) carve-in, 아래).
  - CENSUS inert(관측만, violation 아님 — §결정9.2 predicate): `examples/**` + `presets/**` 의 env-position
    infra-signal 토큰. 데모/템플릿 경로는 execution_unit 이 아니므로 required 대조 대상 아님 → inert 로 흡수
    (born-hollow(candidates==0 ∧ inert==0) 회피의 필요조건 ④⊃②). presets/ 부재 시 glob 0 매치 = 정상.

★ infra-signal surgical scope (ADR-157 §결정7(b) FM1-false-positive seal operationalization — 리뷰 대상):
  scripts/examples/presets 의 bare uppercase 토큰을 전부 flag 하면 ADR-011 path-prefix 오판형 born-red
  (STORY_KEY 85회 등 parse-token 오탐)을 재현한다. 따라서 리터럴 참조 후보를 다음으로 surgical narrow:
    (1) QUOTED string literal 만 후보 (bare 식별자 `STORY_KEY=""` 제외 — 변수명 ≠ env-key 리터럴).
        `SECRET_ENV_VARS = ["CONFLUENCE_API_TOKEN"]`(ADR §결정9.1 예시)는 quoted → 후보.
    (2) infra-signal 매치: suffix ∈ {_TOKEN,_SECRET,_KEY,_PASSPHRASE,_PASSWORD,_PAT,_CREDENTIAL,_URL,
        _DSN,_ACCESS_KEY} OR infix `_API_`.
    (3) `MOCK` 부분문자열 제외 — 테스트 mock fixture(CFP1495_API_MOCK_429 / MOCK_API_401 류)는 인프라
        자격증명 아님. (2)의 `_API_` infix 가 mock 을 오탐하므로 (3)으로 정정. 이 3-piece 는 §결정7(b)
        "surgical scope + allowlist" 의 operationalization 이며 ArchitectPL 리뷰 대상(write-time declaration).
  form-based(secrets. / _env:)는 (2)(3) 미적용 — FORM 이 signal 이라 suffix 무관 infra(예 ATLASSIAN_USER_EMAIL
  은 _EMAIL suffix 라 infra-signal 미매치이나 `user_email_env:` form 으로 infra 확정).

★ 확장자 dispatch — `.py` QUOTED / `.sh` env-passthrough 한정 (§결정8(vi) carve-in):
  `_scan_script` 는 확장자로 추출 form 을 가른다. 근거 = 언어별 "키 리터럴 position" 의 판별력 차이(실측).
    · `.py` → QUOTED 경로(위 3-piece). 실측 정밀도 100% — 변경 없음.
    · `.sh` → env-passthrough 자기참조형 `VAR="${VAR}" <cmd>` 만(`_RE_SHELL_ENV_PASSTHROUGH`). shell 에서
      이 form 은 뒤 명령에 env 를 넘기는 자리라 좌변이 **키 리터럴 position 과 등가** — 실측 1 hit / 0 FP.
      `.sh` 의 QUOTED 경로는 제거했다: (a) 승격 시점 실측 0 hit 이라 동작보존(behavior-preserving),
      (b) 장래 `grep "API_TOKEN" f` 류 **문자열 인자**를 키 참조로 오판하는 FP 를 선제 차단(shell 은 python 과
      달리 quoted 문자열이 리터럴 인자로 흔함).
  ※ 미채택 대안(정직 기록): shell `${VAR}` **읽기 일반형** 스캔은 실측 정밀도 ≈18-20%(163파일 11 hit /
    진성 2 / FP = STORY_KEY×6·PAGE_TOKEN·ISSUE_URL) → §결정7(b) FM1(오탐 봉인) 위반이라 미채택. 잔여
    미검출은 아래 ★정직 천장 (vi) 로 공개하며, PIN-NEGATIVE self-test 가 그 천장을 **집행**한다.

★ AC-7 substring 오분류 제외 (structural extraction, NOT filename-substring classification):
  파일이 env-surface 인지 판정은 STRUCTURAL(실 yaml `secrets.`/`_env:`/env-mapping 위치 / quoted 리터럴)로만.
  파일명에 "compose" 부분문자열(예 team-spec-decompose.yaml — "decompose")이 있어도 실 env-key 0 이면 0 flag.
  파일명이 쓰이는 곳은 corpus 편입 판정 2곳뿐 — (a) glob 멤버십 (b) `_self_exempt` self-source 제외
  (`_SELF_SOURCE_TOKENS` 부분문자열 매치, FM1 seal). 즉 "어떤 파일을 열지"는 이름 기반이나, "그 안에서
  무엇을 env-key 로 추출·분류할지"는 라인 구조로만 판정한다 — 추출면 name-based 분류 0(= AC-7 subject).

★ none-disguise anti-hollow (ADR-157 §결정8 / AC-10·AC-11):
  manifest `infra_resources:` block 부재, 또는 present-but-empty(resources 0) 이면서 `reason`(사유) 필드
  부재인데 LIVE 스캔이 infra 표면 ≥1 을 찾으면 = hollow "none" 위장 → exit 1(baseline 로 억제 불가).

★ census 3-count + born-hollow guard (anti-hollow observability — CFP-2661 §결정15.b 동형):
  candidates_scanned(live judged) / inert_skipped(examples·presets 관측) / undeclared(new, baseline subtract 후)
  / orphan / grandfathered emit. verdict warning-tier(fail-open, PR 미차단) but census fail-closed —
  candidates==0 ∧ inert==0(빈 corpus/empty-scope) → PASS 아니라 FAIL(exit 3, born-hollow). all-inert
  (candidates==0 ∧ inert>0)는 non-vacuous PASS(census 로 관측, over-state "candidate≥1" 금지 — F-CR-2).

★ per-class census floor (CFP-2719 §3.8 — 설계리뷰 P0-1 봉합):
  hard-gate-self-verification: enrolled
  identity_bearing: true
  전역 guard(candidates==0 ∧ inert==0)만으로는 live/inert 가 disjoint 별도 glob 루프라 inert>0 이
  guard 를 꺼서 glob 오타/경로 이동 시 live 열거가 침묵 사망 = 영구 GREEN. 봉합 = 게이트가 자기 스캔
  class 기대치(EXPECTED_NONEMPTY_SCAN_CLASSES = workflow/script/inert)를 선언하고 매 실행 열거 실적과
  대조 — 선언 class 의 glob 열거 파일 수(enumerated file count) == 0 → exit 3. 기준 = candidates
  (추출 결과)가 아니라 glob 열거 파일 수(파일 내용/추출 결과 무관) — mutation-kill 표적이 glob 상수
  (LIVE_WORKFLOW_GLOBS/LIVE_SCRIPT_GLOBS/INERT_GLOBS)이기 때문. 기존 전역 guard 와 OR 결합(전역 guard
  유지). per-class census floor = internal-control identity probe — known-present class(wrapper-self
  기준 3 class 전부 상시 열거>0)의 0 열거 = 계기 사망을 known-answer 로 검출한다. 무조건 활성 —
  opt-in flag 금지(default-off flag = dark-path 재생산, §3.8 명시 기각). compose/overlay 는 미선언
  (wrapper compose=0 정당 / overlay=manifest 부재 exit 2 기커버 — 추가 금지). F-CR-2(all-inert
  non-vacuous PASS)와 무충돌 — floor 는 candidates 축이 아니라 선언-기반 열거 축(all-inert 시나리오는
  열거>0 이므로 무손상).

★ D4 역색인 (ADR-157 §결정6 — 비커밋 ephemeral CI artifact, I-1):
  `--emit-reverse-index` 는 resource-id → [참조 표면] 을 stdout 으로만 방출(커밋 0). VERDICT(census +
  undeclared + orphan + exit code)는 manifest + fresh scan 에서만 도출하며 어떤 커밋/on-disk 역색인도
  read-back 하지 않는다 → 역색인 변조로 판정 불변(I-1). freshness 결박 불요(매 실행 재생성).

★ grandfather baseline (ADR-060 §결정6 Amd20 monotonic shrink — CFP-2661 mirror):
  `docs/infra-resource-baseline.yaml` 가 승격 시점 pre-existing 미선언 `(file, env-key)` pair 를 동결 →
  new-only subtract. baseline 은 candidate/inert census 를 감소시키지 않음(anti-hollow). `--write-baseline`
  은 GENERATED 헤더로 재생성(수기 편집 금지). 잔존 debt 의 목록·건수·키 = `docs/infra-resource-baseline.yaml`
  실파일이 유일 SSOT — 본 주석은 **수치·키를 열거하지 않는다**(CFP-2697 citation-drift 선례: 주석에 박은
  수치가 baseline shrink 를 따라가지 못해 stale 화한다. 그 실패 모드를 경고하면서 바로 아래에 수치를
  박아두는 자기모순이 CFP-2700 G2 리뷰에서 실제 검출됐다 → 열거 삭제, 파일 참조만 유지).
  전건 진성 undeclared(오탐 아님) — manifest 등재로 shrink 가능.

  ▸ monotonic shrink 강제 (실배선 — 선언만 있고 미구현이던 상태를 코드가 따라감):
    `--write-baseline` 은 기존 baseline 을 로드해 `added = new_pairs - old_pairs` 를 계산하고, added 가
    비어있지 않으면 **거부**(exit 1)한다 = baseline 은 줄어들 수만 있다. 정당한 corpus 확장(스캐너 범위
    확대 등)은 `--allow-baseline-growth --reason "<사유>"` 로만 통과하며 사유가 baseline 에 각인된다
    (escape hatch 부재 시 정당 확장이 hard-block 돼 **수기편집**이라는 더 나쁜 실패로 유인되기 때문).
  ▸ content_digest tamper-evident (선례 형상 복사 — `check_deferred_followup_reconcile.py`
    `compute_content_digest`, AC-16 신규발명 0):
    canonical 정렬 `(file, env_key)` pair 에 대한 sha256. `reason`/헤더/주석은 digest **제외**(선례의
    provenance 제외 답습 — 사유 문구 편집이 tamper 로 오판되지 않게). 불일치/필드부재 = **exit 3**
    (substrate-failure, census born-hollow 와 동급): 손상된 baseline 은 undeclared 판정 자체를 vacuous 하게
    만드는 전제조건 실패라 finding(warning) 채널이 아니다. write path 도 동일 — 손상 baseline 은 shrink
    기준으로 신뢰 불가 → `--allow-baseline-growth` 로 명시 재생성해야 통과(untrusted old ⇒ 비확장 증명 불가).

★ 정직 천장 (ADR-157 §결정8 — "완전 봉인" hard-claim 금지):
  (i) 프록시 위장(socat) 미검출 (ii) 자기신고 누락(실행단위 미신고 required) census-floor 부분검출만
  (iii) 동적 구성 env 키(런타임 문자열 조립) out-of-scope — 정적 리터럴만 결정가능·in-scope
  (iv) 스캔 밖 표면(secret manager / 외부 deploy / 수동 운영 스크립트) (v) 기동 후 런타임 변조.
  (vi) shell 변수읽기면 (`$VAR` / `${VAR}` / `${VAR:-}`) 미검출 — shell 은 범용 변수읽기 form 이라
    지역변수와 env 읽기가 어휘적으로 동일하고, `secrets.` 같은 namespace 도 python 인용 키 리터럴 같은
    position 도 없다 ∴ form 이 infra 의미를 보증하지 않는다. 실측(`scripts/*.sh` 163 파일 전수) =
    11 hit 중 진성 2 / 오탐 9(STORY_KEY×6 · PAGE_TOKEN · ISSUE_URL · NEW_TOKEN) = **정밀도 약 18%** →
    §결정7(b) FM1-false-positive 봉인 위반(만성 오탐 → bypass 상시화 = ADR-011 death mode 재현)이라
    **미채택**. carve-in = 키 리터럴 position 등가인 env-passthrough(`VAR="${VAR}" <cmd>`) 한정
    (실측 1 hit / 0 오탐). `.sh` 변수읽기면은 **base corpus 에는 속하나 검출 대상이 아니다**.
    잔여(정직): ① passthrough 아닌 형태로만 소비되는 env-key 는 undeclared 로 안 잡힘 ② shell 로만
    소비되는 자원은 **false-orphan**(선언됐으나 미참조로 오판) 가능 — 현 live blast radius = 0
    (실측 orphan=0, 선언 자원 전건이 workflow `secrets.` 참조면 보유 → 잠재이지 live 아님) = 기수용 리스크.
    ※ 본 (vi) 는 산문 아니라 **PIN-NEGATIVE self-test 로 집행**된다(naive form/bare 스캔 재도입 → RED).
    ※ ADR-157 §결정8(vi) 와 **wording SSOT 일치 의무**(ADR-068 I-4) — 어느 한쪽만 갱신 = 설계리뷰 P0.
  presence ≠ truth (bounded degradation) — 정적 선언-대조 class 의 구조적 상한.

★ input-driven resource exhaustion safety (SecurityArch non-negotiable — ADR-157 §7.2, CFP-2661 SF-1 선례):
  유일 위협 축 = adversarial 입력 파일(초장문 라인 / 폭발적 리터럴)의 파서 자원 고갈(DoS). 완화 bound:
    (1) regex : 전 regex anchored + bounded quantifier(`{0,N}`/`{2,64}`), nested quantifier 0.
    (2) 물리라인 length : MAX_PHYSICAL_LINE_LEN per-line truncate-scan (정당 코드 미도달).
    (3) 복잡도 : O(n) 라인 단위 스캔 — slice-in-loop O(n²) 금지. 토큰 추출은 bounded 토큰에 O(1) 판정.
    (4) read-path : itertools.islice(f, PER_FILE_SCAN_CAP) 로 라인 count bound.
  No eval/exec/yaml.safe_load(순수 substring/regex 라인 파서) — injection 0. No path-traversal:
  스캔 대상 = repo-relative glob, 임의 경로 open 0. bounded degradation — "임의 입력 무해" 가 아님(정직 천장).

CLI 계약 (ADR-061 house style — 고정, self-test + workflow 소비):
  bash scripts/check-infra-resource-drift.sh [--repo-root DIR] [--manifest PATH] [--baseline PATH]
    [--promote-orphan] [--write-baseline] [--allow-baseline-growth --reason TEXT] [--emit-reverse-index]

Exit codes (ADR-060 §결정5 3-tier — verdict warning / census·substrate fail-closed):
  0 = PASS (new undeclared 0; orphan warning-only unless --promote-orphan; census non-vacuous).
  1 = FLAG (≥1 NEW undeclared surface OR none-disguise hollow OR orphan present WITH --promote-orphan) — warning.
      + baseline growth 거부(--write-baseline 이 monotonic shrink 위반을 검출 = 작성자 조치 필요 finding).
  2 = usage 오류(argparse; --allow-baseline-growth 의 --reason 누락 포함) / manifest 부재·unreadable(OSError).
      ※ malformed manifest 는 exit 2 아님 — 본 스캐너는 라인 파서(no yaml.safe_load)라 "malformed" 를
        구조적으로 판정할 수단이 없다. 깨진 manifest 는 부분 파싱되어 resources 0 으로 귀결되고,
        LIVE 표면이 있으면 none-disguise 경로(exit 1)로 표면화된다. "malformed → exit 2" 보장 없음
        (정직 천장 — dependency-free 파서의 구조적 상한이며, 오탐 0 을 위해 감수한 trade-off).
  3 = census fail-closed / born-hollow (전역 candidates==0 ∧ inert==0 — OR per-class census floor:
      EXPECTED_NONEMPTY_SCAN_CLASSES 선언 class 의 glob 열거 파일 수 0, CFP-2719 §3.8) — OR baseline
      substrate-failure (content_digest 불일치·필드부재 = 손상 baseline → verdict 전제조건 파손,
      위 grandfather 블록 참조).
      ※ 현 workflow 는 `continue-on-error: true` 라 오늘은 exit 3 도 PR 을 차단하지 못하고 surfacing 만
        된다(정직 표기 — "fail-closed" 는 스캐너 exit 계약 면의 사실이며, CI 차단력은 별개 축이다).

ADR refs: ADR-157 §결정3/§결정6/§결정7/§결정8/§결정9 (carrier) / ADR-060 §결정5 (warning tier) /
  ADR-061 §결정1 (Python SSOT + thin wrapper) / ADR-005 (byte-identical workflow pair) /
  ADR-119 (게이트=ground-truth, 오탐 저감) / ADR-127 (1 Story = 2 PR).
"""

import argparse
import glob
import hashlib
import itertools
import json
import os
import re
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability 답습).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────── input-driven exhaustion bounded 상수 ───────────────────
PER_FILE_SCAN_CAP = 6000        # per-file 물리 라인 count bound (read-path).
MAX_PHYSICAL_LINE_LEN = 8192    # per-physical-line 길이 bound (정당 코드 미도달, 초과분 truncate).
MAX_BLOCK_SPAN = 4000           # infra_resources block 누적 라인 상한 (병리 방어).

# ─────────────────────── corpus glob (ADR-157 §결정9.1 완전 열거) ────────────────
# LIVE violation 대상 (candidates 기여):
LIVE_WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")
LIVE_PROJECT_YAML_REL = ".claude/_overlay/project.yaml"
# F-CR-005 정정: 구 ("scripts/*.py", "scripts/*.sh", "scripts/lib/*.py") 는 비재귀라 ADR-157 §9.1 의
#   선언(`scripts/**`)과 불일치했다(scripts/jira-channel/*.sh · scripts/lib/*.sh 등 미스캔). 선언에
#   코드를 맞춘다 — 재귀 확장의 실측 영향 = corpus +10 file / 신규 live 표면 0(= verdict·baseline 무변).
LIVE_SCRIPT_GLOBS = ("scripts/**/*.py", "scripts/**/*.sh")
# CENSUS inert (§결정9.2 — 관측만, violation 아님). presets/ 부재 시 glob 0 매치 = 정상.
INERT_GLOBS = (
    "examples/**/*.yml", "examples/**/*.yaml", "examples/**/*.env", "examples/**/Dockerfile",
    "presets/**/*.yml", "presets/**/*.yaml", "presets/**/*.env", "presets/**/Dockerfile",
)

# per-class census floor 선언 (CFP-2719 §3.8 — wrapper-self 기준): 선언 class 는 매 실행 glob 열거
#   파일 수 ≥1 이어야 한다 (0 = 계기 사망 → exit 3). 무조건 활성 — opt-in flag 금지(§3.8 명시 기각).
#   compose/overlay 는 미선언(추가 금지 — wrapper compose=0 정당 / overlay=manifest 부재 exit 2 기커버).
EXPECTED_NONEMPTY_SCAN_CLASSES = ("workflow", "script", "inert")
# class ↔ glob 상수명 (floor 발동 메시지용 — 죽은 class 의 mutation-kill 표적 상수를 명시).
_SCAN_CLASS_GLOB_CONST = {
    "workflow": "LIVE_WORKFLOW_GLOBS",
    "script": "LIVE_SCRIPT_GLOBS",
    "inert": "INERT_GLOBS",
}

# self-source EXEMPT (FM1 seal — 스캐너 소스·wrapper·baseline·생성 역색인 제외).
_SELF_SOURCE_TOKENS = (
    "check_infra_resource_drift",
    "check-infra-resource-drift",
    "infra-resource-baseline",
)

DEFAULT_MANIFEST_REL = ".claude/_overlay/project.yaml"
DEFAULT_BASELINE_REL = "docs/infra-resource-baseline.yaml"

# ─────────────────────── infra-signal surgical scope (§결정7(b) operationalization) ──
# bounded 토큰(추출 시 이미 [A-Z][A-Z0-9_]{2,64} 로 길이 제한)에 anchored suffix 판정 — nested quantifier 0.
_INFRA_SUFFIX_RE = re.compile(
    r"(_TOKEN|_SECRET|_KEY|_PASSPHRASE|_PASSWORD|_PAT|_CREDENTIAL|_URL|_DSN|_ACCESS_KEY)$"
)


def _is_infra_signal(token):
    """리터럴 후보(scripts/examples/presets) infra-signal 판정 — suffix OR `_API_` infix, MOCK 제외.

    form-based(secrets./_env:)에는 미적용(FORM 이 signal). MOCK 부분문자열 = 테스트 fixture(§결정7(b) (3)).
    """
    if "MOCK" in token:
        return False
    if _INFRA_SUFFIX_RE.search(token):
        return True
    if "_API_" in token:
        return True
    return False


# ─────────────────────── bounded 추출 regex (anchored, nested-quantifier 0) ──────
_RE_SECRETS = re.compile(r"secrets\.([A-Z][A-Z0-9_]{2,64})")
# `_env:` 값 앞 공백 bound = {0,40} — yaml 정렬 padding 흡수. 구 {0,4} 는 pad≥5 를 침묵 미탐(F-CR-003:
#   candidate 로도 미계수 = silent drop). `secrets.<KEY>` 는 문법상 pad 면이 없어(구분자 `.`) 애초 무영향 —
#   {0,40} 확장이 그 비대칭을 해소한다. anchored + bounded 유지(nested quantifier 0), DoS bound 는
#   MAX_PHYSICAL_LINE_LEN 소관이라 본 확장과 disjoint.
_RE_ENV_VALUE = re.compile(r"\b[a-z][a-z0-9_]{0,40}_env:\s{0,40}[\"']?([A-Z][A-Z0-9_]{2,64})")
_RE_QUOTED_TOKEN = re.compile(r"[\"']([A-Z][A-Z0-9_]{2,64})[\"']")
# `.sh` env-passthrough 자기참조형: `VAR="${VAR}" <cmd>` / `VAR="${VAR:-def}" <cmd>` (§결정8(vi) carve-in).
#   역참조 `\1` = 좌변과 우변 키가 **동일**할 것을 강제 → `X="${SCRIPT_DIR}/f"` 류 일반 변수읽기 미매치.
#   trailing `\s{1,80}\S` = 뒤에 실행할 명령이 올 것을 요구 → `X="${X:-default}"`(단순 기본값 대입) 미매치.
#   anchored(^) + 전 quantifier bounded + nested quantifier 0 (born-safe 불변 유지 — 위 (1) 참조).
_RE_SHELL_ENV_PASSTHROUGH = re.compile(
    r"^\s{0,80}([A-Z][A-Z0-9_]{2,64})=\"\$\{\1(?::-[^}]{0,64})?\}\"\s{1,80}\S"
)
# examples/presets env-position: yaml mapping key / env `KEY=` / list `- KEY=` (bare) + quoted.
_RE_ENV_POSITION = re.compile(r"^\s{0,80}-?\s{0,4}([A-Z][A-Z0-9_]{2,64})\s{0,4}[:=]")


# ─────────────────────── 공통 read (born-safe read-path) ────────────────────────

def _read_physical(path):
    """islice read cap + per-physical-line truncate. 실패 → None."""
    try:
        physical = []
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, PER_FILE_SCAN_CAP):
                line = raw.rstrip("\n").rstrip("\r")
                if len(line) > MAX_PHYSICAL_LINE_LEN:
                    line = line[:MAX_PHYSICAL_LINE_LEN]
                physical.append(line)
        return physical
    except OSError:
        return None


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


def _strip_hash_comment(text):
    """따옴표 밖 첫 `#` 이후 제거 (yaml/python/shell inline 주석). FP-안전(불확실=절단)."""
    in_s = in_d = False
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "'" and not in_d:
            in_s = not in_s
        elif c == '"' and not in_s:
            in_d = not in_d
        elif c == "#" and not in_s and not in_d:
            return text[:i]
        i += 1
    return text


# ─────────────────────── manifest 파서 (dependency-free — born-safe, no yaml import) ──

class Manifest:
    # plane B(`execution_units{}`)는 G2 시점엔 미보관이었으나(당시 소비처 0 = dead path 회피,
    #   CFP-2661 선례), G3/D2 가 실 소비처(check_infra_manifest_schema.py 스키마 검증 +
    #   infra_startup_validator.py startup fail-closed)로 착지하며 **test 동반 추가**됐다(CFP-2700 G3 —
    #   "소비처가 생기면 그 때 test 와 함께 추가" 원칙 이행). 파서를 여기 단일 SSOT 로 유지하는 근거 =
    #   AC-9 allow-set parity by construction — D3 스캐너와 D2 startup validator 가 같은 파서를 소비하면
    #   허용집합 재구현 불일치가 구조적으로 불가능하다. 스캐너 *verdict* 는 여전히 plane B 무소비
    #   (ADR-157 §결정4 — startup fail-closed 는 본 스캐너 정의역 밖, header 참조).
    __slots__ = ("present", "resources", "none_sentinel", "has_reason",
                 "classified", "all_keys_by_resource", "execution_units",
                 "startup_validation")

    def __init__(self):
        self.present = False
        # [{id, canonical_env, accepted[], deprecated[]}] — F-CR-003: `namespace` 는 파싱만 되고 어떤
        #   verdict/출력도 읽지 않는 write-only dead field 였다(선언≠배선) → 파싱 제거. 소비처가 생기면
        #   그 때 test 와 함께 추가한다(alias_to_canonical 을 같은 근거로 제거한 F-CR-006 선례 답습).
        self.resources = []
        self.none_sentinel = False
        self.has_reason = False
        self.classified = set()           # {canonical ∪ accepted ∪ deprecated names} = AC-9 allow_set
        self.all_keys_by_resource = {}    # {resource-id: {keys}} — orphan 판정 + 역색인 소비.
        # plane B (G3 소비처 전용 — 스캐너 verdict 무소비): {unit: {"required": [rid],
        #   "modes": {rid: mode}, "degraded_behavior": {rid: text}}}. `_degraded_behavior` suffix 키는
        #   mode 엔트리가 아니라 metadata (F-CLA-004 파서 계약 — strip 후 별도 보관).
        self.execution_units = {}
        # D2 채택 선언 (AC-15 — ADR-157 §결정2 I-5 채택-bounded): {"adopted": bool|None, "reason": str|None}.
        self.startup_validation = {"adopted": None, "reason": None}


def _parse_inline_list(value):
    """`[A, B, C]` inline yaml list → [A,B,C]. bracket 없으면 단일 스칼라 1-list."""
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    if not v:
        return []
    return [v.strip('"').strip("'")]


def _find_infra_block(physical):
    """`infra_resources:` block 의 (start_idx, end_idx) 반환 (0-based, end exclusive). 부재 → None.

    block = infra_resources: 라인 다음부터, indent 0 non-blank/non-comment(새 top-level key) 또는 EOF 까지.
    """
    start = None
    for idx, line in enumerate(physical):
        if re.match(r"^infra_resources:\s*(#.*)?$", line) or re.match(r"^infra_resources:\s*\S", line):
            start = idx
            break
    if start is None:
        return None
    end = len(physical)
    for idx in range(start + 1, min(len(physical), start + 1 + MAX_BLOCK_SPAN)):
        line = physical[idx]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if _indent_of(line) == 0:
            end = idx
            break
    return (start, end)


def parse_manifest(path):
    """manifest 파일 → Manifest. 파일 부재/unreadable → None (exit 2 유발)."""
    physical = _read_physical(path)
    if physical is None:
        return None
    m = Manifest()
    span = _find_infra_block(physical)
    if span is None:
        # infra_resources block 부재 — present=False (none-disguise 판정 대상).
        m.present = False
        return m
    m.present = True
    start, end = span
    block = physical[start:end]

    # none-sentinel / reason 감지 (present-but-empty 위장).
    header = _strip_hash_comment(block[0]).strip()
    if re.match(r"^infra_resources:\s*none\s*$", header):
        m.none_sentinel = True
    for line in block:
        code = _strip_hash_comment(line)
        s = code.strip()
        if re.match(r"^resources:\s*none\s*$", s) or re.match(r"^resources:\s*\[\s*\]\s*$", s):
            m.none_sentinel = True
        if re.match(r"^reason(_none)?:\s*\S", s):
            m.has_reason = True

    # resources / execution_units / startup_validation 서브블록 파싱 (indentation 라인 파서).
    section = None            # 'resources' | 'units'(plane B — G3 소비처) | 'sv'(startup_validation)
    cur_res = None
    in_accepted = False
    in_deprecated = False
    cur_unit = None
    in_unit_required = False
    in_unit_modes = False

    for line in block[1:]:
        code = _strip_hash_comment(line)
        stripped = code.strip()
        if not stripped:
            continue
        indent = _indent_of(code)

        # 최상위 서브섹션 전환 (indent 2 기준).
        if re.match(r"^resources:\s*$", stripped) and indent <= 2:
            section = "resources"
            cur_res = None
            in_accepted = in_deprecated = False
            continue
        if re.match(r"^execution_units:\s*$", stripped) and indent <= 2:
            # 경계 인식 (resources 파싱 종료 + 마지막 자원 flush) 후 plane B 파싱 진입 —
            #   소비처 = G3(check_infra_manifest_schema / infra_startup_validator), 스캐너 verdict 무소비.
            if cur_res is not None:
                m.resources.append(cur_res)
                cur_res = None
            section = "units"
            cur_unit = None
            in_unit_required = in_unit_modes = False
            continue
        if re.match(r"^startup_validation:\s*$", stripped) and indent <= 2:
            # D2 채택 선언 sub-block (AC-15) — adopted/reason 2 필드만.
            if cur_res is not None:
                m.resources.append(cur_res)
                cur_res = None
            section = "sv"
            cur_unit = None
            in_unit_required = in_unit_modes = False
            continue

        if section == "resources":
            mm = re.match(r"^-\s+id:\s*(.+?)\s*$", stripped)
            if mm:
                if cur_res is not None:
                    m.resources.append(cur_res)
                cur_res = {"id": mm.group(1).strip().strip('"').strip("'"),
                           "canonical_env": None,
                           "accepted": [], "deprecated": []}
                in_accepted = in_deprecated = False
                continue
            if cur_res is None:
                continue
            mm = re.match(r"^canonical_env:\s*(.+?)\s*$", stripped)
            if mm:
                cur_res["canonical_env"] = mm.group(1).strip().strip('"').strip("'")
                in_accepted = in_deprecated = False
                continue
            if re.match(r"^aliases:\s*$", stripped):
                in_accepted = in_deprecated = False
                continue
            mm = re.match(r"^accepted:\s*(.*)$", stripped)
            if mm:
                rest = mm.group(1).strip()
                if rest:
                    cur_res["accepted"].extend(_parse_inline_list(rest))
                    in_accepted = False
                else:
                    in_accepted = True
                in_deprecated = False
                continue
            if re.match(r"^deprecated:\s*$", stripped):
                in_deprecated = True
                in_accepted = False
                continue
            if in_accepted:
                mm = re.match(r"^-\s+(.+?)\s*$", stripped)
                if mm:
                    cur_res["accepted"].append(mm.group(1).strip().strip('"').strip("'"))
                    continue
            if in_deprecated:
                mm = re.match(r"^-\s+name:\s*(.+?)\s*$", stripped)
                if mm:
                    cur_res["deprecated"].append(mm.group(1).strip().strip('"').strip("'"))
                    continue
            continue
        if section == "units":
            # plane B 파싱 (CFP-2700 G3 — 소비처: 스키마 validator + startup validator, test 동반).
            mm = re.match(r"^required:\s*(.*)$", stripped)
            if mm and cur_unit is not None:
                rest = mm.group(1).strip()
                if rest:
                    cur_unit["required"].extend(_parse_inline_list(rest))
                    in_unit_required = False
                else:
                    in_unit_required = True
                in_unit_modes = False
                continue
            if re.match(r"^resource_modes:\s*$", stripped) and cur_unit is not None:
                in_unit_modes = True
                in_unit_required = False
                continue
            if in_unit_required and cur_unit is not None:
                mm = re.match(r"^-\s+(.+?)\s*$", stripped)
                if mm:
                    cur_unit["required"].append(mm.group(1).strip().strip('"').strip("'"))
                    continue
            if in_unit_modes and cur_unit is not None:
                mm = re.match(r"^([A-Za-z0-9._-]{1,128}):\s*(.+?)\s*$", stripped)
                if mm:
                    key = mm.group(1)
                    val = mm.group(2).strip().strip('"').strip("'")
                    if key.endswith("_degraded_behavior"):
                        # F-CLA-004 파서 계약: `_degraded_behavior` suffix 키 = mode 엔트리 아닌
                        #   metadata — suffix strip 후 별도 보관 (mode enum 값으로 오해 금지).
                        rid = key[: -len("_degraded_behavior")]
                        cur_unit["degraded_behavior"][rid] = val
                    else:
                        cur_unit["modes"][key] = val
                    continue
            # 새 실행단위 경계: `<name>:` 값 없는 라인 (required/resource_modes 키는 위에서 이미 소비).
            mm = re.match(r"^([A-Za-z0-9._-]{1,128}):\s*$", stripped)
            if mm:
                cur_unit = {"required": [], "modes": {}, "degraded_behavior": {}}
                m.execution_units[mm.group(1)] = cur_unit
                in_unit_required = in_unit_modes = False
            continue
        if section == "sv":
            mm = re.match(r"^adopted:\s*(\S+)\s*$", stripped)
            if mm:
                raw = mm.group(1).strip().strip('"').strip("'").lower()
                # true/false 외 값 = None 유지 (미선언 취급 — 소비처가 fail-closed 로 처리).
                if raw in ("true", "yes"):
                    m.startup_validation["adopted"] = True
                elif raw in ("false", "no"):
                    m.startup_validation["adopted"] = False
                continue
            mm = re.match(r"^reason:\s*(.+?)\s*$", stripped)
            if mm:
                m.startup_validation["reason"] = mm.group(1).strip().strip('"').strip("'")
                continue
            continue

    if cur_res is not None:
        m.resources.append(cur_res)

    # classified-key set(= AC-9 allow_set) + resource별 key 집합.
    #   canonical / accepted alias / deprecated alias 3계열 전부 allow_set 에 편입 — deprecated 도
    #   "선언된 자원의 별칭"이라 참조 시 undeclared 아님(sunset 유예). alias→canonical 역방향 map 은
    #   소비처가 없어 보관하지 않는다(F-CR-006 dead-write 제거 — 필요해지면 그 때 test 와 함께 추가).
    for r in m.resources:
        keys = set()
        canon = r.get("canonical_env")
        if canon:
            keys.add(canon)
            m.classified.add(canon)
        for a in r.get("accepted", []):
            keys.add(a)
            m.classified.add(a)
        for d in r.get("deprecated", []):
            keys.add(d)
            m.classified.add(d)
        m.all_keys_by_resource[r.get("id")] = keys
    return m


# ─────────────────────── surface 추출 (structural, born-safe) ────────────────────

class Surface:
    __slots__ = ("rel", "lineno", "key", "form")

    def __init__(self, rel, lineno, key, form):
        self.rel = rel          # repo-relative path
        self.lineno = lineno    # 1-based
        self.key = key          # env-key token
        self.form = form        # 'secrets' | '_env' | 'literal'(.py) | 'passthrough'(.sh) | 'inert'


def _scan_workflow(physical, rel):
    """workflow: `secrets.<KEY>`(form) + `<lower>_env: <KEY>`(form). 둘 다 form=signal(infra-signal 무관)."""
    out = []
    for idx, raw in enumerate(physical):
        code = _strip_hash_comment(raw)
        for mm in _RE_SECRETS.finditer(code):
            out.append(Surface(rel, idx + 1, mm.group(1), "secrets"))
        for mm in _RE_ENV_VALUE.finditer(code):
            out.append(Surface(rel, idx + 1, mm.group(1), "_env"))
    return out


def _scan_project_yaml(physical, rel):
    """project.yaml: `<lower>_env: <KEY>`(form). SELF_EXCLUDE `infra_resources:` block(manifest 자체)."""
    out = []
    span = _find_infra_block(physical)
    skip_lo, skip_hi = (-1, -1)
    if span is not None:
        skip_lo, skip_hi = span
    for idx, raw in enumerate(physical):
        if skip_lo <= idx < skip_hi:
            continue  # infra_resources block = manifest 선언면, 소비면 아님 (SELF_EXCLUDE).
        code = _strip_hash_comment(raw)
        for mm in _RE_ENV_VALUE.finditer(code):
            out.append(Surface(rel, idx + 1, mm.group(1), "_env"))
    return out


def _scan_script(physical, rel):
    """scripts: 확장자 dispatch — `.py` QUOTED 리터럴 / `.sh` env-passthrough 자기참조형.

    양 경로 모두 infra-signal(§결정7(b)) 매치 필수. 근거·미채택 대안 = header ★확장자 dispatch 블록.
    """
    out = []
    if rel.endswith(".sh"):
        for idx, raw in enumerate(physical):
            code = _strip_hash_comment(raw)
            mm = _RE_SHELL_ENV_PASSTHROUGH.match(code)
            if mm:
                token = mm.group(1)
                if _is_infra_signal(token):
                    out.append(Surface(rel, idx + 1, token, "passthrough"))
        return out
    for idx, raw in enumerate(physical):
        code = _strip_hash_comment(raw)
        for mm in _RE_QUOTED_TOKEN.finditer(code):
            token = mm.group(1)
            if _is_infra_signal(token):
                out.append(Surface(rel, idx + 1, token, "literal"))
    return out


def _scan_inert(physical, rel):
    """examples/presets: env-position(mapping key / KEY=) + quoted 중 infra-signal → inert(census only)."""
    out = []
    for idx, raw in enumerate(physical):
        code = _strip_hash_comment(raw)
        seen_on_line = set()
        mm = _RE_ENV_POSITION.match(code)
        if mm:
            token = mm.group(1)
            if _is_infra_signal(token):
                seen_on_line.add(token)
        for mm in _RE_QUOTED_TOKEN.finditer(code):
            token = mm.group(1)
            if _is_infra_signal(token):
                seen_on_line.add(token)
        for token in seen_on_line:
            out.append(Surface(rel, idx + 1, token, "inert"))
    return out


def _rel(path, repo_root):
    return os.path.relpath(path, repo_root).replace(os.sep, "/")


def _self_exempt(rel):
    return any(tok in rel for tok in _SELF_SOURCE_TOKENS)


def scan_corpus(repo_root):
    """corpus 스캔 → (live_surfaces[], inert_surfaces[], scanned_files, class_enumerated{}).

    class_enumerated = per-class glob 열거 파일 수 (CFP-2719 §3.8 census floor 소비 축) —
      glob 이 yield 한 regular file 수. 파일 내용/추출 결과/self-exempt 무관(열거 축 = glob 상수의
      liveness 계측이 목적이므로 isfile 통과 직후 count).
    """
    live = []
    inert = []
    scanned = set()
    class_enumerated = {c: 0 for c in EXPECTED_NONEMPTY_SCAN_CLASSES}

    # LIVE — workflows.
    for pattern in LIVE_WORKFLOW_GLOBS:
        for path in glob.glob(os.path.join(repo_root, *pattern.split("/"))):
            if not os.path.isfile(path):
                continue
            class_enumerated["workflow"] += 1
            rel = _rel(path, repo_root)
            if _self_exempt(rel):
                continue
            physical = _read_physical(path)
            if physical is None:
                continue
            scanned.add(rel)
            live.extend(_scan_workflow(physical, rel))

    # LIVE — project.yaml (root manifest carrier; SELF_EXCLUDE block 내부).
    pj = os.path.join(repo_root, *LIVE_PROJECT_YAML_REL.split("/"))
    if os.path.isfile(pj):
        rel = _rel(pj, repo_root)
        physical = _read_physical(pj)
        if physical is not None:
            scanned.add(rel)
            live.extend(_scan_project_yaml(physical, rel))

    # LIVE — scripts (recursive=True 필수: `**` 는 이 플래그 없으면 단일 계층으로 퇴화 = 정정 무력화).
    for pattern in LIVE_SCRIPT_GLOBS:
        for path in glob.glob(os.path.join(repo_root, *pattern.split("/")), recursive=True):
            if not os.path.isfile(path):
                continue
            class_enumerated["script"] += 1
            rel = _rel(path, repo_root)
            if _self_exempt(rel):
                continue
            physical = _read_physical(path)
            if physical is None:
                continue
            scanned.add(rel)
            live.extend(_scan_script(physical, rel))

    # CENSUS inert — examples/presets (recursive glob).
    for pattern in INERT_GLOBS:
        for path in glob.glob(os.path.join(repo_root, *pattern.split("/")), recursive=True):
            if not os.path.isfile(path):
                continue
            class_enumerated["inert"] += 1
            rel = _rel(path, repo_root)
            if _self_exempt(rel):
                continue
            physical = _read_physical(path)
            if physical is None:
                continue
            scanned.add(rel)
            inert.extend(_scan_inert(physical, rel))

    return live, inert, len(scanned), class_enumerated


# ─────────────────────── grandfather baseline (new-only subtract — CFP-2661 mirror) ──

_BASELINE_FILE_RE = re.compile(r"^\s{0,80}(?:-\s{0,4})?file:\s*[\"']?([^\"'\n]+?)[\"']?\s*$")
_BASELINE_KEY_RE = re.compile(r"^\s{0,80}env_key:\s*[\"']?([^\"'\n]+?)[\"']?\s*$")


def load_baseline(path):
    """grandfather baseline 을 (file, env-key) 집합으로 로드 (dependency-free 라인 파서, born-safe).

    부재/malformed → 빈 집합 (subtract 0, honest).
    """
    keys = set()
    if not os.path.isfile(path):
        return keys
    cur_file = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, 100000):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN]
                mm = _BASELINE_FILE_RE.match(raw)
                if mm:
                    cur_file = mm.group(1).strip()
                    continue
                mm = _BASELINE_KEY_RE.match(raw)
                if mm and cur_file is not None:
                    keys.add((cur_file, mm.group(1).strip()))
    except OSError:
        return set()
    return keys


def subtract_baseline(undeclared, baseline_keys):
    """undeclared surface 가 baseline 에 있으면 억제 (new-only). → (new[], grandfathered_count)."""
    new = []
    gf = 0
    for s in undeclared:
        if (s.rel, s.key) in baseline_keys:
            gf += 1
        else:
            new.append(s)
    return new, gf


def compute_content_digest(pairs):
    """(file, env_key) pair 집합의 canonical tamper-evident digest.

    선례 형상 복사 (신규 발명 0, AC-16): `scripts/lib/check_deferred_followup_reconcile.py`
      `compute_content_digest` — canonical `json.dumps(sort_keys=True, ensure_ascii=False,
      separators=(",",":"))` → `sha256(...).hexdigest()`.
    `reason` / 헤더 / 주석은 digest **제외** — 선례가 provenance(generated_at 등)를 제외한 것과 동형.
      사유 문구를 다듬는 정당 편집이 tamper 로 오판되면 게이트가 거짓말을 하게 되기 때문.
    generate 시점과 verify 시점이 반드시 동일 함수를 통과해야 byte-stable (선례 ID-1 동형).
    """
    surfaces = [{"env_key": k, "file": f} for (f, k) in sorted(set(pairs))]
    payload = json.dumps(
        {"grandfathered_undeclared_surfaces": surfaces},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


_BASELINE_DIGEST_RE = re.compile(r"^content_digest:\s{0,4}[\"']?([0-9a-f]{64})[\"']?\s*$")


def load_baseline_digest(path):
    """baseline 의 `content_digest:` 필드 → hex str. 파일/필드 부재·unreadable → None."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in itertools.islice(f, 100000):
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN]
                mm = _BASELINE_DIGEST_RE.match(raw.rstrip("\n").rstrip("\r"))
                if mm:
                    return mm.group(1)
    except OSError:
        return None
    return None


def baseline_digest_reasons(path, pairs):
    """baseline 무결성 검증 → 손상 사유 list (빈 list = 무결). 파일 부재 → [] (baseline 없음 = subtract 0).

    필드부재 / 불일치 = 손상. 호출자는 exit 3(substrate-failure)으로 승격한다 — 손상 baseline 은
      undeclared 판정을 vacuous 하게 만드는 전제조건 실패라 warning finding 채널이 아니다.
    """
    if not os.path.isfile(path):
        return []
    stored = load_baseline_digest(path)
    if stored is None:
        return ["content_digest 필드 부재 (수기 편집 또는 구 포맷 — 재생성 필요)"]
    recomputed = compute_content_digest(pairs)
    if stored != recomputed:
        return ["content_digest 불일치 (기록=%s 재계산=%s)" % (stored, recomputed)]
    return []


def render_baseline(pairs, growth_reason=None):
    """baseline 본문 렌더 (pure — write 부작용 0, digest 계산과 동일 pair 집합 소비)."""
    pairs = sorted(set(pairs))
    digest = compute_content_digest(pairs)
    lines = [
        "# docs/infra-resource-baseline.yaml — GENERATED by "
        "scripts/lib/check_infra_resource_drift.py --write-baseline (CFP-2700 / ADR-157)",
        "# DO NOT EDIT BY HAND — content_digest 가 (file, env_key) 집합에 결박돼 있어 수기 편집은 "
        "exit 3(substrate-failure)으로 검출된다. Regenerate: bash scripts/check-infra-resource-drift.sh "
        "--repo-root . --write-baseline",
        "# grandfather = 승격 시점 pre-existing 미선언 infra 표면(file, env-key) 동결 → new-only subtract "
        "(ADR-060 §결정6 monotonic shrink). 신규 미선언 유입만 flag. candidate/inert census 무영향.",
        "# monotonic shrink: 본 목록은 줄어들 수만 있다. 정당한 corpus 확장은 "
        "`--allow-baseline-growth --reason \"<사유>\"` 로만 통과하며 사유가 growth_reason 에 각인된다.",
        "schema_version: '1.0'",
        "generated_by: CFP-2700",
        "basis: ADR-157 §결정7(a) FM1-debt 승격 시점 pre-existing undeclared infra surface(file, env-key) 동결",
    ]
    if growth_reason:
        # digest 제외 필드 (provenance 계열) — 사유 편집이 tamper 오판을 유발하지 않는다.
        lines.append("growth_reason: %s" % growth_reason.replace("\n", " ").strip())
    lines.append("content_digest: %s" % digest)
    lines.append("grandfathered_undeclared_surfaces:")
    if not pairs:
        lines[-1] = "grandfathered_undeclared_surfaces: []"
        return "\n".join(lines) + "\n"
    for (rel, key) in pairs:
        lines.append("- file: %s" % rel)
        lines.append("  env_key: %s" % key)
        lines.append("  reason: pre-existing 미선언 (CFP-2700 baseline snapshot grandfather — "
                     "추후 manifest 등재로 shrink)")
    return "\n".join(lines) + "\n"


def write_baseline(path, undeclared, allow_growth=False, reason=None):
    """현 corpus undeclared 를 baseline 으로 동결 write (single writer, canonical LF).

    monotonic shrink 강제 (ADR-060 §결정6 Amd20 실배선):
      기존 baseline 을 로드해 `added = new_pairs - old_pairs` 를 계산 — added 가 비면 write,
      비지 않으면 `--allow-baseline-growth --reason` 없이는 **거부**한다.
    old baseline 이 digest 검증에 실패하면(손상/구포맷) shrink 기준으로 신뢰할 수 없다 →
      비확장 증명이 불가하므로 동일하게 명시 override 를 요구한다(untrusted old ⇒ 확장 여부 미결정).

    → (status, n_written, detail):
        status 0 = written / 1 = growth refused / 3 = untrusted old baseline (digest 손상)
    """
    new_pairs = sorted({(s.rel, s.key) for s in undeclared})
    old_pairs = load_baseline(path)
    if not allow_growth:
        corrupt = baseline_digest_reasons(path, old_pairs)
        if corrupt:
            return (3, 0, corrupt)
        added = sorted(set(new_pairs) - set(old_pairs))
        if added:
            return (1, 0, added)
    body = render_baseline(new_pairs, growth_reason=reason)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return (0, len(new_pairs), [])


# ─────────────────────── 출력 (warning surface) ─────────────────────────────────

_ACTION_GUIDE = (
    "[infra-resource-drift] warning-tier (ADR-157 §결정3 / ADR-060 §결정5 — PR merge 미차단, advisory):\n"
    "  검출 = manifest(.claude/_overlay/project.yaml infra_resources:) 未선언 env-key 가 실 참조면\n"
    "    (workflow secrets. / project.yaml _env: / scripts 정적 리터럴)에 등장 = drift 원천.\n"
    "  remediation 3택: ① manifest resources[] 에 canonical_env 신규 자원으로 등재.\n"
    "    ② 기존 자원의 accepted alias 로 편입(동일 자원 별칭이면). ③ 정당 sunset 이면 참조면 제거.\n"
    "  orphan(선언되나 미참조): manifest 에서 dead 자원 제거 또는 실 참조 배선.\n"
    "  honesty ceiling(ADR-157 §결정8): 정적 리터럴 천장 — 동적 구성 키/프록시 위장/자기신고 누락/\n"
    "    스캔 밖 표면/shell 변수읽기 일반형(§결정8(vi)) 미검출(declared ceiling). presence ≠ truth.\n"
    "    '완전 봉인' 아님."
)


def _emit_reverse_index(live_surfaces, manifest):
    """D4 역색인 (ADR-157 §결정6 — 비커밋 ephemeral CI artifact). resource-id → [참조 표면]. stdout only."""
    print("")
    print("check-infra-resource-drift: reverse-index (D4 — 비커밋 ephemeral CI artifact, 권위 원천 아님, "
          "커밋 0, ADR-157 §결정6; VERDICT 는 이 역색인을 read-back 하지 않음 = 변조 불변 I-1)")
    # key → 참조 표면 map.
    by_key = {}
    for s in live_surfaces:
        by_key.setdefault(s.key, []).append("%s:%d" % (s.rel, s.lineno))
    for r in manifest.resources:
        rid = r.get("id")
        keys = manifest.all_keys_by_resource.get(rid, set())
        refs = []
        for k in sorted(keys):
            refs.extend(by_key.get(k, []))
        canon = r.get("canonical_env") or "(none)"
        refs_sorted = sorted(set(refs))
        print("  resource-id=%s canonical_env=%s referenced_by=[%s]"
              % (rid, canon, ", ".join(refs_sorted) if refs_sorted else ""))
    # 미선언(어느 자원에도 매핑 안 된) live key 도 가시화.
    unmapped = sorted({s.key for s in live_surfaces if s.key not in manifest.classified})
    if unmapped:
        print("  unmapped-undeclared-keys=[%s]" % ", ".join(unmapped))
    print("  coverage: scanned = .github/workflows/**(secrets./_env:) + .claude/_overlay/project.yaml(_env:) "
          "+ scripts/**/*.py(quoted literal) + scripts/**/*.sh(env-passthrough `VAR=\"${VAR}\" <cmd>` 한정); "
          "NOT scanned = shell 변수읽기 일반형(§결정8(vi)) / secret-manager / 동적구성키 / out-of-repo 수동 "
          "스크립트 / cross-repo(G5) — honest-ceiling (ADR-157 §결정8)")


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_infra_resource_drift.py",
        description="infra-resource manifest ↔ 실 참조면 drift scan (D3) + 역색인(D4) — warning tier.",
    )
    parser.add_argument("--repo-root", default=None, help="스캔 루트 (기본 = scripts/lib 기준 자동 탐지).")
    parser.add_argument("--manifest", default=None, help="manifest(project.yaml) 경로 override.")
    parser.add_argument("--baseline", default=None, help="grandfather baseline 경로 override.")
    parser.add_argument("--promote-orphan", action="store_true",
                        help="orphan → non-zero (AC-6 tier flip). 기본 OFF = orphan warning + exit 0.")
    parser.add_argument("--write-baseline", action="store_true",
                        help="현 corpus undeclared 를 baseline 으로 동결 (monotonic shrink 강제).")
    parser.add_argument("--allow-baseline-growth", action="store_true",
                        help="baseline 확장(신규 pair 추가)을 명시 허용 — 정당 corpus 확장 escape hatch. "
                             "--reason 필수.")
    parser.add_argument("--reason", default=None,
                        help="--allow-baseline-growth 사유 (baseline growth_reason 에 각인).")
    parser.add_argument("--emit-reverse-index", action="store_true",
                        help="D4 역색인을 stdout 으로 추가 방출 (비커밋 ephemeral).")
    parser.add_argument("repo_root_pos", nargs="?", default=None, help=argparse.SUPPRESS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    # escape hatch 는 사유 없이 쓸 수 없다 — 무사유 override 는 감사 불가한 조용한 확장이 된다.
    if args.allow_baseline_growth and not (args.reason or "").strip():
        print("::error::check-infra-resource-drift: --allow-baseline-growth 는 "
              "--reason \"<사유>\" 를 요구한다 (사유가 baseline growth_reason 에 각인 = 감사 표면).")
        return 2

    repo_root = args.repo_root or args.repo_root_pos
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)
    manifest_path = args.manifest or os.path.join(repo_root, DEFAULT_MANIFEST_REL)
    baseline_path = args.baseline or os.path.join(repo_root, DEFAULT_BASELINE_REL)

    manifest = parse_manifest(manifest_path)
    if manifest is None:
        print("::error::check-infra-resource-drift: manifest 파일 부재/unreadable — %s" % manifest_path)
        return 2

    live_surfaces, inert_surfaces, scanned_files, class_enumerated = scan_corpus(repo_root)
    candidates = len(live_surfaces)
    inert = len(inert_surfaces)

    # undeclared = live surface 중 key ∉ classified set.
    undeclared_all = [s for s in live_surfaces if s.key not in manifest.classified]
    # orphan = 선언 자원 중 canonical/alias 가 어느 live 표면에도 미참조.
    seen_keys = {s.key for s in live_surfaces}
    orphans = []
    for r in manifest.resources:
        keys = manifest.all_keys_by_resource.get(r.get("id"), set())
        if keys and not (keys & seen_keys):
            orphans.append(r)

    # ── --write-baseline: 현 corpus undeclared 동결 (monotonic shrink 강제) ──
    if args.write_baseline:
        status, n, detail = write_baseline(
            baseline_path, undeclared_all,
            allow_growth=args.allow_baseline_growth, reason=args.reason,
        )
        if status == 3:
            print("::error::check-infra-resource-drift: BASELINE SUBSTRATE-FAILURE — 기존 baseline %s "
                  "무결성 검증 실패라 shrink 기준으로 신뢰 불가: %s" % (baseline_path, "; ".join(detail)))
            print("  → 조치: ① 수기 편집이면 원복(git checkout) 후 재시도. ② 손상 원인이 정당한 재생성이면 "
                  "`--allow-baseline-growth --reason \"<사유>\"` 로 명시 재생성 (사유가 baseline 에 각인됨).")
            return 3
        if status == 1:
            print("::error::check-infra-resource-drift: BASELINE GROWTH REFUSED — monotonic shrink 위반 "
                  "(ADR-060 §결정6 Amd20). baseline 은 줄어들 수만 있는데 신규 (file, env-key) pair %d 건 "
                  "추가가 시도됨:" % len(detail))
            for (rel, key) in detail:
                print("    + %s :: %s" % (rel, key))
            print("  → 조치 2택: ① 정석 — 해당 env-key 를 manifest(.claude/_overlay/project.yaml "
                  "infra_resources:)에 등재해 undeclared 를 해소한다(그러면 baseline 확장 불요).")
            print("             ② 정당한 corpus 확장(스캐너 범위 확대 등)이면 "
                  "`--allow-baseline-growth --reason \"<사유>\"` 로 명시 override — 사유가 "
                  "baseline growth_reason 에 각인되고 리뷰에 노출된다.")
            return 1
        print(
            "check-infra-resource-drift: baseline written %s — %d (file, env-key) frozen "
            "(candidates_scanned=%d inert_skipped=%d)%s" % (
                baseline_path, n, candidates, inert,
                (" [GROWTH ALLOWED — reason=%s]" % args.reason) if args.allow_baseline_growth else "",
            )
        )
        return 0

    baseline_keys = load_baseline(baseline_path)
    new_undeclared, grandfathered = subtract_baseline(undeclared_all, baseline_keys)

    # census emit (anti-hollow observability — always; candidate/inert 은 baseline 무영향).
    print(
        "check-infra-resource-drift: census candidates_scanned=%d inert_skipped=%d undeclared=%d "
        "orphan=%d (grandfathered=%d) over %d file"
        % (candidates, inert, len(new_undeclared), len(orphans), grandfathered, scanned_files)
    )

    # baseline substrate-failure — tamper-evident digest 검증 (census emit 후: 관측은 남기고 판정을 막는다).
    #   손상 baseline 은 grandfather subtract 를 신뢰 불가하게 만들어 위 undeclared 수를 vacuous 하게 한다
    #   → finding(warning) 아니라 전제조건 실패 = exit 3 (born-hollow 와 동급 tier).
    digest_reasons = baseline_digest_reasons(baseline_path, baseline_keys)
    if digest_reasons:
        print(
            "::error::check-infra-resource-drift: FAIL-CLOSED — baseline %s 무결성 검증 실패: %s. "
            "손상된 grandfather baseline 은 undeclared 판정의 전제조건이라 verdict 를 낼 수 없다 "
            "(수기 편집 금지 — `--write-baseline` 로 재생성)." % (baseline_path, "; ".join(digest_reasons))
        )
        return 3

    # census fail-closed — born-hollow guard. candidates==0 ∧ inert==0 = 진짜 vacuous/dead-scope.
    if candidates == 0 and inert == 0:
        print(
            "::error::check-infra-resource-drift: FAIL-CLOSED — candidates_scanned=0 ∧ inert_skipped=0 "
            "(born-hollow guard 발동: infra 표면을 live·inert 어느 것으로도 0 = empty-scope oracle, "
            "ADR-157 §결정9). corpus glob 또는 manifest 조정 없이는 통과 불가."
        )
        return 3

    # per-class census floor (CFP-2719 §3.8 — 전역 guard 와 OR 결합, 무조건 활성/opt-in flag 금지).
    #   live/inert 가 disjoint 별도 glob 루프라 inert>0 이 전역 guard 를 꺼서 glob 오타/경로 이동 시
    #   live 열거가 침묵 사망(영구 GREEN)할 수 있다 — 선언 class(EXPECTED_NONEMPTY_SCAN_CLASSES)의
    #   glob 열거 파일 수 0 을 class 단위로 fail-closed. 기준 = 열거 축(추출 결과 무관 —
    #   mutation-kill 표적 = glob 상수). 발동 메시지 = 죽은 class 명 + 해당 glob 상수명 명시.
    dead_classes = [c for c in EXPECTED_NONEMPTY_SCAN_CLASSES if class_enumerated.get(c, 0) == 0]
    if dead_classes:
        print(
            "::error::check-infra-resource-drift: FAIL-CLOSED — per-class census floor 발동: "
            "선언 scan class 의 glob 열거 파일 수 0 — %s. EXPECTED_NONEMPTY_SCAN_CLASSES 선언 class 는 "
            "매 실행 열거 ≥1 이어야 한다 (glob 오타/경로 이동에 의한 열거 침묵 사망 = 계기 사망 검출, "
            "CFP-2719 §3.8 / ADR-157 §결정9 born-hollow 확장)."
            % "; ".join(
                "class=%s glob=%s enumerated=0" % (c, _SCAN_CLASS_GLOB_CONST[c]) for c in dead_classes
            )
        )
        return 3

    # none-disguise anti-hollow (AC-10/11) — hollow "none" 위장 + live 표면 존재.
    hollow_none = (not manifest.present) or (manifest.none_sentinel and not manifest.has_reason) \
        or (manifest.present and not manifest.resources and not manifest.has_reason)
    if hollow_none and candidates >= 1:
        print(
            "::warning::check-infra-resource-drift: NONE-DISGUISE — manifest infra_resources: block "
            "부재/empty-no-reason 인데 LIVE infra 표면 %d 검출 (hollow 'none' 위장, ADR-157 §결정8/AC-10·11). "
            "manifest 에 실 자원을 선언하거나 사유(reason) 명시 필요." % candidates
        )
        print(
            "check-infra-resource-drift: FLAG none-disguise — candidates_scanned=%d inert_skipped=%d "
            "over %d file — warning tier (continue-on-error 로 비차단)"
            % (candidates, inert, scanned_files)
        )
        if args.emit_reverse_index:
            _emit_reverse_index(live_surfaces, manifest)
        return 1

    # undeclared warning surface (per violation).
    for s in new_undeclared:
        print(
            "::warning::check-infra-resource-drift: UNDECLARED — %s:%d env-key=%s (form=%s, manifest 未선언)"
            % (s.rel, s.lineno, s.key, s.form)
        )
    # orphan warning surface (per orphan).
    for r in orphans:
        print(
            "::warning::check-infra-resource-drift: ORPHAN — resource-id=%s canonical_env=%s "
            "(선언되나 어느 참조면에서도 미참조 = dead 선언)" % (r.get("id"), r.get("canonical_env"))
        )

    flag = False
    reasons = []
    if new_undeclared:
        flag = True
        reasons.append("undeclared=%d" % len(new_undeclared))
    if orphans and args.promote_orphan:
        flag = True
        reasons.append("orphan=%d(promoted)" % len(orphans))

    if args.emit_reverse_index:
        _emit_reverse_index(live_surfaces, manifest)

    if flag:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-infra-resource-drift: FLAG %s over %d file (candidates_scanned=%d inert_skipped=%d "
            "orphan=%d grandfathered=%d) — warning tier (continue-on-error 로 비차단, advisory only)"
            % (", ".join(reasons), scanned_files, candidates, inert, len(orphans), grandfathered)
        )
        return 1

    # PASS — 실 census count 만 사실 서술 (all-inert 시 candidate=0 을 "candidate≥1" 로 overstate 금지, F-CR-2).
    orphan_note = ""
    if orphans:
        orphan_note = " (orphan=%d = warning-only, --promote-orphan 미지정)" % len(orphans)
    print(
        "check-infra-resource-drift: PASS — new undeclared 0%s (candidates_scanned=%d inert_skipped=%d "
        "grandfathered=%d over %d file — empty-scope oracle: candidates==0 ∧ inert==0 아님, warning tier)"
        % (orphan_note, candidates, inert, grandfathered, scanned_files)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
