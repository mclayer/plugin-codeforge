#!/usr/bin/env python3
# CFP-2828 / ADR-081 Amendment 14 §결정 D15 — codex exec `-o out.json` 소비 재검증 helper (AC-6 floor, SSOT)
#
# 목적:
#   CodexReviewAgent 가 `codex exec --output-schema … -o out.json` 로 받은 out.json 을 소비하기 **직전**,
#   구조 정합을 fail-closed 로 재검증한다 (schema silent-drop #4181/#15451/#19816 대비 — `--output-schema`
#   는 request 이지 강제 아님). 재검증 실패 = inconclusive (PASS 승격 절대 금지, I-3/I-7).
#
# 재검증 5단계 (Change Plan §4 소비 규칙):
#   ① 파일 존재            — out.json 부재 = inconclusive (§7.4.1 "0 + out.json 부재" bucket)
#   ② JSON parse           — malformed/truncated = inconclusive
#   ③ schema 준수          — required / additionalProperties:false / enum (verdict·severity closed set)
#   ④ cross-field          — counts.Px ↔ findings[] severity 별 실 개수 재계산 일치 (JSON Schema 표현력 밖)
#   ⑤ category ∈ enum      — findings[].category ∈ packet category_enum (dispatch-시점 정적 schema 로 표현
#                            불가한 lane 동적 enum 을 소비 시점 기계 대조, F-DR-001 1안)
#   ①~⑤ 하나라도 실패 = exit 1 (inconclusive, PASS 승격 0).
#
# 시그니처 (인터페이스 고정 — QADev 테스트가 이 계약에 의존):
#   check_codex_review_output_schema.py <out_json_path> <schema_path> <category_enum>
#     <out_json_path>  = codex exec `-o` 산출 out.json 경로
#     <schema_path>    = plugins/codeforge-review/schemas/codex-review-output-schema-v1.json 경로
#     <category_enum>  = **쉼표구분 문자열** (예: `runtime-bug,layer-violation,naming`) — packet 유래
#
# Exit code:
#   0 = 재검증 5단계 전부 통과 (out.json 소비 가능)
#   1 = 비정합 (①~⑤ 중 1+ 실패) → inconclusive (PASS 승격 금지)
#   2 = setup error (인자 개수 오류 / schema_path 미존재·손상 = dispatch 배선 버그)
#
# stdlib-only (jsonschema 등 외부 dep 금지 — schema shape 고정이라 draft-07 subset 을 수동 검증).
# 검증 로직은 schema_path 를 읽어 enum·required·additionalProperties 를 그로부터 도출한다
#   (literal 하드코딩 drift 회피 — schema 파일이 단일 원본).
#
# fuzz-hardening (§8.8 DO): malformed / truncated / deeply-nested / oversize 입력 → no-crash ∧ fail-closed
#   (never-PASS-on-invalid). 16MB read cap + RecursionError catch = **bounded degradation** — 임의 입력
#   총 작업량 무해성 단정 아님 (honest ceiling, ADR-082 §결정 16 상속 / ADR-151 §결정 7).

import json
import os
import sys


def _configure_utf8_stdout():
    """Windows 콘솔 cp949 기본 인코딩에서 em-dash 등 UTF-8 출력 실패(crash) 방지.
    (CI=Linux UTF-8 무관, 로컬 dev 견고성 — fuzz no-crash floor 정합.)"""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass


_configure_utf8_stdout()

MAX_OUT_JSON_BYTES = 16 * 1024 * 1024  # oversize read cap — 초과 = fail-closed inconclusive (memory bound; 총-작업량 DoS 보증 아님)


def _load_schema(schema_path):
    """schema 파일 로드. 성공=(schema_dict, None) / 실패=(None, err_msg) → main 이 exit 2 (setup error)."""
    if not os.path.isfile(schema_path):
        return None, f'schema 경로 미존재: {schema_path}'
    try:
        with open(schema_path, 'r', encoding='utf-8') as fh:
            return json.load(fh), None
    except (OSError, ValueError, RecursionError) as e:
        return None, f'schema 로드/parse 실패: {schema_path} ({e})'


def _load_out_json(out_json_path):
    """out.json 로드 (재검증 ①②). 성공=(data, None) / 실패=(None, err_msg) → exit 1 (inconclusive).

    파일 부재 / oversize / malformed / truncated / deeply-nested 전부 fail-closed (no-crash)."""
    if not os.path.isfile(out_json_path):
        return None, f'① out.json 부재: {out_json_path} — inconclusive (PASS 금지)'
    try:
        size = os.path.getsize(out_json_path)
    except OSError as e:
        return None, f'① out.json stat 실패: {out_json_path} ({e})'
    if size > MAX_OUT_JSON_BYTES:
        return None, f'① out.json oversize ({size} > {MAX_OUT_JSON_BYTES} bytes) — fail-closed inconclusive'
    try:
        with open(out_json_path, 'r', encoding='utf-8') as fh:
            return json.load(fh), None
    except (OSError, ValueError, RecursionError) as e:
        return None, f'② JSON parse 실패 (malformed/truncated): {out_json_path} ({e})'
    except Exception as e:  # noqa: BLE001 — fuzz fail-closed floor (never-crash, never-PASS-on-invalid)
        return None, f'② JSON 로드 예외 (fail-closed): {out_json_path} ({e})'


