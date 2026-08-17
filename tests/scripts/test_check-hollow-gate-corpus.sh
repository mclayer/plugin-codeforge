#!/usr/bin/env bash
# tests/scripts/test_check-hollow-gate-corpus.sh
# hgsv-enroll
# CFP-2963 / ADR-175 — hollow-gate corpus 판정 하네스(scripts/check-hollow-gate-corpus.sh →
#   scripts/lib/check_hollow_gate_corpus.py) 의 discriminating self-test.
#
# ── positive-control: sanity mutant→RED (결함 앞 RED 를 상시 증명) ────────────────────
#   본 self-test 는 매 실행마다 판정 core 의 **실 파일 사본**에 결함을 주입(MUTATION-SENTINEL
#   M1~M8, M3 은 2 site 개별)하고, 무변형 baseline 과 **다른 exit** 이 나오는지 대조한다.
#   예외 = M7: 대상 불변식이 정상 corpus 에서 발화하지 않아 무변형 baseline 으로는 대조군이
#   성립하지 않으므로 **2단 mutant**(정리 무력화 baseline → 불변식 추가 제거)를 쓴다. 사유는
#   해당 블록 주석에 기재한다 — 예외를 조용히 두지 않는다.
#   예외 = M4·M8: 이 두 축은 **exit-flip 이 아니다**(양 팔 exit 불변). 그래서 exit 대조가 아니라
#   stdout 관측 문면의 소실로 kill 한다 — M4 = census 토큰, M8 = `baseline-cmp:` 축 이름 집합.
#   exit 축을 함께 실측해 '불변'을 관측으로 뒷받침하고(무관측 단정 금지), crash mutant 는 무효로
#   떨어뜨린다. 판정 기준 ③ 참조.
#   mutant 가 죽지 않으면(= baseline 과 같은 exit) 본 self-test 가 FAIL 한다. inline hand-copy
#   금지(ADR-082 §11.A tautology) — 실 core 파일 `cp` 대상만 sed 로 변형한다.
#   double-guard: (a) sed 가 실제로 치환했는지 sentinel grep 으로 확인 → 미치환 = NOT_RUN FAIL
#   (false PASS 금지) / (b) 변형본이 valid python(py_compile) 인지 확인.
#
# ── identity_bearing: true ─────────────────────────────────────────────────────────
#   internal-control identity probe = **known-answer 원문대조**. 하네스가 stdout 으로 emit 하는
#   `resolved-target: unit=s01 entry=gate.py sha256=<X>` 의 <X> 는, 커밋 파일
#   tests/fixtures/hollow-gate-corpus/s01/gate.py.sample 의 sha256 과 **문면 일치**해야 한다.
#   기대값은 하네스 출력이 아니라 sha256sum 으로 **독립 계산**한 known-answer 이며, 일치는
#   "판정기가 실제로 그 커밋 artifact 를 열어 실행했다"의 내부 대조 증거다(자기 출력 순환 인용 아님).
#
# ── ★NON-NEGOTIABLE 판정 기준 3건 (틀리면 정상 corpus 를 오판한다) ──────────────────
#   ① 「균일 = 하네스 사망」의 정의는 **"전 leg 동일"** 이지 *"전부 상이가 아님"* 이 아니다.
#      day-1 실측 8 leg 은 **4 distinct** 가 정상이다 — s01 kill / (s01 clean · s02 kill ·
#      s02 clean) / (s01 empty · s02 empty) / (s01 xkill · s02 xkill). `s02 kill ≡ s02 clean` 은
#      결함이 아니라 **arm-H 의 정의**(kill 에서도 GREEN)다. "전부 상이해야 한다"를 기준으로 삼으면
#      정상 corpus 를 사망으로 오판하므로 본 self-test 는 그 기준을 쓰지 않는다.
#   ② 판별자 = **마커 문면**이지 프로세스 rc 가 아니다. fail-marker = stderr `::error::[<STAGE>]`,
#      terminal-marker = stdout `✓ <gate>: …`. rc 는 I-4(선언 exit_space 이탈)에만 쓰인다.
#      본 self-test 는 verdict 를 rc 로 역추론하지 않고 하네스가 emit 한 `verdict:` 문면을 읽는다.
#   ③ mutation KILLED ⟺ **baseline(무변형)=기대 exit AND mutant=다른 exit**. 한쪽만 보면 무효.
#      exit-flip 축(`mutation_kill_exit`)도 **양 팔 stderr Traceback 0건**을 함께 요구한다 —
#      core 에 top-level catch-all 이 없어 미포착 예외의 rc=1 이 `EXIT_FAIL` 과 **동값**이라,
#      가드가 없으면 baseline=0 자리에서 mutant 가 그냥 죽기만 해도 rc flip 이 KILL 로 계상된다.
#      또한 mutant 는 **존재가 아니라 치환 실증**으로 확인한다(무변형 사본 오인 차단).
#      exit-flip 이 아닌 축(M4 = stdout census 토큰 소실)은 별도 함수로 kill 하되, 거기서도
#      **한쪽만 보지 않는다** — stdout 축 KILLED ⟺ baseline token ≥1 ∧ mutant token 0 ∧
#      **양 팔 exit 을 실측해 둘 다 기대치** ∧ **양 팔 stderr Traceback 0건**. 프로세스가 대상
#      분기에 **닿기 전 죽어도** 토큰은 똑같이 사라지므로, crash mutant 를 걸러내지 않으면
#      「해당 분기 중화」와 「조기 사망」이 구별되지 않는다(축 귀속 붕괴). 그러므로 crash mutant 는
#      KILL 로 계상하지 않고 **무효(FAIL)** 로 떨어뜨린다. 무효 판정은 baseline 팔에도 대칭
#      배치한다 — 대조군이 이미 crash 중이면 대조 자체가 성립하지 않는다.
#      (F-CR20-8 봉합: 종전 라벨은 "exit 은 양쪽 $expect 로 불변" 을 **관측 없이 단정**했고,
#       실측 결과 crash mutant(rc=1)·rc-flip mutant(rc=9)가 모두 그 문면으로 초록 보고됐다.)
#      ★ F-CR22-1 봉합 — 위 "crash 0" 은 **부재-assert**(「Traceback 이 없다」)이고, 흔적을 남기지
#        않는 종료(`sys.exit(N)`·`os._exit`·시그널)는 그 술어의 **정의역 밖**이다. 실측으로
#        `mutation_kill_exit`·`mutation_kill_stdout`·M7·M8 **4 site 전부** 조용한 종료를 KILLED 로
#        계상했다(전건 초록). 그래서 판정을 「crash 흔적 부재」가 아니라 **「rc 가 주장하는 종점에
#        닿았다는 양성 증거」**(§1a `announce_gap`)로 바꾼다 — 재는 것이 **가드 존재**가 아니라
#        **가드 충분**이다. crash 유형을 열거하지 않으므로 새 종료 형태에 정의역이 종속되지 않는다.
#
# ── 검사 대상 (READ-ONLY — 본 self-test 는 repo 실파일을 일절 수정하지 않는다) ────────
#   scripts/lib/check_hollow_gate_corpus.py        (core)
#   scripts/check-hollow-gate-corpus.sh            (thin wrapper — PINNED entry)
#   docs/hollow-gate-corpus-manifest.yaml          (좌표 SSOT)
#   docs/hollow-gate-corpus-baseline.yaml          (census baseline, content_digest 결박)
#   tests/fixtures/hollow-gate-corpus/{s01,s02}/** (2-arm 표본)
#   변형은 전부 mktemp -d 안 **shadow repo-root** 와 core 사본에서만 일어난다.
#
# ── 정직 천장 (ADR-175 / ADR-151 §결정7 / INV-5 상속) ───────────────────────────────
#   본 self-test 가 보장하는 것은 **등재 표본에 대한 관측 기반 판별력**까지다. corpus 밖 게이트
#   일반으로 외삽하지 않는다 — 미등재 게이트의 hollow 여부는 본 채널의 값공간 밖(미판정)이다.
#   presence ≠ truth 를 상속한다: 본 self-test 의 GREEN 은 "하네스가 주입된 결함 앞에서 RED 를
#   냈다"이지 "hollow 게이트가 더 이상 존재하지 않는다"가 아니다. 검출 sufficiency 는 undecidable.
#   (그래서 'universal' / '완전 봉인' / 'class 봉쇄' / '근절' 류 단정은 하지 않는다.)
#
# Exit code: 0 = 전 케이스 PASS ∧ PASS > 0 / 1 = 1건이라도 FAIL 또는 NOT_RUN (vacuous green 금지)

set -uo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# 0. Preamble — 경로 / 러너 / tally / cleanup
# ═══════════════════════════════════════════════════════════════════════════════
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CORE_PY="$REPO_ROOT/scripts/lib/check_hollow_gate_corpus.py"
WRAPPER="$REPO_ROOT/scripts/check-hollow-gate-corpus.sh"
MANIFEST="$REPO_ROOT/docs/hollow-gate-corpus-manifest.yaml"
BASELINE="$REPO_ROOT/docs/hollow-gate-corpus-baseline.yaml"
CORPUS_ROOT="$REPO_ROOT/tests/fixtures/hollow-gate-corpus"
GATE_SRC="$REPO_ROOT/scripts/lib/check_hard_gate_self_verification.py"

PASS=0
FAIL=0
SKIP=0

# ── 케이스 총량 pin 기대치 (F-CR26-5 / F-CR25-7 봉합) ──────────────────────────────
#   ★ 무엇이 열려 있었나 (실측 — 추론 아님). 종료 규칙이 `FAIL -eq 0 ∧ PASS -gt 0` 뿐이라
#     **케이스가 tally 에서 사라져도 회계되지 않았다**. loop 항목표에서 1줄을 지우면 총계만
#     1 줄고 rc=0 · RED 0 이다(F-CR26-5: T-ANN-d 삭제 · T-DEP-b 삭제 각각 SILENT).
#     그 두 항목은 P0 2건(F-CR25-1 · F-CR25-2) 봉합의 **음성 소비 site 자신**이라, 1줄 삭제로
#     **P0 의 거짓 초록이 문면 그대로 복원**된다. 봉합의 *효과*(born-RED)는 유효했는데 봉합의
#     *존재*가 관측면에 흔적을 남기지 않았다 — 「봉합된 세계」와 「봉합이 없던 세계」의 하네스
#     출력이 구별되지 않았다(양쪽 `PASS=64 FAIL=0` rc=0).
#   ⇒ 기대 케이스 총량을 리터럴로 결박한다. 케이스 증감은 **의도적 행위**이므로 이 값을 함께
#     갱신하는 마찰이 정상이고, 갱신 없는 증감은 RED 다.
#
#   ★ **공격면 열거는 「하한」이며 닫히지 않는다 — closed-set 주장을 하지 않는다.**
#     종전 문면 「공격면은 2곳이다」(9회차) → 「3곳이다」(10회차)는 **두 회차 연속 같은 방식으로
#     반증**됐다: 매번 열거를 **정본**으로 삼았고 매번 **한 칸 옆**에서 새 얼굴이 나왔다.
#     그래서 이번에는 4곳으로 고치지 않는다 — **열거를 하한으로 강등**한다. 아래는 *지금까지
#     실측된 것*이며, 더 있다는 쪽이 기본 가정이다.
#       (1) §14 총량 pin 케이스    — 케이스 소실/증가를 FAIL 로 발화
#       (2) §15 종료 가드 conjunct — pin 블록 **자신의 삭제**를 rc=1 로 발화
#       (3) **본 리터럴 자신**      — (1)(2) 의 **공유 앵커**. 값을 고치면 두 소비자가 함께
#                                    정합하게 이동하므로 **상호 보호가 원리적으로 무효**다.
#       (4) **tally 누산기 축 (중간량)** — (1)(2) 가 읽는 것은 스칼라 합 `$((PASS+FAIL+SKIP))`
#           **뿐**인데 라벨은 **케이스 집합의 구성(composition)**을 주장한다. 그 사이의 중간량을
#           건드리면 **총량이 보존**되어 상수 접촉 0 으로 조용하다. 실측된 세 얼굴:
#             · 카운터 **정의 본체** 1행 (`:135` `fail_case` 의 `FAIL=` → `PASS=`) — 전 실패가
#               PASS 로 계상되는데 총계는 그대로다.
#             · pin 직전 **tally 보정** 1행 삽입 — 케이스 소실을 상쇄해 은닉한다.
#             · 카운터 **호출 site 1토큰** relabel (`fail_case` → `pass_case`) — **117 site**
#               (`fail_case` 80 · `pass_case` 37, 앵커 grep 정본) 전건이 대상이고 relabel 가드는 0.
#           ★ 12회차에 **네 얼굴이 더 실측**됐다 — 열거가 하한이라는 판정이 한 회차에 4회 확증됐다.
#             열거를 늘리는 것이 처방이 아니므로 아래는 **관측 기록**이고, 처방은 §13.5 앵커 대상
#             교체 하나다:
#             · **XPOST — 스냅샷-후 주입**(5번째). 종료 가드가 읽던 tally 스냅샷 **이후**에 케이스를
#               주입하면 총계가 실제로 움직였는데도 요약행이 **과소보고**하고 rc=0 이었다.
#               대조군 XPIN(스냅샷 **이전** 주입)은 rc=1 ⇒ 판별축은 **스냅샷 상대 위치**.
#               § 종료 가드 라이브 tally 전환으로 **봉합**(창 축소 — 0 아님).
#             · **N5 — loop 항목 파라미터 1문자**(6번째). `ann_case` 표의 `c:NONEMPTY:2` → `…:0`
#               은 leg c 를 leg b 의 **중복으로 붕괴**시켜 rc-이탈 축을 통째로 없앤다. 케이스 수
#               보존 · 상수 무접촉 · **호출 site census 불변** ⇒ R1 보다 조용하다.
#               §13.5 `loopdecl` 성분이 **도달**한다(12회차 실측).
#             · **N4 — assert 술어 리터럴 본문 교체**(7번째, 부분). 침묵·census 불변은 실측 확인.
#               **커버리지 손실 leg 은 `[hypothesis]`** — 두 리터럴이 포함관계가 아니라 「약화」
#               판정에 core 발화 조건 실측이 필요한데 아직 하지 않았다. §13.5 **미도달**.
#             · **XINL — census 보상형**(8번째, 12회차 실측). 실결함(D1)을 주입한 뒤 그 실패
#               site 를 **인라인 전개**해 `fail_case` 호출을 1 줄이고, **도달 불가 블록**
#               (`if false; then fail_case …; fi`)에 1 줄을 넣어 census 를 되돌린다. rc=0 ·
#               tally 불변 · **§13.5 서명 3 성분 전건 불변** ⇒ **총량 앵커와 구성 앵커를 동시에
#               통과**한다. 기전 = **정적 계수는 「존재」를 세고 「도달 가능성」을 보지 않는다**.
#               ★ 이 얼굴은 §13.5 를 신설한 **그 회차에 그 신설물을 상대로** 나왔다 — 앵커를
#               한 층 안으로 옮기면 공격도 한 층 안으로 따라온다는 것의 실물이며, **열거 확장이
#               처방이 아니라는 판정(T6)을 다시 지지**한다. §13.5 **미도달**.
#     (1)(2) 만 놓고 보면 서로의 삭제를 덮는 것이 맞다(X3·X4 실측). (3) 을 넣으면 그 상호 보호가
#     깨지고, (4) 를 넣으면 **상수를 건드리지 않고도** 깨진다.
#   ★ 정직 천장 (전건 실측 — 추론 0):
#       · **본 pin 이 재는 것은 tally 스칼라 합 하나뿐**이다. 그래서 성질이 둘로 갈린다:
#         - **총량이 움직이는** 변경 → 상수의 명시적 diff 를 강제한다(미갱신이면 RED).
#           원 회귀 class(우발적 케이스 소실)가 여기 속한다 — 삭제 M-A rc=1 · 증가 U1 rc=1.
#         - **총량이 보존되는** 변경 → **상수 접촉 0 으로 통과**한다. 위 (4) 세 얼굴이 전부
#           여기 속하며, pin 은 구성 변화에 **원리적으로 눈이 없다**.
#       · **silencing 1-편집으로 거짓 초록이 성립한다** — 두 계열 모두 실측됐다:
#         상수 갱신형(M-B: 케이스 삭제 + `66→65`) rc=0 · ✗0 · 경고 0줄 /
#         상수 무접촉형((4) 계열) rc=0 이고 **요약행이 baseline 과 문면 동일**하다.
#         ★ **후자가 더 조용하다** — 전자는 `PASS=65` 로 수라도 달라 리뷰어가 볼 기회가 있지만
#         후자는 `PASS=66 FAIL=0 SKIP=0` 으로 판정면이 정본과 구별되지 않는다.
#       · ⇒ 본 pin 의 잔여 가치는 **「총량이 움직이는 변경」에 한정된 리뷰 가시성**이다.
#         무력화 불가능성이 아니며, 총량 보존형에는 그 가시성조차 없다.
#   ★ **기계 판정 종결 = 「미탐색(실행 가능)」 — 종전 「구조적 불가」 판정을 철회한다.**
#     종전 문면 「어떤 in-repo 앵커든 같은 커밋에서 1행 수정 가능하므로 기계 판정 불가 **확정**」은
#     **거짓**이다. 같은 repo 에 반례가 이미 돌고 있다 —
#       `scripts/lib/check_adr_amendment_threshold.py`
#         `:315 _threshold_n_at()`   — `git show <merge-base>:<path>` 로 **merge-base 리비전의**
#                                      상수 리터럴을 읽는다(작업트리 값이 아니다).
#         `:453 b1_monotone_seal()`  — merge-base baseline 대비 **단조 비증가를 강제**한다.
#       `.github/workflows/adr-amendment-threshold.yml` 로 **CI 배선**돼 있다.
#     PR 저자는 자기 커밋으로 merge-base 를 바꿀 수 없으므로 「함께 수정」이 무력화된다.
#     ⇒ 올바른 닫는 조건은 하네스 **「밖」**이 아니라 **「이전 리비전」** — **merge-base 대조 앵커**다.
#     ★★ **종전 미채택 사유는 거짓이었다 — 철회하고 12회차에 착수했다(§13.5).**
#       종전 문면: *「merge-base 대조가 보는 것은 **상수의 변화**뿐이라 (4) 총량 보존형(상수 접촉 0)
#       에는 **원리적으로 미도달**이다」*. 이것은 **실행 측정으로 반증**됐다 — merge-base 는 **축**
#       (「지금 ↔ 이전」)이고 *그 축 위에서 무엇을 앵커할지는 자유 선택*인데, 종전 판단은 **한
#       인스턴스(스칼라 상수)의 성질을 축 전체의 성질로 일반화**했다. 앵커 대상을 **구성 서명**
#       (호출 site census · 헬퍼 본체 해시 · loop 항목 선언면 해시)으로 두면 총량 보존형에
#       **도달한다** — 단 「전건 도달」이 아니고 관측면이 갈린다: **rc=1 = 5종**(R1 · U2 · U2B ·
#       XPOST · N5) / **stdout 문면만 = 1종**(D2 — 본 앵커의 RED 를 세는 카운터가 그 편집의
#       표적이라 rc=0) / **미도달 = 2종**(N4 assert 리터럴 · XINL census 보상). 실결함 D1 은
#       통과한다(거짓 양성 0). 실측 = Story §8.14.2/.3 (14-run 배터리).
#       ★ 이 오류는 바로 위 라벨 규율 ⓐ(**반증 시도 후에만 「불가」를 부여한다**)를 **규율 신설
#       직후 스스로 위반**한 것이다 — 반증을 시도하지 않은 채 「원리적 미도달」을 적었다.
#       ⇒ 규율 ⓓ 추가: **전칭을 세우기 전에 「내가 고정한 것이 축인가, 축 위의 한 대상인가」를
#       묻는다.** 축 위의 대상이 자유 선택이면 그 전칭은 성립하지 않는다.
#     Story §8.11.8 #12 = **「닫힘(도달범위 한정) — 12회차 착수」**(종전 「미탐색」·「무효(구조적
#       불가)」 표시 전건 철회). 도달범위 한정 = N4(assert 리터럴 본문) 미도달.
HGC_EXPECTED_CASE_TOTAL=68   # = 실 케이스 65 + §13.5 구성 앵커 2 + 본 pin 케이스 자신 1

# ── 구성 서명 선언 (§13.5 구성 앵커의 in-file 기준값) ───────────────────────────────
#   ★ 이것은 **새 공유 앵커**다 — §0 (3) 축과 같은 성질을 갖는다(저자가 실측과 함께 갱신하면
#     정합 이동한다). 종전 상수와 다른 점은 **baseline 이 저자가 쓸 수 없는 리비전**(merge-base)
#     이라 그 이동이 **고지**된다는 것 하나뿐이다. 「봉인」이 아니다 — §13.5 정직 천장 ⓐ 참조.
#   ★ 갱신 절차: 실패 문면이 실측 서명을 그대로 출력하므로 그 값을 여기에 옮긴다.
HGC_DECLARED_COMPOSITION="census=83/40/1 helper=9f1950b3fd0e loopdecl=d3b1cf3a6631"

