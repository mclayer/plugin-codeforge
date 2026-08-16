#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_hollow_gate_corpus.py
CFP-2963 / ADR-175 — hollow-gate corpus 판정 하네스 pure core.

커밋된 2-arm corpus(표본 = 게이트 artifact + kill/clean/empty/xkill fixture leg)를 **실행**해
그 표본이 LIVE(결함 앞에서 RED) 인지 HOLLOW(결함 앞에서도 GREEN) 인지 **arm-invariant** 로 분류한다.
판정 입력은 오직 leg 실행의 관측 마커이며, 표본이 어느 arm(L/H)으로 선언됐는지는 판정 함수에
구조적으로 도달하지 못한다(`_verdict()` 시그니처에 arm/declared/expected 부재).

━━ 정직 천장 (honest-ceiling, ADR-175 / INV-5 P0 불가침) ━━
  본 하네스는 **corpus 에 담긴 표본에 대한 관측 기반 verdict 까지만** 보장한다. corpus 밖 게이트
  일반으로 외삽하지 않는다 — "landed 게이트 전수가 hollow 아님"을 증명하지 않는다. 분모(N)는
  등재된 표본 수일 뿐이며, 미등재 게이트의 hollow 여부는 본 채널의 값공간 밖(미판정)이다.
  presence ≠ truth 를 상속한다: GREEN 은 "등재 표본이 선언대로 관측됐다"이지 "게이트가 결함류를
  실제로 죽인다"가 아니다(검출 sufficiency = undecidable, ADR-154 §결정4 승계).
  'universal' / '완전 봉인' / 'class 봉쇄' / '근절' 류 framing 은 하지 않는다(그런 hard-claim 부재).
  game-able residual 정직 공개: (a) 표본 제작자가 kill-fixture 를 게이트가 이미 잡는 축으로만
  고르면 corpus 는 LIVE 를 내지만 그 게이트의 다른 축은 여전히 미검증이다(축 선택 = 사람 판단,
  기계강제 불가) — xkill 축-disjoint 대조가 "상수 footer 자동적중"만 막을 뿐 축 대표성은 못 막는다.
  (b) IC-4 blinding 이 닫는 표면은 **열거된 5종뿐**이다: exec tree 표면의 arm 누설 4종
  (stamp / manifest / baseline / probe basename 토큰) + **실행 순번(형제 디렉터리 수)**.
  순번 표면은 원래 이 열거에 없었다 — 깨진 선언이 아니라 **미열거 공백**이었고(F-CR18-9),
  leg 별 즉시 정리 + `exec_root` 직속 디렉터리 수 == 1 assert 로 이제 닫는다.
  여전히 **열려 있는 것**(닫혔다고 읽지 말 것): ① artifact 내용 자체로부터의 역산(예: 중화 주석
  문자열 read) ② basename 토큰 매칭 회피 — 금지 토큰 없는 이름으로 개명하면 통과(내용 검사 아님)
  ③ `_run_leg` 이 `env=` 를 주지 않아 자식이 부모 env 전체를 상속 — `GITHUB_WORKSPACE` 등을 경유한
  repo 도달(따라서 manifest/stamp/baseline 원본 read)은 막지 않는다 ④ 시계·파일시스템 mtime 등
  미열거 side-channel 일반. IC-4 는 격리 경계가 아니라 **표면 위생 assert** 다.
  (c) ⓺ 커밋 표본 파생 provenance 검사의 **정의역 = `build[]` 자기신고분 한정**(F-CR19-3).
  `_check_sample_provenance()` 는 `build[]` 를 순회하므로, 표본을 `samples[]` 와 `classification[]`
  에만 등재하고 `build[]` 항목을 **생략하면** 그 표본은 파생 대조를 **한 번도 받지 않고 통과**한다.
  firsthand 재현(s04 = s02 byte-copy + `gate.py.sample` 자유 편집 1줄 + stamp 재각인, `build[]`
  미등재): **rc=0 · stderr 0행 · provenance/파생 문면 0건 · `N_armH` 1→2 · `N_detected` 2→3 ·
  축별 baseline `ok=1` · `verdict: unit=s04 … HOLLOW labels=-` · 최종 PASS 발화**.
  즉 F-CR18-1 이 지적한 "커밋 표본이
  선언된 파생물인지 아무도 대조하지 않는다" 는 구멍은 **좁혀졌을 뿐 닫히지 않았다** — 파생을
  *선언한* 표본은 이제 대조되지만, 파생을 *선언하지 않은* 자유 편집 표본은 여전히 무성 통과한다.
  검사기 자신이 검사 대상에게 정의역을 물어보는 구조라 자기신고 누락에 구조적으로 무력하다.
  **닫혔다고 읽지 말 것.** 완전 봉합은 manifest 계약 변경(예: day-1 origin 표본을 제외한 전
  `samples[]` 에 `build[]` 항목 존재를 의무화)을 요구하며 **설계 소관**이다 — 본 회차는 설계
  동결 중이므로 계약을 바꾸지 않고 이 공백을 열거만 한다(설계 동결 해제 회차 잔여).

━━ SCOPE disjoint ━━
  ⊥ ADR-154(hard-gate self-verification 번들 presence/shape 정적 lint — 본 하네스의 day-1 표본
     대상일 뿐 동일 채널 아님) / ⊥ ADR-151(self-test 채널 execution-liveness) / ⊥ ADR-060(등급·승격)
   / ⊥ runtime soak / DAST. 본 채널 = "커밋 표본 실행 → LIVE·HOLLOW 분류" 단일 축.

━━ input-driven resource bound (정직 천장 동반) ━━
  입력 = repo-local manifest/baseline YAML + corpus 표본 파일 body + 자식 프로세스 출력(전부 repo
  또는 자기 파생). 완화: (1) 전 regex anchored + bounded quantifier(`{0,N}`), nested/lazy 0,
  매칭 우선순위는 리터럴 substring/startswith. (2) 관측 라인 MAX_CAPTURE_LINES 개 + 라인당
  MAX_LINE_LEN 절단. (3) manifest/baseline read 는 MAX_MANIFEST_BYTES 절단. (4) 자식 실행은
  TIMEOUT_SEC 전역 단일 timeout(표본별 override 없음) — timeout = INDETERMINATE(I-3), HOLLOW 계상 금지.
  정직 천장: 위는 **bounded degradation** 이지 "임의 입력 무해"가 아니다(무증거 안전성 단정 금지,
  ADR-151 §결정7 상속). 자식 프로세스는 표본 게이트 코드를 실행하므로 corpus 등재 = 실행 신뢰 부여다.

━━ CLI 계약 (고정 — self-test + workflow 가 소비; 임의 변경 금지) ━━
  python3 check_hollow_gate_corpus.py [--repo-root DIR] [--manifest FILE] [--baseline FILE]
                                      [--init-baseline] [--allow-baseline-shrink] [--reason TEXT]
    --repo-root              repo 루트 (기본 = __file__ parents[2]).
    --manifest               sidecar manifest (기본 = <repo>/docs/hollow-gate-corpus-manifest.yaml).
    --baseline               census baseline (기본 = <repo>/docs/hollow-gate-corpus-baseline.yaml).
    --init-baseline --reason TEXT   baseline **부재 시에만** 최초 각인. 이미 있으면 거부(exit 3).
    --allow-baseline-shrink --reason TEXT   기존 baseline 재기록(사유 각인). 플래그·사유 없이는 거부.
  `--write-baseline` 형 자기 하향 재생성 경로는 **부재**(ADR-175 명시 금지).

━━ Exit codes ━━
  0 = PASS — 선언 arm 전건 일치(arm-L 전건 LIVE ∧ arm-H 전건 HOLLOW) ∧ 축별 baseline 하한 충족
      ∧ N_indeterminate = 0 ∧ xkill 축-disjoint 성립 ∧ IC-1/2/5/6 성립.
  1 = FAIL — N_indeterminate ≥ 1 / verdict 불충족 / 축별 baseline 하한 미달 /
      kill_target_stage ∈ fail_stage(xkill) / IC assert 미성립 / pyyaml 부재(판정불가).
  3 = substrate-failure — ⓵ N_gates·N_armL·N_armH·N_probe 中 0 / ⓶ baseline 부재·digest 불일치·
      parse 실패 / ⓷ stamp drift / ⓸ bijection 파손 / ⓹ exec-tree blinding 파손(IC-4) /
      ⓺ recipe 정합 파손 — 대상이 samples[] 밖 / `build[].sample` 파생 provenance 불일치
      (커밋 표본 ≠ derived_from + recipe: anchor 매치 ≠ 1 · 재적용 sha256 불일치 · 트리 동일성 파손).
      추가: exit_space 미선언·빈 리스트(T-2ⓐ),
      금지키 ∩ manifest 키공간 ≠ ∅, manifest 부재·parse 실패(판정 기반 부재 = substrate, in-file 확장 declare),
      classification 정합 파손(선언 arm ↔ expected_verdict 불일치 / 미분류 unit).
  2 = argparse usage 전용 (argparse 기본 동작).

━━ 판정 계약 (동결 — ADR-175) ━━
  LIVE   ⟺ kill.fail=1 ∧ kill_target_stage ∈ fail_stage(kill) ∧ clean.fail=0 ∧ clean.term=1 ∧ DELIVERED
  HOLLOW ⟺ kill.fail=0 ∧ kill.term=1              ∧ clean.fail=0 ∧ clean.term=1 ∧ DELIVERED
  그 외 = INDETERMINATE.  `<leg>.fail`/`<leg>.term` = 마커 관측 여부(1/0) — **프로세스 rc 가 아니다**.
  rc 는 I-4(선언 exit_space 이탈)에만 쓴다. fail_stage(leg) = 관측된 `::error::[<STAGE-ID>]` 의
  stage id **집합**(순서·개수 미사용, 멤버십만). 상수 footer(SUMMARY) 공존은 문제삼지 않으며
  제외 목록을 두지 않는다. DELIVERED ⟺ observed_line_set(kill) ≠ observed_line_set(empty).
  observed_line_set = 4-part union: ①`::error::[STAGE]`(선언 stream) ②`::notice::` ③census 라인
  (`scanned-N:` 형) ④terminal-marker(선언 stream). corpus PASS ⟺ arm-L 전건 LIVE ∧ arm-H 전건 HOLLOW.

