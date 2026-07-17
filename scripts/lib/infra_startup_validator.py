#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/infra_startup_validator.py
CFP-2700 (Epic) G3 / ADR-157 §결정2 — D2 startup fail-closed 대조 **reference implementation**
  (AC-3 / AC-9 / AC-15). consumer 제품 실행단위가 채택해 쓰는 참조 구현이다.

실행단위는 부팅 시 자신이 manifest(`.claude/_overlay/project.yaml` `infra_resources:`)에 선언한
  required 자원이 실제 설정됐는지를 **첫 business 동작 이전 startup 단계에서 대조**하고, 미설정 시
  non-zero exit + 미설정 자원 ID 를 loud 하게 로그한다 (지연 크래시 = 불합격 — AC-3).

★ 4 계약 (proto-D2 4중 결함의 올바른 형 — ADR-157 §결정2, 결함별 대응):
  (1) **프로세스 env 검사** — `os.environ` 을 본다 (`.env` **파일 파싱 아님** — 실행단위가 실제 보는
      환경이 판정 대상. proto 결함 (b) `.env` grep 봉인).
  (2) **exit-masking 금지** — 미설정 = non-zero exit 로 전파. `|| echo` 류 삼킴 0, 본 모듈에
      광역 try/except 삼킴 0 (proto 결함 (a) `grep -q ... || echo` 봉인).
  (3) **빈 값 reject** — set-but-empty(공백 포함)도 미설정으로 간주 (proto 결함 (c) `^KEY=` 봉인).
  (4) **fail-closed default** — 선언된 required 자원은 감지 대상이며 "미정의 시 비활성" 금지
      (proto 결함 (d) 봉인). required → 부팅 거부 / optional_degradable → degrade + WARN 계속
      (§결정1 EDGE). resource_modes 엔트리 부재 = **required 취급**(fail-closed default),
      enum 밖 mode 값 = required 취급 + WARN (저작 시점 차단은 check_infra_manifest_schema.py).

★ AC-9 allow-set parity **by construction**: 자원별 허용 env-key 집합(canonical ∪ accepted ∪
  deprecated alias)은 D3 스캐너(`check_infra_resource_drift.py`)의 `parse_manifest` 를 **import
  재사용**해 얻는다 — 재구현 0. 스캐너가 classified 로 인정하는 키 == 본 validator 가 자원 충족으로
  인정하는 키 (동일 파서 산출 `all_keys_by_resource` / `classified`). `--emit-allow-set` 가 그 집합을
  방출해 parity diff 0 을 실측 가능하게 한다.

★ lazy env 접근: import 시점 os.environ deref **0** — 전 env 읽기는 함수 호출 내부에서만 발생
  (import-time deref 는 테스트 주입 불능 + 부팅 순서 결합을 낳는다).

★ deprecated alias 로만 충족 시: 충족 인정(sunset 유예 — 참조돼도 undeclared 가 아닌 것과 대칭)
  + WARN (canonical 이행 촉구). alias-model = ADR-157 §결정5.

★ consumer 채택 경로 (AC-15 — `--adoption-check`): manifest `infra_resources.startup_validation:`
  선언(`adopted: true|false` + 미채택 시 `reason` 필수)을 판정한다:
    · adopted: true  → 전 실행단위(또는 --unit 지정 1개) startup 대조 실행 — 미설정 required 존재
                       = FAIL(부팅거부와 동일 exit) — "채택 consumer 누락 → FAIL".
    · adopted: false + reason → 비적용 PASS ("미채택 + 사유 → 비적용 PASS" — I-5 채택-bounded 의
                       정직 선언 경로. wrapper-self 가 이 경로: declarative-only, 런타임 0).
    · adopted: false/미선언 + 사유 부재 → FAIL ("미채택 + 사유부재 → FAIL" — silent 미채택 금지,
                       none-disguise 동형).

★ crash-loop 완화 (ADR-157 §결정2 운영 주의): 구성 오류 exit code = **78 (sysexits EX_CONFIG)** —
  `restart: always` 무한 재시작 루프에서 오케스트레이터/운영자가 "구성 오류(재시작 무익)"를 exit code
  만으로 판별 가능하게 distinct code 를 쓴다 (bounded restart / readiness probe 배선은 consumer 소관).