note() { echo "::notice::$*" >&2; }
log()  { echo "$*" >&2; }
pass_case() { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail_case() { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
skip_case() { echo "  ⊘ SKIP: $1"; SKIP=$((SKIP+1)); }
# ★ `skip_case` 는 **호출 site 0 건(휴면)** 인데 SKIP 은 총량 tally 에 계상된다 (F-CR28-4).
#   **존치**를 택한다 — 사유: ⓐ SKIP 은 요약행·tally 가 이미 1급으로 다루는 결과 범주라 헬퍼만
#   지우면 표현이 불완전해지고, ⓑ 무엇보다 이것은 §0 (4) **relabel 표면의 한 원소**일 뿐이라
#   삭제해도 **117 site 중 1 종류의 목적지가 줄 뿐 표면은 그대로**다. 「한 얼굴을 지워 닫았다」는
#   것이 정확히 본 Story 가 두 회차 연속 반증당한 열거-확장 처방이므로 되풀이하지 않는다.
#   ★ 다만 휴면이 **비용 0 은 아니다** — `fail_case` → `skip_case` relabel 은 총량을 보존하면서
#   `FAIL` 도 0 으로 유지하므로 종료 가드 conjunct 를 **둘 다** 통과하고, 출력이 `⊘ SKIP` 이라
#   `✓ PASS` 위장보다 오히려 자연스러워 보인다. §0 (4) 하한 열거에 포함해 읽어야 한다.

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python3/python 부재 — 하네스 실행 불가 (NOT_RUN, false PASS 금지)"
  exit 1
fi

TEST_TMP="$(mktemp -d)"
cleanup() { rm -rf "$TEST_TMP" 2>/dev/null; }
trap cleanup EXIT

# ── NOT_RUN 가드: 검사 대상 부재 = 무엇도 검증하지 못함 → 즉시 exit 1 (false PASS 금지) ──
missing=""
for f in "$CORE_PY" "$WRAPPER" "$MANIFEST" "$BASELINE" "$GATE_SRC"; do
  [ -f "$f" ] || missing="$missing $f"
done
[ -d "$CORPUS_ROOT/s01" ] || missing="$missing $CORPUS_ROOT/s01"
[ -d "$CORPUS_ROOT/s02" ] || missing="$missing $CORPUS_ROOT/s02"
if [ -n "$missing" ]; then
  echo "✗ FAIL: NOT_RUN — 검사 대상 부재:$missing"
  echo "        (대상 미착륙 상태에서 초록을 내지 않는다 — false PASS 금지)"
  exit 1
fi
if ! "$PY" -c "import yaml" >/dev/null 2>&1; then
  echo "✗ FAIL: NOT_RUN — pyyaml 부재. 하네스 판정 자체가 불가하므로 초록을 내지 않는다."
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 실행 helper — REAL exit code / REAL stdout·stderr 캡처
# ═══════════════════════════════════════════════════════════════════════════════
CORE_RC=0
CORE_OUT=""
CORE_ERR=""
RUN_SEQ=0

# run_core <py_path> <repo_root> [args...] — CORE_RC / CORE_OUT / CORE_ERR 설정.
run_core() {
  local py="$1" root="$2"; shift 2
  RUN_SEQ=$((RUN_SEQ+1))
  CORE_OUT="$TEST_TMP/run${RUN_SEQ}.out"
  CORE_ERR="$TEST_TMP/run${RUN_SEQ}.err"
  "$PY" "$py" --repo-root "$root" "$@" >"$CORE_OUT" 2>"$CORE_ERR"
  CORE_RC=$?
}

# run_wrapper <repo_root> [args...] — PINNED entry(thin bash wrapper) 경유.
run_wrapper() {
  local root="$1"; shift
  RUN_SEQ=$((RUN_SEQ+1))
  CORE_OUT="$TEST_TMP/run${RUN_SEQ}.out"
  CORE_ERR="$TEST_TMP/run${RUN_SEQ}.err"
  bash "$WRAPPER" --repo-root "$root" "$@" >"$CORE_OUT" 2>"$CORE_ERR"
  CORE_RC=$?
}

# verdict_of <unit> — 하네스가 emit 한 `verdict:` 문면에서 verdict 만 추출 (rc 역추론 금지).
verdict_of() {
  sed -n "s/^verdict: unit=$1 .*verdict=\([A-Z]*\) .*/\1/p" "$CORE_OUT" | head -1
}

# census_of <axis> — stdout `census: <axis>=<int>` 문면에서 값 추출.
census_of() {
  sed -n "s/^census: $1=\([0-9]*\)$/\1/p" "$CORE_OUT" | head -1
}

# ═══════════════════════════════════════════════════════════════════════════════
# 1a. 종점 announce 실측 (F-CR22-1 봉합) — "가드 존재" 가 아니라 "가드 충분" 을 잰다
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 무엇이 틀렸었나 (정직 기재). 종전 crash 가드의 판별자는 stderr `Traceback` **단일 문자열**
#   이었다. 그것은 **부재-assert**(「crash 흔적이 없다」)라서, 흔적을 남기지 않는 종료
#   (`sys.exit(N)` · `os._exit` · 시그널)는 **술어의 정의역 밖**이다. 문자열을 더 열거하는
#   봉합은 같은 기전(정의역 열거)의 반복이므로 쓰지 않는다.
#
# ★ 교체한 술어 (양성-assert). core 의 선언 exit_space 는 {0,1,3} 이고
#   (`check_hollow_gate_corpus.py` EXIT_PASS/EXIT_FAIL/EXIT_SUBSTRATE · 2 = argparse usage 전용),
#   **각 값은 그 rc 를 반환하기 직전에 자기 도달을 스스로 발화한다**. 그래서 rc 마다
#   「그 rc 가 주장하는 종점에 실제로 닿았다는 양성 증거」를 요구한다 — 전 정의역 total:
#   **종점 전수 분류 실측** (core 를 직접 훑어 `return EXIT_*` 전건과 그 직전 `_error` 를 대조):
#     rc=0 → stdout `✓ check-hollow-gate-corpus:`      (`return EXIT_PASS` **1 site** `:1250` — 최종 _emit 직후)
#     rc=1 → stderr `::error::[SUMMARY]` | `[DEP]`     (`return EXIT_FAIL` **2 site** — 아래 F-CR23-2)
#     rc=3 → stderr `::error::[SUBSTRATE]`|`[BASELINE]`(`return EXIT_SUBSTRATE` **26 site** 전건 직전 _error)
#     그 외 → 선언 exit_space 이탈 자체가 위반
#   crash 유형을 열거하지 않는데도 ⓐ`sys.exit(2)` ⓑ`sys.exit(0)` ⓒ예외 ⓓ`os._exit` 가 **함께**
#   걸리는 이유가 이것이다: 조용히 죽은 프로세스는 종점 문면을 **낼 수 없다**.
#
# ★ F-CR23-2 정정 — rc=1 「유일 실패 종점」 전제는 **거짓이었다**. 종전 주석은 *"EXIT_FAIL 은
#   violations 집계 후 SUMMARY 발화 직후에**만** 반환된다"* 고 적었으나, 실측은 `return EXIT_FAIL`
#   이 **2 site** 임을 보인다:
#     `:1242` ← 직전 `_error(STAGE_SUMMARY, …)`  (집계 종점)
#     `:835`  ← 직전 `_error(STAGE_DEP, …)`      (pyyaml 부재 = 판정불가 fail-closed)
#   종전 술어는 후자를 「조용한 종료」로 **오진**했다(재현: yaml import 를 강제 실패시키면
#   rc=1 · `::error::[DEP]` · SUMMARY 0건인데 위반으로 발화). 오늘 오판이 나지 않은 이유는 술어의
#   건전성이 아니라 **하네스 밖 전제**(`:124` pyyaml preflight 가 DEP 경로를 도달 불가로 만듦)였고,
#   주석은 그 전제 대신 **거짓 명제**를 적었다. ⇒ 전제에 기대는 대신 술어를 **실 구조에 맞춘다** —
#   rc=1 의 종점 집합을 {SUMMARY, DEP} 로 정정한다(이로써 이 leg 은 preflight 유무와 무관하게
#   total 이다). 느슨해지지 않는다: 두 문면 다 core 가 **loud 하게** 낸 종점 마커이고, 조용한
#   종료는 여전히 어느 쪽도 내지 못한다.
#
# ★ 정직 천장. 이 술어가 닫는 것은 「종점 announce **전** 사망」이다. rc 가 주장하는 종점
#   문면을 실제로 낸 뒤의 종료는 정의상 그 종점에 닿은 것이라 위반이 아니다.
#   **다중 종점 leg(rc=1 = 2개 · rc=3 = 26개)은 「어떤 loud 실패 종점에 닿음」까지만** 말하고
#   「의도한 그 종점」은 말하지 않는다 — 축 귀속은 각 site 의 별도 문면 conjunct(M7 형제 수·leg
#   순번, M8 축 집합, M4 census 토큰)가 맡는다.
#   ★ rc=3 leg 의 잔여 느슨함(실측·미봉합): `[BASELINE]` 은 **비종점**에서도 발화한다
#     (`:1223` `:1229` — violations 적재 후 SUMMARY 로 흘러 rc=1). 따라서 「`[BASELINE]` 존재」가
#     「rc=3 종점 도달」을 엄밀히 함의하지는 않는다. 실해가 성립하려면 mutant 가 그 비종점을 지난
#     뒤 **정확히 rc=3 으로 조용히** 죽어야 해서 오늘 도달 경로는 없다 — **닫지 않고 기재한다**.
ANN_PASS="✓ check-hollow-gate-corpus:"
ANN_FAIL='::error::\[SUMMARY\]'
ANN_DEP='::error::[DEP]'
ANN_SUB='::error::\[(SUBSTRATE|BASELINE)\]'

# ★ `[DEP]` 를 **무효 관측**으로 분류한다 (F-CR24-4). 직전 회차는 rc=1 의 종점 집합을
#   {SUMMARY, DEP} 로 넓혀 두 문면 다 통과시켰다. 구조적 사실(둘 다 loud 종점)로는 옳았으나,
#   **소비처가 gap 으로 판정하는 축**은 「loud 하게 죽었나」가 아니라 **「끝까지 돌아 관측을
#   그 분기에 귀속할 수 있나」**다. `[DEP]` 문면은 *"판정불가"* — **아무것도 평가하지 않은 종점**
#   이라 그 실행에서 나온 rc·토큰 차이는 어느 분기에도 귀속되지 않는다. `Traceback` 가드가
#   배제하는 것과 **같은 무효 관측 class** 인데 종전에는 `gap=""` 로 통과했다.
#   실측(본 회차): `yaml` import 를 강제 실패시키면 rc=1 · `::error::[DEP]` 1건 · SUMMARY 0 ·
#   **Traceback 0** · stdout 공백 — 어떤 가드도 잡지 못하는 조합이었다.
#   ★ 이것은 F-CR23-2 정정의 **철회가 아니다**. 그 정정이 고친 것은 「rc=1 ⟹ SUMMARY 유일」이라는
#     **거짓 명제**였고, 여기서도 DEP 는 여전히 **명시 열거**된다 — 다만 「유효 종점」이 아니라
#     「무효 관측 종점」으로 분류될 뿐이다. rc=1 에 대한 술어는 여전히 total 이다:
#     SUMMARY = 유효 / DEP = 무효(사유 명시) / 둘 다 부재 = 조용한 종료.
ANN_MSG_DEP="exit=1 이고 종점 마커가 ::error::[DEP] — 의존성 부재로 **판정불가**하게 끝난 실행이다. loud 종점이긴 하나 core 가 아무 분기도 평가하지 않았으므로, 이 실행의 rc·stdout 차이는 어떤 분기 중화에도 귀속되지 않는다(Traceback 과 동급의 무효 관측)"

# ★ 사유 문면의 rc-분기 선두 — **`announce_gap` 이 산출했음의 지문**. T-WIRE 가 (3b) conjunct 로
#   이 값을 요구하므로, 배선이 비공백 상수로 치환되면 그 지문이 없어 즉시 RED 다(F-CR24-1 봉합).
#   ★ 반드시 `announce_gap` 의 echo 와 **같은 변수**를 쓴다 — 별도 리터럴로 두면 한쪽만 바뀔 때
#     대조군이 조용히 무력화된다(본 Story 가 반복 관측한 형).
ANN_MSG_RC0="exit=0 인데 stdout 종점 문면"
ANN_MSG_RC1="exit=1 인데 stderr 에 loud 실패 마커"

# announce_gap <rc> <outfile> <errfile> — 위반 사유 1줄을 stdout 으로 반환(정상이면 빈 문자열).
announce_gap() {
  local rc="$1" out="$2" err="$3"
  case "$rc" in
    0)
      grep -qF "$ANN_PASS" "$out" && { echo ""; return 0; }
      echo "$ANN_MSG_RC0 '$ANN_PASS' 부재 — EXIT_PASS 는 최종 emit 직후에만 반환되므로, 이 조합은 그 종점에 닿기 전 **조용한 종료**(sys.exit(0)/os._exit 등)를 뜻한다" ;;
    1)
      grep -qF "$ANN_DEP" "$err" && { echo "$ANN_MSG_DEP"; return 0; }
      grep -qE "$ANN_FAIL" "$err" && { echo ""; return 0; }
      echo "$ANN_MSG_RC1(::error::[SUMMARY]|[DEP]) 부재 — EXIT_FAIL 은 그 2 종점(집계 후 SUMMARY · 의존성 부재 DEP) 직후에만 반환되므로, 이 조합은 어느 종점에도 닿기 전 **조용한 종료**를 뜻한다(rc=1 은 미포착 예외 기본값과도 동값)" ;;
    3)
      grep -qE "$ANN_SUB" "$err" && { echo ""; return 0; }
      echo "exit=3 인데 stderr 에 loud 실패 마커(::error::[SUBSTRATE]|[BASELINE]) 부재 — EXIT_SUBSTRATE 는 전 경로에서 _error 발화 직후 반환되므로, 이 조합은 그 종점에 닿기 전 **조용한 종료**를 뜻한다" ;;
    *)
      echo "exit=$rc 가 core 선언 exit_space {0,1,3} 밖 (2 = argparse usage 전용) — 판정 core 가 선언한 종점 중 어디에도 닿지 않았다" ;;
  esac
  return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# 2. shadow repo-root 빌더 — repo 실파일 무오염 (변형은 전부 사본에서만)
# ═══════════════════════════════════════════════════════════════════════════════
# new_shadow [extra] — extra: none(기본) / s03(축 어긋난 신규 표본) / s04(오염 kill fixture)
#   corpus 하위 전 파일이 정확히 1개 samples[] 를 참조해야 하므로(bijection), shadow 에는 그
#   시나리오가 manifest 로 참조할 표본 디렉터리만 담는다.
new_shadow() {
  local extra="${1:-none}" d
  d="$(mktemp -d "$TEST_TMP/sh.XXXXXX")"
  mkdir -p "$d/docs" "$d/scripts/lib" "$d/tests/fixtures/hollow-gate-corpus"
  cp "$BASELINE" "$d/docs/hollow-gate-corpus-baseline.yaml"
  cp "$GATE_SRC" "$d/scripts/lib/"
  cp -r "$CORPUS_ROOT/s01" "$CORPUS_ROOT/s02" "$d/tests/fixtures/hollow-gate-corpus/"
  if [ "$extra" = "s03" ]; then
    cp -r "$CORPUS_ROOT/s01" "$d/tests/fixtures/hollow-gate-corpus/s03"
  fi
  if [ "$extra" = "s04" ]; then
    cp -r "$CORPUS_ROOT/s01" "$d/tests/fixtures/hollow-gate-corpus/s04"
    # 오염 = 목표 축(AC-1, kill 의 test_subject_good) + 타 축(AC-8, xkill 의 concept doc) 동시 발화.
    cp "$CORPUS_ROOT/s01/xkill/docs/domain-knowledge/concept/hard-gate-self-verification.md.sample" \
       "$d/tests/fixtures/hollow-gate-corpus/s04/kill/docs/domain-knowledge/concept/hard-gate-self-verification.md.sample"
  fi
  echo "$d"
}

# ── manifest emitter — 시나리오별 knob 은 MF_* 환경변수로 주입 (reset_mf 로 초기화) ──
MF_STAGE=""; MF_EXIT_SPACE=""; MF_EXTRA=""; MF_FLIP=""; MF_PROBE=""
MF_SAMPLES=""; MF_RECIPE_TARGET=""; MF_FORBIDDEN=""
reset_mf() {
  MF_STAGE="AC-1"; MF_EXIT_SPACE="[0, 1]"; MF_EXTRA="none"; MF_FLIP="0"; MF_PROBE="1"
  MF_SAMPLES="normal"; MF_RECIPE_TARGET="gate.py.sample"; MF_FORBIDDEN="0"
}
reset_mf