def _validate_schema(instance, schema, path, errors):
    """draft-07 subset 수동 검증 (type/required/additionalProperties/properties/items/enum/minimum).

    재귀 깊이 = schema 깊이(고정 ~4)에 bound — instance 깊이 무관 (schema 정의 노드만 하강)."""
    t = schema.get('type')
    if t == 'object':
        if not isinstance(instance, dict):
            errors.append(f'{path}: object 기대, {type(instance).__name__} 수신')
            return
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            for k in instance:
                if k not in props:
                    errors.append(f'{path}: 허용되지 않은 키 "{k}" (additionalProperties:false)')
        for r in schema.get('required', []):
            if r not in instance:
                errors.append(f'{path}: 필수 키 "{r}" 누락')
        for k, sub in props.items():
            if k in instance:
                _validate_schema(instance[k], sub, f'{path}.{k}', errors)
    elif t == 'array':
        if not isinstance(instance, list):
            errors.append(f'{path}: array 기대, {type(instance).__name__} 수신')
            return
        items = schema.get('items')
        if items is not None:
            for i, el in enumerate(instance):
                _validate_schema(el, items, f'{path}[{i}]', errors)
    elif t == 'string':
        if not isinstance(instance, str):
            errors.append(f'{path}: string 기대, {type(instance).__name__} 수신')
            return
        enum = schema.get('enum')
        if enum is not None and instance not in enum:
            errors.append(f'{path}: enum 밖 값 "{instance}" (허용: {enum})')
    elif t == 'integer':
        # JSON bool 은 Python bool(=int subclass) — integer 로 오인 금지 (counts BVA edge).
        if isinstance(instance, bool) or not isinstance(instance, int):
            errors.append(f'{path}: integer 기대, {type(instance).__name__} 수신')
            return
        minimum = schema.get('minimum')
        if minimum is not None and instance < minimum:
            errors.append(f'{path}: minimum {minimum} 미만 ({instance})')
    # 그 외 type = 검증 스킵 (본 schema 미사용)


def _check_cross_field(data, errors):
    """④ cross-field: counts.Px ↔ findings[] severity 별 실 개수 재계산 일치."""
    recomputed = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
    for f in data['findings']:
        sev = f.get('severity')
        if sev in recomputed:
            recomputed[sev] += 1
    counts = data['counts']
    for k in ('P0', 'P1', 'P2', 'P3'):
        if counts.get(k) != recomputed[k]:
            errors.append(
                f'④ cross-field 불일치: counts.{k}={counts.get(k)} ≠ findings[] {k} 실개수 {recomputed[k]}')


def _check_category_enum(data, category_enum, errors):
    """⑤ category ∈ enum: findings[].category ∈ packet category_enum (쉼표구분)."""
    allowed = {c.strip() for c in category_enum.split(',') if c.strip()}
    for i, f in enumerate(data['findings']):
        cat = f.get('category')
        if cat not in allowed:
            errors.append(
                f'⑤ category∉enum: findings[{i}].category="{cat}" ∉ packet category_enum {sorted(allowed)}')


def revalidate(out_json_path, schema, category_enum):
    """재검증 ①~⑤ 실행. 성공=(True, []) / 실패=(False, [err, ...]).

    ③ schema 실패 시 ④⑤ 는 skip (구조 미보장 상태에서 cross-field/category 접근 = 2차 예외 회피)."""
    data, err = _load_out_json(out_json_path)  # ①②
    if err is not None:
        return False, [err]
    errors = []
    _validate_schema(data, schema, 'root', errors)  # ③
    if errors:
        return False, errors
    _check_cross_field(data, errors)     # ④
    _check_category_enum(data, category_enum, errors)  # ⑤
    return (not errors), errors


def main(argv):
    args = argv[1:]
    if len(args) != 3:
        print('setup error: 인자 3개 필요 — '
              'check_codex_review_output_schema.py <out_json_path> <schema_path> <category_enum>',
              file=sys.stderr)
        return 2
    out_json_path, schema_path, category_enum = args
    schema, schema_err = _load_schema(schema_path)
    if schema_err is not None:
        print(f'setup error: {schema_err}', file=sys.stderr)
        return 2
    try:
        ok, errors = revalidate(out_json_path, schema, category_enum)
    except RecursionError:
        # deeply-nested out.json — fail-closed (no-crash, never-PASS-on-invalid)
        print('② JSON 재귀 깊이 초과 (deeply-nested) — fail-closed inconclusive', file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001 — fuzz fail-closed floor
        print(f'재검증 예외 (fail-closed inconclusive): {e}', file=sys.stderr)
        return 1
    if ok:
        print('[codex-review-output-schema] PASS — 재검증 5단계 통과 (out.json 소비 가능).')
        return 0
    print('[codex-review-output-schema] FAIL (inconclusive — PASS 승격 금지):')
    for e in errors:
        print(f'  {e}')
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