★ 정직 천장 (ADR-157 §결정8 상속 — 은폐 금지):
  - **I-5 채택-bounded**: 본 구현은 참조 구현이다 — consumer 가 채택하지 않으면 강제되지 않는다.
    wrapper 는 plugin 이라 consumer 런타임에 코드를 주입할 수 없다. "wrapper green = 전 consumer 안전"
    아님. wrapper-self 는 declarative-only(부팅하는 제품 바이너리 0)라 본 구현을 fixture 로만 falsify
    한다 (AC-4 honest-ceiling 정합 — tests/fixtures/infra-refimpl/ 참조).
  - 자기신고 누락(§결정8(ii)): 실행단위가 required 를 과소선언하면 대조 지점 자체가 없다 — 본
    validator 는 선언된 것만 대조한다 (census-floor 는 D3 스캐너 소관).
  - env 설정의 **값 유효성**(잘못된 URL/만료 토큰 등)은 검증하지 않는다 — presence ≠ truth.

CLI 계약 (ADR-061 house style):
  python3 scripts/lib/infra_startup_validator.py --unit NAME [--manifest PATH] [--repo-root DIR]
  python3 scripts/lib/infra_startup_validator.py --adoption-check [--unit NAME] [--manifest PATH]
  python3 scripts/lib/infra_startup_validator.py --emit-allow-set [--manifest PATH]

Exit codes:
  0  = STARTUP-OK (required 전건 충족; optional_degradable 미설정은 degrade+WARN 계속) /
       NOT-ADOPTED-PASS (미채택 + 사유 — 비적용) / ADOPTED-PASS / allow-set 방출.
  78 = 구성 오류 fail-closed (sysexits EX_CONFIG): required 미설정 / manifest 부재·block 부재 /
       실행단위 미선언 / dangling resource-id / 미채택 + 사유부재 (adoption-check).
  2  = CLI usage 오류 (argparse).

ADR refs: ADR-157 §결정2 (D2 4계약) / §결정5 (alias-model) / §결정8 (honest-ceiling) /
  ADR-061 §결정1 (Python SSOT) / ADR-119 (게이트 = ground-truth).