emit_manifest() {
  local out="$1"
  cat > "$out" <<YAML
schema_version: "1.0"
gates:
  - id: check-hard-gate-self-verification
    source_path: scripts/lib/check_hard_gate_self_verification.py
    entry: gate.py
    invoke_args: ["--repo-root", "{fixture}"]
    fail_marker_stream: stderr
    terminal_marker_stream: stdout
    fail_marker_stage_id: "$MF_STAGE"
    terminal_marker_prefix: "✓ check-hard-gate-self-verification:"
    exit_space: $MF_EXIT_SPACE
YAML
  if [ "$MF_SAMPLES" = "empty" ]; then
    printf 'samples: []\n' >> "$out"
  else
    cat >> "$out" <<'YAML'
samples:
  - id: s01
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s01
    fixtures: { kill: kill, clean: clean, empty: empty, xkill: xkill }
  - id: s02
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s02
    fixtures: { kill: kill, clean: clean, empty: empty, xkill: xkill }
YAML
    if [ "$MF_EXTRA" = "s03" ]; then
      # ★ 축 어긋남을 fixtures 매핑으로 만든다 — kill 자리에 xkill(AC-8 위반) 을 앉히면
      #   관측 stage 는 {AC-8, SUMMARY} 인데 선언 kill_target_stage 는 AC-1 이라 짝이 어긋난다.
      cat >> "$out" <<'YAML'
  - id: s03
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s03
    fixtures: { kill: xkill, clean: clean, empty: empty, xkill: kill }
YAML
    fi
    if [ "$MF_EXTRA" = "s04" ]; then
      cat >> "$out" <<'YAML'
  - id: s04
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s04
    fixtures: { kill: kill, clean: clean, empty: empty, xkill: xkill }
YAML
    fi
  fi
  cat >> "$out" <<YAML
build:
  - sample: s02
    derived_from: s01
    target: $MF_RECIPE_TARGET
    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"
    anchor_to: "    if False:  # neutralized M1 positive-control-presence"
YAML
  if [ "$MF_PROBE" = "1" ]; then
    cat >> "$out" <<'YAML'
  - probe: p01
    derived_from: s01
    target: gate.py.sample
    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"
    anchor_to: "    if False:  # neutralized M1 positive-control-presence"
YAML
  fi
  printf 'classification:\n' >> "$out"
  if [ "$MF_SAMPLES" != "empty" ]; then
    if [ "$MF_FLIP" = "1" ]; then
      printf '  - sample: s01\n    declared_arm: H\n    expected_verdict: HOLLOW\n' >> "$out"
      printf '  - sample: s02\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
    else
      printf '  - sample: s01\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
      printf '  - sample: s02\n    declared_arm: H\n    expected_verdict: HOLLOW\n' >> "$out"
    fi
    [ "$MF_EXTRA" = "s03" ] && printf '  - sample: s03\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
    [ "$MF_EXTRA" = "s04" ] && printf '  - sample: s04\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
  fi
  if [ "$MF_PROBE" = "1" ]; then
    if [ "$MF_FLIP" = "1" ]; then
      printf '  - probe: p01\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
    else
      printf '  - probe: p01\n    declared_arm: H\n    expected_verdict: HOLLOW\n' >> "$out"
    fi
  fi
  if [ "$MF_FORBIDDEN" = "1" ]; then
    printf '\nwaiver: "판정 회피 키공간 — denylist 명명 3종 중 1"\n' >> "$out"
  fi
  return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. mutation helper — 실 core 파일 사본만 변형 (double-guard)
# ═══════════════════════════════════════════════════════════════════════════════
# mutate_core <label> <sed_expr> <sentinel> — 성공 시 변형본 경로 echo, 실패 시 빈 문자열 + rc 1.
#   파일명은 순번으로만 만든다 (label 에 공백·수식기호가 들어가므로 경로에 쓰지 않는다).
MUT_SEQ=0
MUT_PATH=""
mutate_core() {
  local label="$1" expr="$2" sentinel="$3"
  MUT_SEQ=$((MUT_SEQ+1))
  local mut="$TEST_TMP/mut_${MUT_SEQ}.py"
  # ★ 사전 부재 가드 (F-CR24-2) — **presence-assert 봉합**. 아래 사후 존재 검사만으로는
  #   「sed 가 마커를 도입했다」가 아니라 「마커가 있다」까지만 증명된다. sentinel 이 원본에
  #   **이미 있으면** 치환 0건이어도 통과해 **무변형 core 가 mutant 로 반환**된다(실증: sentinel
  #   `"def run"` · 치환 0건 → 두 가드 통과 · `cmp` 원본↔반환본 **바이트 동일**).
  #   `사전 부재 ∧ 사후 존재` 두 관측이 함께 「이 sed 실행이 이 마커를 만들었다」를 함의한다.
  #   ★ 이 가드가 `WIRE_SILENT` 전제도 함께 처리한다 — `CORE_PY` 가 조용한 종료 사본으로
  #     재지정된 구간에서 그 사본이 담은 마커(`WIRE-silent-exit`)를 sentinel 로 넘기면 종전에는
  #     무변형 사본이 통과했으나 이제 NOT_RUN 으로 떨어진다. 안전 근거가 **sentinel 명명 규율
  #     하나**였던 것을 기계 검사로 옮긴다.
  #   ★ 정직 천장: 이 조합도 「sed 가 **의도한 줄**을 쳤다」는 증명하지 않는다. 다른 줄을 치면서
  #     마커를 도입해도 통과한다 — 축 귀속은 각 케이스의 별도 관측(rc/토큰/축 집합)이 맡는다.
  if grep -qF "$sentinel" "$CORE_PY"; then
    echo ""
    return 1
  fi
  cp "$CORE_PY" "$mut"
  sed -i "$expr" "$mut"
  # ★ 실패 경로에서 **무변형 사본을 남기지 않는다** (F-CR20 단위 C — latent born-broken).
  #   `cp` 가 실패 판정보다 앞서므로, 치환이 안 됐는데 파일만 남으면 그 경로에는 **무변형 core**
  #   가 놓인다. 게다가 `MUT_SEQ` 증가가 명령치환(서브셸) 밖으로 전파되지 않아 전 호출이 **같은
  #   파일명**을 쓰므로, 하류에서 `[ -f ... ]` 같은 **존재-only** 검사를 하면 무변형 core 를
  #   mutant 로 착각해 통과시킨다. 파일 존재는 치환의 증거가 아니다 — 실패 시 즉시 지운다.
  if ! grep -qF "$sentinel" "$mut"; then
    rm -f "$mut"
    echo ""
    return 1
  fi
  if ! "$PY" -m py_compile "$mut" >/dev/null 2>&1; then
    rm -f "$mut"
    echo ""
    return 1
  fi
  MUT_PATH="$mut"
  echo "$mut"
  return 0
}

# mutation_kill_exit <label> <sed_expr> <sentinel> <root> <expect_base_rc> [args...]
#   KILLED ⟺ **양 팔 crash 0** ∧ baseline(무변형)=expect_base_rc ∧ mutant rc != baseline rc.
#
#   ★ crash mutant 무효 (F-CR20-8 형제 대칭 봉합). 종전 구현은 `mut_rc != base_rc` 하나만 보고
#     KILL 을 발화했다. 그런데 core 에는 top-level catch-all 이 없어(`sys.exit(main())` 직접)
#     **미포착 예외 → 파이썬 기본 rc=1** 이고, 이 값은 `EXIT_FAIL` 과 **정확히 같다**. 따라서
#     baseline=0 인 자리에서 mutant 가 그냥 죽기만 해도 rc 는 0→1 로 "flip" 하고 하네스는 그것을
#     판별력으로 계상한다 — 「분기 중화」와 「분기 도달 전 사망」이 **원리적으로 구별되지 않는다**.
#     실측(본 회차): M1·M2·M3-siteA 3건은 Traceback 0건 = 오늘은 전부 정상 판정 경로였다.
#     **결함은 오늘의 오판이 아니라 가드 부재**이며, 이 헬퍼는 sentinel **5개**
#     (M1 · M2 · M3-siteA · M3-siteB · M5)를 운반하므로 실패 시 5 site 가 동시에 눈이 먼다.
#     형제 `mutation_kill_stdout` 은 이미 같은 가드를 갖고 있다 — 여기만 비워두면 그 봉합이
#     자기 형제를 안 본 것이 된다. 그래서 **동일 강도**로 맞춘다.
mutation_kill_exit() {
  local label="$1" expr="$2" sentinel="$3" root="$4" expect="$5"; shift 5
  local mut base_rc mut_rc base_tb mut_tb base_gap mut_gap
  local tb_mark="Traceback (most recent call last)"
  run_core "$CORE_PY" "$root" "$@"
  base_rc=$CORE_RC
  base_tb=$(grep -cF "$tb_mark" "$CORE_ERR")
  base_gap="$(announce_gap "$base_rc" "$CORE_OUT" "$CORE_ERR")"
  # 대조군 crash 가드 — 대조군이 이미 죽어 있으면 어떤 exit 차이도 해당 분기로 귀속되지 않는다.
  if [ "$base_tb" -ge 1 ]; then
    fail_case "$label: 무효 — baseline(무변형) stderr 에 Traceback ${base_tb}건 (exit=$base_rc). 대조군이 이미 crash 라 대조 자체가 성립하지 않는다"
    sed 's/^/        base-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  if [ "$base_rc" -ne "$expect" ]; then
    fail_case "$label: baseline 기대 exit=$expect 인데 실제 $base_rc — 대조군 성립 불가(무효 kill)"
    return 1
  fi
  # 대조군 종점 announce (F-CR22-1) — rc 가 맞아도 그 종점에 닿았다는 양성 증거가 없으면 무효.
  if [ -n "$base_gap" ]; then
    fail_case "$label: 무효 — baseline 종점 미도달: $base_gap"
    return 1
  fi
  # ★ mutate_core 는 명령치환(서브셸)에서 돌므로 그 안의 전역 대입은 살아남지 않는다.
  #   변형본 경로는 반드시 여기(부모 셸)에서 MUT_PATH 로 옮긴다. (최초 실행에서 실측 검출된 함정.)
  mut="$(mutate_core "$label" "$expr" "$sentinel")"
  if [ -z "$mut" ]; then
    fail_case "$label: NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
    return 1
  fi
  MUT_PATH="$mut"
  run_core "$mut" "$root" "$@"
  mut_rc=$CORE_RC
  mut_tb=$(grep -cF "$tb_mark" "$CORE_ERR")
  mut_gap="$(announce_gap "$mut_rc" "$CORE_OUT" "$CORE_ERR")"
  # crash mutant = 무효 kill. rc 가 움직인 원인을 「분기 중화」로 귀속할 수 없다.
  if [ "$mut_tb" -ge 1 ]; then
    fail_case "$label: 무효 kill — mutant stderr 에 Traceback ${mut_tb}건 (exit=$base_rc→$mut_rc). rc 이동 원인이 「분기 중화」인지 「미포착 예외로 인한 조기 사망」인지 구별되지 않는다(rc=1 은 EXIT_FAIL 과 동값)"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  # ★ 종점 announce (F-CR22-1) — Traceback 부재-assert 가 못 보는 조용한 종료를 여기서 잡는다.
  #   rc flip 을 「분기 중화」로 귀속하려면 mutant 가 **끝까지 돌아 종점을 발화**했어야 한다.
  if [ -n "$mut_gap" ]; then
    fail_case "$label: 무효 kill — mutant 종점 미도달 (exit=$base_rc→$mut_rc): $mut_gap. rc 이동을 「분기 중화」로 귀속할 수 없다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  if [ "$mut_rc" -ne "$base_rc" ]; then
    pass_case "$label: KILLED (baseline exit=$base_rc → mutant exit=$mut_rc 실측 · 양 팔 종점 announce 도달 확인, 판별력 load-bearing · Traceback base=${base_tb}건 mut=${mut_tb}건)"
    return 0
  fi
  fail_case "$label: SURVIVED (baseline exit=$base_rc == mutant exit=$mut_rc — 해당 분기가 판별에 기여하지 않음)"
  return 1
}

# mutation_kill_stdout <label> <sed_expr> <sentinel> <root> <token> <expect_rc>
#   exit-flip 이 아닌 축 전용. KILLED ⟺ **양 팔 crash 0** ∧ **양 팔 exit=expect (실측)** ∧
#   baseline stdout token ≥1 ∧ mutant stdout token 0.
#
#   ★ crash mutant 무효 (F-CR20-8 봉합). 종전 구현은 `base_hit>=1 && mut_hit==0` 두 술어만
#     보면서 라벨로는 "exit 은 양쪽 $expect 로 불변" 을 단정했다 — mutant 팔의 rc 를 **한 번도
#     읽지 않은 채** 한 단정이라 관측 없는 발화였다. 토큰이 사라지는 원인은 두 가지다:
#       (i) 대상 분기가 중화됐다      = 우리가 재려는 판별력
#      (ii) 프로세스가 그 분기에 **닿기 전 죽었다** = 아무것도 재지 못한 무효 실행
#     둘을 구별할 신호가 없으면 (ii) 가 KILL 로 계상된다(축 귀속 붕괴). 그래서
#     **stderr Traceback = crash 신호**를 양 팔 대칭으로 보고, mutant 팔 exit 을 실측해
#     기대치와 대조한다. crash 또는 exit 이탈이면 pass_case 가 아니라 fail_case 다 —
#     무효 실행을 초록으로 세지 않는다(본 Story 의 "crash mutant 무효" 규율의 집행 지점).
#     실측 근거: 이 가드 없이 census emit 자리를 `raise` 로 바꾼 mutant(실제 rc=1·Traceback 1건)와
#     `sys.exit(9)` 로 바꾼 mutant(실제 rc=9)가 **둘 다** "exit 은 양쪽 0 로 불변" KILLED 로
#     초록 보고됐다. 라벨이 주장하던 명제가 거짓인데도 통과한 것이다.
mutation_kill_stdout() {
  local label="$1" expr="$2" sentinel="$3" root="$4" token="$5" expect="$6"
  local mut base_rc mut_rc base_hit mut_hit base_tb mut_tb base_gap mut_gap
  local tb_mark="Traceback (most recent call last)"

  # ── baseline 팔 (대조군) — crash 가드를 대칭 배치한다(대조군이 죽어 있으면 대조 무의미) ──
  run_core "$CORE_PY" "$root"
  base_rc=$CORE_RC
  base_tb=$(grep -cF "$tb_mark" "$CORE_ERR")
  base_hit=$(grep -cF "$token" "$CORE_OUT")
  base_gap="$(announce_gap "$base_rc" "$CORE_OUT" "$CORE_ERR")"
  if [ "$base_tb" -ge 1 ]; then
    fail_case "$label: 무효 — baseline(무변형) stderr 에 Traceback ${base_tb}건 (exit=$base_rc). 대조군이 이미 crash 라 어떤 관측도 해당 분기로 귀속되지 않는다"
    sed 's/^/        base-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  if [ "$base_rc" -ne "$expect" ]; then
    fail_case "$label: baseline 기대 exit=$expect 인데 실제 $base_rc — 대조군 성립 불가"
    return 1
  fi
  if [ -n "$base_gap" ]; then
    fail_case "$label: 무효 — baseline 종점 미도달: $base_gap"
    return 1
  fi

  # ── mutant 팔 ──
  mut="$(mutate_core "$label" "$expr" "$sentinel")"
  if [ -z "$mut" ]; then
    fail_case "$label: NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
    return 1
  fi
  MUT_PATH="$mut"
  run_core "$mut" "$root"
  mut_rc=$CORE_RC
  mut_tb=$(grep -cF "$tb_mark" "$CORE_ERR")
  mut_hit=$(grep -cF "$token" "$CORE_OUT")
  mut_gap="$(announce_gap "$mut_rc" "$CORE_OUT" "$CORE_ERR")"

  # crash mutant = 무효 kill. 토큰 소실(hit=$mut_hit)을 「분기 중화」로 귀속할 수 없다.
  if [ "$mut_tb" -ge 1 ]; then
    fail_case "$label: 무효 kill — mutant stderr 에 Traceback ${mut_tb}건 (exit=$base_rc→$mut_rc, token hit=$base_hit→$mut_hit). 프로세스가 대상 분기 도달 전 사망했을 수 있어 토큰 소실을 판별력으로 계상하지 않는다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  # exit 축 실측 단언 — 라벨이 주장하는 '불변' 을 관측으로 뒷받침한다(무관측 단정 금지).
  if [ "$mut_rc" -ne "$expect" ]; then
    fail_case "$label: 무효 kill — mutant exit=$mut_rc (기대 $expect · baseline=$base_rc). exit 축이 함께 흔들리면 토큰 소실을 stdout 축 단독 판별로 귀속할 수 없다"
    return 1
  fi
  # ★ 종점 announce (F-CR22-1) — 여기가 **stdout 축에서 가장 위험한 자리**다.
  #   위 rc pin 은 rc 가 **이탈**하는 종료만 막는다. 그런데 이 오라클은 '토큰 소실' 을 판별로
  #   읽으므로, rc 를 **보존한 채** 조용히 죽는 종료(`sys.exit(0)`, 기대 rc 와 동값)가 오면
  #   ① rc pin 통과 ② 토큰 소실 ③ Traceback 0 → **거짓 KILLED** 가 된다. 실측(F-CR22-1 봉합 시):
  #   census emit 자리를 `sys.exit(0)` 로 바꾼 mutant 가 `✓ PASS: M4 … KILLED … exit=0→0 실측 불변`
  #   을 발화하고 전건 PASS=46 FAIL=0 · rc=0 이었다. rc pin 이 이 축을 막는다는 기대는 **거짓**이다.
  if [ -n "$mut_gap" ]; then
    fail_case "$label: 무효 kill — mutant 종점 미도달 (exit=$base_rc→$mut_rc, token hit=$base_hit→$mut_hit): $mut_gap. 토큰 소실을 「분기 중화」로 귀속할 수 없다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    return 1
  fi

  if [ "$base_hit" -ge 1 ] && [ "$mut_hit" -eq 0 ]; then
    pass_case "$label: KILLED (stdout 축 — baseline '$token' ${base_hit}건 → mutant ${mut_hit}건 / exit=$base_rc→$mut_rc 실측 불변 · 양 팔 종점 announce 도달 확인 · Traceback base=${base_tb}건 mut=${mut_tb}건)"
    return 0
  fi
  fail_case "$label: SURVIVED (baseline hit=$base_hit / mutant hit=$mut_hit · exit=$base_rc→$mut_rc 실측 — stdout 토큰 소실 미관측)"
  return 1
}

# expect_exit <label> <expected_rc> <actual_rc> [stderr_grep_token]
expect_exit() {
  local label="$1" want="$2" got="$3" token="${4:-}"
  if [ "$got" -ne "$want" ]; then
    fail_case "$label: exit=$got (기대 $want)"
    sed 's/^/        stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  if [ -n "$token" ] && ! grep -qF "$token" "$CORE_ERR"; then
    fail_case "$label: exit=$got 은 맞으나 stderr 에 '$token' 미관측 (다른 사유로 우연히 같은 exit)"
    sed 's/^/        stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  pass_case "$label: exit=$got${token:+ + stderr '$token' 관측}"
  return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. T-1 양방향 — 정방향(무변형 PASS) ↔ 역방향(축 어긋난 fixture 는 여전히 RED)
#    ★ ⓐ 만으로는 "고쳐서 통과"와 "판별력을 죽여서 통과"를 구별할 수 없다. ⓑ 가 필수다.
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-1 양방향 (정방향 PASS ↔ 역방향 RED) ─────────────────────────────────────"

# ── T-1ⓐ 정방향: 무변형 corpus → exit 0 (PINNED entry = thin wrapper 경유) ──
bash "$WRAPPER" >"$TEST_TMP/t1a.out" 2>"$TEST_TMP/t1a.err"; clean_rc=$?
if [ "$clean_rc" -eq 0 ]; then
  pass_case "T-1ⓐ 정방향: 무변형 corpus → wrapper exit=0"
else
  fail_case "T-1ⓐ 정방향: clean corpus must PASS — wrapper exit=$clean_rc"
  sed 's/^/        stderr> /' "$TEST_TMP/t1a.err" >&2
fi

CORE_OUT="$TEST_TMP/t1a.out"
CORE_ERR="$TEST_TMP/t1a.err"
t1a_ind="$(census_of N_indeterminate)"
if [ "$t1a_ind" = "0" ]; then
  pass_case "T-1ⓐ: N_indeterminate=0 (판정불가 표본 0 — 상한 축 충족)"
else
  fail_case "T-1ⓐ: N_indeterminate='$t1a_ind' (기대 0)"
fi

# ★ 판별자 = 마커 문면 (rc 역추론 아님) — 하네스가 emit 한 verdict: 라인을 직접 읽는다.
for pair in "s01:LIVE" "s02:HOLLOW" "p01:HOLLOW"; do
  unit="${pair%%:*}"; want="${pair##*:}"
  got="$(verdict_of "$unit")"
  if [ "$got" = "$want" ]; then
    pass_case "T-1ⓐ verdict: $unit=$want (마커 문면 판정 — 프로세스 rc 역추론 아님)"
  else
    fail_case "T-1ⓐ verdict: $unit='$got' (기대 $want)"
  fi
done

# ── T-1ⓑ 역방향: 축이 어긋난(=자동 적중하는) stage 선언은 여전히 RED ──
#   SUMMARY 는 상수 footer 라 kill·xkill 양쪽 fail_stage 에 상주해 자동 적중한다 = 공허 선언.
#   ★ 이 어긋남을 잡는 **유일 검출자는 xkill 축-disjoint 검사**다 — verdict(LIVE/HOLLOW/HOLLOW)·
#   IC-1/2/5/6·census·baseline 은 전부 정상 통과한다. 그래서 M6 가 load-bearing 이다.
MUT_MANIFEST="$TEST_TMP/manifest_summary_stage.yaml"
reset_mf; MF_STAGE="SUMMARY"; emit_manifest "$MUT_MANIFEST"
bash "$WRAPPER" --manifest "$MUT_MANIFEST" >"$TEST_TMP/t1b.out" 2>"$TEST_TMP/t1b.err"; mutant_rc=$?
if [ "$mutant_rc" -ne 0 ]; then
  pass_case "T-1ⓑ 역방향: mutant corpus must FAIL — wrapper exit=$mutant_rc"
else
  fail_case "T-1ⓑ 역방향: 축 어긋난 stage 선언이 통과함 (판별력 사망 — exit=$mutant_rc)"
fi
CORE_OUT="$TEST_TMP/t1b.out"
CORE_ERR="$TEST_TMP/t1b.err"
if grep -qF "::error::[XKILL-AXIS]" "$TEST_TMP/t1b.err"; then
  pass_case "T-1ⓑ: stderr 에 ::error::[XKILL-AXIS] 관측 (자동 적중 = 공허 선언 검출)"
else
  fail_case "T-1ⓑ: exit 은 non-zero 이나 XKILL-AXIS 마커 미관측 (다른 사유로 우연히 RED)"
  sed 's/^/        stderr> /' "$TEST_TMP/t1b.err" >&2
fi
# ★ 유일 검출자 실증: T-1ⓑ 에서 verdict·census 축은 **정상 통과**한다.
if [ "$(verdict_of s01)" = "LIVE" ] && [ "$(verdict_of s02)" = "HOLLOW" ] && [ "$(census_of N_indeterminate)" = "0" ]; then
  pass_case "T-1ⓑ: verdict·N_indeterminate 축은 정상 통과 — xkill 축-disjoint 가 유일 검출자임을 실증"
else
  fail_case "T-1ⓑ: verdict/census 축 관측이 기대와 다름 (유일-검출자 실증 전제 파손)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. identity probe — known-answer 원문대조 (internal control)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── identity probe (known-answer 원문대조) ────────────────────────────────────"
known_sha="$("$PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" \
             "$CORPUS_ROOT/s01/gate.py.sample")"
emitted_sha="$(sed -n 's/^resolved-target: unit=s01 entry=gate.py sha256=\([0-9a-f]*\)$/\1/p' "$TEST_TMP/t1a.out" | head -1)"
if [ -n "$known_sha" ] && [ "$known_sha" = "$emitted_sha" ]; then
  pass_case "identity probe: resolved-target sha256 == 커밋 s01/gate.py.sample sha256 (독립 계산 known-answer 일치)"
else
  fail_case "identity probe: known=$known_sha emitted=$emitted_sha 불일치 — 판정기가 연 artifact 가 커밋 표본이 아님"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 6. MUTATION-SENTINEL 8축 (M3 은 2 site 개별 mutant / M7 은 2단 mutant)
# ═══════════════════════════════════════════════════════════════════════════════
# ━━ MUTATION-SENTINEL — 무엇을 죽이며 왜 load-bearing 인가 ━━━━━━━━━━━━━━━━━━━━━━━
#   M1: I-8 협착 conjunct (`kill.fail=1`)           — 제거 시 arm-H 정상 표본이 INDETERMINATE 전멸.
#   M2: I-11 `¬LIVE ∧ ¬HOLLOW` 가드                 — 제거 시 arm-H(kill 관측 ≡ clean 관측)가 전멸.
#   M3: exit_space 검사 (2 site — 선언검사 + 런타임 I-4) — 제거 시 rc 이탈이 조용히 통과.
#   M4: census 축별 개별 emit                       — 제거 시 축 축소가 총합 1줄에 숨는다. (stdout 축)
#   M5: IC-4 exec-tree blinding **호출부**          — 제거 시 arm 누설 표면이 exec dir 에 잔존.
#   M6: xkill 축-disjoint 검사                      — 제거 시 상수 footer stage 선언이 공허 통과.
#   M7: 형제 부재 불변식 (`len(siblings) != 1`)     — 제거 시 실행 순번 누설 채널이 무성 복원.
#   M8: 하한 대조의 **정의역** (`LOWER_BOUND_AXES`) — 축소 시 baseline 하한 대조가 6축 → 1축으로
#       도려내져도 하네스 전건이 초록으로 통과한다. 이 tuple 은 "어느 축을 하한 대조하는가"
#       **그 자체**이므로, 빠진 축은 대조가 **일어나지 않아** census 축소가 무성 통과한다.
#       M4 와 겹치지 않는다 — M4 는 "축이 stdout 에 보이는가"를, M8 은 "보이는 축이 실제로
#       대조되는가"를 지킨다(M4 mutant 는 census emit 을 지우고, M8 mutant 는 census 를 그대로
#       둔 채 대조 루프의 정의역만 좁힌다). (stdout 축 — exit-flip 아님)
#   ★ 정직 기재: core(`scripts/lib/check_hollow_gate_corpus.py`)의 in-file MUTATION-SENTINEL
#     절은 여전히 **M1~M7** 로 적혀 있다(M8 미기재). core 는 본 회차 수정 금지 대상(설계 동결·
#     제품 코드)이라 여기서 갱신하지 못했다 — 문서 drift 를 조용히 두지 않고 잔여로 남긴다.
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── MUTATION-SENTINEL 8축 (M3 = 2 site 개별 / M7 = 2단 / M4·M8 = stdout 축) ──"

# M1 = I-8 협착 conjunct (kill.fail=1). 중화 시 arm-H(fail_stage=∅)에서 공허 참 → 정상 HOLLOW 전멸.
#   ★ 이 conjunct 는 본 Story 가 실제로 겪은 born-RED 의 봉합점이다.
mutation_kill_exit "M1 (I-8 협착 conjunct)" \
  's/    if bundle.kill.fail and kill_target_stage not in bundle.kill.fail_stages:/    if kill_target_stage not in bundle.kill.fail_stages:  # M1-neutralized/' \
  "M1-neutralized" "$REPO_ROOT" 0

# M2 = I-11 ¬LIVE ∧ ¬HOLLOW 가드. 중화 시 arm-H(kill 관측 ≡ clean 관측 = arm-H 의 정의)가 전멸.
mutation_kill_exit "M2 (I-11 ¬LIVE∧¬HOLLOW 가드)" \
  's/    if (not live) and (not hollow) and (bundle.kill.observed == bundle.clean.observed):/    if (bundle.kill.observed == bundle.clean.observed):  # M2-neutralized/' \
  "M2-neutralized" "$REPO_ROOT" 0

# M3 = exit_space 검사 — ★ 2 site. 각각 독립 mutant 로 돌려 각 site 가 load-bearing 임을 분리 확인.
#   site A = 선언검사(T-2ⓐ loud 실패, _validate_manifest) / site B = 런타임 I-4 (rc ∉ exit_space).
ES_EMPTY="$TEST_TMP/manifest_exit_space_empty.yaml"
reset_mf; MF_EXIT_SPACE="[]"; emit_manifest "$ES_EMPTY"
ES_NARROW="$TEST_TMP/manifest_exit_space_narrow.yaml"
reset_mf; MF_EXIT_SPACE="[0]"; emit_manifest "$ES_NARROW"
SH_M3="$(new_shadow none)"

mutation_kill_exit "M3-siteA (exit_space 선언검사 · T-2ⓐ loud 실패)" \
  's/        if not isinstance(es, list) or len(es) == 0:/        if False:  # M3a-neutralized/' \
  "M3a-neutralized" "$SH_M3" 3 --manifest "$ES_EMPTY"

mutation_kill_exit "M3-siteB (런타임 I-4 · rc ∉ exit_space)" \
  's/                    if rc not in gate\["exit_space"\]:/                    if False:  # M3b-neutralized/' \
  "M3b-neutralized" "$SH_M3" 1 --manifest "$ES_NARROW"

# ★ site 독립성: siteB 만 중화해도 siteA 는 살아있어야 한다 (한 번에 둘 다 지우면 분리 불가).
mut_m3b="$MUT_PATH"
# ★ 존재-only 금지 (F-CR20 단위 C). `MUT_PATH` 는 `mutate_core` **성공 시에만** 대입되므로 직전
#   호출이 실패하면 **이전 값이 잔존**하고, 전 mutant 가 같은 파일명을 쓰므로 그 경로 내용이
#   siteB 처치본이라는 보장이 없다. 존재가 아니라 **치환이 실제로 일어났음**을 판정에 넣는다.
if [ -n "$mut_m3b" ] && [ -f "$mut_m3b" ] && grep -qF "M3b-neutralized" "$mut_m3b"; then
  run_core "$mut_m3b" "$SH_M3" --manifest "$ES_EMPTY"
  expect_exit "M3 site 독립성: siteB 중화본도 빈 exit_space 는 여전히 loud 실패" 3 "$CORE_RC" "T-2ⓐ loud 실패"
else
  fail_case "M3 site 독립성: NOT_RUN — siteB 변형본 부재 또는 그 경로 내용에 'M3b-neutralized' 미검출(치환 미실증 = 무변형 core 를 mutant 로 오인할 수 있는 상태)"
fi

# M4 = census 개별 emit (7축). exit-flip 아님 → stdout 토큰 소실로 kill.
mutation_kill_stdout "M4 (census 축별 개별 emit)" \
  's/        _emit(f"census: {a}={census\[a\]}")/        pass  # M4-neutralized/' \
  "M4-neutralized" "$REPO_ROOT" "census: N_armL=" 0

# M5 = IC-4 exec-tree blinding assert. 오염 shadow(fixture 안에 stamp 잠입)로 baseline=3 을 만든 뒤 중화.
SH_M5="$(new_shadow none)"
# s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
echo "leaked-arm-signal" > "$SH_M5/tests/fixtures/hollow-gate-corpus/s01/kill/stamp_leak.txt"
echo "leaked-arm-signal" > "$SH_M5/tests/fixtures/hollow-gate-corpus/s02/kill/stamp_leak.txt"
MF_M5="$TEST_TMP/manifest_m5.yaml"; reset_mf; emit_manifest "$MF_M5"
mutation_kill_exit "M5 (IC-4 exec-tree blinding assert)" \
  's/                        bad = _blinding_violations(unit_dir, exec_root)/                        bad = []  # M5-neutralized/' \
  "M5-neutralized" "$SH_M5" 3 --manifest "$MF_M5"

# M6 = xkill 축-disjoint 검사. 중화 시 §4 T-1ⓑ 가 통과해버린다 = 판별력 사망.
mutation_kill_exit "M6 (xkill 축-disjoint 검사)" \
  's/                if tgt in legs\["xkill"\].fail_stages:/                if False:  # M6-neutralized/' \
  "M6-neutralized" "$REPO_ROOT" 1 --manifest "$MUT_MANIFEST"

# M7 = 형제 부재 불변식 (F-CR18-9 실행 순번 누설 채널 가드).
# ★ 2단 mutant 인 이유 (정직 기재): 이 불변식은 정상 corpus 에서 **절대 발화하지 않는다** —
#   leg 별 즉시 정리가 선행해 exec_root 직속 dir 수가 항상 1 이기 때문이다. 그래서 무변형
#   core 를 baseline 으로 잡으면 baseline exit=0 이라 대조군이 성립하지 않고(무효 kill),
#   `mutation_kill_exit` 를 그대로 쓸 수 없다. 정리를 먼저 무력화해 **불변식이 실제로
#   발화하는 상태**를 baseline 으로 만든 뒤 거기서 불변식만 더 제거한다:
#     baseline (정리만 무력화)       = 형제 누적 → 불변식 발화 → exit 3
#     mutant   (정리 + 불변식 무력화) = 무성 통과              → exit 0
#   mutant 상태가 곧 구현리뷰 iter1 P1 결함(자식이 형제 수로 실행 순번을 역산하는 채널)의
#   **원상복원**이며, 그 앞에서 RED 를 내는 것이 본 케이스의 판별력이다.
#   KILLED 판정은 exit flip 만으로 하지 않는다 — baseline stderr 에 **관측된 형제 개수 문면**이
#   있는지까지 확인해, exit 3 이 다른 substrate 사유로 난 경우를 대조군 실패로 떨어뜨린다.
SH_M7="$(new_shadow none)"
MF_M7="$TEST_TMP/manifest_m7.yaml"; reset_mf; emit_manifest "$MF_M7"
M7_SED_CLEANUP='s/^                        shutil.rmtree(unit_dir, ignore_errors=True)$/                        pass  # M7-cleanup-off/'
M7_SED_INVARIANT='s/^    if len(siblings) != 1:$/    if False:  # M7-sibling-invariant-off/'
m7_base="$(mutate_core "M7 baseline" "$M7_SED_CLEANUP" "M7-cleanup-off")"
# ★ 실측 함정 (본 케이스 작성 중 재현): mutate_core 는 명령치환(서브셸)에서 돌아 MUT_SEQ 증가가
#   부모에 남지 않는다 → 연속 2회 호출이 **같은 파일명**을 쓰고 두 번째가 첫 번째를 덮어쓴다.
#   그러면 baseline 이 mutant 와 동일해져 baseline exit=0 이 나오고 "대조군 성립 불가" 로 착지한다
#   (파일 상단이 경고한 그 함정의 2차 발현). 두 번째 호출 전에 baseline 을 별 경로로 확보한다.
if [ -n "$m7_base" ]; then cp "$m7_base" "$TEST_TMP/m7_base.py"; m7_base="$TEST_TMP/m7_base.py"; fi
m7_mut="$(mutate_core "M7 mutant" "$M7_SED_CLEANUP; $M7_SED_INVARIANT" "M7-sibling-invariant-off")"
if [ -z "$m7_base" ] || [ -z "$m7_mut" ]; then
  fail_case "M7 (형제 부재 불변식): NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
elif grep -qF "M7-sibling-invariant-off" "$m7_base"; then
  # baseline 에 mutant 처치가 섞이면 두 군의 차이가 사라져 대조 자체가 무의미해진다.
  fail_case "M7 (형제 부재 불변식): baseline 오염 — baseline 에 불변식 제거 처치가 섞였다(대조군 무효)"
elif ! grep -qF "M7-cleanup-off" "$m7_mut"; then
  # ── F-CR20-1 봉합: mutant **저처치** 가드 (오염 가드의 대칭 위치) ────────────────
  #   mutant 는 2단 처치("$M7_SED_CLEANUP; $M7_SED_INVARIANT")인데 mutate_core 의 sentinel
  #   인자는 2번째(M7-sibling-invariant-off) **하나만** 검증한다. 1번째(정리 무력화)가 빠지면
  #   두 팔이 **2축(정리·불변식) 차이**가 되고, exit flip 3→0 은 정리 복원만으로도 나므로
  #   불변식 축 귀속이 성립하지 않는다. 바로 위 오염 가드는 baseline 방향(mutant 처치가 baseline
  #   으로 새는 것)만 막으므로 **반대 방향인 mutant 저처치는 무방비**였다.
  fail_case "M7 (형제 부재 불변식): mutant 저처치 — mutant 에 정리 무력화 처치(M7-cleanup-off)가 없다. 두 팔이 2축 차이라 exit flip 을 불변식 축에 귀속할 수 없다(무효 kill)"
else
  run_core "$m7_base" "$SH_M7" --manifest "$MF_M7"; m7_base_rc=$CORE_RC
  # ── F-CR21-1 봉합: crash 가드 (형제 3 site 와 동일 강도) ────────────────────────
  #   본 판정은 **차분 오라클**(m7_mut_rc != m7_base_rc)이다. 차분 오라클에서 mutant 가 대상
  #   불변식에 **닿기 전 죽으면** 파이썬 기본 rc=1 이 나오고, 여기 baseline 은 3 이므로 `1 != 3`
  #   이 성립해 조기 사망이 **flip 으로 보인다**. 형제 `mutation_kill_exit`/`mutation_kill_stdout`
  #   /M8 이 이미 같은 가드를 갖는데 여기만 비어 있었다 — 그 봉합이 자기 형제를 안 본 자리다.
  #   실증(F-CR21-1): 불변식 자리를 `{}["M7-sibling-invariant-off"]`(구문 유효·평가 시 KeyError)로
  #   바꾼 mutant 가 `✓ PASS: M7 … KILLED … mutant exit=1` 을 발화하고 전건 PASS=46 FAIL=0 · rc=0
  #   이었다. 「불변식 중화」와 「조기 사망」이 원리적으로 구별되지 않는다.
  #   ★ baseline stderr 는 mutant 팔 run_core 가 $CORE_ERR 를 덮어쓰므로 여기서 별도 보존한다.
  M7_TB="Traceback (most recent call last)"
  m7_base_tb=$(grep -cF "$M7_TB" "$CORE_ERR")
  cp "$CORE_ERR" "$TEST_TMP/m7_base.err"
  # ★ 종점 announce (F-CR22-1) — Traceback 가드는 **부재-assert** 라 조용한 종료를 못 본다.
  #   실측: 이 불변식 자리를 `if sys.exit(2):` 로 바꾼 mutant 가 `✓ PASS: M7 … KILLED …
  #   mutant exit=2 · Traceback base=0건 mut=0건` 을 발화하고 전건 PASS=46 FAIL=0 · rc=0 이었다.
  m7_base_gap="$(announce_gap "$m7_base_rc" "$CORE_OUT" "$TEST_TMP/m7_base.err")"
  # ── F-CR20-7 상속분 봉합: 개수 리터럴 단일점 의존 제거 ──────────────────────────
  #   종전: grep -cF "exec-root 직속 디렉터리 2개" — 개수 '2' 를 대조 문면에 **박아** 두었다.
  #   core 문면은 f"...{len(siblings)}개..." 이므로 개수가 관측과 무관한 상수로 바뀌어도 이
  #   검사는 그대로 통과했다(형제 pytest 축과 같은 구멍). 정정 2건:
  #     (i) **귀속**은 개수 비의존 정규식으로 한다 — 개수가 정당하게 달라져도 귀속은 유지되고,
  #         "형제 불변식이 발화했다"는 명제만을 판별한다.
  #    (ii) **개수**는 파싱해 self-test 가 독립 관측한 **발화 leg 의 순번**과 결부시킨다. 정리를
  #         무력화했으므로 형제는 leg 마다 1씩 누적하고, 최초 위반 시점의 형제 수 == 그 leg 의
  #         순번이다. leg 이름은 stderr 의 `leg=<role>` 에서 읽고, 순서 리스트는 **self-test 안
  #         리터럴로 pin** 한다 — core 의 LEG_ROLES 를 읽어오면 좌우변이 동시 파생돼 항진한다.
  #   ★ 정직 천장(실측에 딸린 잔여): core 는 최초 위반에서 `return EXIT_SUBSTRATE` 하므로 한 실행에
  #     관측점은 **1개**뿐이고 그 참값은 2다. 참값이 단일한 관측 1개로는 "계산된 2"와 "상수 2"를
  #     원리적으로 구별할 수 없다 — 이 정정이 없애는 것은 **리터럴 단일점 의존**이지 core 측 개수
  #     하드코딩 mutant 의 kill 이 아니다. 후자를 닫으려면 참값이 다른 2번째 관측이 필요하고, 그건
  #     abort 무력화(새 표면)를 요구하므로 여기서 하지 않는다. 못 닫은 것을 닫았다고 적지 않는다.
  m7_base_hit=$(grep -cE "exec-root 직속 디렉터리 [0-9]+개 \(정확히 1 필요\)" "$CORE_ERR")
  m7_base_sib=$(sed -n 's/.*exec-root 직속 디렉터리 \([0-9][0-9]*\)개 (정확히 1 필요).*/\1/p' "$CORE_ERR" | head -1)
  m7_base_leg=$(sed -n 's/^::error::\[SUBSTRATE\] unit=[^ ]* leg=\([a-z]*\): exec-tree blinding 파손.*/\1/p' "$CORE_ERR" | head -1)
  m7_leg_ord=0; m7_i=0
  for m7_r in kill clean empty xkill; do          # ★ leg 순서 pin (self-test 리터럴 — core 미참조)
    m7_i=$((m7_i+1))
    [ "$m7_r" = "$m7_base_leg" ] && m7_leg_ord=$m7_i
  done
  run_core "$m7_mut" "$SH_M7" --manifest "$MF_M7"; m7_mut_rc=$CORE_RC
  m7_mut_tb=$(grep -cF "$M7_TB" "$CORE_ERR")
  m7_mut_gap="$(announce_gap "$m7_mut_rc" "$CORE_OUT" "$CORE_ERR")"
  if [ "$m7_base_tb" -ge 1 ]; then
    # 대조군 crash 가드 — 대조군이 이미 죽어 있으면 어떤 exit 차이도 불변식 축에 귀속되지 않는다.
    fail_case "M7 (형제 부재 불변식): 무효 — baseline(정리 무력화) stderr 에 Traceback ${m7_base_tb}건 (exit=$m7_base_rc). 대조군이 이미 crash 라 대조 자체가 성립하지 않는다"
    sed 's/^/        base-stderr> /' "$TEST_TMP/m7_base.err" >&2
  elif [ "$m7_base_rc" -ne 3 ] || [ "$m7_base_hit" -lt 1 ]; then
    fail_case "M7 (형제 부재 불변식): 대조군 성립 불가 — 정리 무력화 baseline exit=$m7_base_rc (기대 3) / 형제 불변식 문면 ${m7_base_hit}건 (기대 ≥1). 무효 kill 금지"
  elif [ -n "$m7_base_gap" ]; then
    fail_case "M7 (형제 부재 불변식): 무효 — baseline 종점 미도달: $m7_base_gap"
    sed 's/^/        base-stderr> /' "$TEST_TMP/m7_base.err" >&2
  elif [ "$m7_mut_tb" -ge 1 ]; then
    # mutant crash = 무효 kill. rc 이동 원인을 「불변식 중화」로 귀속할 수 없다.
    fail_case "M7 (형제 부재 불변식): 무효 kill — mutant stderr 에 Traceback ${m7_mut_tb}건 (exit=$m7_base_rc→$m7_mut_rc). rc 이동 원인이 「불변식 중화」인지 「미포착 예외로 인한 조기 사망」인지 구별되지 않는다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
  elif [ -n "$m7_mut_gap" ]; then
    fail_case "M7 (형제 부재 불변식): 무효 kill — mutant 종점 미도달 (exit=$m7_base_rc→$m7_mut_rc): $m7_mut_gap. rc 이동을 「불변식 중화」로 귀속할 수 없다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
  elif [ "$m7_leg_ord" -eq 0 ] || [ "$m7_base_sib" != "$m7_leg_ord" ]; then
    fail_case "M7 (형제 부재 불변식): 대조군 무효 — 보고된 형제 수 '$m7_base_sib' 가 발화 leg '$m7_base_leg'(pin 순번 $m7_leg_ord)과 결부되지 않는다. 개수가 관측과 어긋나면 exit 3 을 형제 축으로 귀속할 수 없다"
  elif [ "$m7_mut_rc" -eq "$m7_base_rc" ]; then
    fail_case "M7 (형제 부재 불변식): SURVIVED (baseline exit=$m7_base_rc == mutant exit=$m7_mut_rc — 불변식이 판별에 기여하지 않음 = 실행 순번 누설 채널 무방비)"
  else
    pass_case "M7 (형제 부재 불변식): KILLED (정리 무력화 baseline exit=$m7_base_rc + 형제 불변식 문면 ${m7_base_hit}건 · 형제 수 ${m7_base_sib} == 발화 leg '$m7_base_leg' pin 순번 ${m7_leg_ord} 결부 → 불변식 제거 mutant exit=$m7_mut_rc · 양 팔 종점 announce 도달 확인 · Traceback base=${m7_base_tb}건 mut=${m7_mut_tb}건)"
  fi
fi

# M8 = 하한 대조의 **정의역** (`LOWER_BOUND_AXES`). census 축 6개를 baseline 하한과 대조하는
#      루프의 정의역 그 자체이므로, 이 tuple 을 좁히면 빠진 축은 **대조가 일어나지 않는다**.
#      실측(본 회차 착수 전): `LOWER_BOUND_AXES = ("N_gates",)` 로 좁힌 mutant 는 rc=0 ·
#      Traceback 0 · `baseline-cmp:` 6행 → 1행이며, 그 상태로 본 shell self-test 전건이 초록이었다
#      (변경 전 이 파일의 `baseline-cmp` 참조 = 0건 — load-bearing 성질에 커버리지가 없었다).
#
# ★ exit-flip 축이 아니다 — 정상 corpus 는 전 축이 하한을 만족하므로 대조를 도려내도 rc 는 0 그대로다.
#   그래서 판정을 exit 에 걸지 않고 **stdout 관측 문면**(`baseline-cmp: <axis> ...` 의 축 이름 집합)의
#   축소로 한다. exit 은 '불변'을 주장하는 대신 **양 팔 실측**해 뒷받침하고(무관측 단정 금지),
#   crash mutant 는 KILL 로 계상하지 않고 무효(FAIL)로 떨어뜨린다 — 판정 기준 ③ 와 동일 규율.
#
# ★ 대조군(자기 대조군 보유): mutant 와 대조하기 **전에** baseline(무변형)에서 6축이 실제로
#   관측됨을 확인한다. baseline 이 이미 축을 못 내고 있으면 mutant 와의 차이는 아무것도 뜻하지
#   않는다(무효 kill). M7 에서 실제로 대조군이 붕괴한 전례가 있다 — mutate_core 는 명령치환
#   (서브셸)에서 돌아 MUT_SEQ 증가가 부모에 전파되지 않으므로 연속 2회 호출이 같은 파일명을
#   덮어썼다. M8 은 baseline 팔이 **무변형 $CORE_PY** 라 그 함정을 구조적으로 밟지 않는다.
#
# ★ 기대값 출처(항진 방지): 6축 이름을 **self-test 안 리터럴로 pin** 한다. core 의 CENSUS_AXES /
#   LOWER_BOUND_AXES 에서 파생시키면 검사 대상이 곧 기대값의 원천이 되어(좌우변 동시 파생)
#   상수를 좁힐 때 양변이 함께 좁아져 검사가 **항진**한다.
M8_PIN_AXES="N_gates N_armL N_armH N_probe N_detected N_flip"   # ← 리터럴 pin 6축 (core 미참조)
M8_SED='s/^LOWER_BOUND_AXES = tuple(a for a in CENSUS_AXES if a != "N_indeterminate")$/LOWER_BOUND_AXES = ("N_gates",)  # M8-lower-bound-axes-narrowed/'
M8_TB="Traceback (most recent call last)"
# 축 이름만 뽑아 정렬 (emit 순서 변경 같은 무해한 리팩터로 오검출하지 않도록 집합 비교)
m8_axes_of() { sed -n 's/^baseline-cmp: \([A-Za-z_][A-Za-z_0-9]*\) .*/\1/p' "$1" | sort | tr '\n' ' '; }
m8_pin_sorted="$(printf '%s\n' $M8_PIN_AXES | sort | tr '\n' ' ')"

# ── baseline 팔 (대조군) ──
run_core "$CORE_PY" "$REPO_ROOT"
m8_base_rc=$CORE_RC
m8_base_tb=$(grep -cF "$M8_TB" "$CORE_ERR")
m8_base_axes="$(m8_axes_of "$CORE_OUT")"
m8_base_n=$(grep -cE '^baseline-cmp: ' "$CORE_OUT")
m8_base_gap="$(announce_gap "$m8_base_rc" "$CORE_OUT" "$CORE_ERR")"
m8_ok=1
if [ "$m8_base_tb" -ge 1 ]; then
  fail_case "M8 대조군: 무효 — baseline(무변형) stderr 에 Traceback ${m8_base_tb}건 (exit=$m8_base_rc). 대조군이 이미 crash 라 어떤 관측도 이 축으로 귀속되지 않는다"
  sed 's/^/        base-stderr> /' "$CORE_ERR" >&2
  m8_ok=0
elif [ "$m8_base_rc" -ne 0 ]; then
  fail_case "M8 대조군: 성립 불가 — baseline exit=$m8_base_rc (기대 0)"
  m8_ok=0
elif [ -n "$m8_base_gap" ]; then
  fail_case "M8 대조군: 무효 — baseline 종점 미도달: $m8_base_gap"
  m8_ok=0
elif [ "$m8_base_axes" != "$m8_pin_sorted" ]; then
  fail_case "M8 대조군: 붕괴 — baseline 이 하한 대조한 축 집합 [$m8_base_axes] ≠ self-test pin [$m8_pin_sorted]. 죽이려는 성질이 baseline 에서 관측되지 않으면 mutant 와의 차이는 무의미"
  m8_ok=0
else
  pass_case "M8 대조군: baseline 이 ${m8_base_n}축을 실제로 하한 대조 (관측 축 집합 == self-test 리터럴 pin — mutant 대조 전제 성립 · N_indeterminate 는 상한 축이라 부재)"
fi

# ── mutant 팔 ──
if [ "$m8_ok" -eq 1 ]; then
  m8_mut="$(mutate_core "M8 mutant" "$M8_SED" "M8-lower-bound-axes-narrowed")"
  if [ -z "$m8_mut" ]; then
    fail_case "M8 (하한 대조 정의역 LOWER_BOUND_AXES): NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
  else
    run_core "$m8_mut" "$REPO_ROOT"
    m8_mut_rc=$CORE_RC
    m8_mut_tb=$(grep -cF "$M8_TB" "$CORE_ERR")
    m8_mut_axes="$(m8_axes_of "$CORE_OUT")"
    m8_mut_n=$(grep -cE '^baseline-cmp: ' "$CORE_OUT")
    m8_mut_gap="$(announce_gap "$m8_mut_rc" "$CORE_OUT" "$CORE_ERR")"
    m8_lost=""
    for m8_a in $m8_base_axes; do
      case " $m8_mut_axes " in *" $m8_a "*) ;; *) m8_lost="$m8_lost $m8_a";; esac
    done
    if [ "$m8_mut_tb" -ge 1 ]; then
      fail_case "M8 (하한 대조 정의역): 무효 kill — mutant stderr 에 Traceback ${m8_mut_tb}건 (exit=$m8_base_rc→$m8_mut_rc). 프로세스가 대조 루프 도달 전 사망했을 수 있어 축 소실을 판별력으로 계상하지 않는다"
      sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    elif [ "$m8_mut_rc" -ne "$m8_base_rc" ]; then
      fail_case "M8 (하한 대조 정의역): 무효 kill — mutant exit=$m8_mut_rc ≠ baseline exit=$m8_base_rc. exit 축이 함께 흔들리면 축 집합 축소를 stdout 축 단독 판별로 귀속할 수 없다"
    elif [ -n "$m8_mut_gap" ]; then
      # ★ 종점 announce (F-CR22-1) — 위 rc 대조는 rc **이탈**만 막는다. rc 를 보존한 채
      #   조용히 죽으면(예: `baseline-cmp` emit 자리 `sys.exit(0)`) 축 집합이 통째로 비고
      #   rc=0→0 불변이라 **거짓 KILLED** 가 된다. 실측: 그 mutant 가 `baseline-cmp 6행 → 0행`
      #   으로 KILLED 를 발화하고 전건 PASS=46 FAIL=0 · rc=0 이었다.
      fail_case "M8 (하한 대조 정의역): 무효 kill — mutant 종점 미도달 (exit=$m8_base_rc→$m8_mut_rc, baseline-cmp ${m8_base_n}행→${m8_mut_n}행): $m8_mut_gap. 축 소실을 「정의역 축소」로 귀속할 수 없다"
      sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    elif [ "$m8_mut_axes" != "$m8_base_axes" ] && [ "$m8_mut_n" -lt "$m8_base_n" ]; then
      pass_case "M8 (하한 대조 정의역 LOWER_BOUND_AXES): KILLED (stdout 축 — baseline-cmp ${m8_base_n}행 [$m8_base_axes] → mutant ${m8_mut_n}행 [$m8_mut_axes] · 대조 소실 축 =[$m8_lost] / exit=$m8_base_rc→$m8_mut_rc 실측 불변 · 양 팔 종점 announce 도달 확인 · Traceback base=${m8_base_tb}건 mut=${m8_mut_tb}건)"
    else
      fail_case "M8 (하한 대조 정의역): SURVIVED (baseline ${m8_base_n}행 [$m8_base_axes] == mutant ${m8_mut_n}행 [$m8_mut_axes] — 하한 대조 정의역을 도려내도 관측이 그대로 = 판별력 0)"
    fi
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# T-ANN = 종점 announce 술어 자신의 판별력 대조군 (born-RED 짝 · F-CR22-1)
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 왜 상시 등재하나 (본 Story 계보의 직접 산물). 반복된 형이 「봉합이 자기 대조군을 갖지
#   않아 다음 회차에 조용히 죽는다」 였다. announce 술어는 M1~M8 · IC-4 가 **공유하는 공용
#   술어**라 한 번 무력화되면 전 site 가 동시에 눈이 먼다 — 정확히 F-CR22-1 이 실증한 형이다.
#   그래서 여기서 죽이는 대상은 core 의 어떤 분기가 아니라 **가드 자신의 충분성**이다.
# ★ 대조군 동반 (무조건-true 술어 차단). 위반만 세면 「항상 위반을 반환하는」 술어와
#   구별되지 않으므로, 같은 술어를 무변형 실행에도 적용해 위반 0 을 함께 관측한다.
# ★ 이 3 케이스가 RED 로 뒤집히는 조건 = announce 술어의 정의역이 다시 좁아졌을 때다.
echo ""
echo "── T-ANN: 종점 announce 술어 판별력 (born-RED 대조군) ───────────────────────"