━━ INDETERMINATE 11 조건 + 평가 순서 ━━
  I-1 anchor 매치 ≠ 1 **(정의역 = run-time recipe unit(probe) 한정 — 커밋 sample unit 은 units
      구성에서 recipe=None 이라 I-1 가드에 구조적으로 미도달; 커밋 `build[].sample` 파생은 ⓺
      provenance 검사 소관)** / I-2 표본 syntax invalid **(정의역 = `entry` 가 `.py` 로 끝나는 leg
      한정 — 비-`.py` entry 는 compile 검사 자체에 미도달하여 I-2 가 구조적으로 성립하지 않는다.
      day-1 entry 는 전건 `gate.py` 라 현재는 공허-무해이나, 비-`.py` 게이트 편입 시 무고지로 I-2 가
      소실된다)** / I-3 기동 실패·timeout / I-4 rc ∉ exit_space /
  I-5 kill·clean 양쪽 FAIL / I-6 마커 전무 / I-7 ¬DELIVERED /
  I-8 kill.fail=1 ∧ kill_target_stage ∉ fail_stage(kill) / I-9 clean.term=0 /
  I-10 선언한 stream 이 아닌 곳에서 마커 관측 / I-11 ¬LIVE ∧ ¬HOLLOW ∧ (kill 관측 ≡ clean 관측).
  순서: **I-1·I-2·I-3·I-4·I-10 = 관측 무결성, verdict 함수 평가 前**(하나라도 성립 시 verdict 함수
  미호출, 즉시 INDETERMINATE). **I-5~I-9·I-11 = verdict 계산 後**.
  ┌ in-file declare (자기제한 등가성 — 뒤집힘 금지의 근거) ─────────────────────────────────────┐
  │ I-5~I-9·I-11 은 각 조건이 **자기제한적**(각각 ¬LIVE ∧ ¬HOLLOW 를 함의)이므로, "verdict 미해당 │
  │ 분에만 평가" 와 "전건 평가 후 성립 시 INDETERMINATE 로 강등" 이 **관측적으로 동일**하다.       │
  │ 증명: I-5(kill.fail=1 → ¬HOLLOW, clean.fail=1 → ¬LIVE) / I-6(관측 전무 leg → term=0 ∧ fail=0  │
  │ → 양 정의 모두 불성립) / I-7(양 정의가 DELIVERED 요구) / I-8(kill.fail=1 → ¬HOLLOW, 그리고    │
  │ target ∉ fail_stage → ¬LIVE) / I-9(양 정의가 clean.term 요구) / I-11(명시 conjunct).           │
  │ 본 구현은 후자(전건 평가 + 강등)를 택한다 — 등가이면서 각 conjunct 가 load-bearing 으로 남아   │
  │ mutation 으로 반증 가능하기 때문이다. conjunct 를 제거하면 등가성이 깨지고 정상 arm 이 죽는다: │
  │  · I-8 의 `kill.fail=1` 협착(T-1)을 빼면 arm-H(fail_stage=∅)에서 공허 참 → 정상 HOLLOW 전멸.  │
  │  · I-11 의 `¬LIVE ∧ ¬HOLLOW` 가드를 빼면 arm-H(kill 관측 ≡ clean 관측 = arm-H 의 정의)가 전멸.│
  └──────────────────────────────────────────────────────────────────────────────────────────────┘

━━ xkill leg — 검증 tier 전용 (verdict 미투입) ━━
  verdict 함수는 kill/clean/empty 3 leg 만 본다. xkill 은 **축-disjoint 대조** 전용:
  `kill_target_stage ∉ fail_stage(xkill)` 이어야 한다(위반 = exit 1). 상수 footer(SUMMARY)를
  kill_target_stage 로 선언하면 SUMMARY ∈ fail_stage(xkill) 이라 RED — 이것이 "자동 적중해 공허해진
  stage 선언"의 유일 기계 검출자다. xkill 은 samples[].fixtures 에 등재되어 bijection(orphan 0)을 만족한다.

━━ in-file declare ① T-2 exit_space 를 [0, 1] 로 좁힌 근거 ━━
  day-1 표본 게이트(check_hard_gate_self_verification.py)의 실 exit space 는 {0,1,2} 이나 rc=2 는
  argparse usage 전용(미지 플래그·잉여 positional)이다. corpus leg 은 명시 인자 주입으로만 구동하므로
  rc=2 관측 = **표본 구동 오류**이며 I-4 로 잡아야 한다. {0,1,2} 를 그대로 선언하면 I-4 가 이 게이트에서
  영구 발동 불가가 되어 "선언됐는데 절대 안 걸리는 조건" = 본 Story 가 겨냥한 hollow 패턴 그 자체가 된다.
  T-2ⓐ 닫힘: exit_space 미선언/빈 리스트는 **loud 실패(exit 3)** — `rc ∉ ∅` 공허 참으로 전 leg 이
  조용히 INDETERMINATE 로 흐르는 경로를 만들지 않는다.

━━ in-file declare ② 금지키 denylist — 설계 문면 9종 vs 명명 3종 ━━
  설계 문면은 금지키 denylist "9종(`non_applicable` · `waiver` · `xfail` 등)"이라 적으나 **명명된 것은
  3종뿐이며 나머지 6종과 '9' 라는 수의 술어(모집단·판정 규칙)는 어디에도 기재돼 있지 않다.**
  본 구현은 **명명 3종만** 강제하고(manifest 키공간과의 교집합 ≠ ∅ = exit 3) 그 사실을 여기 기록한다.
  6종을 추정으로 지어내지 않는다(미기재를 발명으로 메우면 그 자체가 근거 없는 강제가 된다).
  잔여: 설계가 나머지 6종과 '9' 의 술어를 명시하면 상수를 확장한다.

━━ in-file declare ③ baseline 재생성 경로 — ADR-175 ↔ CP 문면 충돌 ━━
  ADR-175 는 `--write-baseline` 형 **자기 하향 재생성 경로**를 명시 금지한다. 한편 CP 는 day-1
  bootstrap 을 요구한다. 본 구현의 정산: `--init-baseline` 은 **파일 부재 시에만** 동작하고 이미 있으면
  거부하므로 "자기 하향 재생성"이 될 수 없다(하향은 기존 값이 있어야 성립) → ADR-175 금지와 비충돌.
  하향(및 상향) 재기록은 `--allow-baseline-shrink --reason TEXT` 단일 경로로만 가능하며 사유가 baseline
  파일에 각인되고 content_digest 에 결박된다. 잔여(정직 공개): ratchet-UP(고수위 상향)도 현재 같은
  플래그를 쓴다 — 플래그 이름이 위험 방향(shrink)을 따르므로 상향 시 이름과 의도가 어긋난다.
  baseline content_digest 산식(수기 편집 검출):
    payload = "schema_version=1.0\n" + "<axis>=<value>\n"(CENSUS_AXES 순서) + "reason=<reason>\n"
    content_digest = "sha256:" + sha256(payload.encode("utf-8")).hexdigest()

━━ in-file declare ④ census emit 형식 (설계 미규정 — 본 구현이 확정) ━━
  7축을 **개별** emit 한다(총합 emit 금지 — 총합만 내면 어느 축이 줄었는지 구별 불가).
  stdout 에 축별 1줄, 고정 형식: `census: <axis>=<int>`  (예: `census: N_gates=1`).
  축 순서 = N_gates, N_armL, N_armH, N_probe, N_detected, N_flip, N_indeterminate.
  N_armL/N_armH = **커밋 표본** 계수(probe 제외), N_probe = run-time materialize 되는 probe 계수.
  N_detected = HOLLOW 계상분, N_flip = IC-2 뒤집힘(PRE=LIVE → POST=HOLLOW) 관측 수.
  INDETERMINATE 는 분모 N 에 **포함**, detected·flip 에는 **불포함**.
  baseline 대조는 **축별**이다(집계 비교 금지). 6축 = 하한(N < baseline = FAIL),
  N_indeterminate = 상한(≥ 1 = exit 1).