"""

import argparse
import os
import sys

# Windows cp949 인코딩 문제 회피 (ADR-061 portability 답습).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# D3 스캐너 파서 import 재사용 (AC-9 parity by construction — 재구현 금지).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_infra_resource_drift as drift  # noqa: E402

EX_CONFIG = 78  # sysexits EX_CONFIG — 구성 오류 distinct exit code (§결정2 crash-loop 완화).
_MODE_ENUM = ("required", "optional_degradable")


def _is_set(environ, key):
    """계약 (1)+(3): 프로세스 env 기준, set-but-empty(공백 포함) = 미설정."""
    val = environ.get(key)
    return val is not None and val.strip() != ""


def _resource_key_tiers(manifest):
    """자원별 (canonical, accepted set, deprecated set) — deprecated-alias WARN 판별용.

    집합 원천은 전부 공유 파서 산출(m.resources) — all_keys_by_resource 와 동일 파서, parity 유지.
    """
    tiers = {}
    for r in manifest.resources:
        tiers[r.get("id")] = {
            "canonical": r.get("canonical_env"),
            "accepted": set(r.get("accepted", [])),
            "deprecated": set(r.get("deprecated", [])),
        }
    return tiers


def validate_startup(manifest_path, unit_name, environ=None):
    """실행단위 startup 대조 (pure 판정 — 출력은 lines 로 반환, 호출자가 render).

    → (exit_code, lines): 0 = OK / EX_CONFIG(78) = 부팅 거부.
    environ 미주입 시에만 os.environ 을 lazy 로 잡는다 (import-time deref 0).
    """
    if environ is None:
        environ = os.environ  # lazy — 함수 호출 시점에만 deref.
    lines = []

    manifest = drift.parse_manifest(manifest_path)
    if manifest is None:
        lines.append("::error::infra-startup-validator: STARTUP-FAILCLOSED — manifest 파일 부재/"
                     "unreadable (%s). 검증 불능 = 부팅 거부 (fail-closed, 계약 (4))." % manifest_path)
        return (EX_CONFIG, lines)
    if not manifest.present:
        lines.append("::error::infra-startup-validator: STARTUP-FAILCLOSED — `infra_resources:` "
                     "block 부재 (%s). 선언 부재 시 \"감지 비활성\" 금지 (계약 (4) — proto-D2 결함 (d) "
                     "봉인): 자원을 선언하거나 `resources: none` + reason 으로 명시하라." % manifest_path)
        return (EX_CONFIG, lines)
    unit = manifest.execution_units.get(unit_name)
    if unit is None:
        lines.append("::error::infra-startup-validator: STARTUP-FAILCLOSED — 실행단위 미선언: "
                     "unit=%s (manifest execution_units 에 없음 — 선언 없이 부팅 대조 불가, "
                     "fail-closed)." % unit_name)
        return (EX_CONFIG, lines)

    tiers = _resource_key_tiers(manifest)
    missing = []
    degraded = []
    for rid in unit["required"]:
        keys = manifest.all_keys_by_resource.get(rid, set())  # = D3 allow-set 원천 (AC-9)
        mode = unit["modes"].get(rid, "required")  # 엔트리 부재 = required (fail-closed default, 계약 (4))
        if mode not in _MODE_ENUM:
            lines.append("::warning::infra-startup-validator: resource_modes 값 '%s' 은 enum 밖 — "
                         "required 취급 (fail-closed default)." % mode)
            mode = "required"
        satisfied_key = None
        for k in sorted(keys):
            if _is_set(environ, k):
                satisfied_key = k
                break
        if satisfied_key is None:
            if not keys:
                lines.append("::error::infra-startup-validator: 자원 %s = manifest plane A 미정의 "
                             "(dangling ID 참조) — 충족 불능, fail-closed." % rid)
            if mode == "optional_degradable":
                behavior = unit["degraded_behavior"].get(rid, "(degraded_behavior 선언 부재)")
                degraded.append(rid)
                lines.append("::warning::infra-startup-validator: DEGRADED — unit=%s 자원 %s 미설정 "
                             "(optional_degradable) → degrade 계속: %s" % (unit_name, rid, behavior))
            else:
                missing.append(rid)
                lines.append("::error::infra-startup-validator: STARTUP-FAILCLOSED — unit=%s 미설정 "
                             "required 자원: %s (env 후보 %s 전건 미설정/빈 값 — 빈 값 = 미설정, "
                             "계약 (3))" % (unit_name, rid, ",".join(sorted(keys)) or "(없음)"))
        else:
            tier = tiers.get(rid, {})
            if satisfied_key in tier.get("deprecated", set()):
                lines.append("::warning::infra-startup-validator: unit=%s 자원 %s 가 deprecated alias "
                             "%s 로만 충족됨 — canonical %s 이행 필요 (sunset 유예, ADR-157 §결정5)."
                             % (unit_name, rid, satisfied_key, tier.get("canonical")))

    if missing:
        lines.append("infra-startup-validator: BOOT-REFUSED unit=%s missing=[%s] — 첫 business 동작 "
                     "이전 startup 단계 거부 (exit %d EX_CONFIG, ADR-157 §결정2; 지연 크래시 아님)"
                     % (unit_name, ",".join(missing), EX_CONFIG))
        return (EX_CONFIG, lines)
    lines.append("infra-startup-validator: STARTUP-OK unit=%s required=%d satisfied%s"
                 % (unit_name, len(unit["required"]),
                    (" degraded=[%s]" % ",".join(degraded)) if degraded else ""))
    return (0, lines)


def check_adoption(manifest_path, unit_name=None, environ=None):
    """AC-15 consumer 채택 경로 판정 → (exit_code, lines).

    adopted:true → startup 대조 실행(채택 consumer 누락 = FAIL) /
    adopted:false + reason → 비적용 PASS / 미채택 + 사유부재 → FAIL.
    """
    lines = []
    manifest = drift.parse_manifest(manifest_path)
    if manifest is None or not manifest.present:
        lines.append("::error::infra-startup-validator: ADOPTION-FAIL — manifest/`infra_resources:` "
                     "block 부재 (%s): 채택 여부 판정 불능 = FAIL (fail-closed — silent 미채택 금지, "
                     "AC-15)." % manifest_path)
        return (EX_CONFIG, lines)

    adopted = manifest.startup_validation.get("adopted")
    reason = (manifest.startup_validation.get("reason") or "").strip()

    if adopted is True:
        units = [unit_name] if unit_name else sorted(manifest.execution_units.keys())
        if not units:
            lines.append("::error::infra-startup-validator: ADOPTION-FAIL — adopted: true 인데 "
                         "execution_units 선언 0 (대조 대상 부재 = hollow 채택).")
            return (EX_CONFIG, lines)
        worst = 0
        for u in units:
            code, sub = validate_startup(manifest_path, u, environ=environ)
            lines.extend(sub)
            worst = max(worst, code)
        if worst != 0:
            lines.append("infra-startup-validator: ADOPTION-FAIL — 채택 consumer 에 미설정 required "
                         "자원 존재 (AC-15: 채택 + 누락 = FAIL)")
            return (worst, lines)
        lines.append("infra-startup-validator: ADOPTED-PASS — 채택 + 전 실행단위 required 충족")
        return (0, lines)

    if adopted is False and reason:
        lines.append("infra-startup-validator: NOT-ADOPTED-PASS — 비적용 (미채택 + 사유: %s) "
                     "(AC-15 / I-5 채택-bounded 정직 선언 경로)" % reason)
        return (0, lines)

    lines.append("::error::infra-startup-validator: ADOPTION-FAIL — startup_validation 미채택인데 "
                 "사유(reason) 부재 (adopted=%s): silent 미채택 금지 (AC-15 — `adopted: false` + "
                 "`reason:` 를 선언하거나 채택하라)." % adopted)
    return (EX_CONFIG, lines)


def emit_allow_set(manifest_path):
    """AC-9 parity 실측 표면: 자원별/합집합 allow-set 방출 → (exit_code, lines).

    원천 = D3 스캐너와 동일 파서 산출 (all_keys_by_resource / classified) — diff 0 by construction.
    """
    lines = []
    manifest = drift.parse_manifest(manifest_path)
    if manifest is None or not manifest.present:
        lines.append("::error::infra-startup-validator: allow-set 방출 불능 — manifest/block 부재 (%s)"
                     % manifest_path)
        return (EX_CONFIG, lines)
    union = set()
    for rid in sorted(manifest.all_keys_by_resource.keys()):
        keys = sorted(manifest.all_keys_by_resource[rid])
        union.update(keys)
        lines.append("allow-set resource=%s keys=%s" % (rid, ",".join(keys)))
    lines.append("allow-set union=%s" % ",".join(sorted(union)))
    # classified(스캐너 allow_set)와 all_keys_by_resource 합집합의 동일성 self-assert (parity 내부 결박).
    if union != manifest.classified:
        lines.append("::error::infra-startup-validator: PARITY-BROKEN — union(all_keys_by_resource) != "
                     "classified (동일 파서 산출인데 불일치 = 파서 결함)")
        return (EX_CONFIG, lines)
    return (0, lines)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="infra_startup_validator.py",
        description="D2 startup fail-closed 대조 reference-impl (ADR-157 §결정2 4계약 — AC-3/9/15).",
    )
    parser.add_argument("--unit", default=None, help="검증 대상 실행단위 이름 (execution_units 키).")
    parser.add_argument("--manifest", default=None, help="manifest(project.yaml) 경로 override.")
    parser.add_argument("--repo-root", default=None, help="repo 루트 (기본 = scripts/lib 기준 자동 탐지).")
    parser.add_argument("--adoption-check", action="store_true",
                        help="AC-15 채택 경로 판정 (adopted/reason 선언 기반).")
    parser.add_argument("--emit-allow-set", action="store_true",
                        help="AC-9 parity 실측용 allow-set 방출.")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    manifest_path = args.manifest or os.path.join(repo_root, drift.DEFAULT_MANIFEST_REL)

    if args.emit_allow_set:
        code, lines = emit_allow_set(manifest_path)
    elif args.adoption_check:
        code, lines = check_adoption(manifest_path, unit_name=args.unit)
    elif args.unit:
        code, lines = validate_startup(manifest_path, args.unit)
    else:
        print("::error::infra-startup-validator: --unit NAME / --adoption-check / --emit-allow-set "
              "중 하나 필요.")
        return 2

    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