# (a) 대조군 — 무변형 실행은 종점을 발화하므로 위반 0 이어야 한다.
run_core "$CORE_PY" "$REPO_ROOT"
ann_ctl_rc=$CORE_RC
ann_ctl_gap="$(announce_gap "$ann_ctl_rc" "$CORE_OUT" "$CORE_ERR")"
if [ "$ann_ctl_rc" -eq 0 ] && [ -z "$ann_ctl_gap" ]; then
  pass_case "T-ANN-a 대조군: 무변형 실행(exit=$ann_ctl_rc)에 announce 위반 0 — 술어가 무조건-true 가 아님(대조군 성립)"
else
  fail_case "T-ANN-a 대조군: 무변형 실행 exit=$ann_ctl_rc / 위반='$ann_ctl_gap' (기대 exit=0 · 위반 0). 대조군이 서지 않으면 아래 판별력 관측이 무의미"
fi

# (b)(c) 조용한 종료 mutant 2종 — 종전 `Traceback` 단일점 가드는 **둘 다** 통과시켰다.
#   ⓑ rc 보존형(`sys.exit(0)`)은 **rc 집합 pin 으로도 안 걸린다**(0 ∈ 선언 exit_space {0,1,3}).
#     그래서 처방을 rc 집합이 아니라 **종점 도달 양성 증거**로 잡았다 — 이 케이스가 그 차이를
#     상시 실증한다. ⓒ rc 이탈형(`sys.exit(2)`)은 exit_space 밖 축을 덮는다.
#
# ★★ (d) **F-CR25-1 봉합 — 이 배선의 음성 소비자**. (b)(c) 는 둘 다 「gap 이 비지 않았을 것」을
#   요구하는 **양성 소비**뿐이었고, 그래서 **봉합 전에는** 이 배선을 비공백 상수로 치환해도
#   **그대로 통과했다** (`e91f94cb3` 실측: 총계 불변 · RED 0건). 즉 `announce_gap` 이
#   **호출되지 않아도** 라벨은 계속 *"announce 술어가 위반으로 검출 — 가드 충분성 실증"* 을
#   발화했다. 「양성 1 = 자기보호」 분류가 거기서 반증됐다.
#   ★ **시제 주의** — 위는 **봉합 전** 상태 기술이다. (d) 가 붙은 뒤로는 같은 치환이 (d) 에서
#     RED 다. 봉합이 거짓으로 만든 명제를 현재형으로 남기지 않는다(총계 수치는 SHA 앵커로만).
#   ⇒ (d) 는 **무해 변형**(주석 1개 삽입 — 동작 불변)을 넣고 **gap 이 비어 있을 것**을 요구한다.
#     배선이 비공백 상수로 죽으면 (d) 가 RED 다. 이제 이 배선은 **양성 ∧ 음성 공존** = 닫힘:
#     「항상 공백」 변이는 (b)(c) 가, 「항상 비공백」 변이는 (d) 가 잡는다(서로의 맹점).
#   ★ 잔여 천장(알고 안 닫음): 이 **극성 분기(`ann_pol`) 자신에는 대조군이 없다** — 분기 1줄
#     중화는 여전히 신호 0 일 수 있다. 닫은 것은 **배선 층까지**이고 분기 층은 열려 있다.
ANN_TB="Traceback (most recent call last)"
# 항목 형식: <id>:<기대 극성 NONEMPTY|EMPTY>:<exit code | benign>:<설명>
for ann_case in \
  "b:NONEMPTY:0:rc 보존형 — 선언 exit_space 안" \
  "c:NONEMPTY:2:rc 이탈형 — 선언 exit_space 밖" \
  "d:EMPTY:benign:무해 변형 — 종점 정상 도달"; do
  ann_id="${ann_case%%:*}"; ann_rest="${ann_case#*:}"
  ann_pol="${ann_rest%%:*}"; ann_rest="${ann_rest#*:}"
  ann_code="${ann_rest%%:*}"; ann_desc="${ann_rest#*:}"
  if [ "$ann_code" = "benign" ]; then
    # 동작 불변 주석 1개 삽입 — core 는 정상 완주하므로 gap 은 **비어야** 한다.
    ann_sed='s/        _emit(f"census: {a}={census\[a\]}")/&  # ANN-benign-noop/'
    ann_sentinel="ANN-benign-noop"
  else
    ann_sed='s/        _emit(f"census: {a}={census\[a\]}")/        sys.exit(CODE)  # ANN-silent-exit/'
    ann_sed="${ann_sed/CODE/$ann_code}"
    ann_sentinel="ANN-silent-exit"
  fi
  ann_mut="$(mutate_core "T-ANN-$ann_id" "$ann_sed" "$ann_sentinel")"
  if [ -z "$ann_mut" ]; then
    fail_case "T-ANN-$ann_id: NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
    continue
  fi
  run_core "$ann_mut" "$REPO_ROOT"
  ann_rc=$CORE_RC
  ann_tb=$(grep -cF "$ANN_TB" "$CORE_ERR")
  ann_gap="$(announce_gap "$ann_rc" "$CORE_OUT" "$CORE_ERR")"
  if [ "$ann_tb" -ne 0 ]; then
    # 이 mutant 가 Traceback 을 내면 그것은 **종전 가드가 이미 잡는 형**이라, 여기서의 검출을
    # announce 술어의 판별력으로 귀속할 수 없다(축 귀속 붕괴). 대조 자체를 무효로 떨어뜨린다.
    fail_case "T-ANN-$ann_id: 대조 무효 — 조용해야 할 mutant 가 Traceback ${ann_tb}건 (exit=$ann_rc). 검출을 announce 축에 귀속할 수 없다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
  elif [ "$ann_pol" = "EMPTY" ]; then
    # ★ 음성 소비 (F-CR25-1 봉합) — 배선이 **비공백 상수**로 치환되면 여기서 RED 가 난다.
    if [ "$ann_rc" -eq 0 ] && [ -z "$ann_gap" ]; then
      pass_case "T-ANN-$ann_id ($ann_desc): 무해 변형(exit=$ann_rc · Traceback 0건)에 announce 위반 0 — 이 배선이 상수로 치환되지 않았다는 **음성 증거**(양성 (b)(c) 의 맹점을 덮는다)"
    else
      fail_case "T-ANN-$ann_id ($ann_desc): 무해 변형인데 exit=$ann_rc · 위반='$ann_gap' (기대 exit=0 · 위반 0) — 배선이 비공백 상수로 치환됐거나 「무해」 변형이 무해하지 않다"
      sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    fi
  elif [ -n "$ann_gap" ]; then
    pass_case "T-ANN-$ann_id ($ann_desc): 종전 Traceback 가드가 통과시키는 조용한 종료(exit=$ann_rc · Traceback 0건)를 announce 술어가 위반으로 검출 — 가드 충분성 실증"
  else
    fail_case "T-ANN-$ann_id ($ann_desc): announce 술어가 조용한 종료(exit=$ann_rc · Traceback 0건)를 통과시켰다 — 가드 판별력 사망(거짓 KILLED 재유입 경로)"
  fi