━━ MUTATION-SENTINEL (self-test 가 sed 로 죽일 분기 — M1~M7) ━━
  M1: I-8 협착 conjunct (`kill.fail=1`)            — 제거 시 arm-H 정상 표본이 INDETERMINATE 로 전멸.
  M2: I-11 `¬LIVE ∧ ¬HOLLOW` 가드                  — 제거 시 arm-H(kill 관측 ≡ clean 관측)가 전멸.
  M3: exit_space 검사 (I-4 + T-2ⓐ loud 실패)        — 제거 시 rc 이탈이 조용히 통과.
  M4: census 개별 emit (7축 축별)                   — 제거 시 축 축소가 총합에 숨는다.
  M5: IC-4 exec-tree blinding **호출부**            — 제거 시 stamp 등 arm 누설 표면이 exec dir 에 잔존.
  M7: 형제 부재 불변식 (`len(siblings) != 1`)       — 제거 시 **실행 순번 누설 채널**(자식이 형제
      dir 수로 leg 순번을 역산)이 무성 복원.
  M6: xkill 축-disjoint 검사                        — 제거 시 상수 footer stage 선언이 공허하게 통과.

  ★ M7 신설 경위 (F-CR19-1/-2 정정 — 종전 단정의 실행 반증):
    종전 이 자리에는 "형제 부재 conjunct 는 M5 가 덮는 같은 함수 안에 있다(신규 M 번호 없음)" 가
    적혀 있었다. **실행으로 반증됐다.** M5 시나리오는 fixture 에 `stamp_leak.txt` 를 주입하는
    구성이라 KILL 을 내는 것은 금지-토큰 분기이고, 형제 conjunct 는 그 시나리오에서 한 번도
    발화하지 않는다. 실제로 형제 conjunct 만 제거한 mutant 는 self-test·pytest 전건 생존했다
    (= 회귀 가드 판별력 0). 같은 함수 안에 있다는 사실은 같은 mutant 가 죽인다는 뜻이 아니다.
    ⇒ 형제 불변식은 **자기 번호(M7)와 자기 대조군**을 갖는다.
    M7 은 2단 mutant 를 쓴다 — 이 불변식은 정상 corpus 에서 절대 발화하지 않으므로(정리가 선행해
    형제 수가 항상 1) 무변형 baseline 으로는 대조군이 성립하지 않는다. 정리를 먼저 무력화해
    발화 상태를 만든 뒤 불변식을 제거해 exit flip(3 → 0)을 본다. 상세 = self-test §6 M7 주석.
    비대칭 실측(정직 기재): **정리만** 무력화한 mutant 는 불변식이 살아 있는 한 기존 케이스
    다수가 이미 RED 로 잡는다. 무방비였던 것은 **불변식 축 단독**이며 M7 이 그 축을 겨냥한다.

ADR refs: ADR-175 (결정 SSOT — 동적 hollow 분류 · arm-invariant 판정기 계약 · 분모 단조 하한 ·
  sidecar manifest) / ADR-154 (day-1 표본 게이트 + honest-ceiling 상속) / ADR-151 (§결정7 정직 천장
  상속) / ADR-061 §결정1 (Python entry-point + thin bash wrapper) / ADR-119 (게이트 = ground-truth,
  검증 후 단언).
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections import namedtuple
from pathlib import Path

# 출력 인코딩 robust 화 (Windows cp949 등 비-UTF-8 locale 에서 한글·기호 print 차단 — ADR-061 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

try:
    import yaml  # pyyaml (requirements.txt 등재)
except ImportError:  # 부재 = 판정불가 = fail-closed exit 1 (silent skip 금지)
    yaml = None

EXIT_PASS = 0       # PASS
EXIT_FAIL = 1       # verdict 불충족 / INDETERMINATE / baseline 하한 미달 / xkill 축 / IC assert
EXIT_SUBSTRATE = 3  # substrate-failure (판정 기반 자체가 깨짐)
# EXIT 2 = argparse usage 전용.

# ── 실행 규약 (전역 단일 값 — 표본별 override 금지) ────────────────────────────────
TIMEOUT_SEC = 30

# ── 입력 bound (bounded degradation — 임의 입력 무해 아님) ─────────────────────────
MAX_MANIFEST_BYTES = 256 * 1024
MAX_CAPTURE_LINES = 2000
MAX_LINE_LEN = 8192

# ── corpus 좌표 ───────────────────────────────────────────────────────────────────
CORPUS_ROOT_REL = "tests/fixtures/hollow-gate-corpus"
SAMPLE_SUFFIX = ".sample"
LEG_ROLES = ("kill", "clean", "empty", "xkill")   # xkill = 검증 tier 전용 (verdict 미투입)
VERDICT_LEGS = ("kill", "clean", "empty")

# ── census 7축 ────────────────────────────────────────────────────────────────────
CENSUS_AXES = (
    "N_gates", "N_armL", "N_armH", "N_probe", "N_detected", "N_flip", "N_indeterminate",
)
LOWER_BOUND_AXES = tuple(a for a in CENSUS_AXES if a != "N_indeterminate")

# ── 금지키 denylist — 설계 문면 "9종" 중 **명명된 3종만** (in-file declare ② 참조) ──
FORBIDDEN_MANIFEST_KEYS = ("non_applicable", "waiver", "xfail")

# ── IC-4 exec-tree blinding: exec dir 에 있어선 안 되는 basename 토큰 ──────────────
BLINDING_FORBIDDEN_TOKENS = ("manifest", "stamp", "baseline", "probe")

# ── 관측면 4-part 분류자 (anchored + bounded quantifier) ───────────────────────────
_FAIL_MARKER_RE = re.compile(r"^::error::\[([A-Za-z0-9_.\-]{1,64})\]")
_NOTICE_RE = re.compile(r"^::notice::")
_CENSUS_LINE_RE = re.compile(r"^\s{0,8}(?:census\s{0,4}:|[A-Za-z][A-Za-z0-9_]{0,40}-N\s{0,4}:)")

# ── STAGE-ID 어휘 (self-test grep 대상 — 고정) ────────────────────────────────────
STAGE_DEP = "DEP"
STAGE_SUBSTRATE = "SUBSTRATE"
STAGE_VERDICT = "VERDICT"
STAGE_INDETERMINATE = "INDETERMINATE"
STAGE_BASELINE = "BASELINE"
STAGE_XKILL = "XKILL-AXIS"
STAGE_SUMMARY = "SUMMARY"

# ── 판정 자료구조 ─────────────────────────────────────────────────────────────────
# LegObs = **관측만** 담는다 (arm/declared/expected 부재 — 판정 함수 도달 불가 구조).
LegObs = namedtuple("LegObs", "fail term fail_stages observed")
VerdictBundle = namedtuple("VerdictBundle", "kill clean empty")


def _error(stage_id, msg):
    """위반 1건을 stderr 에 STAGE-ID prefix + 1행 출력 (단일 진입점, fail-closed 계약)."""
    print(f"::error::[{stage_id}] {msg}", file=sys.stderr)


def _emit(line):
    """verdict / census / echo = stdout (관측면 선언 stream)."""
    print(line)


# ── 기본 어댑터 ───────────────────────────────────────────────────────────────────
def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError:
        return None


def _rel_file_map(root):
    """디렉터리 하위 전 파일 → {상대 posix 경로: Path}. (트리 동일성 대조 어댑터)"""
    out = {}
    if not root.is_dir():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = p
    return out


def _load_yaml(path, what):
    """bounded read + safe_load. (data, None) 또는 (None, 오류메시지)."""
    if yaml is None:
        return None, "pyyaml 미설치"
    try:
        raw = path.read_bytes()[:MAX_MANIFEST_BYTES]
    except OSError as exc:
        return None, f"{what} 읽기 불가: {exc}"
    try:
        data = yaml.safe_load(raw.decode("utf-8", errors="replace"))
    except Exception as exc:  # yaml.YAMLError 포함 — parse 실패 = substrate
        return None, f"{what} YAML parse 실패: {exc}"
    if not isinstance(data, dict):
        return None, f"{what} 최상위가 mapping 이 아님"
    return data, None