done

# ═══════════════════════════════════════════════════════════════════════════════
# T-WIRE = 종점 announce 술어의 **배선(설치)** 대조군 (born-RED 짝 · F-CR23-1)
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 무엇이 틀렸었나 (정직 기재). T-ANN 은 술어 **자신**의 충분성을 양방향으로 닫았다. 그러나
#   그 술어를 각 오라클에 **설치한 배선**에는 대조군이 없었다 — 배선 1줄을 `gap=""` 로 바꿔도
#   전건 초록이 baseline 과 **바이트 단위로 구별되지 않으면서**, 라벨은 계속 「양 팔 종점
#   announce 도달 확인」을 단언했다(F-CR23-1 실증). 본 Story 가 닫으려는 class 가 그것을 닫는
#   봉합 자신의 배선 층에서 재현된 것이다. 정직 천장이 아니라 **미기재 공백**이었다.
#
# ★ 전수 재계수 — **재현 규칙을 정본으로 둔다**(고정 좌표는 정본이 아니다). 배선 site 열거:
#       grep -cE '\$\(announce_gap ' <이 파일>
#   ★★ **출력을 여기에 리터럴로 적지 않는다** (F-CR25-5 ① 봉합). 직전 회차는 바로 이 자리에
#     `→ 12` 를 박았는데, **그 값을 쓴 커밋 자신이 같은 커밋에서 14 로 만들었다**(커밋별 실측:
#     `56f440eee`·`1a8e70b50`·`a82161961` = 12 / `5920122b2`·`e91f94cb3` = 14). 재현 규칙을
#     정본으로 세워놓고 **그 출력을 다시 리터럴로 동결**하면 규칙을 세운 의미가 사라진다.
#     수치가 꼭 필요하면 **SHA 를 동반**한다 — 규칙은 여기, 값은 Story §8.10.1(SHA 앵커).
#   좌표를 열거로 박아두면 다음 삽입에서 통째로 stale 이 된다(F-CR24-3 실측: 주 계열 −19 ·
#   IC-4 계열 −128 로 17건 전건 어긋났고, 그중 하나는 **우연 충돌로 거짓 확증**까지 유발했다).
#   본 회차 삽입만으로도 배선 좌표가 다시 전부 이동했다 — 좌표 갱신은 처방이 아니다.
#
# ★★ 소비 assert 방향 분류 — **정적 독해가 아니라 mutant 실측으로만 부여한다** (F-CR25-1 봉합).
#   직전 회차는 「양성 소비면 자기보호」로 **추론**해 1 site 를 취약 집합에서 뺐고, 그 위에
#   「취약 11」이 섰다. **그 추론이 바로 결함의 기전이었다** — 양성 assert 는 자기-건전하되
#   **자기-보호하지 않는다**(비공백 상수로 치환하면 그대로 통과). 판정 절차는 Story §8.10.1:
#     배선당 `<var>=""`(→ 신호면 **양성** 소비자 존재) 와 `<var>="<적대적 내용일치 비공백>"`
#     (→ 신호면 **음성** 소비자 존재) 를 각각 넣고 **하네스 신호를 실측**. 둘 다 신호 = 닫힘.
#   ★ 적대적 상수가 **load-bearing** 이다 — 일반 비공백 상수를 쓰면 내용 검사형 양성 소비자가
#     반응해 **거짓 「닫힘」**이 나온다(실측 대조군: T-DEP 배선에서 일반 상수 = 신호,
#     적대적 상수 = 신호 0). 아래 (3b) 의 잔여 천장과 같은 뿌리다.
#
# ★ 왜 이 형태인가 — **바닥 형태의 재사용**. 「배선이 있다」를 세는 presence-lint(= 같은 기전의
#   반복)가 아니라, **그 배선이 실제로 거부 문면을 낸 것**을 요구한다.
#
# ★★ 직전 회차의 「회귀 종결 / L5 = 공집합」 결론은 **실행으로 반증됐다** (F-CR24-1). 정정:
#   ① 「양성 assert 만족 ⟹ 배선 생존」 **거짓** — 배선을 **비공백 상수**로 치환하면 배선이 죽은
#      채 T-WIRE-c 가 초록이었다(실측). 양성이 증명하는 것은 「소비 assert 가 발화했다」까지고
#      「announce_gap 이 호출됐다」가 아니다. ⇒ 아래 (3b) conjunct 로 봉합했다.
#   ② 「대조군의 대조군 층은 불요」 **거짓** — `wire_case` conjunct 를 1줄 중화하니 신호 0
#      (`PASS=53 FAIL=0` rc=0)이었다. ⇒ T-WIRE-E 블록으로 그 층을 닫았다.
#   ⇒ **정정된 함의**: 양성 assert 는 **자기-건전**하되 **자기-보호하지 않는다**. 배선을 닫는
#      것은 양성 단독이 아니라 **양성 ∧ 음성 소비자의 공존**이다 — 음성은 「항상 비공백」을,
#      양성은 「항상 공백」을 잡는다(서로의 맹점).
#   ⇒ **「종결」이라는 말을 쓰지 않는다.** 층은 닫을 때마다 한 칸 아래로 이동하며, 아래 층도
#      1줄 중화로 조용히 죽는다(T-WIRE-E 블록 말미에 실측치 기재). 적을 수 있는 것은 「어디까지
#      내려갔는가 + 각 층의 제품-수준 파급」이지 「유한하다」가 아니다.
#
# ★ 이번 회차가 닫는 범위 = 공용 helper 2종의 **4 배선**(`mutation_kill_exit` ·
#   `mutation_kill_stdout` 의 baseline-arm / mutant-arm). 이 둘은 M1·M2·M3-siteA·M3-siteB·M5
#   (exit 축) + M4(stdout 축)을 운반하므로 blast radius 가 가장 크다.
#   나머지 **7 배선**(M7 2 · M8 2 · T-ANN-a 1 · IC-4 2)은 **알고 안 닫았다** — 각 닫는 조건은
#   Story §8 「검증 층 스택」 표에 기재한다(「몰랐다」 상태로 두지 않는다).
#   ★ 그 7 중 하나(T-ANN-a 대조군의 배선)는 직전 회차가 「양방향으로 정직하게 닫힘」이라
#     기술한 T-ANN 자신의 대조군 배선이다 — 칭찬받은 자리가 취약군에 있었다.
echo ""
echo "── T-WIRE: announce 배선(설치) 대조군 (born-RED) ────────────────────────────"

# 조용한 종료 mutant — T-ANN 과 **동일 주입점**(census emit)에 rc 만 달리한다.
#   CODE=0 → rc 보존형(기대 rc 와 동값이라 rc pin 을 통과)  CODE=1 → rc 이탈형(flip 을 위조)
WIRE_SED_TPL='s/        _emit(f"census: {a}={census\[a\]}")/        sys.exit(CODE)  # WIRE-silent-exit/'
WIRE_SED_0="${WIRE_SED_TPL/CODE/0}"
WIRE_SED_1="${WIRE_SED_TPL/CODE/1}"
# (c)(d) 의 mutant 팔은 **의도적으로 도달 불가**다 — baseline 팔 배선만 겨누므로, mutant 팔에
#   닿았다는 것 자체가 baseline 배선 미발화의 신호가 되게 한다(도달 시 NOT_RUN 으로 떨어진다).
WIRE_SED_NOOP='s/^### T-WIRE-never-matches$/### unreachable/'

# wire_case <라벨> <기대 문면> <금지 문면> <helper 출력> <helper rc> <종점판정 문면>
#   conjunct (1) helper rc   = 거부했는가            (음성 — 초록이면 배선 미발화)
#   conjunct (2) 금지 문면   = 초록 문면이 없는가    (음성)
#   conjunct (3a) 기대 문면  = 그 배선이 **발화했을 때만** 나오는 라벨-한정 거부 문면 (양성)
#   conjunct (3b) 종점판정 문면 = 그 거부 사유가 **`announce_gap` 이 산출한 내용**인가 (양성)
#
# ★ (3b) 가 왜 있나 — **F-CR24-1 반례의 직접 봉합**. (3a) 만 있을 때는 배선을 **비공백 상수**로
#   치환해도(`base_gap="HARDCODED-NONEMPTY"`) 소비 assert 가 그대로 발화해 라벨-한정 문면이 나오고
#   케이스가 **초록**이었다(실측: T-WIRE-c ✓ PASS, 배선 사망). 즉 (3a) 는 「소비 assert 가 발화했다」
#   까지만 증명하고 「`announce_gap` 이 호출됐다」는 증명하지 못한다. (3b) 는 거부 사유 문자열이
#   `announce_gap` 의 rc-분기 산출물임을 요구하므로 상수 치환이 이 conjunct 를 만족시키지 못한다.
#   ★ 잔여 천장(알고 안 닫음): 상수가 `announce_gap` 의 문면 자체를 **문자 단위로 복제**하면 여전히
#     통과한다. (3b) 가 좁히는 것은 「아무 비공백 값」이지 「그 함수의 호출」이 아니다 — 기계 pin 0.
#
# ★ 빈 문자열 pin — `want`/`deny`/`want_ann` 중 하나를 `""` 로 중화하면 `grep -qF ""` 가 항상
#   매치해 그 conjunct 가 조용히 사라진다(중화 1줄, 하네스는 전건 초록). 값 자체를 pin 한다.
wire_case() {
  local label="$1" want="$2" deny="$3" out="$4" hrc="$5" want_ann="$6"
  if [ -z "$want" ] || [ -z "$deny" ] || [ -z "$want_ann" ]; then
    fail_case "$label: 무효 — 판정 문면 인자가 비었다(want='$want' deny='$deny' want_ann='$want_ann'). 빈 문자열은 grep -qF 에서 항상 매치해 해당 conjunct 를 소리 없이 제거한다"
    return 1
  fi
  if [ "$hrc" -eq 0 ]; then
    fail_case "$label: helper 가 rc=0 (거부 안 함) — 조용한 종료가 KILL 로 계상됐다 = 배선 미발화"
    printf '%s\n' "$out" | sed 's/^/        helper> /' >&2
    return 1
  fi
  if printf '%s\n' "$out" | grep -qF "$deny"; then
    fail_case "$label: 금지 문면 '$deny' 관측 — 조용한 종료가 초록으로 계상됐다"
    printf '%s\n' "$out" | sed 's/^/        helper> /' >&2
    return 1
  fi
  if ! printf '%s\n' "$out" | grep -qF "$want"; then
    fail_case "$label: 기대 거부 문면 '$want' 부재 — announce 배선이 판정에 도달하지 않았다(gap 값 미소비). 다른 사유로 실패한 것은 배선 발화의 증거가 아니다"
    printf '%s\n' "$out" | sed 's/^/        helper> /' >&2
    return 1
  fi
  if ! printf '%s\n' "$out" | grep -qF "$want_ann"; then
    fail_case "$label: 종점 판정 문면 '$want_ann' 부재 — 거부는 났으나 그 사유가 announce_gap 산출물이 아니다(배선이 상수 등으로 치환됐을 때의 형)"
    printf '%s\n' "$out" | sed 's/^/        helper> /' >&2
    return 1
  fi
  pass_case "$label"
  return 0
}

# ── (a) `mutation_kill_exit` / **mutant-arm** 배선 (삽입 불변 표기) ───────────────────────
#   rc 이탈형 조용한 종료(0→1). 배선이 살아 있으면 「무효 kill — mutant 종점 미도달」,
#   죽으면 `mut_rc != base_rc` 가 성립해 **KILLED** 로 초록이 난다(F-CR23-1 이 실증한 바로 그 형).
wire_out="$(mutation_kill_exit "T-WIRE-a probe" "$WIRE_SED_1" "WIRE-silent-exit" "$REPO_ROOT" 0 2>&1)"; wire_rc=$?
wire_case "T-WIRE-a (mutation_kill_exit / mutant-arm 배선): 조용한 rc-flip 을 무효로 거부" \
  "T-WIRE-a probe: 무효 kill — mutant 종점 미도달" "T-WIRE-a probe: KILLED" "$wire_out" "$wire_rc" \
  "$ANN_MSG_RC1"

# ── (b) `mutation_kill_stdout` / **mutant-arm** 배선 (삽입 불변 표기) ─────────────────────
#   rc 보존형 조용한 종료(0→0). rc pin 을 통과하고 토큰만 사라지므로, 배선이 죽으면
#   `✓ PASS: … KILLED … exit=0→0 실측 불변` 이라는 **거짓 초록**이 정확히 재현된다.
wire_out="$(mutation_kill_stdout "T-WIRE-b probe" "$WIRE_SED_0" "WIRE-silent-exit" "$REPO_ROOT" "census: " 0 2>&1)"; wire_rc=$?
wire_case "T-WIRE-b (mutation_kill_stdout / mutant-arm 배선): rc 보존 조용한 종료를 무효로 거부" \
  "T-WIRE-b probe: 무효 kill — mutant 종점 미도달" "T-WIRE-b probe: KILLED" "$wire_out" "$wire_rc" \
  "$ANN_MSG_RC0"

# ── (c)(d) 두 helper 의 **baseline-arm** 배선 (삽입 불변 표기) ────────────────────────────────
#   baseline 팔은 무변형 core 를 돌므로 정상 실행에서 gap 이 **구조적으로 항상 빈다** — 즉 이
#   배선을 발화시키는 입력이 하네스에 없다. 대조군을 세우려면 대조군 팔 자신이 조용히 죽어야
#   하므로, helper 가 baseline 으로 읽는 `$CORE_PY` 를 조용한 종료 사본으로 **1회성 치환**한다
#   (호출 직후 즉시 원복 — 이후 전 케이스가 무변형 core 로 도는 것이 원복의 관측 증거다).
WIRE_SILENT="$TEST_TMP/wire_silent_core.py"
wire_pre="$(mutate_core "T-WIRE 사전(조용한 종료 core)" "$WIRE_SED_0" "WIRE-silent-exit")"
if [ -z "$wire_pre" ]; then
  fail_case "T-WIRE-c (mutation_kill_exit / baseline-arm 배선): NOT_RUN — 조용한 종료 core 사본 생성 실패"
  fail_case "T-WIRE-d (mutation_kill_stdout / baseline-arm 배선): NOT_RUN — 조용한 종료 core 사본 생성 실패"
else
  mv "$wire_pre" "$WIRE_SILENT"
  wire_saved_core="$CORE_PY"

  CORE_PY="$WIRE_SILENT"
  wire_out="$(mutation_kill_exit "T-WIRE-c probe" "$WIRE_SED_NOOP" "T-WIRE-never-matches" "$REPO_ROOT" 0 2>&1)"; wire_rc=$?
  CORE_PY="$wire_saved_core"
  wire_case "T-WIRE-c (mutation_kill_exit / baseline-arm 배선): 조용히 죽은 대조군을 무효로 거부" \
    "T-WIRE-c probe: 무효 — baseline 종점 미도달" "T-WIRE-c probe: KILLED" "$wire_out" "$wire_rc" \
    "$ANN_MSG_RC0"

  CORE_PY="$WIRE_SILENT"
  wire_out="$(mutation_kill_stdout "T-WIRE-d probe" "$WIRE_SED_NOOP" "T-WIRE-never-matches" "$REPO_ROOT" "census: " 0 2>&1)"; wire_rc=$?
  CORE_PY="$wire_saved_core"
  wire_case "T-WIRE-d (mutation_kill_stdout / baseline-arm 배선): 조용히 죽은 대조군을 무효로 거부" \
    "T-WIRE-d probe: 무효 — baseline 종점 미도달" "T-WIRE-d probe: KILLED" "$wire_out" "$wire_rc" \
    "$ANN_MSG_RC0"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# T-WIRE-E = `wire_case` **자신의 conjunct** 대조군 (born-RED · F-CR24-1)
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 왜 필요한가 (반증된 논법의 자리). 직전 회차는 「대조군의 대조군 층은 불요 = L5 공집합」이라
#   결론했다. **실행으로 반증됐다** — `wire_case` 의 (3a) conjunct 를 `if false` 로 중화하니
#   `PASS=53 FAIL=0 rc=0`, 신호 0 이었다(T-WIRE a~d 전건 초록 유지). 즉 conjunct 자신에게
#   대조군이 없었다. 아래 6 케이스가 그 층을 닫는다.
# ★ 형태 = T-ANN 과 동일한 바닥 형태(**양성 assert + 무조건-거부 대조군**). 각 케이스는 그
#   conjunct 가 **발화했을 때만** 나오는 문면을 요구하므로, conjunct 가 사라지면 즉시 RED 다.
# ★ 비용 = core 실행 0 (합성 문자열만). `wire_case` 는 명령치환 안에서 돌므로 그 안의
#   pass_case/fail_case 는 서브셸에 갇혀 부모 카운터를 오염시키지 않는다.
# ★★ 다음 층(L6)의 상태 — **추정이 아니라 실측**. 이 6 케이스를 소비하는 판정 leg 자신에는
#   대조군이 없고, **각각 1줄 중화로 신호 0** 이다:
#     · `we_run` 의 rc-요구 leg 중화        → 신호 0 (baseline 과 바이트 구별 불가)
#     · `we_run` 의 축귀속(expect) leg 중화 → 신호 0 (**실질 손실**:
#       어떤 사유의 거부든 초록이 되어 「이 conjunct 가 거부를 냈다」는 귀속이 사라진다)
#     · E6 대조군 판정 중화                  → 신호 0
#   ★ **수치를 여기에 동결하지 않는다** (F-CR25-5 ② 봉합) — 종전 문면은 `PASS=62` 를 3회 박았고
#     그 값은 **중간 Unit 스냅샷**이라 최종 커밋에서 재현되지 않았다. load-bearing 한 것은
#     「신호 0」이라는 **성질**이지 총계 숫자가 아니다. SHA 동반 실측치는 Story §8.10.5.
#   ⇒ **닫지 않았고, 「천장」으로 면책하지도 않는다.** 「assert 중화는 천장」이라는 면책을 쓰면
#     그 면책은 **직전 회차의 L5 결함도 똑같이 면책**했을 것이다(그것도 `if` 조건 1줄 중화였다).
#     즉 이 Story 의 어느 회차 findings 도 성립하지 않게 된다 — 그러므로 그 면책 논거를 **기각**한다.
#   ⇒ 층을 하나 더 쌓아도 L7 이 같은 값(1줄 중화)으로 열린다. 따라서 이 축은 **닫힘 선언 대상이
#     아니라 비용-편익 판단 대상**이다. 오늘의 판단 = **폭 축 우선** — 깊이 잔여는 제품 오라클
#     (M1~M8 · IC-4 판별력)을 건드리지 않는 메타 검사인 반면(위 3 실측 모두 M-케이스 전건 무손상),
#     폭 잔여 7 배선은 각각 **제품 오라클의 유효성에 직결**한다(동형 사례가 F-CR23-1 로 이미 실측).
#     ★ 단 그 7 자신에 대한 중화 실측은 **본 회차 미수행** — 구조적 동형에 근거한 판단이다.
echo ""
echo "── T-WIRE-E: wire_case conjunct 자신의 대조군 (born-RED) ─────────────────────"

WE_WANT="WE-want-token"
WE_DENY="WE-deny-token"
WE_ANN="WE-ann-token"
WE_OK="거부함 $WE_WANT 그리고 $WE_ANN"

# id | hrc | helper 출력 | 기대 거부 문면(양성 assert) | 설명
we_run() {
  local id="$1" want="$2" deny="$3" out="$4" hrc="$5" ann="$6" expect="$7" desc="$8"
  local o r
  o="$(wire_case "T-WIRE-E$id probe" "$want" "$deny" "$out" "$hrc" "$ann" 2>&1)"; r=$?
  if [ "$r" -eq 0 ]; then
    fail_case "T-WIRE-E$id ($desc): wire_case 가 통과시켰다 — 해당 conjunct 가 판정에 기여하지 않는다(중화 시 조용히 사라지는 층)"
    printf '%s\n' "$o" | sed 's/^/        wire_case> /' >&2
    return 1
  fi
  if ! printf '%s\n' "$o" | grep -qF "$expect"; then
    fail_case "T-WIRE-E$id ($desc): 거부는 났으나 기대 사유 '$expect' 부재 — 거부를 이 conjunct 에 귀속할 수 없다(다른 conjunct 가 먼저 발화)"
    printf '%s\n' "$o" | sed 's/^/        wire_case> /' >&2
    return 1
  fi
  pass_case "T-WIRE-E$id ($desc): conjunct 가 단독으로 거부를 산출 — 판별력 load-bearing"
  return 0
}

we_run 1 "$WE_WANT" "$WE_DENY" "$WE_OK" 0 "$WE_ANN" \
  "helper 가 rc=0 (거부 안 함)" "conjunct 1 · helper rc"
we_run 2 "$WE_WANT" "$WE_DENY" "$WE_OK $WE_DENY" 1 "$WE_ANN" \
  "금지 문면" "conjunct 2 · 금지 문면"
we_run 3 "$WE_WANT" "$WE_DENY" "다른 사유로 실패 $WE_ANN" 1 "$WE_ANN" \
  "기대 거부 문면" "conjunct 3a · 라벨-한정 기대 문면"
we_run 4 "$WE_WANT" "$WE_DENY" "$WE_WANT 인데 사유가 상수" 1 "$WE_ANN" \
  "종점 판정 문면" "conjunct 3b · announce_gap 산출 사유"
we_run 5 "" "$WE_DENY" "$WE_OK" 1 "$WE_ANN" \
  "판정 문면 인자가 비었다" "빈 문자열 pin · want 중화"

# 대조군 — 세 conjunct 를 모두 만족하는 입력은 반드시 통과해야 한다.
# (없으면 위 5 건은 「항상 거부하는 술어」와 구별되지 않는다 = 무조건-true 검사)
we_ctl_out="$(wire_case "T-WIRE-E6 probe" "$WE_WANT" "$WE_DENY" "$WE_OK" 1 "$WE_ANN" 2>&1)"; we_ctl_rc=$?
if [ "$we_ctl_rc" -eq 0 ] && printf '%s\n' "$we_ctl_out" | grep -qF "✓ PASS: T-WIRE-E6 probe"; then
  pass_case "T-WIRE-E6 대조군: 전 conjunct 만족 입력을 통과 — wire_case 가 무조건-거부 술어가 아님(위 5 건의 관측이 유의미)"
else
  fail_case "T-WIRE-E6 대조군: 전 conjunct 만족 입력을 rc=$we_ctl_rc 로 거부 — 대조군이 서지 않으면 위 5 건은 판별력 관측이 아니다"
  printf '%s\n' "$we_ctl_out" | sed 's/^/        wire_case> /' >&2
fi

# ═══════════════════════════════════════════════════════════════════════════════
# T-MUT = `mutate_core` 변형 성립 가드의 대조군 (born-RED · F-CR24-2)
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 왜 상시 등재하나. 「사전 부재 ∧ 사후 존재」 가드는 오늘 하네스가 쓰는 sentinel 6종이
#   전부 core 에 부재라 **한 번도 행사되지 않는다**. 본 Story 의 기준으로 미행사 = 무대조군이다
#   — 가드가 조용히 사라져도 아무 케이스가 붉어지지 않으면 그것은 봉합이 아니다.
echo ""
echo "── T-MUT: mutate_core 변형 성립 가드 (born-RED) ──────────────────────────────"

# (a) 사전 부재 가드 — sentinel 이 원본에 이미 있고 치환은 0건. 종전 구현은 **무변형 core 를
#     mutant 로 반환**했다(바이트 동일 실증). 이제 거부해야 한다.
tmut_a="$(mutate_core "T-MUT-a probe" 's/T-MUT-never-matches-anchor/x/' "def run")"; tmut_a_rc=$?
if [ -z "$tmut_a" ] && [ "$tmut_a_rc" -ne 0 ]; then
  pass_case "T-MUT-a (사전 부재 가드): 원본에 이미 있는 sentinel('def run') + 치환 0건 을 거부 — 무변형 core 가 mutant 로 반환되지 않음"
else
  fail_case "T-MUT-a (사전 부재 가드): 치환 0건인데 변형본을 반환했다(rc=$tmut_a_rc, path='$tmut_a') — 문면 존재를 치환의 증거로 쓰는 presence-assert 재유입"
fi

# (b) 사후 존재 가드 — sentinel 이 전후 모두 부재(치환 0건). 이 leg 은 종전에도 있었다.
tmut_b="$(mutate_core "T-MUT-b probe" 's/T-MUT-never-matches-anchor/x/' "T-MUT-absent-both-sides")"; tmut_b_rc=$?
if [ -z "$tmut_b" ] && [ "$tmut_b_rc" -ne 0 ]; then
  pass_case "T-MUT-b (사후 존재 가드): 치환 0건 + 마커 미도입 을 거부"
else
  fail_case "T-MUT-b (사후 존재 가드): 치환 0건인데 변형본을 반환했다(rc=$tmut_b_rc, path='$tmut_b')"
fi

# (c) 대조군 — 실제로 치환되고 마커가 새로 생기는 변형은 반드시 통과해야 한다.
#     (없으면 (a)(b) 는 「항상 거부하는 헬퍼」와 구별되지 않는다.)
#     추가로 반환본이 원본과 **바이트 상이**함을 직접 관측한다 — F-CR24-2 의 실증이 `cmp` 동일이었다.
tmut_c="$(mutate_core "T-MUT-c probe" 's/        _emit(f"census: {a}={census\[a\]}")/        pass  # T-MUT-control-marker/' "T-MUT-control-marker")"; tmut_c_rc=$?
if [ -n "$tmut_c" ] && [ "$tmut_c_rc" -eq 0 ] && [ -f "$tmut_c" ] && ! cmp -s "$CORE_PY" "$tmut_c"; then
  pass_case "T-MUT-c 대조군: 실 치환 변형을 통과시키고 반환본이 원본과 바이트 상이 — 헬퍼가 무조건-거부가 아님((a)(b) 관측이 유의미)"
else
  fail_case "T-MUT-c 대조군: 실 치환 변형이 rc=$tmut_c_rc / path='$tmut_c' / 원본과 바이트 동일 여부=$(cmp -s "$CORE_PY" "$tmut_c" 2>/dev/null && echo 동일 || echo 상이) — 대조군이 서지 않으면 (a)(b) 는 판별력 관측이 아니다"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# T-DEP = `[DEP]` 무효-관측 분류의 대조군 (born-RED · F-CR24-4)
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 이 arm 은 하네스 preflight(pyyaml 부재 시 즉시 NOT_RUN)가 도달 불가로 만들어 **한 번도
#   행사되지 않는다**. 미행사 = 무대조군이므로 도달 경로를 직접 만들어 행사한다 —
#   `yaml` 을 import 즉시 실패시키는 스텁을 `PYTHONPATH` 선두에 놓아 core 의 DEP 분기를 태운다.
# ★ (a) 는 「그 조합이 실제로 무효로 분류되는가」를, (b) 는 「무효 분류가 무조건-true 가 아닌가」를
#   본다. (b) 없이 (a) 만 두면 「항상 무효라 답하는 술어」와 구별되지 않는다.
echo ""
echo "── T-DEP: [DEP] 무효-관측 분류 (born-RED) ────────────────────────────────────"

tdep_dir="$TEST_TMP/dep_stub"
mkdir -p "$tdep_dir"
printf 'raise ImportError("T-DEP forced-absent")\n' > "$tdep_dir/yaml.py"
tdep_out="$TEST_TMP/tdep.out"; tdep_err="$TEST_TMP/tdep.err"

# ★★ F-CR25-2 봉합 — (a)(b) 를 **단일 배선의 2 시나리오**로 합친다.
#   종전에는 배선이 2개였고 **각각 단방향 소비자뿐**이었다 (`e91f94cb3` 실측 · **봉합 전** 상태):
#     · (a) 의 배선 = 「gap 이 `판정불가` 를 포함할 것」만 요구 → **양성 단독**. 그 문면을 담은
#       **적대적 상수**로 치환하면 총계 불변 · RED 0건으로 **통과했다**.
#     · (b) 의 배선 = 「gap 이 빌 것」만 요구 → **음성 단독**. 빈 상수로 치환하면 **통과했다**.
#   ★ 그 (a) 판정에는 **적대적 상수가 필수**였다 — 일반 비공백 상수를 쓰면 (a) 의 내용 검사가
#     반응해 신호가 나므로 **거짓 「닫힘」**이 된다(대조군 실측). 「보호됨」은 **적대적 상수로만**
#     부여한다. 후속 회차가 일반 상수로 재측정하면 거짓 닫힘이 되돌아온다.
#   ★ **시제 주의** — 위는 **봉합 전** 상태다. 병합 후에는 같은 치환이 반대 극성 케이스에서 RED 다.
#   이 결함은 「알고 안 닫았다」가 아니라 **모르고 새로 열었다** — 직전 회차가 T-DEP 를 신설하며
#   같은 형을 재생산했고 잔여 목록에 등재하지 않았다. 선언된 천장으로 면책되지 않는다.
#   ⇒ 이제 **같은 배선 1줄**이 stub 시나리오에서 **비공백**(양성)을, 무변형 시나리오에서
#     **공백**(음성)을 요구받는다. 어느 방향 상수 치환도 최소 1 케이스를 RED 로 만든다.
#   ★ 잔여 천장(알고 안 닫음): **극성 분기(`tdep_pol`) 자신에는 대조군이 없다.** 닫은 것은
#     배선 층까지이고 분기 층은 열려 있다 — T-ANN-d 와 동형의 잔여다.
# 항목 형식: <id>:<기대 극성 NONEMPTY|EMPTY>:<모드 stub|none>:<설명>
for tdep_case in \
  "a:NONEMPTY:stub:판정불가 종점 — 의존성 부재" \
  "b:EMPTY:none:무변형 정상 실행"; do
  tdep_id="${tdep_case%%:*}"; tdep_rest="${tdep_case#*:}"
  tdep_pol="${tdep_rest%%:*}"; tdep_rest="${tdep_rest#*:}"
  tdep_mode="${tdep_rest%%:*}"; tdep_desc="${tdep_rest#*:}"
  if [ "$tdep_mode" = "stub" ]; then
    PYTHONPATH="$tdep_dir" "$PY" "$CORE_PY" --repo-root "$REPO_ROOT" > "$tdep_out" 2> "$tdep_err"
  else
    "$PY" "$CORE_PY" --repo-root "$REPO_ROOT" > "$tdep_out" 2> "$tdep_err"
  fi
  tdep_rc=$?
  tdep_dep=$(grep -cF "$ANN_DEP" "$tdep_err")
  tdep_sum=$(grep -cF '::error::[SUMMARY]' "$tdep_err")
  tdep_tb=$(grep -cF "Traceback (most recent call last)" "$tdep_err")
  # ── 단일 배선 (양 극성이 공유 소비) ──
  tdep_gap="$(announce_gap "$tdep_rc" "$tdep_out" "$tdep_err")"
  if [ "$tdep_pol" = "NONEMPTY" ]; then
    # 양성 소비 — 분류 문면이 나와야 통과. 빈 상수 치환은 여기서 RED.
    if [ "$tdep_rc" -eq 1 ] && [ "$tdep_dep" -ge 1 ] && [ "$tdep_sum" -eq 0 ] && [ "$tdep_tb" -eq 0 ] \
       && printf '%s\n' "$tdep_gap" | grep -qF "판정불가"; then
      pass_case "T-DEP-$tdep_id ($tdep_desc): 판정불가 종점(exit=$tdep_rc · [DEP] ${tdep_dep}건 · SUMMARY 0 · Traceback 0)을 무효 관측으로 분류 — 아무 분기도 평가하지 않은 실행이 유효 관측으로 통과하지 않음"
    else
      fail_case "T-DEP-$tdep_id ($tdep_desc): exit=$tdep_rc · [DEP]=$tdep_dep · SUMMARY=$tdep_sum · Traceback=$tdep_tb · gap='$tdep_gap' — 판정불가 종점이 무효로 분류되지 않았거나 도달 경로가 성립하지 않았다"
      sed 's/^/        dep-stderr> /' "$tdep_err" >&2
    fi
  else
    # 음성 소비 (F-CR25-2 봉합) — 무조건-무효 술어 배제 ∧ **비공백 상수 치환 검출**.
    if [ "$tdep_rc" -eq 0 ] && [ "$tdep_tb" -eq 0 ] && [ -z "$tdep_gap" ]; then
      pass_case "T-DEP-$tdep_id 대조군 ($tdep_desc): 무변형 실행(exit=$tdep_rc · Traceback 0건)은 무효 분류 0 — 술어가 무조건-무효가 아니고((a) 관측이 유의미), **같은 배선이 공백을 요구받는 음성 소비 site**"
    else
      fail_case "T-DEP-$tdep_id 대조군 ($tdep_desc): 무변형 실행 exit=$tdep_rc · Traceback=$tdep_tb · gap='$tdep_gap' (기대 exit=0 · Traceback 0 · gap 공백) — 대조군이 서지 않으면 (a) 는 판별력 관측이 아니며, 배선이 비공백 상수로 치환된 형도 여기서 잡힌다"
      sed 's/^/        ctl-stderr> /' "$tdep_err" >&2
    fi
  fi