def _walk_keys(node, out):
    """mapping 키공간 재귀 수집 (denylist 교집합 검사용)."""
    if isinstance(node, dict):
        for k, v in node.items():
            out.add(str(k))
            _walk_keys(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk_keys(v, out)


# ── manifest 검증 (substrate) ─────────────────────────────────────────────────────
def _validate_manifest(manifest):
    """4블록 + 필드 shape 검증. 오류메시지 리스트 반환(비어있으면 통과)."""
    errs = []
    for block in ("gates", "samples", "build", "classification"):
        if block not in manifest:
            errs.append(f"필수 블록 '{block}' 부재")
        elif not isinstance(manifest[block], list) or not manifest[block]:
            errs.append(f"블록 '{block}' 이 비어있거나 리스트가 아님")
    if errs:
        return errs
    if len(manifest["samples"]) < 1:
        errs.append("samples[] 길이 < 1")

    gate_fields = (
        "id", "source_path", "entry", "invoke_args", "fail_marker_stream",
        "terminal_marker_stream", "fail_marker_stage_id", "terminal_marker_prefix", "exit_space",
    )
    for g in manifest["gates"]:
        if not isinstance(g, dict):
            errs.append("gates[] 항목이 mapping 아님")
            continue
        for f in gate_fields:
            if f not in g:
                errs.append(f"gates[{g.get('id', '?')}]: 필수 필드 '{f}' 부재")
        # MUTATION-SENTINEL M3: exit_space 선언 강제 (T-2ⓐ — 미선언/빈 리스트 = loud 실패).
        es = g.get("exit_space")
        if not isinstance(es, list) or len(es) == 0:
            errs.append(
                f"gates[{g.get('id', '?')}]: exit_space 미선언 또는 빈 리스트 — "
                f"`rc ∉ ∅` 공허 참으로 I-4 가 영구 발동 불가가 되는 경로 차단(T-2ⓐ loud 실패)"
            )
        elif not all(isinstance(x, int) for x in es):
            errs.append(f"gates[{g.get('id', '?')}]: exit_space 원소가 정수가 아님")
        if g.get("fail_marker_stream") not in ("stdout", "stderr"):
            errs.append(f"gates[{g.get('id', '?')}]: fail_marker_stream 은 stdout/stderr 중 하나")
        if g.get("terminal_marker_stream") not in ("stdout", "stderr"):
            errs.append(f"gates[{g.get('id', '?')}]: terminal_marker_stream 은 stdout/stderr 중 하나")

    gate_ids = {g.get("id") for g in manifest["gates"] if isinstance(g, dict)}
    sample_ids = set()
    for s in manifest["samples"]:
        if not isinstance(s, dict):
            errs.append("samples[] 항목이 mapping 아님")
            continue
        for f in ("id", "gate", "path", "fixtures"):
            if f not in s:
                errs.append(f"samples[{s.get('id', '?')}]: 필수 필드 '{f}' 부재")
        if s.get("id") in sample_ids:
            errs.append(f"samples[]: id 중복 '{s.get('id')}'")
        sample_ids.add(s.get("id"))
        if s.get("gate") not in gate_ids:
            errs.append(f"samples[{s.get('id', '?')}]: 미지 gate '{s.get('gate')}'")
        fx = s.get("fixtures")
        if not isinstance(fx, dict):
            errs.append(f"samples[{s.get('id', '?')}]: fixtures 가 mapping 아님")
        else:
            for role in LEG_ROLES:
                if role not in fx:
                    errs.append(f"samples[{s.get('id', '?')}]: fixtures.{role} 미등재 (orphan 유발)")
    return errs


# ── ⓸ bijection: corpus 하위 전 파일이 정확히 1개 samples[] 를 참조 ────────────────
def _check_bijection(repo_root, samples, gates_by_id):
    """corpus 파일 ↔ samples[] 1:1. (오류메시지 리스트, 검사 파일 수).

    표본 루트 직속으로 인정하는 파일 = 그 표본 gate 의 `entry` + `.sample` 과 stamp 뿐이다
    (entry 이름은 manifest 에서 파생 — 하드코딩 금지).
    """
    errs = []
    corpus_root = repo_root / CORPUS_ROOT_REL
    if not corpus_root.is_dir():
        return [f"{CORPUS_ROOT_REL}: corpus 루트 부재"], 0
    claims = {}
    for s in samples:
        s_path = (repo_root / s["path"]).resolve()
        entry_names = {gates_by_id[s["gate"]]["entry"] + SAMPLE_SUFFIX, "stamp.yaml" + SAMPLE_SUFFIX}
        claims[s["id"]] = (s_path, set(s["fixtures"].values()), entry_names)
    n = 0
    for p in sorted(corpus_root.rglob("*")):
        if not p.is_file():
            continue
        n += 1
        rp = p.resolve()
        owners = []
        for sid, (s_path, fx_dirs, entry_names) in claims.items():
            try:
                rel = rp.relative_to(s_path)
            except ValueError:
                continue
            parts = rel.parts
            if len(parts) == 1 and parts[0] in entry_names:
                owners.append(sid)
            elif len(parts) > 1 and parts[0] in fx_dirs:
                owners.append(sid)
        if len(owners) != 1:
            errs.append(
                f"{rp.relative_to(repo_root).as_posix()}: samples[] 참조 {len(owners)}개 "
                f"(정확히 1 필요 — orphan 0 / 중복 참조 0). owners={owners}"
            )
    return errs, n


# ── ⓷ stamp drift (정의역 = 커밋 표본 한정) ───────────────────────────────────────
def _check_stamps(repo_root, samples, gates_by_id):
    errs = []
    for s in samples:
        s_path = repo_root / s["path"]
        stamp_path = s_path / ("stamp.yaml" + SAMPLE_SUFFIX)
        data, err = _load_yaml(stamp_path, f"samples[{s['id']}].stamp")
        if err:
            errs.append(err)
            continue
        gate = gates_by_id[s["gate"]]
        declared_source = data.get("source_path")
        if not declared_source:
            errs.append(f"samples[{s['id']}].stamp: source_path 부재")
            continue
        if data.get("gate_id") != gate["id"]:
            errs.append(
                f"samples[{s['id']}].stamp: gate_id '{data.get('gate_id')}' ≠ manifest gate '{gate['id']}'"
            )
        src_actual = _sha256_file(repo_root / declared_source)
        if src_actual is None:
            errs.append(f"samples[{s['id']}].stamp: source_path '{declared_source}' 읽기 불가")
        elif src_actual != data.get("source_sha256"):
            errs.append(
                f"samples[{s['id']}].stamp: source_sha256 drift — 선언 {data.get('source_sha256')} "
                f"≠ 현행 {src_actual} ({declared_source}). 자동 갱신 금지 — 표본 재제작 필요."
            )
        art_path = s_path / (gate["entry"] + SAMPLE_SUFFIX)
        art_actual = _sha256_file(art_path)
        if art_actual is None:
            errs.append(f"samples[{s['id']}].stamp: artifact '{art_path.name}' 읽기 불가")
        elif art_actual != data.get("artifact_sha256"):
            errs.append(
                f"samples[{s['id']}].stamp: artifact_sha256 drift — 선언 {data.get('artifact_sha256')} "
                f"≠ 현행 {art_actual} ({s['path']}/{art_path.name})."
            )
    return errs


# ── recipe (build[]) ──────────────────────────────────────────────────────────────
def _recipe_runtime_path(target_rel, fixtures, unit_dir, fx_dir, gate_entry):
    """recipe target(sample 상대, `.sample` 포함) → materialize 된 런타임 경로. 미해석 = None."""
    stripped = target_rel[:-len(SAMPLE_SUFFIX)] if target_rel.endswith(SAMPLE_SUFFIX) else target_rel
    parts = [p for p in stripped.split("/") if p]
    if not parts:
        return None
    if len(parts) == 1 and parts[0] == gate_entry:
        return unit_dir / gate_entry
    if parts[0] in set(fixtures.values()):
        return fx_dir.joinpath(*parts[1:])
    return None


def _apply_recipe(data_bytes, recipe):
    """anchor_from → anchor_to 1회 치환. (bytes, 매치수)."""
    text = data_bytes.decode("utf-8", errors="replace")
    n = text.count(recipe["anchor_from"])
    if n != 1:
        return None, n
    return text.replace(recipe["anchor_from"], recipe["anchor_to"], 1).encode("utf-8"), n


# ── ⓺(확장) 커밋 `build[].sample` 파생 provenance ─────────────────────────────────
def _check_sample_provenance(repo_root, build, samples_by_id):
    """커밋 표본이 정말 `derived_from + recipe` 의 산물인지 검사. 오류메시지 리스트 반환.

    정의역 = **커밋 표본**(`build[]` 항목 中 `sample:` 키를 가진 것). run-time probe 는 대상이
    아니다(그쪽은 I-1 이 본다). 검사 3항:
      ① 파생 지점 특정 — derived_from 원본 target 에서 anchor 매치 수 == 1.
      ② 파생 일치 — recipe 재적용 결과 bytes 의 sha256 == 커밋 표본 target 의 sha256.
      ③ 트리 동일성 — 두 표본 하위 전 파일이 상대경로 집합·바이트 모두 동일. 예외 2개뿐:
         (a) recipe target(=②가 검사) (b) `stamp.yaml.sample`(표본별 메타 — ⓷ stamp drift 소관).
    위반 = ⓺ substrate-failure(exit 3). 신규 조건 번호를 만들지 않고 ⓺ 문면을 확장 재사용한다.

    배경(F-CR18-1): 커밋 sample unit 은 `units` 에 recipe=None 으로 실려 I-1(anchor 매치 ≠ 1)
    가드에 **구조적으로 도달하지 못한다**. 그래서 이 함수 이전에는 "커밋 s02 가 s01+recipe 파생인가"
    를 검사하는 경로가 **전무**했다(manifest 는 파생을 선언만 하고 아무도 대조하지 않았다).
    ⓷ stamp drift 와 disjoint: stamp 는 `<표본 자신의 현재 파일> ↔ <자신의 선언 해시>` 를 보고,
    본 검사는 `<표본> ↔ <다른 표본 + recipe>` 관계를 본다(stamp 를 함께 위조하면 ⓷ 는 통과한다).

    ★ 정의역 공백 — **닫혔다고 읽지 말 것** (F-CR19-3, 모듈 docstring 정직 천장 (c) 와 동일 항목):
    본 루프는 `build[]` 를 순회한다. 따라서 표본을 `samples[]`·`classification[]` 에만 등재하고
    `build[]` 항목을 **생략한** 자유 편집 표본은 이 검사에 **한 번도 걸리지 않는다**. 검사기가
    검사 대상의 자기신고로 정의역을 정하는 구조라 신고 누락에 구조적으로 무력하다. F-CR18-1 의
    구멍은 **좁혀졌을 뿐 닫히지 않았다**. 완전 봉합 = manifest 계약 변경(설계 소관, 동결 중).
    """
    errs = []
    for b in build:
        if not isinstance(b, dict) or not b.get("sample"):
            continue
        sid = b["sample"]
        src = samples_by_id.get(b.get("derived_from"))
        dst = samples_by_id.get(sid)
        if src is None or dst is None:
            continue   # 미지 id = build[] 정합 루프(⓺)가 이미 loud 실패로 잡는다
        src_root = repo_root / src["path"]
        dst_root = repo_root / dst["path"]
        target_rel = str(b.get("target", "")).replace("\\", "/").strip("/")

        # ① 파생 지점 특정
        try:
            src_bytes = (src_root / target_rel).read_bytes()
        except OSError as exc:
            errs.append(f"build[{sid}]: derived_from target '{src['path']}/{target_rel}' 읽기 불가: {exc}")
            continue
        patched, n_match = _apply_recipe(src_bytes, b)
        if patched is None:
            errs.append(
                f"build[{sid}]: 커밋 표본 파생 지점 특정 실패 — derived_from '{src['id']}' 의 "
                f"'{target_rel}' 에서 anchor 매치 {n_match} ≠ 1 (파생 관계 선언이 대조 불가)."
            )
            continue

        # ② 파생 일치
        dst_sha = _sha256_file(dst_root / target_rel)
        if dst_sha is None:
            errs.append(f"build[{sid}]: 커밋 표본 target '{dst['path']}/{target_rel}' 읽기 불가.")
        elif dst_sha != _sha256_bytes(patched):
            errs.append(
                f"build[{sid}]: 파생 불일치 — 커밋 '{dst['path']}/{target_rel}' sha256={dst_sha} "
                f"≠ derived_from '{src['id']}' + recipe 재적용 sha256={_sha256_bytes(patched)} "
                f"(커밋 표본이 선언된 파생물이 아니다 — 자유 편집분 유입)."
            )

        # ③ 트리 동일성 (예외 = recipe target + stamp 2개뿐)
        exempt = {target_rel, "stamp.yaml" + SAMPLE_SUFFIX}
        src_files = _rel_file_map(src_root)
        dst_files = _rel_file_map(dst_root)
        for rel in sorted((set(src_files) | set(dst_files)) - exempt):
            if rel not in dst_files:
                errs.append(
                    f"build[{sid}]: 트리 동일성 파손 — '{rel}' 이 derived_from '{src['id']}' 에만 "
                    f"존재(커밋 표본 누락)."
                )
            elif rel not in src_files:
                errs.append(
                    f"build[{sid}]: 트리 동일성 파손 — '{rel}' 이 커밋 표본 '{sid}' 에만 존재(잉여)."
                )
            elif _sha256_file(src_files[rel]) != _sha256_file(dst_files[rel]):
                errs.append(
                    f"build[{sid}]: 트리 동일성 파손 — '{rel}' 바이트 불일치 "
                    f"(recipe target·stamp 외 전 파일 byte-identical 요구 — 축 대표성 위조 차단)."
                )
    return errs


# ── materialize (전 표본 동일 절차 + IC-4 blinding) ───────────────────────────────
def _materialize(exec_root, repo_root, source_sample, fixture_dirname, gate_entry, recipe):
    """exec unit 1개 생성 → (unit_dir, fx_dir, entry_sha, 오류메시지 or None).

    exec dir 명은 실행별 재배정(uuid4) — 표본 id·leg 이름은 경로에 남기지 않는다(IC-4).
    at-rest `.sample` 확장자는 **벗겨서** materialize 한다.
    오류 반환 시 **자기가 만든 unit_dir 을 스스로 정리**한다 — 남기면 그 잔재가 다음 leg 의
    형제 디렉터리로 세어져 "실행 순번 누설 0"(IC-4) 불변식을 오염시킨다.
    """
    unit_dir = exec_root / uuid.uuid4().hex[:16]
    fx_dir = unit_dir / "fx"
    fx_dir.mkdir(parents=True, exist_ok=False)

    def _fail(msg):
        shutil.rmtree(unit_dir, ignore_errors=True)
        return None, None, None, msg

    src_entry = repo_root / source_sample["path"] / (gate_entry + SAMPLE_SUFFIX)
    try:
        entry_bytes = src_entry.read_bytes()
    except OSError as exc:
        return _fail(f"entry '{src_entry}' 읽기 불가: {exc}")
    (unit_dir / gate_entry).write_bytes(entry_bytes)

    src_fx = repo_root / source_sample["path"] / fixture_dirname
    if src_fx.is_dir():
        for p in sorted(src_fx.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(src_fx)
            name = rel.name[:-len(SAMPLE_SUFFIX)] if rel.name.endswith(SAMPLE_SUFFIX) else rel.name
            dst = fx_dir / rel.parent / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst)

    if recipe is not None:
        rt = _recipe_runtime_path(
            recipe["target"], source_sample["fixtures"], unit_dir, fx_dir, gate_entry
        )
        if rt is None or not rt.is_file():
            return _fail(f"recipe target '{recipe['target']}' 런타임 미해석")
        patched, _n = _apply_recipe(rt.read_bytes(), recipe)
        if patched is None:
            return _fail(f"recipe anchor 매치 ≠ 1 (런타임): {recipe['target']}")
        rt.write_bytes(patched)

    entry_sha = _sha256_file(unit_dir / gate_entry)
    return unit_dir, fx_dir, entry_sha, None


def _blinding_violations(unit_dir, exec_root):
    """IC-4: exec dir 에 manifest/stamp/baseline/probe 부재 ∧ `.sample` 잔재 0 ∧ 형제 unit 0.

    ━━ 정직 기재 — IC-4 는 격리 경계가 **아니다** (F-CR18-3, P2 관측-only) ━━
      본 함수는 **표면 위생 assert** 이지 sandbox·격리 경계가 아니다. 구체적으로:
       · basename **토큰 매칭**이라 금지 토큰이 없는 이름으로 개명하면 그대로 통과한다
         (예: `stamp.yaml` → `meta.yaml`). 내용 기반 검사가 아니다.
       · `_run_leg` 의 `subprocess.run(...)` 에 **`env=` 인자가 없어** 자식이 부모 env 전체를
         상속한다 — `GITHUB_WORKSPACE` 등을 경유해 자식이 repo(따라서 manifest/stamp/baseline)
         에 도달할 수 있다. 본 회차 처분 = **정직 기재**이며 `env=` 를 추가하지 않았다.
      즉 IC-4 가 닫는 것은 "exec tree 표면에 arm 신호가 놓여있음"까지이고, 표면 밖 역산 채널
      (내용 read / env 경유 repo 도달 / 개명 회피)은 열려 있다.

    ━━ 형제 부재 불변식 (F-CR18-9) — MUTATION-SENTINEL M7 ━━
      `exec_root` 직속 하위 디렉터리 수 != 1 = violation. 자식 표본이
      `Path(__file__).resolve().parent.parent.iterdir()` 로 형제 수를 세면 그 값이
      **실행 순번**(kill→clean→empty→xkill)이 되어, fixture 를 한 번도 열지 않고 순번만으로
      기대 마커를 위조할 수 있다 = 실행 순번 누설 채널. leg 별 즉시 정리(caller)의 기계 대조.
      회귀 가드 = **M7 자기 대조군**(self-test §6, 2단 mutant) + pytest
      `test_f_cr18_9_sibling_invariant_counts_actual_exec_root_dirs`(형제 1개/2개 대조).
      ★ 이 conjunct 는 M5 시나리오가 덮지 않는다 — 실행 반증됨(F-CR19-2). 위 docstring 상단
      MUTATION-SENTINEL 절의 "M7 신설 경위" 참조.
    """
    bad = []
    for p in sorted(unit_dir.rglob("*")):
        name = p.name.lower()
        for tok in BLINDING_FORBIDDEN_TOKENS:
            if tok in name:
                bad.append(f"{p.name} (금지 토큰 '{tok}')")
        if p.name.endswith(SAMPLE_SUFFIX):
            bad.append(f"{p.name} (`.sample` 확장자 잔재 — materialize 절차 파손)")
    siblings = sorted(d.name for d in exec_root.iterdir() if d.is_dir())
    if len(siblings) != 1:
        bad.append(
            f"exec-root 직속 디렉터리 {len(siblings)}개 (정확히 1 필요) — 자식이 형제 수를 세어 "
            f"실행 순번을 역산하는 **실행 순번 누설 채널**. leg 별 즉시 정리 파손."
        )
    return bad


# ── leg 실행 + 관측 ───────────────────────────────────────────────────────────────
def _run_leg(unit_dir, fx_dir, gate_entry, invoke_args):
    """(rc, stdout, stderr, err) — err 비어있지 않으면 I-3."""
    argv = [sys.executable, str(unit_dir / gate_entry)]
    for a in invoke_args:
        argv.append(str(a).replace("{fixture}", str(fx_dir)))
    try:
        proc = subprocess.run(
            argv, cwd=str(unit_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return None, "", "", f"timeout {TIMEOUT_SEC}s 초과 (I-3 — HOLLOW 계상 금지)"
    except OSError as exc:
        return None, "", "", f"기동 실패: {exc} (I-3)"
    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err, None


def _observe(stdout_text, stderr_text, gate):
    """4-part union 관측 → (LegObs, wrong_stream 리스트[I-10])."""
    fail_stream = gate["fail_marker_stream"]
    term_stream = gate["terminal_marker_stream"]
    term_prefix = gate["terminal_marker_prefix"]
    observed = set()
    stages = set()
    wrong = []
    fail_seen = False
    term_seen = False
    for stream, text in (("stdout", stdout_text), ("stderr", stderr_text)):
        for raw in text.splitlines()[:MAX_CAPTURE_LINES]:
            ln = raw.rstrip()[:MAX_LINE_LEN]
            m = _FAIL_MARKER_RE.match(ln)
            is_fail = m is not None
            is_term = ln.startswith(term_prefix)
            is_notice = bool(_NOTICE_RE.match(ln))
            is_census = bool(_CENSUS_LINE_RE.match(ln))
            if is_fail and stream != fail_stream:
                wrong.append(f"fail-marker 가 선언 stream({fail_stream}) 아닌 {stream} 에서 관측")
            if is_term and stream != term_stream:
                wrong.append(f"terminal-marker 가 선언 stream({term_stream}) 아닌 {stream} 에서 관측")
            if is_fail or is_term or is_notice or is_census:
                observed.add((stream, ln))
            if is_fail and stream == fail_stream:
                fail_seen = True
                stages.add(m.group(1))
            if is_term and stream == term_stream:
                term_seen = True
    return LegObs(fail_seen, term_seen, frozenset(stages), frozenset(observed)), wrong


def _observed_digest(obs):
    payload = "\n".join(f"{stream}\t{text}" for stream, text in sorted(obs.observed))
    return _sha256_bytes(payload.encode("utf-8"))


# ── ★ verdict — arm-invariant (시그니처에 arm/declared/expected 구조적 부재) ───────
def _verdict(bundle, kill_target_stage):
    """동결 판정식. 입력 = leg 관측 3종 + 선언 stage id. **arm 을 볼 수 없다.**

    LIVE   ⟺ kill.fail ∧ target ∈ fail_stage(kill) ∧ ¬clean.fail ∧ clean.term ∧ DELIVERED
    HOLLOW ⟺ ¬kill.fail ∧ kill.term ∧ ¬clean.fail ∧ clean.term ∧ DELIVERED
    """
    delivered = bundle.kill.observed != bundle.empty.observed
    live = (
        bundle.kill.fail
        and kill_target_stage in bundle.kill.fail_stages
        and not bundle.clean.fail
        and bundle.clean.term
        and delivered
    )
    hollow = (
        not bundle.kill.fail
        and bundle.kill.term
        and not bundle.clean.fail
        and bundle.clean.term
        and delivered
    )
    if live:
        return "LIVE", delivered
    if hollow:
        return "HOLLOW", delivered
    return "INDETERMINATE", delivered


def _post_verdict_labels(bundle, kill_target_stage, verdict, delivered):
    """I-5~I-9 · I-11 (verdict 계산 後). 각 조건은 자기제한적 — docstring 등가성 증명 참조."""
    live = verdict == "LIVE"
    hollow = verdict == "HOLLOW"
    labels = []
    if bundle.kill.fail and bundle.clean.fail:
        labels.append("I-5")
    if not bundle.kill.observed or not bundle.clean.observed:
        labels.append("I-6")
    if not delivered:
        labels.append("I-7")
    # MUTATION-SENTINEL M1: I-8 협착 conjunct — `kill.fail` 를 빼면 arm-H(fail_stage=∅)에서
    # 공허 참이 되어 정상 HOLLOW 표본이 INDETERMINATE 로 전멸(day-1 born-RED).
    if bundle.kill.fail and kill_target_stage not in bundle.kill.fail_stages:
        labels.append("I-8")
    if not bundle.clean.term:
        labels.append("I-9")
    # MUTATION-SENTINEL M2: I-11 `¬LIVE ∧ ¬HOLLOW` 가드 — 제거 시 arm-H 는 정의상
    # kill 관측 ≡ clean 관측 이므로 정상 표본이 전멸한다 (비협상 가드).
    if (not live) and (not hollow) and (bundle.kill.observed == bundle.clean.observed):
        labels.append("I-11")
    return labels


# ── baseline ──────────────────────────────────────────────────────────────────────
def _baseline_payload(axes, reason):
    parts = ["schema_version=1.0\n"]
    for a in CENSUS_AXES:
        parts.append(f"{a}={int(axes[a])}\n")
    parts.append(f"reason={reason}\n")
    return "".join(parts)


def _baseline_digest(axes, reason):
    return "sha256:" + _sha256_bytes(_baseline_payload(axes, reason).encode("utf-8"))


def _write_baseline(path, axes, reason, mode):
    body = [
        "# docs/hollow-gate-corpus-baseline.yaml — GENERATED by scripts/check-hollow-gate-corpus.sh",
        f"# mode={mode} (수기 편집 = content_digest 불일치 = exit 3 substrate-failure).",
        "# 재생성 경로 2종 ONLY: --init-baseline --reason TEXT (파일 부재 시에만) /",
        "#   --allow-baseline-shrink --reason TEXT (기존 파일 재기록, 사유 각인).",
        "# `--write-baseline` 형 자기 하향 재생성 경로 부재 (ADR-175 명시 금지).",
        '# content_digest 산식 = sha256("schema_version=1.0\\n" + "<axis>=<value>\\n"*7 + "reason=<reason>\\n").',
        'schema_version: "1.0"',
        "axes:",
    ]
    for a in CENSUS_AXES:
        body.append(f"  {a}: {int(axes[a])}")
    body.append("reason: " + json.dumps(reason, ensure_ascii=False))
    body.append('content_digest: "' + _baseline_digest(axes, reason) + '"')
    body.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body), encoding="utf-8", newline="\n")


def _load_baseline(path):
    data, err = _load_yaml(path, "baseline")
    if err:
        return None, err
    axes = data.get("axes")
    if not isinstance(axes, dict):
        return None, "baseline: axes mapping 부재"
    vals = {}
    for a in CENSUS_AXES:
        if a not in axes or not isinstance(axes[a], int):
            return None, f"baseline: 축 '{a}' 부재 또는 비정수"
        vals[a] = int(axes[a])
    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        return None, "baseline: reason 부재"
    expect = _baseline_digest(vals, reason)
    if data.get("content_digest") != expect:
        return None, (
            "baseline: content_digest 불일치 — 수기 편집 또는 산식 이탈 "
            "(재기록 경로 = --allow-baseline-shrink --reason TEXT)"
        )
    return {"axes": vals, "reason": reason}, None


# ── 오케스트레이션 ────────────────────────────────────────────────────────────────
def run(args):
    if yaml is None:
        _error(STAGE_DEP, "pyyaml 미설치 — corpus manifest/baseline parse 불가 = 판정불가 (fail-closed exit 1).")
        return EXIT_FAIL

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        _error(STAGE_SUBSTRATE, f"--repo-root '{args.repo_root}' 미존재/비-디렉터리 — 판정 기반 부재.")
        return EXIT_SUBSTRATE

    manifest_path = Path(args.manifest) if args.manifest else repo_root / "docs/hollow-gate-corpus-manifest.yaml"
    baseline_path = Path(args.baseline) if args.baseline else repo_root / "docs/hollow-gate-corpus-baseline.yaml"

    # ── manifest (substrate) ──────────────────────────────────────────────────
    manifest, err = _load_yaml(manifest_path, "manifest")
    if err:
        _error(STAGE_SUBSTRATE, f"{manifest_path}: {err} — 판정 기반 부재.")
        return EXIT_SUBSTRATE
    keyspace = set()
    _walk_keys(manifest, keyspace)
    hit = sorted(set(FORBIDDEN_MANIFEST_KEYS) & keyspace)
    if hit:
        _error(STAGE_SUBSTRATE, f"manifest 금지키 사용 {hit} — 판정 회피 키공간 (denylist 명명 3종).")
        return EXIT_SUBSTRATE
    merrs = _validate_manifest(manifest)
    if merrs:
        for m in merrs:
            _error(STAGE_SUBSTRATE, f"manifest: {m}")
        return EXIT_SUBSTRATE

    gates_by_id = {g["id"]: g for g in manifest["gates"]}
    samples = manifest["samples"]
    samples_by_id = {s["id"]: s for s in samples}

    # ⓸ bijection
    berrs, n_files = _check_bijection(repo_root, samples, gates_by_id)
    if berrs:
        for m in berrs:
            _error(STAGE_SUBSTRATE, f"bijection 파손: {m}")
        return EXIT_SUBSTRATE

    # ⓷ stamp drift
    serrs = _check_stamps(repo_root, samples, gates_by_id)
    if serrs:
        for m in serrs:
            _error(STAGE_SUBSTRATE, f"stamp drift: {m}")
        return EXIT_SUBSTRATE

    # ── build[] recipe 정합 (⓺ + I-1 정의역) ──────────────────────────────────
    recipes = {}   # uid -> recipe dict
    probe_ids = []
    for b in manifest["build"]:
        if not isinstance(b, dict):
            _error(STAGE_SUBSTRATE, "build[] 항목이 mapping 아님")
            return EXIT_SUBSTRATE
        uid = b.get("sample") or b.get("probe")
        if not uid:
            _error(STAGE_SUBSTRATE, "build[]: sample/probe 키 부재")
            return EXIT_SUBSTRATE
        for f in ("derived_from", "target", "anchor_from", "anchor_to"):
            if f not in b:
                _error(STAGE_SUBSTRATE, f"build[{uid}]: 필수 필드 '{f}' 부재")
                return EXIT_SUBSTRATE
        if b["derived_from"] not in samples_by_id:
            _error(STAGE_SUBSTRATE, f"build[{uid}]: derived_from '{b['derived_from']}' 이 samples[] 밖 (⓺).")
            return EXIT_SUBSTRATE
        if b.get("sample") and b["sample"] not in samples_by_id:
            _error(STAGE_SUBSTRATE, f"build[{uid}]: sample '{uid}' 이 samples[] 밖 (⓺).")
            return EXIT_SUBSTRATE
        src_sample = samples_by_id[b["derived_from"]]
        tgt = (repo_root / src_sample["path"] / b["target"]).resolve()
        try:
            tgt.relative_to((repo_root / src_sample["path"]).resolve())
        except ValueError:
            _error(STAGE_SUBSTRATE, f"build[{uid}]: recipe target '{b['target']}' 이 samples[] 밖 (⓺).")
            return EXIT_SUBSTRATE
        if not tgt.is_file():
            _error(STAGE_SUBSTRATE, f"build[{uid}]: recipe target '{b['target']}' 파일 부재 (⓺).")
            return EXIT_SUBSTRATE
        recipes[uid] = b
        if b.get("probe"):
            probe_ids.append(uid)

    # ── ⓺(확장) 커밋 build[].sample 파생 provenance ────────────────────────────
    #   I-1 은 probe 정의역 전용이라 커밋 표본에 도달하지 못한다(F-CR18-1) — 커밋 표본이
    #   선언된 파생물인지는 여기서만 검사된다. 위반 = substrate-failure(exit 3).
    perrs = _check_sample_provenance(repo_root, manifest["build"], samples_by_id)
    if perrs:
        for m in perrs:
            _error(STAGE_SUBSTRATE, f"provenance 파손: {m}")
        return EXIT_SUBSTRATE

    # ── classification (reconciler 전용 — 판정기 미투입) ──────────────────────
    ARM_EXPECT = {"L": "LIVE", "H": "HOLLOW"}
    declared = {}
    for c in manifest["classification"]:
        if not isinstance(c, dict):
            _error(STAGE_SUBSTRATE, "classification[] 항목이 mapping 아님")
            return EXIT_SUBSTRATE
        uid = c.get("sample") or c.get("probe")
        arm = c.get("declared_arm")
        exp = c.get("expected_verdict")
        if not uid or arm not in ARM_EXPECT or exp not in ("LIVE", "HOLLOW"):
            _error(STAGE_SUBSTRATE, f"classification[{uid}]: declared_arm/expected_verdict shape 파손")
            return EXIT_SUBSTRATE
        if ARM_EXPECT[arm] != exp:
            _error(
                STAGE_SUBSTRATE,
                f"classification[{uid}]: declared_arm '{arm}' ↔ expected_verdict '{exp}' 불일치 "
                f"(L↔LIVE / H↔HOLLOW 고정 — 재라벨링으로 통과하는 경로 차단).",
            )
            return EXIT_SUBSTRATE
        declared[uid] = {"arm": arm, "expected": exp, "kind": "probe" if c.get("probe") else "sample"}

    units = []   # (uid, kind, source_sample, recipe or None)
    for s in samples:
        units.append((s["id"], "sample", s, None))
    for pid in probe_ids:
        units.append((pid, "probe", samples_by_id[recipes[pid]["derived_from"]], recipes[pid]))
    for uid, _kind, _src, _rc in units:
        if uid not in declared:
            _error(STAGE_SUBSTRATE, f"classification: unit '{uid}' 미분류 (전 unit 분류 필요).")
            return EXIT_SUBSTRATE
    for uid in declared:
        if uid not in {u[0] for u in units}:
            _error(STAGE_SUBSTRATE, f"classification: 미지 unit '{uid}' (samples[]/build[] 밖).")
            return EXIT_SUBSTRATE

    # ── ⓵ 0-count substrate ───────────────────────────────────────────────────
    n_gates = len(manifest["gates"])
    n_armL = sum(1 for u, d in declared.items() if d["kind"] == "sample" and d["arm"] == "L")
    n_armH = sum(1 for u, d in declared.items() if d["kind"] == "sample" and d["arm"] == "H")
    n_probe = sum(1 for u, d in declared.items() if d["kind"] == "probe")
    zero = [k for k, v in (("N_gates", n_gates), ("N_armL", n_armL), ("N_armH", n_armH),
                           ("N_probe", n_probe)) if v == 0]
    if zero:
        _error(STAGE_SUBSTRATE, f"분모 0 축 {zero} — corpus 실체 부재 (⓵ substrate-failure).")
        return EXIT_SUBSTRATE

    # ── ⓶ baseline 존재·정합 (fail-fast; 기록은 census 계산 後) ────────────────
    baseline = None
    if baseline_path.is_file():
        if args.init_baseline:
            _error(
                STAGE_BASELINE,
                f"{baseline_path}: 이미 존재 — --init-baseline 은 부재 시에만 허용(하향 재생성 경로 아님). "
                f"재기록은 --allow-baseline-shrink --reason TEXT.",
            )
            return EXIT_SUBSTRATE
        baseline, berr = _load_baseline(baseline_path)
        if berr:
            _error(STAGE_SUBSTRATE, f"{baseline_path}: {berr} (⓶).")
            return EXIT_SUBSTRATE
    else:
        if not args.init_baseline:
            _error(
                STAGE_SUBSTRATE,
                f"{baseline_path}: baseline 부재 — day-1 각인은 --init-baseline --reason TEXT (⓶).",
            )
            return EXIT_SUBSTRATE
    if (args.init_baseline or args.allow_baseline_shrink) and not (args.reason or "").strip():
        _error(STAGE_BASELINE, "--init-baseline / --allow-baseline-shrink 은 --reason TEXT 동반 필수 (사유 각인).")
        return EXIT_SUBSTRATE
    if args.allow_baseline_shrink and not baseline_path.is_file():
        _error(STAGE_BASELINE, f"{baseline_path}: 부재 상태에서 --allow-baseline-shrink 불가 (--init-baseline 사용).")
        return EXIT_SUBSTRATE

    # ── 실행: materialize + 4 leg ─────────────────────────────────────────────
    violations = []
    exec_root = Path(tempfile.mkdtemp(prefix="hgc-exec-"))
    _emit(f"exec-root: {exec_root.name} (실행별 재배정 — IC-4)")
    results = {}
    try:
        for uid, kind, src_sample, recipe in units:
            gate = gates_by_id[src_sample["gate"]]
            entry = gate["entry"]
            integrity = []
            legs = {}
            entry_sha = None

            # I-1: 파생 지점 특정 (커밋 원본에서 anchor 매치 수 == 1)
            if recipe is not None:
                src_target = repo_root / src_sample["path"] / recipe["target"]
                _patched, n_match = _apply_recipe(src_target.read_bytes(), recipe)
                if n_match != 1:
                    integrity.append("I-1")
                    _error(
                        STAGE_INDETERMINATE,
                        f"unit={uid}: anchor 매치 {n_match} ≠ 1 — 표본 파생 지점 특정 실패 (I-1).",
                    )

            if not integrity:
                for role in LEG_ROLES:
                    unit_dir, fx_dir, sha, merr = _materialize(
                        exec_root, repo_root, src_sample, src_sample["fixtures"][role], entry, recipe
                    )
                    if merr:
                        integrity.append("I-3")
                        _error(STAGE_INDETERMINATE, f"unit={uid} leg={role}: materialize 실패 — {merr} (I-3).")
                        break
                    # ★ leg 별 즉시 정리 (F-CR18-9): unit_dir 을 누적하면 그 개수가 곧 실행
                    #   순번이 되어 자식이 fixture 를 열지 않고 leg 을 역산할 수 있다. 정상 종료·
                    #   break·return·예외 전 경로에서 반드시 정리되도록 try/finally 로 감싼다.
                    #   entry_sha·obs 는 정리 전에 확보되므로 이후 사용에 지장 없다.
                    try:
                        entry_sha = sha
                        # MUTATION-SENTINEL M5(호출부) / M7(형제 부재 conjunct — 함수 내부):
                        # IC-4 exec-tree blinding assert (manifest/stamp/baseline/probe 부재 ∧
                        # `.sample` 잔재 0 ∧ 형제 unit 0). 파손 = exit 3 (⓹).
                        # 두 sentinel 은 별 대조군을 갖는다 — 같은 함수라고 같은 mutant 가
                        # 죽이지 않는다(F-CR19-2 실행 반증).
                        bad = _blinding_violations(unit_dir, exec_root)
                        if bad:
                            _error(STAGE_SUBSTRATE, f"unit={uid} leg={role}: exec-tree blinding 파손 {bad} (⓹).")
                            return EXIT_SUBSTRATE

                        # I-2: 표본 syntax invalid
                        if entry.endswith(".py"):
                            try:
                                compile((unit_dir / entry).read_text(encoding="utf-8", errors="replace"),
                                        str(unit_dir / entry), "exec")
                            except SyntaxError as exc:
                                integrity.append("I-2")
                                _error(STAGE_INDETERMINATE, f"unit={uid} leg={role}: 표본 syntax invalid — {exc} (I-2).")
                                break

                        rc, out, errtxt, rerr = _run_leg(unit_dir, fx_dir, entry, gate["invoke_args"])
                        if rerr:
                            integrity.append("I-3")
                            _error(STAGE_INDETERMINATE, f"unit={uid} leg={role}: {rerr}")
                            break
                        obs, wrong = _observe(out, errtxt, gate)
                        # MUTATION-SENTINEL M3: exit_space 검사 (I-4 — rc 는 여기에만 쓴다).
                        if rc not in gate["exit_space"]:
                            integrity.append("I-4")
                            _error(
                                STAGE_INDETERMINATE,
                                f"unit={uid} leg={role}: rc={rc} ∉ 선언 exit_space {gate['exit_space']} (I-4).",
                            )
                        if wrong:
                            integrity.append("I-10")
                            for w in sorted(set(wrong)):
                                _error(STAGE_INDETERMINATE, f"unit={uid} leg={role}: {w} (I-10).")
                        legs[role] = obs
                        _emit(
                            f"obs-digest: unit={uid} leg={role} rc={rc} n={len(obs.observed)} "
                            f"fail={int(obs.fail)} term={int(obs.term)} "
                            f"stages={sorted(obs.fail_stages)} sha256={_observed_digest(obs)}"
                        )
                    finally:
                        shutil.rmtree(unit_dir, ignore_errors=True)

            if integrity or len(legs) != len(LEG_ROLES):
                verdict = "INDETERMINATE"
                labels = sorted(set(integrity)) or ["I-3"]
                delivered = False
            else:
                bundle = VerdictBundle(legs["kill"], legs["clean"], legs["empty"])
                verdict, delivered = _verdict(bundle, gate["fail_marker_stage_id"])
                labels = _post_verdict_labels(bundle, gate["fail_marker_stage_id"], verdict, delivered)
                if labels:
                    verdict = "INDETERMINATE"
                    for lb in labels:
                        _error(STAGE_INDETERMINATE, f"unit={uid}: {lb} 성립 — verdict INDETERMINATE 강등.")

            if entry_sha:
                _emit(f"resolved-target: unit={uid} entry={entry} sha256={entry_sha}")
            _emit(
                f"verdict: unit={uid} kind={kind} verdict={verdict} delivered={int(delivered)} "
                f"labels={','.join(labels) if labels else '-'}"
            )
            results[uid] = {
                "kind": kind, "verdict": verdict, "labels": labels, "legs": legs,
                "gate": gate, "src": src_sample["id"], "entry_sha": entry_sha,
            }

            # MUTATION-SENTINEL M6: xkill 축-disjoint 검사 — kill_target_stage 가 xkill 의
            # fail_stage 에도 있으면 그 stage 선언은 자동 적중(공허)이다. 제거 시 상수 footer
            # (SUMMARY 류) 선언이 무증상 통과한다.
            if "xkill" in legs:
                tgt = gate["fail_marker_stage_id"]
                if tgt in legs["xkill"].fail_stages:
                    violations.append("xkill-axis")
                    _error(
                        STAGE_XKILL,
                        f"unit={uid}: kill_target_stage '{tgt}' ∈ fail_stage(xkill)="
                        f"{sorted(legs['xkill'].fail_stages)} — 축-disjoint 파손(자동 적중 = 공허 선언).",
                    )
    finally:
        shutil.rmtree(exec_root, ignore_errors=True)

    # ── IC-1 / IC-2 / IC-5 / IC-6 (probe 계열) ────────────────────────────────
    # IC-1 측정 대상 = probe 의 파생 원점(derived_from)이 **arm-L 선언 표본**인가 (falsifiable).
    armL_sample_ids = {uid for uid, d in declared.items()
                       if d["kind"] == "sample" and d["arm"] == "L"}
    n_flip = 0
    for pid in probe_ids:
        pre_id = recipes[pid]["derived_from"]
        pre = results.get(pre_id)
        post = results.get(pid)
        if pre is None or post is None:
            violations.append("ic-missing")
            _error("IC-2", f"probe={pid}: PRE/POST 결과 부재 — flip assert 불가.")
            continue
        # IC-1: probe 의 파생 원점이 **arm-L 선언 표본**인가 (기대 verdict 만 반대).
        # ★ 측정 대상 = derived_from 의 선언 arm(L 필수). probe 의 커밋 좌표 동일성은 `units`
        #   구성상 참이므로 **측정 대상이 아니다** (F-CR18-10 — 이전 구현은 이 항진명제를
        #   `coords-match` 로 측정한 것처럼 emit 했다: post["src"] 와 pre["src"] 가 둘 다
        #   derived_from 에서 나온 같은 출처라 어떤 manifest 로도 False 가 될 수 없었다).
        pre_arm = declared[pre_id]["arm"]
        armL_ok = pre_id in armL_sample_ids
        _emit(
            f"ic1: probe={pid} derived_from={pre_id} derived_arm={pre_arm} "
            f"gate={post['gate']['id']} armL-anchored={int(armL_ok)}"
        )
        if not armL_ok:
            violations.append("ic1")
            _error(
                "IC-1",
                f"probe={pid}: derived_from '{pre_id}' 이 arm-L 선언 표본이 아님 "
                f"(선언 arm={pre_arm}) — probe 는 arm-L 표본에서 파생되고 기대 verdict 만 반대여야 한다.",
            )
        # IC-5: resolved target echo — 판정기가 연 artifact 해시가 실제로 다름.
        _emit(f"ic5: probe={pid} sha_armL={pre['entry_sha']} sha_probe={post['entry_sha']}")
        if pre["entry_sha"] == post["entry_sha"]:
            violations.append("ic5")
            _error("IC-5", f"probe={pid}: sha(S_L) == sha(P) — in-place 섭동 미반영(동일 artifact).")
        # IC-2: flip assert (PRE=LIVE → POST=HOLLOW).
        flip = pre["verdict"] == "LIVE" and post["verdict"] == "HOLLOW"
        _emit(f"ic2: probe={pid} PRE={pre['verdict']} POST={post['verdict']} flip={int(flip)}")
        if flip:
            n_flip += 1
        else:
            violations.append("ic2")
            _error("IC-2", f"probe={pid}: flip 미성립 (PRE={pre['verdict']} → POST={post['verdict']}, LIVE→HOLLOW 요구).")
        # IC-6: recipe ↔ kill-fixture **축** 짝짓기 (파일 짝짓기 아님).
        tgt = pre["gate"]["fail_marker_stage_id"]
        pre_k = pre["legs"].get("kill")
        post_k = post["legs"].get("kill")
        axis_ok = (pre_k is not None and post_k is not None
                   and tgt in pre_k.fail_stages and tgt not in post_k.fail_stages)
        _emit(
            f"ic6: probe={pid} axis={tgt} in_PRE_kill="
            f"{int(pre_k is not None and tgt in pre_k.fail_stages)} in_POST_kill="
            f"{int(post_k is not None and tgt in post_k.fail_stages)} paired={int(axis_ok)}"
        )
        if not axis_ok:
            violations.append("ic6")
            _error(
                "IC-6",
                f"probe={pid}: recipe 가 중화한 축 ≠ kill-fixture 위반 축 '{tgt}' "
                f"(arm-L kill 에 존재 ∧ probe kill 에서 소멸 이어야 함).",
            )

    # ── reconcile (declared ↔ observed) ───────────────────────────────────────
    for uid, d in sorted(declared.items()):
        actual = results[uid]["verdict"]
        if actual != d["expected"]:
            violations.append("verdict")
            _error(
                STAGE_VERDICT,
                f"unit={uid}: 선언 arm={d['arm']} expected={d['expected']} ≠ 관측 verdict={actual} "
                f"(labels={','.join(results[uid]['labels']) or '-'}).",
            )

    # ── census 7축 (개별 emit — 총합 emit 금지) ────────────────────────────────
    n_detected = sum(1 for r in results.values() if r["verdict"] == "HOLLOW")
    n_indeterminate = sum(1 for r in results.values() if r["verdict"] == "INDETERMINATE")
    census = {
        "N_gates": n_gates, "N_armL": n_armL, "N_armH": n_armH, "N_probe": n_probe,
        "N_detected": n_detected, "N_flip": n_flip, "N_indeterminate": n_indeterminate,
    }
    # MUTATION-SENTINEL M4: census 축별 개별 emit — 총합 1줄로 degrade 하면 어느 축이
    # 줄었는지 구별 불가(N 축소 은닉). 축별 1줄 고정 형식 `census: <axis>=<int>`.
    for a in CENSUS_AXES:
        _emit(f"census: {a}={census[a]}")

    # ── baseline 대조(축별) 또는 기록 ─────────────────────────────────────────
    if args.init_baseline:
        _write_baseline(baseline_path, census, args.reason.strip(), "init-baseline")
        _emit(f"baseline: init 각인 → {baseline_path} (reason 각인 + content_digest 결박)")
    elif args.allow_baseline_shrink:
        _write_baseline(baseline_path, census, args.reason.strip(), "allow-baseline-shrink")
        _emit(f"baseline: 재기록(사유 각인) → {baseline_path}")
    else:
        for a in LOWER_BOUND_AXES:
            base = baseline["axes"][a]
            cur = census[a]
            _emit(f"baseline-cmp: {a} current={cur} floor={base} ok={int(cur >= base)}")
            if cur < base:
                violations.append("baseline")
                _error(
                    STAGE_BASELINE,
                    f"축 '{a}' 하한 미달 — current={cur} < baseline={base} (분모 단조 하한, 축별 대조).",
                )
    if census["N_indeterminate"] >= 1:
        violations.append("indeterminate")
        _error(
            STAGE_BASELINE,
            f"N_indeterminate={census['N_indeterminate']} ≥ 1 (상한 축) — 판정불가 표본 존재, "
            f"HOLLOW 계상 금지 · fail-closed exit 1.",
        )

    if violations:
        _error(
            STAGE_SUMMARY,
            f"hollow-gate corpus FAIL — 위반 {len(violations)}건 {sorted(set(violations))} (exit 1). "
            f"천장: 등재 표본의 관측 기반 verdict 까지만 — corpus 밖 게이트 일반으로 외삽하지 않는다. "
            f"presence ≠ truth (검출 sufficiency=undecidable, ADR-175 정직 천장).",
        )
        return EXIT_FAIL

    _emit(
        f"✓ check-hollow-gate-corpus: units={len(results)} "
        f"(armL={n_armL} armH={n_armH} probe={n_probe}) 선언 arm 전건 일치 — "
        f"arm-L 전건 LIVE ∧ arm-H 전건 HOLLOW, INDETERMINATE=0, 축별 baseline 하한 충족. "
        f"천장: 등재 표본의 관측 기반 verdict 까지만 (corpus 밖 외삽 없음). presence ≠ truth."
    )
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_hollow_gate_corpus.py",
        description=(
            "hollow-gate corpus 판정 하네스 (커밋 2-arm corpus 실행 → LIVE/HOLLOW arm-invariant 분류). "
            "천장: 등재 표본의 관측 기반 verdict 까지만 — corpus 밖 게이트 일반으로 외삽하지 않는다. "
            "presence ≠ truth."
        ),
    )
    default_root = Path(__file__).resolve().parents[2]  # scripts/lib → scripts → repo-root
    parser.add_argument("--repo-root", default=str(default_root),
                        help="repo 루트 (기본 = __file__ parents[2]).")
    parser.add_argument("--manifest", default=None,
                        help="sidecar manifest (기본 = <repo>/docs/hollow-gate-corpus-manifest.yaml).")
    parser.add_argument("--baseline", default=None,
                        help="census baseline (기본 = <repo>/docs/hollow-gate-corpus-baseline.yaml).")
    parser.add_argument("--init-baseline", action="store_true",
                        help="baseline **부재 시에만** 최초 각인 (--reason 필수). 이미 있으면 거부.")
    parser.add_argument("--allow-baseline-shrink", action="store_true",
                        help="기존 baseline 재기록 (--reason 필수, 사유가 파일에 각인).")
    parser.add_argument("--reason", default="",
                        help="baseline 각인/재기록 사유 (content_digest 에 결박).")
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