done

# ═══════════════════════════════════════════════════════════════════════════════
# 7. substrate-failure (exit 3) 조건
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── substrate-failure (exit 3) 조건 ──────────────────────────────────────────"

# ⓵-a 분모 0 — probe 축 제거 (N_probe=0). ★ zero-count 분기 그 자체를 친다.
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_zero_probe.yaml"
reset_mf; MF_PROBE="0"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓵-a 분모 0 (N_probe=0)" 3 "$CORE_RC" "분모 0 축"

# ⓵-b samples[] 비움 — manifest shape 층에서 loud 실패.
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_samples_empty.yaml"
reset_mf; MF_SAMPLES="empty"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓵-b samples[] 비움" 3 "$CORE_RC" "블록 'samples' 이 비어있거나"

# ⓶-a baseline 부재
SH="$(new_shadow none)"; rm -f "$SH/docs/hollow-gate-corpus-baseline.yaml"
MF="$TEST_TMP/mf_nobase.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓶-a baseline 부재" 3 "$CORE_RC" "baseline 부재"

# ⓶-b baseline digest 변조 (수기 편집 검출 — content_digest 결박)
SH="$(new_shadow none)"
sed -i 's/^  N_detected: 2$/  N_detected: 1/' "$SH/docs/hollow-gate-corpus-baseline.yaml"
MF="$TEST_TMP/mf_digest.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓶-b baseline digest 변조(수기 편집)" 3 "$CORE_RC" "content_digest 불일치"

# ⓷ stamp drift — source_sha256 변조
SH="$(new_shadow none)"
sed -i 's/^source_sha256: .*/source_sha256: "0000000000000000000000000000000000000000000000000000000000000000"/' \
  "$SH/tests/fixtures/hollow-gate-corpus/s01/stamp.yaml.sample"
MF="$TEST_TMP/mf_stamp.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓷ stamp drift (source_sha256 변조)" 3 "$CORE_RC" "source_sha256 drift"

# ⓸ bijection orphan — corpus 파일이 samples[] 참조 0
SH="$(new_shadow none)"; echo "orphan" > "$SH/tests/fixtures/hollow-gate-corpus/s01/orphan.txt"
MF="$TEST_TMP/mf_orphan.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓸ bijection orphan" 3 "$CORE_RC" "samples[] 참조 0개"

# ⓹ exec-tree blinding 파손 — fixture 안에 stamp 잠입 (IC-4)
# s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
SH="$(new_shadow none)"
echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s01/clean/stamp_probe_leak.txt"
echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s02/clean/stamp_probe_leak.txt"
MF="$TEST_TMP/mf_blind.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓹ exec-tree blinding 파손 (stamp 잠입)" 3 "$CORE_RC" "exec-tree blinding 파손"

# ⓺ recipe 대상이 samples[] 밖
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_recipe_out.yaml"
reset_mf; MF_RECIPE_TARGET="../s02/gate.py.sample"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓺ recipe target 이 samples[] 밖" 3 "$CORE_RC" "samples[] 밖"

# 추가-a exit_space 빈 리스트 (T-2ⓐ — 조용한 INDETERMINATE 아니라 loud 실패)
SH="$(new_shadow none)"
run_core "$CORE_PY" "$SH" --manifest "$ES_EMPTY"
expect_exit "exit3 추가-a exit_space 빈 리스트 (T-2ⓐ loud)" 3 "$CORE_RC" "T-2ⓐ loud 실패"

# 추가-b 금지키 (denylist 명명 3종) 주입
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_forbidden.yaml"
reset_mf; MF_FORBIDDEN="1"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 추가-b manifest 금지키(waiver)" 3 "$CORE_RC" "금지키 사용"

# ═══════════════════════════════════════════════════════════════════════════════
# 8. T-2 exit_space 3분기
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-2 exit_space ───────────────────────────────────────────────────────────"
# ⓐ 빈 리스트 = exit 3 (위 추가-a 에서 확인 — 여기서는 "조용한 INDETERMINATE 아님"을 추가 확인)
#   ★ 판정 술어 주의: "I-4" 문자열 부재로 검사하면 안 된다 — SUBSTRATE 메시지 본문이 *왜* loud
#   실패시키는지 설명하며 'I-4' 를 인용하기 때문이다(설명 문면 ≠ 라벨 발동). 실제 발동 여부는
#   `::error::[INDETERMINATE]` stage 라벨의 유무로만 읽는다. (이 오판은 최초 실행에서 실측 검출됐다.)
SH="$(new_shadow none)"
run_core "$CORE_PY" "$SH" --manifest "$ES_EMPTY"
if [ "$CORE_RC" -eq 3 ] && grep -qF "::error::[SUBSTRATE]" "$CORE_ERR" \
   && ! grep -qF "::error::[INDETERMINATE]" "$CORE_ERR"; then
  pass_case "T-2ⓐ: 빈 exit_space = loud exit 3 (SUBSTRATE 라벨 · INDETERMINATE 라벨 0 — 조용한 흐름 경로 미형성)"
else
  fail_case "T-2ⓐ: exit=$CORE_RC 또는 INDETERMINATE 라벨 출현 — loud 실패 계약 파손"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
fi

# ⓑ [0,1] 정상 → exit 0 ∧ I-4 미발동
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_es_normal.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
if [ "$CORE_RC" -eq 0 ] && ! grep -qF "::error::[INDETERMINATE]" "$CORE_ERR"; then
  pass_case "T-2ⓑ: exit_space [0,1] → exit 0, I-4 미발동 (day-1 실측 rc kill=1/clean=0/empty=0/xkill=1 전건 포함)"
else
  fail_case "T-2ⓑ: exit=$CORE_RC 또는 I-4 발동 — 정상 exit_space 에서 오검출"
fi

# ⓒ [0] 으로 좁힘 → kill leg rc=1 이 I-4 발동 → exit 1
SH="$(new_shadow none)"
run_core "$CORE_PY" "$SH" --manifest "$ES_NARROW"
expect_exit "T-2ⓒ: exit_space [0] 으로 좁힘 → I-4 발동" 1 "$CORE_RC" "∉ 선언 exit_space"

# ═══════════════════════════════════════════════════════════════════════════════
# 9. T-4 post-day-1 편입 시뮬레이션 — 축 짝짓기가 어긋난 신규 표본은 RED 인가
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-4 post-day-1 편입 (축 어긋난 신규 표본) ────────────────────────────────"
# day-1 이후 새 표본 s03 이 편입되되, kill 자리에 AC-8 축 fixture(xkill)를 앉혀 축 짝짓기를 어긋나게 한다.
# 선언 kill_target_stage 는 AC-1 인데 관측 stage 는 {AC-8, SUMMARY} 이므로 짝이 맞지 않는다.
SH="$(new_shadow s03)"; MF="$TEST_TMP/mf_t4.yaml"
reset_mf; MF_EXTRA="s03"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
if [ "$CORE_RC" -eq 1 ]; then
  pass_case "T-4: 축 어긋난 신규 표본 편입 → exit 1 (RED)"
else
  fail_case "T-4: 축 어긋난 신규 표본이 exit=$CORE_RC — 강제 게이트가 RED 를 내지 않음"
fi
t4_hits=0
grep -qF "unit=s03: I-8 성립" "$CORE_ERR" && t4_hits=$((t4_hits+1))
grep -qF "::error::[XKILL-AXIS] unit=s03" "$CORE_ERR" && t4_hits=$((t4_hits+1))
grep -qF "::error::[VERDICT] unit=s03" "$CORE_ERR" && t4_hits=$((t4_hits+1))
if [ "$t4_hits" -eq 3 ]; then
  pass_case "T-4: 3중 검출 (I-8 강등 + XKILL-AXIS 축 파손 + VERDICT reconcile 불일치)"
else
  fail_case "T-4: 검출 신호 ${t4_hits}/3 — 기대 3중 검출 미달"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
fi
# ★ 정직 천장 (실측 결과에 딸린 잔여): 위 RED 는 **선언 kill_target_stage 와 관측 stage 의 불일치**를
#   잡은 것이지 "새 표본의 kill 축이 그 게이트를 대표하는가"(축 대표성)를 잡은 것이 아니다. 축 대표성은
#   사람 판단이며 bearer 는 문서 규약뿐이다 — 기계 강제 없음. 통과를 만들려고 검사를 약화시키지 않는다.

# ═══════════════════════════════════════════════════════════════════════════════
# 10. T-6 fixture 순도 가드 — 목표 축 + 타 축 동시 발화 시 의도한 착지 확정
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-6 fixture 순도 (오염 fixture 의 의도한 착지) ───────────────────────────"
# 오염 fixture = s04 의 kill 이 목표 축(AC-1)과 타 축(AC-8)을 **동시** 발화 → stages={AC-1,AC-8,SUMMARY}.
#
# ★ 의도한 착지 = **LIVE 허용 (RED 아님)**. 근거를 여기에 기재한다:
#   판정식의 conjunct 는 `kill_target_stage ∈ fail_stage(kill)` 즉 **멤버십**이지 배타성이 아니다
#   (ADR-175 DR4-M1 — 한 leg 이 내는 stage id 개수는 고정이 아니며 상수 footer 와 공존한다).
#   따라서 "목표 축이 실제로 적중했다"는 요구는 그대로 살아있고, 타 축이 함께 울렸다는 사실만으로는
#   RED 로 만들지 않는다. 배타성을 요구하도록 좁히면 day-1 정상 표본(AC-1 + SUMMARY 상수 footer 공존)이
#   즉시 born-RED 가 된다 — 정상 corpus 오판.
#   ⇒ 순도(축이 하나만 울릴 것)는 **기계 강제 대상이 아니고** 표본 제작 규약이 진다. 이 잔여는
#     하네스 docstring 의 game-able residual (a) 축 대표성 = 사람 판단 과 같은 뿌리다.
SH="$(new_shadow s04)"; MF="$TEST_TMP/mf_t6.yaml"
reset_mf; MF_EXTRA="s04"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
s04_stages="$(sed -n 's/^obs-digest: unit=s04 leg=kill .*stages=\(\[[^]]*\]\).*/\1/p' "$CORE_OUT" | head -1)"
if [ "$CORE_RC" -eq 0 ] && [ "$(verdict_of s04)" = "LIVE" ]; then
  pass_case "T-6: 오염 fixture(stages=$s04_stages) → 의도한 착지 LIVE 허용 (멤버십 판정, 배타성 미요구)"
else
  fail_case "T-6: exit=$CORE_RC verdict=$(verdict_of s04) — 문서화한 의도 착지(LIVE 허용)와 불일치"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
fi
if echo "$s04_stages" | grep -qF "AC-1" && echo "$s04_stages" | grep -qF "AC-8"; then
  pass_case "T-6: 오염이 실제로 2축 동시 발화했음을 관측 (stages=$s04_stages — 무의미 fixture 아님)"
else
  fail_case "T-6: stages=$s04_stages — 2축 동시 발화 미관측 (오염 fixture 제작 실패, 검사 전제 파손)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 11. IC-4 exec-tree blinding + exec dir 재배정
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── IC-4 exec-tree blinding / exec dir 재배정 ────────────────────────────────"
# 배경: stamp.yaml.sample 의 source_sha256 == artifact_sha256 여부가 arm 과 1:1 상관이다
#   (s01 참 / s02 거짓). stamp 가 exec dir 로 새면 라벨 역산 채널이 된다 — IC-4 가 그것을 닫는다.
#   exec dir 은 실행 종료 시 삭제되므로, 여기서는 (a) 누설 시 loud 실패하는가 (b) 이름이 매 실행
#   재배정되는가 로 관측한다. exec tree 표면의 직접 assert 는 형제 pytest self-test 가
#   _materialize 를 in-process 로 불러 수행한다 (tests/scripts/test_check_hollow_gate_corpus.py).
for tok in stamp manifest baseline probe; do
  SH="$(new_shadow none)"
  # s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
  echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s01/clean/${tok}_leak.txt"
  echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s02/clean/${tok}_leak.txt"
  MF="$TEST_TMP/mf_blind_${tok}.yaml"; reset_mf; emit_manifest "$MF"
  run_core "$CORE_PY" "$SH" --manifest "$MF"
  if [ "$CORE_RC" -eq 3 ] && grep -qF "금지 토큰 '${tok}'" "$CORE_ERR"; then
    pass_case "IC-4 blinding: exec dir 에 '${tok}' 토큰 누설 → exit 3 (라벨 역산 채널 차단)"
  else
    fail_case "IC-4 blinding: '${tok}' 누설이 exit=$CORE_RC 로 통과 (역산 채널 개방)"
  fi
done

# ── F-CR21-1 전수 분류 산출분: 본 케이스도 **차분 오라클**이다 ────────────────────
#   판정식 `ex1 != ex2` 의 기대값은 리터럴이 아니라 **다른 실행의 관측**이다. 따라서 차분 축이며
#   crash 가드가 필수다. 종전에는 `-n` 공백 가드뿐이라, exec-root 를 emit **한 뒤** 죽는 실행에서
#   두 팔 모두 이름은 남기고 죽어도 `ex1 != ex2` 가 성립해 초록이 났다.
#   실증(본 회차): core 의 `results = {}` 직후에 `{}["IC4-post-emit-crash"]` 를 주입해 emit 이후
#   crash 하게 만든 뒤 실행 → 하네스 전체는 PASS=14 FAIL=31 로 무너지는데 **본 케이스만
#   `✓ PASS: IC-4 재배정 … (hgc-exec-mvk6z1ji → hgc-exec-1t_nq5vg)`** 를 발화했다. 두 팔 다 무효
#   실행인데 재배정을 관측했다고 보고한 것이다.
#   ★ 이 site 는 「mutant 판정 site」 열거에는 안 잡힌다(mutant 가 없다). 차분/절대값 축으로
#     **전 오라클**을 훑어야 드러난다 — 열거 정의역을 mutant site 로 좁힌 것이 F-CR21-1 의 기전이었다.
IC4_TB="Traceback (most recent call last)"
run_wrapper "$REPO_ROOT"
ic4_rc1=$CORE_RC; ic4_tb1=$(grep -cF "$IC4_TB" "$CORE_ERR")
ex1="$(sed -n 's/^exec-root: \([^ ]*\) .*/\1/p' "$CORE_OUT" | head -1)"
# ★ 종점 announce (F-CR22-1) — 위 실증(emit 후 crash)의 조용한 종료판. exec-root 를 emit 한 뒤
#   `sys.exit(0)` 로 죽으면 Traceback 0 · rc=0/0 이라 종전 두 가드를 **모두** 통과하고 이름 차이만
#   남아 초록이 난다. rc=0 이 주장하는 종점(최종 emit) 도달을 양성으로 요구해 그 형을 닫는다.
ic4_gap1="$(announce_gap "$ic4_rc1" "$CORE_OUT" "$CORE_ERR")"
run_wrapper "$REPO_ROOT"
ic4_rc2=$CORE_RC; ic4_tb2=$(grep -cF "$IC4_TB" "$CORE_ERR")
ex2="$(sed -n 's/^exec-root: \([^ ]*\) .*/\1/p' "$CORE_OUT" | head -1)"
ic4_gap2="$(announce_gap "$ic4_rc2" "$CORE_OUT" "$CORE_ERR")"
if [ "$ic4_tb1" -ge 1 ] || [ "$ic4_tb2" -ge 1 ]; then
  fail_case "IC-4 재배정: 무효 — 실행 stderr 에 Traceback (run1=${ic4_tb1}건 run2=${ic4_tb2}건 · exit=$ic4_rc1/$ic4_rc2). 두 팔 중 하나라도 조기 사망하면 이름 차이를 '재배정' 으로 귀속할 수 없다"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
elif [ "$ic4_rc1" -ne 0 ] || [ "$ic4_rc2" -ne 0 ]; then
  # 무변형 corpus 의 정상 종료 exit=0 을 **리터럴 pin** 으로 둔다 (관측 유효성 전제).
  fail_case "IC-4 재배정: 무효 — 무변형 corpus 실행이 exit=$ic4_rc1/$ic4_rc2 (기대 0/0). 실행이 정상 완주하지 않으면 재배정 관측이 성립하지 않는다"
elif [ -n "$ic4_gap1" ] || [ -n "$ic4_gap2" ]; then
  fail_case "IC-4 재배정: 무효 — 종점 미도달 (run1: ${ic4_gap1:-정상} / run2: ${ic4_gap2:-정상}). 두 팔 중 하나라도 종점에 닿지 않으면 이름 차이를 '재배정' 으로 귀속할 수 없다"
elif [ -n "$ex1" ] && [ -n "$ex2" ] && [ "$ex1" != "$ex2" ]; then
  pass_case "IC-4 재배정: exec dir 명이 실행마다 다름 ($ex1 → $ex2 · 양 팔 exit=$ic4_rc1/$ic4_rc2 · 양 팔 종점 announce 도달 확인 · Traceback ${ic4_tb1}/${ic4_tb2}건)"
else
  fail_case "IC-4 재배정: exec dir 명이 고정/미관측 (ex1='$ex1' ex2='$ex2')"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 12. arm-invariance — 라벨을 뒤집어도 verdict 는 불변 (판정기가 classification 을 못 본다)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── arm-invariance (라벨 역산 판정기 falsify) ────────────────────────────────"
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_armflip.yaml"
reset_mf; MF_FLIP="1"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
inv_ok=1
[ "$(verdict_of s01)" = "LIVE" ]   || inv_ok=0
[ "$(verdict_of s02)" = "HOLLOW" ] || inv_ok=0
[ "$(verdict_of p01)" = "HOLLOW" ] || inv_ok=0
if [ "$inv_ok" -eq 1 ]; then
  pass_case "arm-invariance: declared_arm/expected_verdict 를 뒤집어도 verdict 3건 불변 (LIVE/HOLLOW/HOLLOW)"
else
  fail_case "arm-invariance: 라벨 뒤집기가 verdict 를 바꿈 — 판정기가 classification 을 본다(역산 채널)"
fi
if [ "$CORE_RC" -eq 1 ] && [ "$(grep -cF "::error::[VERDICT]" "$CORE_ERR")" -eq 3 ]; then
  pass_case "arm-invariance: 불일치는 reconcile 단계에서만 발생 (VERDICT 3건, exit 1)"
else
  fail_case "arm-invariance: exit=$CORE_RC / VERDICT 건수=$(grep -cF "::error::[VERDICT]" "$CORE_ERR") (기대 exit 1 · 3건)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 13. 정직 천장 문면 — over-claim 어휘 부재 (INV-5)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── 정직 천장 문면 (INV-5) ───────────────────────────────────────────────────"
overclaim_hits=0
for word in "완전 봉인" "universal detection" "class 봉쇄" "근절"; do
  if grep -qF "$word" "$TEST_TMP/t1a.out"; then
    overclaim_hits=$((overclaim_hits+1))
    log "    over-claim 어휘 '$word' 가 하네스 stdout 에 등장"
  fi
done
if [ "$overclaim_hits" -eq 0 ]; then
  pass_case "정직 천장: 하네스 stdout 에 over-claim 어휘 0건"
else
  fail_case "정직 천장: over-claim 어휘 ${overclaim_hits}건 (INV-5 위반)"
fi
if grep -qF "presence ≠ truth" "$TEST_TMP/t1a.out"; then
  pass_case "정직 천장: PASS 발화가 'presence ≠ truth' 천장을 동반"
else
  fail_case "정직 천장: PASS 발화에 천장 문면 부재"
fi

# ─ F-CR18-9 회귀 가드는 §6 M7 로 이설 (F-CR19-1/-2 정정) ───────────────────────
# 종전 이 자리에는 `rc==0` + `exec-root:` 라인 2술어만 보는 케이스가 있었고, 그 라벨이
# "즉시 정리 작동" 을 PASS 로 발화했다. 실측 결과 형제 부재 불변식과 leg 정리를 **둘 다
# 제거한 mutant 가 본 suite 전건 생존**했으므로 그 라벨은 **관측하지 않은 것을 초록으로
# 보고하는 거짓 라벨**이었다. 관측 없는 발화는 무커버리지보다 나쁘다 — 케이스를 삭제하고
# 실제 판별력을 갖는 M7(§6)로 대체했다.

# ═══════════════════════════════════════════════════════════════════════════════
# 13.5. 구성 앵커 — 케이스 집합의 **구성(composition)** 서명 (F-CR29-1 봉합)
# ═══════════════════════════════════════════════════════════════════════════════
# ★ 무엇이 열려 있었나. §14 총량 pin 이 재는 것은 **tally 스칼라 합 하나**뿐이라 총량이
#   보존되는 변경(§0 (4) 축)에는 원리적으로 눈이 없다 — 실측 5종(D2 카운터 본체 1행 ·
#   R1 호출 site 1토큰 relabel · U2 삭제+tally 보정 · U2B net-zero swap · XPOST 스냅샷-후
#   주입)이 **전건 rc=0 · 요약행이 baseline 과 문면 동일**로 통과했다.
#
# ★ 처방의 형태 = **열거 확장이 아니라 앵커 대상의 교체**다.
#   종전 판단 「merge-base 대조는 **상수의 변화**만 보므로 총량 보존형에 **원리적으로 미도달**」은
#   **거짓**이었다(반증 = Story §8.14 실행 측정). merge-base 는 **축**(「지금 ↔ 이전」)이고
#   *그 축 위에서 무엇을 앵커할지는 자유 선택*인데, 종전 판단은 **한 인스턴스(스칼라 상수)의
#   성질을 축 전체의 성질로 일반화**했다. 앵커 대상을 **구성 서명**으로 바꾸면 도달한다.
#   ⇒ 일반 규율: **전칭을 세우기 전에 「내가 고정한 것이 축인가, 축 위의 한 대상인가」를 묻는다.**
#
# ★ 서명 3 성분 — 전부 **선언면**(실행 관측면에 흔적을 남기지 않으면서 케이스 집합의 구성·
#   의미를 정하는 표면). **구조적 class 로 정의**하며 「공격당한 자리」 열거가 아니다:
#     census   — 카운터 **호출 site 수** 3종 (줄머리 `fail_case` / `pass_case` / `skip_case`)
#     helper   — 카운터 **헬퍼 정의 본체** 해시
#     loopdecl — **케이스 생성 반복 항목 선언면** 해시 (`for … in` 헤더행 ∧ 이어지는 인용 항목행).
#                한 표가 아니라 `ann_case`·`tdep_case`·`pair`·`tok`·`word` **전건**이 같은 술어로 덮인다.
#
# ★ **도달범위 = 실측**(구조적 도출 아님 — Story §8.14.2/.3 14-run 배터리). **「도달」을 한
#   덩어리로 적지 않는다** — rc(병합 차단)와 stdout(리뷰 가시성)은 서로 다른 관측면이고, 둘을
#   뭉쳐 적는 것이 정확히 이 Story 의 지배 class(**재는 것 < 주장하는 것**)의 재발이다:
#     ⓐ **rc-도달**(rc=1 로 차단) : R1(호출 site 1토큰) · U2(삭제+tally 보정) · U2B(net-zero
#        swap) · XPOST(스냅샷-후 주입) · N5(loop 항목 파라미터 1문자)
#     ⓑ **stdout-도달 · rc 미도달** : **D2**(카운터 **정의 본체** 1행). 본 앵커는 `✗ FAIL:` 문면을
#        정확히 발화하지만 **그 발화가 지나는 카운터 자신이 D2 의 표적**이라 `FAIL` 이 0 으로
#        계상되고 **rc=0** 이다(실측 `PASS=67 FAIL=0 SKIP=1`, ✗ 1줄). ⇒ D2 에 대해 본 앵커가
#        주는 것은 **stdout 가시성**이지 병합 차단이 **아니다**. 「D2 도달」로 적으면 거짓이다.
#     ⓒ **미도달 2종** :
#        · **N4** — assert 술어의 **리터럴 본문** 교체. 그 축은 「선언면」이 아니라 「단언
#          내용」이라 본 서명 class **밖**이다.
#        · **XINL — census 보상형**(12회차 실측 신규). 실패 site 를 인라인 전개해 `fail_case`
#          호출을 1 줄이고 **도달 불가 블록**(`if false; then … fi`)에 `fail_case` 1 줄을 넣어
#          census 를 되돌린다 ⇒ 서명 3 성분 전건 불변 · rc=0. **census 는 호출 site 의 「존재」를
#          셀 뿐 「도달 가능성」을 보지 않는다** — 정적 선언면 계수의 구조적 한계이고 얼굴을
#          하나 더 열거해서 닫히지 않는다. 닫혔다고 적지 않는다.
#     거짓 양성 **0** : D1(실결함 단독 주입)은 본 앵커를 **통과**한다 — 「무엇이든 RED」인 항진
#             오라클이 아니라 **대조군이 붙은 판별**이다.
#
# ★ **정직 천장 — 본 블록이 하지 않는 것**(전건 실측·선언):
#   ⓐ RED 를 내는 것은 **선언 정합 leg** 이다. 저자가 구성을 바꾸면서 §0 선언을 **함께** 갱신하면
#      초록이다. 얻은 것은 「1-편집 무성 우회 → **2-편집 + 의미 있는 선언 diff**」이고 **봉인이
#      아니다**. 값은 「구성이 움직였다」가 **diff 한 줄로 드러남**이다.
#   ⓑ baseline leg 의 기준점(merge-base)은 **저자가 쓸 수 없는** 유일 성분이지만, **본 파일은
#      merge-base 에도 origin/main 에도 부재**(신규 도입)라 **본 PR 에서는 구조적으로 무발화**다.
#      유효 시점 = 본 파일이 main 에 착지한 **다음 PR 부터**. 그래서 미판정을 `pass` 가 아니라
#      **`⊘ SKIP`** 으로 낸다 — 관측하지 않은 것을 초록으로 계상하지 않는다.
#   ⓒ **본 블록 자신의 발화가 본 블록 자신의 카운터를 지난다** — 카운터 본체 무력화(D2)는 본
#      블록의 `✗ FAIL:` 을 **찍기는 하지만** 그 ✗ 가 `FAIL` 에 계상되지 않아 rc=0 이다. 즉 본
#      블록은 **자기 발화 경로를 자기가 보호하지 못한다**(대조군 D2 실측). 「닫혔다」고 적지 않는다.
echo ""
echo "── 구성 앵커 (케이스 집합 구성 서명) ────────────────────────────────────────"

hgc_md5() { "$PY" -c 'import sys,hashlib;print(hashlib.md5(sys.stdin.buffer.read()).hexdigest()[:12])'; }
hgc_composition_signature() {
  _hcs_src="$1"
  _hcs_f=$(awk '/^[[:space:]]*fail_case /{n++} END{print n+0}' "$_hcs_src")
  _hcs_p=$(awk '/^[[:space:]]*pass_case /{n++} END{print n+0}' "$_hcs_src")
  _hcs_s=$(awk '/^[[:space:]]*skip_case /{n++} END{print n+0}' "$_hcs_src")
  _hcs_h=$(sed -n '/^pass_case() {/,/^skip_case() {/p' "$_hcs_src" | hgc_md5)
  # loopdecl = `for X in` 헤더부터 `; do` 까지의 **항목 선언 블록 전체**(다중행 이어쓰기 포함).
  #   ★ 줄 단위 정규식(이어쓰기 백슬래시 매칭)을 쓰지 않는다 — 12회차 실측에서 그 술어가
  #     **헤더만 잡고 항목행을 놓쳤다**(정확히 N5 가 노리는 줄). 블록 술어가 정의상 전수다.
  _hcs_l=$(awk '/^[[:space:]]*for [a-z_]+ in /{inloop=1} inloop{print; if ($0 ~ /;[[:space:]]*do[[:space:]]*$/) inloop=0}' "$_hcs_src" | hgc_md5)
  printf 'census=%s/%s/%s helper=%s loopdecl=%s' "$_hcs_f" "$_hcs_p" "$_hcs_s" "$_hcs_h" "$_hcs_l"
}

hgc_self_src="${BASH_SOURCE[0]}"
hgc_self_rel="tests/scripts/$(basename -- "$hgc_self_src")"
hgc_cur_sig="$(hgc_composition_signature "$hgc_self_src")"

if [ "$hgc_cur_sig" = "$HGC_DECLARED_COMPOSITION" ]; then
  pass_case "구성 앵커(선언 정합): 실측 구성 서명 = §0 선언 [$hgc_cur_sig] — 총량 보존형 구성 변경(카운터 본체 · 호출 site relabel · tally 보정 · net-zero swap · 스냅샷-후 주입 · loop 항목 파라미터)은 본 서명을 움직이므로 선언 미갱신이면 본 검사가 발화한다. ★ 천장 3종(전건 실측 — 봉인 아님): ⓐ 선언을 **함께** 갱신하는 2-편집은 통과한다(얻은 것은 「구성 이동이 diff 한 줄로 드러남」) ⓑ **카운터 정의 본체 1행(D2)에는 rc 가 따라오지 않는다** — 본 검사의 RED 를 세는 카운터가 바로 그 편집의 표적이라 FAIL 이 0 으로 계상되고 rc=0 이다. D2 에 대해 본 검사가 주는 것은 **stdout 가시성**뿐이다 ⓒ assert 술어 리터럴 교체(N4)와 **도달불가 보상행으로 census 를 되돌리는 형(XINL)**은 **미도달** — census 는 호출 site 의 존재를 셀 뿐 도달 가능성을 보지 않는다"
else
  fail_case "구성 앵커(선언 정합): 실측 [$hgc_cur_sig] ≠ §0 HGC_DECLARED_COMPOSITION [$HGC_DECLARED_COMPOSITION] — 케이스 집합의 **구성**이 바뀌었는데 선언이 갱신되지 않았다(총량은 보존됐을 수 있다). 의도적 변경이면 §0 선언을 실측 서명으로 갱신하라"
fi

# baseline leg — 기준점을 **저자가 쓸 수 없는 리비전**(merge-base)에 둔다.
#   ★ F-1 계열 조용실패 방지: `git -C` 를 명시하고(다른 CWD 로의 fall-through 차단),
#     최상위 일치를 확인하고, `cat-file -e` rc 와 `show` 산출 **비어있지 않음**을 각각 검사한다.
#   ★ 최상위 판정에 `--show-toplevel` 문자열 대조를 쓰지 않는다 — Windows Git Bash 는
#     `C:/Users/…` 를 돌려주고 셸 `pwd` 는 `/c/Users/…` 를 돌려줘 **실 worktree 에서도 항상
#     불일치**한다(12회차 실측 — 첫 구현이 정확히 이 이유로 조용히 NOT_APPLICABLE 로 떨어졌다).
#     경로 표기에 의존하지 않는 `--show-prefix == ""` 로 판정한다.
hgc_mb=""
hgc_mb_state="git 부재 또는 REPO_ROOT 가 work tree 최상위 아님"
if [ "$(git -C "$REPO_ROOT" rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ] \
   && [ -z "$(git -C "$REPO_ROOT" rev-parse --show-prefix 2>/dev/null)" ]; then
  hgc_mb="$(git -C "$REPO_ROOT" merge-base --end-of-options origin/main HEAD 2>/dev/null)"
  [ -n "$hgc_mb" ] || hgc_mb="$(git -C "$REPO_ROOT" merge-base --end-of-options main HEAD 2>/dev/null)"
  if [ -z "$hgc_mb" ]; then
    hgc_mb_state="merge-base 미취득 (base ref 부재 또는 shallow clone)"
  elif git -C "$REPO_ROOT" cat-file -e "$hgc_mb:$hgc_self_rel" 2>/dev/null; then
    hgc_mb_state="취득"
  else
    hgc_mb_state="merge-base 시점 본 파일 부재 (신규 도입)"
  fi
fi

if [ "$hgc_mb_state" = "취득" ]; then
  git -C "$REPO_ROOT" show --end-of-options "$hgc_mb:$hgc_self_rel" > "$TEST_TMP/hgc-base-self.sh" 2>/dev/null
  if [ ! -s "$TEST_TMP/hgc-base-self.sh" ]; then
    fail_case "구성 앵커(baseline): cat-file -e 는 성공했는데 show 산출이 비었다 — 조용실패(NOT_RUN)를 초록으로 내지 않는다"
  else
    hgc_base_sig="$(hgc_composition_signature "$TEST_TMP/hgc-base-self.sh")"
    hgc_base_decl="$(sed -n 's/^HGC_DECLARED_COMPOSITION="\(.*\)"$/\1/p' "$TEST_TMP/hgc-base-self.sh")"
    if [ "$hgc_base_sig" = "$hgc_cur_sig" ]; then
      pass_case "구성 앵커(baseline): merge-base ${hgc_mb:0:12} 대비 구성 **무이동** [$hgc_cur_sig]"
    elif [ -n "$hgc_base_decl" ] && [ "$hgc_base_decl" = "$HGC_DECLARED_COMPOSITION" ]; then
      fail_case "구성 앵커(baseline): 구성이 merge-base ${hgc_mb:0:12} 대비 이동했는데 [$hgc_base_sig → $hgc_cur_sig] §0 선언은 merge-base 와 **동일**하다 — 저자가 쓸 수 없는 기준점 대비 이동이 선언에 반영되지 않았다"
    else
      pass_case "구성 앵커(baseline): 구성이 merge-base ${hgc_mb:0:12} 대비 이동 [$hgc_base_sig → $hgc_cur_sig] 하고 §0 선언도 함께 이동했다 — 의도적 변경으로 계상한다. ★ 본 leg 의 값은 RED 가 아니라 **저자가 쓸 수 없는 기준점 대비 「이동했다」는 고지** 자체다"
    fi
  fi
else
  skip_case "구성 앵커(baseline): **본 실행에서 판정하지 않았다**(NOT_APPLICABLE — 사유 = ${hgc_mb_state}). 관측을 수행하지 않았으므로 커버리지로 읽지 말 것. 본 실행에서 구성 변경에 RED 를 내는 것은 위 **선언 정합 leg 하나**다"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 14. 케이스 총량 pin — 케이스가 tally 에서 조용히 사라지지 않는다 (F-CR26-5 / F-CR25-7)
# ═══════════════════════════════════════════════════════════════════════════════
# 기대치의 사유·공격면 **하한 열거**·정직 천장은 §0 `HGC_EXPECTED_CASE_TOTAL` 정의 주석이 SSOT.
# ★ 본 케이스는 **자기 자신을 세지 않는다** — 발화 시점 tally 는 pin 이전 값이라 기대치가
#   `총량 − 1` 이고, pin 발화 후 총계가 `총량` 이 되어 §15 종료 가드가 그것을 다시 잰다.
#   이 어긋난 두 시점 덕에 **두 소비자 중 한쪽만 지우면** 다른 쪽 산술이 어긋난다(X3·X4).
#   ★ 단 그 성질은 다음 **둘 다**에 한정된다 — 하나라도 깨지면 조용해진다:
#     ⓐ **공유 앵커(리터럴)를 건드리지 않는** 편집 (리터럴을 함께 갱신하면 두 소비자가 정합
#        이동한다 — F-CR27-1 / M-B).
#     ⓑ **총량을 움직이는** 편집 (총량 보존형은 두 소비자의 산술이 **양쪽 다 맞아떨어져** 애초에
#        어긋날 것이 없다 — §0 (4) tally 누산기 축. 이쪽은 상수 접촉조차 필요 없다).
echo ""
echo "── 케이스 총량 pin (은닉 소실 검출) ─────────────────────────────────────────"
hgc_cases_before_pin=$((PASS+FAIL+SKIP))
if [ "$hgc_cases_before_pin" -eq $((HGC_EXPECTED_CASE_TOTAL-1)) ]; then
  pass_case "케이스 총량 pin: 등재 케이스 ${hgc_cases_before_pin}건 = 선언 총량 ${HGC_EXPECTED_CASE_TOTAL} 기준 기대치 $((HGC_EXPECTED_CASE_TOTAL-1))건 — 본 검사가 재는 것은 tally 스칼라 합 하나뿐이고, 그것도 **본 검사 발화 시점의 값**이다: 본 검사 이후 구간은 §15 종료 가드의 **라이브 tally** 가 덮는다(F-CR29-2 봉합 — 종전 문면 「총량이 움직이는 증감에 한해 상수 diff 를 강제한다」는 스냅샷-후 주입 XPOST 에서 **거짓**이었다). 총량 보존형 변경(구성 치환·tally 보정·카운터 재분류·카운터 본체 편집)은 상수 접촉 0 으로 **본 검사를 통과**하며, 그쪽은 §13.5 **구성 앵커**가 잡는다 — §0 공격면 (4) 참조, 그 열거도 하한이다"
else
  fail_case "케이스 총량 pin: 등재 케이스 ${hgc_cases_before_pin}건 ≠ 선언 총량 ${HGC_EXPECTED_CASE_TOTAL} 기준 기대치 $((HGC_EXPECTED_CASE_TOTAL-1))건 — 케이스가 tally 에서 조용히 사라졌거나(loop 항목 삭제·조기 continue·블록 제거) 신설분이 기대치에 미반영이다. 의도적 증감이면 §0 HGC_EXPECTED_CASE_TOTAL 을 함께 갱신하라"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 15. 요약
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "  test_check-hollow-gate-corpus: PASS=$PASS FAIL=$FAIL SKIP=$SKIP"
echo "  천장: 등재 표본에 대한 관측 기반 판별력까지 — corpus 밖 게이트 일반으로 외삽하지 않는다."
echo "        presence ≠ truth (검출 sufficiency = undecidable)."
echo "════════════════════════════════════════════════════════════════════════════"

# ── 종료 가드 = §14 pin 의 **짝 소비자** (공유 앵커 = §0 리터럴) ────────────────────
# ★ 「상호 보호」의 정의역 (둘 다 필요 — §0 정직 천장 SSOT):
#   ⓐ 공유 리터럴을 건드리지 않는 편집일 것 (F-CR27-1 / M-B 가 ⓐ 를 깬다)
#   ⓑ 총량을 움직이는 편집일 것 (§0 (4) tally 누산기 축이 ⓑ 를 깬다 — 상수 접촉 0)
# ★ 본 가드가 읽는 것도 §14 와 **같은 스칼라 합**이다. 두 소비자가 같은 축을 두 시점에서 잴 뿐이라
#   **구성(composition) 변화에는 둘 다 눈이 없다** — 소비자를 늘려도 이 맹점은 줄지 않는다.
# pin 블록 자신이 삭제되면 총계가 기대치에 미달하고 여기서 rc=1 이 난다(FAIL 은 0 이지만
# 초록을 내지 않는다 — 「케이스가 줄었는데 남은 것이 전부 통과」를 성공으로 계상하지 않는다).
# ★ F-CR29-2 봉합 — **스냅샷 제거**. 종전에는 여기서 `hgc_cases_final=$((PASS+FAIL+SKIP))` 를
#   한 번 떠서 고지행·종료 조건 **두 소비자가 그 스냅샷**을 읽었다. 그래서 스냅샷 **이후**에
#   케이스를 주입하면 총계가 실제로 움직였는데도(`✓` 67줄) 요약행·가드가 **66 으로 과소보고**하고
#   rc=0 이었다(XPOST). 대조군 XPIN(스냅샷 **이전** 주입)은 정확히 rc=1 이었으므로 판별축은
#   「주입 일반」이 아니라 **스냅샷 상대 위치**였다. ⇒ 열거 확장이 아니라 **창 자체를 없앤다** —
#   두 소비자가 각자 **판정 시점 라이브 tally** 를 읽는다.
#   ★ 정직 천장 — **창은 0 이 되지 않는다**. 남는 것은 두 자리다:
#     · 요약행 `echo` 와 아래 판정 사이 → 요약행 수치는 과소보고될 수 있으나 **rc=1 이 난다**.
#     · 아래 판정과 `exit` 사이 한 자리 → 순차 프로그램에 내재. 「창 제거」가 아니라 **「N 줄 →
#       2 자리로 축소」**가 정확한 서술이다.
if [ "$((PASS+FAIL+SKIP))" -ne "$HGC_EXPECTED_CASE_TOTAL" ]; then
  echo "  ✗ 종료 가드: 케이스 총계 $((PASS+FAIL+SKIP)) ≠ 기대 ${HGC_EXPECTED_CASE_TOTAL} — 총량 pin 자신이 제거됐거나 케이스 집합이 변했다 (초록 금지)"
fi

if [ "$FAIL" -eq 0 ] && [ "$PASS" -gt 0 ] && [ "$((PASS+FAIL+SKIP))" -eq "$HGC_EXPECTED_CASE_TOTAL" ]; then
  exit 0
else
  # PASS=0 도 실패다 — 아무 케이스도 돌지 않은 vacuous green 을 초록으로 내지 않는다.
  exit 1
fi
