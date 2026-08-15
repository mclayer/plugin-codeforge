#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_output_hardening.py
#   — 보안테스트 lane 구현 원인 2건(F-SEC-3 · F-SEC-4)의 회귀 오라클
#
# 대상 SUT: scripts/lib/scheduled_task_reconcile.py (산출 계층)
#
# ── F-SEC-3: argparse 오류 경로의 종료 신호 소실 ──────────────────────────────────
#   실측(보안 lane): `--nonexistent-flag` · `--channel`(값 누락) → **rc=0 + stdout 빈
#   문자열**. INV-F 가 rc 를 오라클에서 배제했으므로 DONE 마커가 **유일 오라클**인데
#   그것이 사라져, 호출자가 "관측 0건" 과 "인자 오류로 미기동" 을 분별할 수 없었다.
#   ⇒ 계약: **모든 종료 경로가 DONE 줄 정확히 1개**. rc 는 0 유지(INV-F 무손상).
#
# ── F-SEC-4: 채널 본문 마크다운 메타문자 미무해화 (방어심층) ──────────────────────
#   실측(보안 lane): `` `rm -rf ~` `` · `@mclayer` · `](evil.example)` 가 본문에 원문
#   그대로 착지했고 `@name` 은 **실 알림**, `#NNNN` 은 **역참조 백링크**를 만들었다.
#   ⇒ 계약: 산출 필드(`_safe_text` 통과분)에 **활성 마크다운 구성자 0**.
#
#   ★ 도달성 정직 표기 (과장 금지 — 보안 lane 판정 그대로):
#     현 입력원은 `~/.claude/worktrees/<repo>` 1-level listdir(= repo 명)과 로컬 temp
#     슬러그뿐이라 **원격 공격자 통제 불가**다. HOME 쓰기 권한자만 심을 수 있고 그는
#     이미 동일 신뢰도메인이다. 지금은 **방어심층**이며, 향후 branch 명(depth 2)·PR
#     제목 등 덜 신뢰되는 이름원이 유입되면 즉시 live 가 된다.
#
#   ★ 정의역 제약 (미측정 축 — "전부 막았다" 금지):
#     Windows 는 `*` `:` `<` `>` `|` 를 파일명에서 거부하므로 **그 문자군을 실 파일명으로
#     심는 경로는 이 호스트에서 미측정**이다. POSIX consumer 에서는 전부 합법이라 실
#     표면이 더 넓다. 그래서 아래 오라클은 파일시스템을 거치지 않고 **문자열 축**에서
#     직접 단언한다(정의역을 OS 제약에 종속시키지 않는다).
#
#   ★ 무해화의 상한 (선언된 잔여 — 이 파일이 주장하지 않는 것):
#     · `~`(strikethrough `~~`) · `|`(표 셀) 은 **이스케이프하지 않는다**. 전자는 홈-상대
#       표기의 가독성이 load-bearing 이고(`~/.claude/...`) 짝(`~~`)이 있어야 발동하며,
#       후자는 본문에 구분행이 없어 표가 성립하지 않는다. 둘 다 **표시 축 cosmetic** 이라
#       링크·코드·HTML·알림·역참조와 등급이 다르다.
#     · 렌더러가 실제로 어떻게 그리는지는 여기서 **단정하지 않는다**(ADR-119 — 외부
#       렌더러 동작은 출처 없는 단정 금지). 재는 것은 **우리 산출 문자열의 형상**뿐이다:
#       활성 구성자를 남기지 않았는가. 이것은 렌더러 무관하게 참·거짓이 갈린다.

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

import scheduled_task_reconcile as sut                                # noqa: E402

CLI_PATH = REPO_ROOT / "scripts" / "lib" / "scheduled_task_reconcile.py"

# stdout 종료 마커 (형제 파일 `test_scheduled_task_dispatch_path.py` 와 동일 형상)
_DONE_RE = re.compile(
    r"^\[scheduled-task\] DONE: observed=(\d+) new=(\d+) posted=(\d+) halted=(\d+)$"
)


# ══════════════════════════ 실행 헬퍼 (사설 격리) ═══════════════════════════════
def _run_cli(args, tmp_path, extra_env=None, timeout=120):
    """CLI 를 **사설 tmp** 상태로 격리해 subprocess 실행.

    ★ 격리 (규율 5): heartbeat 는 tmp 로 돌리고 채널 env 는 제거한다 — 실 사용자
      `~/.claude/worktree-gc-state/` 및 실 GitHub 에 절대 닿지 않는다. argparse 오류
      경로는 그 이전에 종료하지만, 대조군(F1 정지)까지 같은 격리를 공유해야 대조가
      같은 조건에서 성립한다.
    """
    env = dict(os.environ)
    env["SCHEDULED_TASK_HEARTBEAT_FILE"] = str(tmp_path / "hb.epoch")
    for leak in ("SCHEDULED_TASK_CHANNEL", "SCHEDULED_TASK_NAME", "SCHEDULED_TASK_RUN_ID"):
        env.pop(leak, None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI_PATH)] + list(args),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=timeout, cwd=str(tmp_path),
    )


def _done_lines(stdout):
    return [ln.strip() for ln in (stdout or "").splitlines()
            if _DONE_RE.match(ln.strip())]


def _halted_repo(tmp_path):
    """F1 정지 플래그를 심은 repo 루트 — 스캐너 미호출 대조군(빠르고 부수효과 0)."""
    root = tmp_path / "repo"
    (root / ".codeforge").mkdir(parents=True, exist_ok=True)
    (root / ".codeforge" / "post-merge-automation.disabled").write_text(
        "", encoding="utf-8", newline="\n")
    return root


# ═════════════ F-SEC-3: 모든 종료 경로가 DONE 줄 1개 ═══════════════════════════
class TestArgparseErrorPathKeepsDoneMarker:
    """F-SEC-3 — argparse 오류 경로에서 **유일 오라클**이 사라지지 않는다.

    ★ 왜 이것이 결함인가: 모듈 헤더 INV-F 는 exit code 를 성공/실패 신호로 **쓰지
      않겠다**고 선언했다. 그 선언의 대가로 관측 가능한 종료 신호가 DONE 줄 하나로
      좁혀졌는데, 그 하나가 argparse 오류 경로에서 통째로 사라졌다 —
      rc=0 ∧ stdout="" 은 "정상 완주, 관측 0건" 과 **구별 불가**다.
      (완화: 그 경로는 heartbeat 도 미기록이라 watchdog 이 결국 발화한다. 구조적
       무음은 아니지만, 즉시 신호가 사라진 것은 사실이다.)

    mutant kill: `main()` 의 SystemExit 분기에서 `_emit_done(0, 0, 0, 0)` 제거
      ⇒ leg A·B·D RED (대조군 leg C 는 GREEN 유지 — "무조건 DONE" 구현이 아님).
    """

    ARG_ERROR_CASES = (
        ("미정의 플래그", ["--nonexistent-flag"]),
        ("값 누락 (--channel)", ["--channel"]),
        ("값 누락 (--task-name)", ["--task-name"]),
    )

    def test_argparse_error_paths_emit_exactly_one_done_line(self, tmp_path):
        """leg A·B: 인자 오류 → rc 0 ∧ DONE 줄 정확히 1개.

        ★ 비공허 앵커 2겹:
          ① 정의역 non-empty — 케이스 목록이 비어 있지 않음을 먼저 단언한다
             (규율 3: 부정 단언의 공허 통과 차단).
          ② argparse 경로 도달 증거 — stderr 에 **prog 이름**이 실린다. 이 앵커가
             없으면 "인자를 아예 안 봤다" 와 구별되지 않는다. `usage:` 문면 대신
             prog 이름을 쓰는 이유는 argparse 문면이 로캘 의존이기 때문이다.
        """
        assert len(self.ARG_ERROR_CASES) >= 2, "정의역 붕괴: 인자 오류 케이스가 없다"

        for label, argv in self.ARG_ERROR_CASES:
            cp = _run_cli(argv, tmp_path)
            dones = _done_lines(cp.stdout)

            assert cp.returncode == 0, (
                f"[{label}] INV-F 위반: rc={cp.returncode} (advisory 계약은 항상 0)"
            )
            assert len(dones) == 1, (
                f"[{label}] DONE 줄 {len(dones)}개 (1개 기대) — 유일 오라클 소실. "
                f"stdout={cp.stdout!r} stderr={cp.stderr[:200]!r}"
            )
            m = _DONE_RE.match(dones[0])
            assert m is not None, f"[{label}] DONE 줄 형식 불일치: {dones[0]!r}"
            assert m.groups() == ("0", "0", "0", "0"), (
                f"[{label}] 인자 오류 경로가 관측·발화를 계상했다: {dones[0]!r}"
            )
            assert "scheduled_task_reconcile.py" in (cp.stderr or ""), (
                f"[{label}] argparse usage 경로 도달 근거 부재 — 다른 경로로 빠졌을 수 "
                f"있다: stderr={cp.stderr[:200]!r}"
            )

    def test_help_path_also_emits_done_line(self, tmp_path):
        """leg D: `--help`(SystemExit(0)) 도 같은 줄을 낸다 — 불변식이 조건부가 아니다."""
        cp = _run_cli(["--help"], tmp_path)
        assert cp.returncode == 0, f"rc={cp.returncode}"
        assert "usage" in (cp.stdout or "").lower() or "usage" in (cp.stderr or "").lower(), (
            f"전제 붕괴: --help 인데 usage 산출이 없다 (다른 경로): {cp.stdout[:200]!r}"
        )
        assert len(_done_lines(cp.stdout)) == 1, (
            f"--help 경로 DONE 줄 부재 — 종료 신호 계약이 조건부가 됐다: {cp.stdout!r}"
        )

    def test_control_halted_path_emits_distinct_done_line(self, tmp_path):
        """leg C (**대조군**): 정지 경로는 `halted=1` 인 **다른** DONE 을 낸다.

        두 역할:
          · 하네스 생존 앵커 — DONE 탐지 정규식·subprocess 배관이 실제로 줄을 본다.
          · 판별력 앵커 — 인자 오류 경로의 `halted=0` 과 값이 **갈린다**. 즉 leg A 의
            GREEN 이 "무조건 같은 줄을 찍는 구현" 으로는 설명되지 않는다.
        """
        repo = _halted_repo(tmp_path)
        cp = _run_cli(["--repo-root", str(repo)], tmp_path)

        assert cp.returncode == 0, f"rc={cp.returncode}"
        dones = _done_lines(cp.stdout)
        assert len(dones) == 1, f"정지 경로 DONE 줄 {len(dones)}개: {cp.stdout!r}"
        assert _DONE_RE.match(dones[0]).groups() == ("0", "0", "0", "1"), (
            f"정지 경로 DONE 값 불일치(대조 붕괴): {dones[0]!r}"
        )

    def test_in_process_argparse_error_emits_done(self, capsys):
        """leg A': 같은 성질을 **in-process** 로 결정론 재확인 (subprocess 무관).

        subprocess 층이 죽어도(하네스 사망) 이 leg 은 계약을 계속 잰다.
        """
        rc = sut.main(["--nonexistent-flag"])
        cap = capsys.readouterr()

        assert rc == 0, f"main() 은 항상 0: rc={rc!r}"
        dones = _done_lines(cap.out)
        assert len(dones) == 1, f"DONE 줄 {len(dones)}개: out={cap.out!r}"
        assert "인자 파싱 단계에서 종료" in cap.err, (
            f"인자 오류 흡수 경고 부재 — 다른 분기로 빠졌다: {cap.err!r}"
        )
        assert not sut.contains_verdict_lexicon(cap.out + cap.err), (
            f"INV-E 위반: 신규 산출에 verdict 어휘 잔존: {cap.out!r} / {cap.err!r}"
        )


# ═════════════ F-SEC-4: 채널 본문 마크다운 무해화 ═══════════════════════════════
# 보안 lane 이 **실측한 payload 그대로** (문자열 축 — 파일시스템을 거치지 않으므로
#   Windows 파일명 제약과 무관하게 POSIX 표면까지 정의역에 든다).
# (a) **활성 payload** — 술어의 양성 대조군 정의역. 원문 상태에서 반드시 위반으로 잡힌다.
ACTIVE_PAYLOADS = (
    ("코드 스팬", "cfp-`rm -rf ~`-worktree"),
    ("mention 2종", "cfp-@mclayer-@mccho-mclayer"),
    ("링크 꼬리", "cfp-](evil.example)-x"),
    ("이슈 역참조", "cfp-#2949-#1-x"),
    ("이미지·강조", "cfp-![img](u)-*b*-_i_-x"),
    ("HTML 주석 은폐", "cfp-<!-- hide -->-x"),
    ("HTML 태그", "cfp-<img src=x onerror=y>-x"),
    ("엔티티 위조", "cfp-&lt;workspace&gt;-x"),
)

# (b) **선언상 비활성** payload — 커버리지엔 넣되 양성 대조군에서는 뺀다.
#   · `\](…)` 는 원문에서 이미 `]` 가 이스케이프돼 링크가 성립하지 않는다(우리 무해화가
#     `\` 를 doubling 해도 여전히 비활성 — 이스케이프 무력화 시도가 실패하는지 본다).
#   · `|` `~~` 는 **의도적 비대상**(모듈 상단 "무해화하지 않는 것" 절의 선언된 잔여)이다.
#     여기서 양성 대조군에 넣으면 술어가 계약보다 넓어져 정상 코드에 false RED 가 된다.
INERT_BY_DECLARATION = (
    ("이스케이프 무력화 시도", "cfp-\\](evil.example)-x"),
    ("표 셀·취소선 (선언된 잔여)", "cfp-|cell|-~~s~~-x"),
)

ADVERSARIAL_NAMES = ACTIVE_PAYLOADS + INERT_BY_DECLARATION

# 활성 구성자 잔존 술어 — **이스케이프되지 않은** 구성자만 위반으로 센다.
_UNESCAPED_ACTIVE_RE = re.compile(r"(?<!\\)[`*_\[\]<>&!]")
_LIVE_MENTION_RE = re.compile(r"@[A-Za-z0-9]")
_LIVE_ISSUEREF_RE = re.compile(r"#[0-9]")


def _active_markdown_hits(text):
    """산출 필드에 남은 **활성** 마크다운 구성자 열거 (0 = 빈 리스트)."""
    hits = []
    m = _UNESCAPED_ACTIVE_RE.search(text)
    if m:
        hits.append(("unescaped-constructor", m.group(0), m.start()))
    m = _LIVE_MENTION_RE.search(text)
    if m:
        hits.append(("live-mention", m.group(0), m.start()))
    m = _LIVE_ISSUEREF_RE.search(text)
    if m:
        hits.append(("live-issue-ref", m.group(0), m.start()))
    return hits


def _obs(path, cls="worktree"):
    return sut.Observation(cls=cls, display_path=path,
                           declared="완결 직후 정리", measured="age=9d 보존사유=none",
                           mismatch=True)


class TestMarkdownNeutralizationOfPathFields:
    """F-SEC-4 — 관측 대상의 **이름**이 보고 채널의 **구조**를 바꾸지 못한다.

    ★ 술어의 자기 건전성부터 고정한다: `_active_markdown_hits` 가 원문 payload 를
      **실제로 위반으로 잡는지**(양성 대조군) 먼저 확인한다. 그게 없으면 아래 "위반 0"
      단언은 술어가 아무것도 못 잡는 상태에서도 통과한다(공허).

    mutant kill: `_safe_text` 에서 `_neutralize_markdown(...)` 호출 제거
      ⇒ 본 클래스 3 테스트 RED (양성 대조군은 GREEN 유지 — 균일 실패 아님).
    """

    def test_predicate_positive_control_flags_raw_payload(self):
        """양성 대조군: 술어가 **원문 활성 payload** 를 전량 위반으로 잡는다 (비공허 앵커).

        ★ 정의역 = `ACTIVE_PAYLOADS` 뿐이다. `INERT_BY_DECLARATION` 을 여기 넣으면 술어가
          SUT 계약보다 넓어져(=`|`·`~~` 까지 요구) 정상 코드에 false RED 가 된다 —
          "계약을 넘는 단언 금지" 는 형제 fuzz 오라클이 이미 세운 규율이다.
        """
        assert len(ACTIVE_PAYLOADS) >= 8, "정의역 붕괴: 활성 payload 목록이 비었다"
        missed = [label for label, name in ACTIVE_PAYLOADS
                  if not _active_markdown_hits(name)]
        assert missed == [], (
            f"술어 자해: 원문 활성 payload 를 위반으로 잡지 못한다 — {missed}. "
            "이 상태면 아래 '위반 0' 단언이 공허하다"
        )
        # 선언된 비활성군은 **원문에서도** 위반이 아니다 — 그 사실을 같이 고정해
        #   "무해화 덕분에 깨끗해졌다" 는 잘못된 귀속을 막는다(귀속 분리).
        for label, name in INERT_BY_DECLARATION:
            assert _active_markdown_hits(name) == [], (
                f"[{label}] 선언상 비활성인데 술어가 잡는다 — 술어와 계약이 어긋났다: "
                f"{_active_markdown_hits(name)}"
            )

    def test_rendered_body_has_no_active_markdown_constructor(self):
        """적대 이름 10종이 실린 **실 발화 본문**에 활성 구성자 0.

        ★ 검사 대상은 `render_report` 산출 전문이다 — 필드 단위가 아니라 채널에 실제로
          올라가는 문자열이어야 계약이 성립한다.
        ★ 마커 줄(sentinel/trailer)은 **우리 자신의 고정 리터럴**이므로 정의역에서
          제외한다 — 그 줄이 이스케이프되면 `fetch_existing_keys` 의 자기 코멘트 식별이
          깨져 dedup 이 죽는다(별도 테스트가 그 반대 방향을 고정한다).
        """
        body = sut.render_report([_obs(n) for _, n in ADVERSARIAL_NAMES],
                                 "task-`x`", "run-@who-#7")
        fact_lines = [ln for ln in body.splitlines()
                      if sut.SENTINEL not in ln and sut.TRAILER not in ln]
        assert len(fact_lines) == len(ADVERSARIAL_NAMES), (
            f"정의역 붕괴: 사실 줄 {len(fact_lines)}개 (기대 {len(ADVERSARIAL_NAMES)}) — "
            f"검사할 줄이 사라졌다: {body!r}"
        )

        violations = []
        for ln in fact_lines:
            # 렌더 템플릿이 소유한 줄머리 `- ` 는 우리 자신의 리스트 마커다(정의역 밖).
            payload = ln[2:] if ln.startswith("- ") else ln
            hits = _active_markdown_hits(payload)
            if hits:
                violations.append((hits, payload[:160]))
        assert violations == [], (
            f"활성 마크다운 구성자 {len(violations)}건 잔존 — 이름이 채널 구조를 바꾼다: "
            f"{violations[:3]}"
        )

        # trailer 의 가변 필드(task=/run=)도 같은 계약 (마커 리터럴 뒤 값 축)
        trailer = [ln for ln in body.splitlines() if sut.TRAILER in ln]
        assert len(trailer) == 1, f"trailer 줄 {len(trailer)}개: {body!r}"
        assert _active_markdown_hits(trailer[0].replace(sut.TRAILER, "")) == [], (
            f"trailer 가변 필드에 활성 구성자 잔존: {trailer[0]!r}"
        )

    def test_payload_is_neutralized_not_deleted(self):
        """무해화는 **삭제가 아니다** — 역무해화하면 원 이름이 정확히 복원된다.

        ★ 이 축이 없으면 "위반 0" 을 **필드를 통째로 지워** 달성하는 구현이 통과한다
          (F-CR5-03 이 정확히 그 형상: 삭제 치환 → 서로 다른 잔재가 한 키로 붕괴 →
          한쪽 영구 억제). 잔재 관측이 주제인 모듈에서 위치 특정 불능은 기능 상실이다.
        """
        for label, name in ADVERSARIAL_NAMES:
            key = sut.dedup_key(_obs(name))
            restored = sut.unneutralize_markdown(key)
            assert restored == "worktree:" + name, (
                f"[{label}] 무해화가 가역이 아니다(정보 손실) — "
                f"{name!r} → {key!r} → {restored!r}"
            )

        # 서로 다른 적대 이름은 **서로 다른 키**로 남는다 (붕괴 0 — 영구 억제 방지)
        keys = [sut.dedup_key(_obs(n)) for _, n in ADVERSARIAL_NAMES]
        assert len(set(keys)) == len(keys), (
            f"키 붕괴: 적대 이름 {len(keys)}종이 {len(set(keys))}개 키로 합쳐졌다 — "
            "한쪽 잔재가 영구 억제된다"
        )

    def test_normalization_still_runs_before_neutralization(self):
        """순서 계약: 경로 정규화가 **원문 경로**를 보고 끝낸 뒤 무해화한다.

        ★ 무해화를 앞에 두면 삽입된 `\\` 가 리터럴 find·`[\\/]` 매칭을 교란해 마스킹이
          실패하거나 과잉 접힘이 된다. 여기서는 정규화가 여전히 성립함을 산출로 잰다.
        """
        got = sut._safe_text("/Users/alice/.claude/worktrees/x")
        assert "\\<user-home\\>" in got, f"정규화가 무해화 뒤로 밀렸다: {got!r}"
        assert "/Users/alice" not in got, f"미정규화 경로 잔존: {got!r}"
        # fail-closed 축도 무손상 (무해화가 가드를 우회시키지 않았는가)
        assert sut._safe_text(r"보존사유=tempD:\zzq1") == "\\<미정규화-경로-제거\\>", (
            f"잔여 가드 결론이 바뀌었다: {sut._safe_text(r'보존사유=tempD:zzq1')!r}"
        )


class TestMarkdownNeutralizationKeepsD3Roundtrip:
    """F-SEC-4 봉합이 **D3 라운드트립을 깨지 않았는가** (형제 회귀 — 지시 ★).

    D3 = 역추출(`_FACT_KEY_RE`)(render_fact_tuple(o)) == dedup_key(o).
    이 항등이 깨지면 채널에 실린 키와 다음 실행 재유도값이 갈려 **매 실행 중복 발화**가
    된다. 무해화를 `_safe_text` **안**(= 식별 축과 표시 축 공유)에 둔 이유가 이것이다 —
    표시 축에만 걸면 여기서 즉시 RED.

    mutant kill: 무해화를 `render_fact_tuple` 의 declared/measured 에만 적용하고
      `dedup_key` 에서 빼기 ⇒ 본 클래스 RED.
    """

    def test_roundtrip_holds_for_adversarial_names(self):
        """적대 이름 10종 + 기존 3형상 회귀 케이스에서 항등 유지."""
        cases = list(ADVERSARIAL_NAMES) + [
            ("① 후행 공백", "~/.claude/worktrees/trailing-space   "),
            ("② 키 주입 · key=", "~/.claude/worktrees/x · key=INJECTED-EVIL"),
            ("③ 상한 초과", "~/.claude/codeforge-scratch/" + "z" * 600),
            ("④ 적대+상한 초과", "cfp-`x`-@who-" + "z" * 600),
        ]
        assert len(cases) >= 12, "정의역 붕괴"

        failures = []
        for label, path in cases:
            obs = _obs(path)
            expected = sut.dedup_key(obs)
            extracted = sut._FACT_KEY_RE.match(sut.render_fact_tuple(obs))
            got = None if extracted is None else extracted.group(1)
            if got != expected:
                failures.append((label, expected[:70], None if got is None else got[:70]))
            if len(expected) > sut._MAX_KEY_LEN:
                failures.append((label + " [상한 비대칭]", str(len(expected)), "-"))
        assert failures == [], f"D3 라운드트립 파괴 {len(failures)}건: {failures}"

    def test_roundtrip_survives_channel_recovery(self):
        """end-to-end: 무해화된 본문을 채널로 되먹여 회수 → 재발화 0.

        ★ `fetch_existing_keys` 의 실 경로(sentinel 필터 + 길이 폐기 + set 수집)까지
          살아남는지 — 마커 줄을 이스케이프해 버리면 sentinel 매치가 깨져 여기서 RED.
        """
        import json
        from unittest import mock

        observations = [_obs(n) for _, n in ADVERSARIAL_NAMES]
        body = sut.render_report(observations, "d3-task", "d3-run")
        assert sut.SENTINEL in body, (
            f"마커 무결성 파괴: sentinel 이 본문에서 변형됐다 — 자기 코멘트 식별 불능: {body[:200]!r}"
        )

        fake_gh = mock.Mock(return_value=mock.Mock(
            returncode=0, stdout=json.dumps({"comments": [{"body": body}]})))
        recovered = sut.fetch_existing_keys("owner/repo#1", gh=fake_gh)

        assert recovered, f"채널 회수 실패(빈 집합) — dedup 무력화: {recovered!r}"
        missing = [sut.dedup_key(o) for o in observations
                   if sut.dedup_key(o) not in recovered]
        assert missing == [], (
            f"기보고 키 {len(missing)}건 회수 누락 — 매 실행 중복 발화: "
            f"{[k[:60] for k in missing]}"
        )

    def test_neutralization_is_injective_over_corpus(self):
        """단사성 — 좌역원 존재(ㄱ) + pairwise 충돌 0(ㄴ) + INV-E 무손상(ㄷ).

        비단사 무해화는 서로 다른 두 잔재를 한 키로 접어 한쪽을 **영구 억제**한다.

        ★ **정의역 = 어휘 스크럽 산출** (= 실 파이프라인에서 무해화가 받는 값).
          임의 문자열 위에서는 단사가 아니며 그 반례를 케이스에 **명시적으로 넣어**
          경계를 고정한다: `#1` 과 `#%-1` 은 raw 로는 둘 다 `#%-1` 이 되지만, 스크럽을
          통과시키면 `#%-1` · `#%%-1` 로 갈린다(원문 `%` 가 doubling 되므로 `#%-` 형상은
          스크럽 산출에 존재할 수 없다). 선언을 코드보다 넓게 쓰지 않기 위한 결박이다.
        """
        corpus_file = (REPO_ROOT / "tests" / "fixtures" / "cfp_2949"
                       / "fuzz-corpus" / "paths.txt")
        assert corpus_file.is_file(), f"corpus 부재: {corpus_file}"
        corpus = [ln.strip() for ln in corpus_file.read_text(encoding="utf-8").splitlines()
                  if ln.strip() and not ln.strip().startswith("#")]
        cases = corpus + [n for _, n in ADVERSARIAL_NAMES] + [
            "", "\\", "\\\\", "\\[", "@", "@@", "#", "#1", "@1", "a@b", "a#1b",
            "%-", "%%", "@%-x", "#%-1", "`", "<", ">", "&", "!",
        ]
        assert len(cases) >= len(corpus) + 8, "정의역 붕괴"

        # (ㄱ) 좌역원 — 실 파이프라인 위치(어휘 스크럽 산출)에서 성립
        broken = [c for c in cases
                  if sut.unneutralize_markdown(
                      sut._neutralize_markdown(sut._scrub_verdict_tokens(c)))
                  != sut._scrub_verdict_tokens(c)]
        assert broken == [], f"가역성 파괴 {len(broken)}건: {[b[:50] for b in broken[:5]]}"

        # (ㄴ) pairwise 충돌 0 — **파이프라인 정의역**(스크럽 산출) 위에서
        seen, collisions = {}, []
        for c in cases:
            src = sut._scrub_verdict_tokens(c)
            out = sut._neutralize_markdown(src)
            if out in seen and seen[out] != src:
                collisions.append((seen[out][:40], src[:40], out[:40]))
            seen[out] = src
        assert collisions == [], f"무해화 충돌 {len(collisions)}건: {collisions[:3]}"

        # (ㄴ') 정의역 경계 실증 — raw 에서는 충돌하는 쌍이 파이프라인 위에서는 갈린다.
        #   이 leg 이 없으면 위 (ㄴ) 이 "정의역을 좁혀 통과시킨 것" 인지, 애초에 충돌이
        #   불가능한 것인지 구별되지 않는다(귀속 분리).
        assert sut._neutralize_markdown("#1") == sut._neutralize_markdown("#%-1"), (
            "raw 정의역 반례가 사라졌다 — 위 정의역 한정의 근거가 없어졌다"
        )
        assert (sut._neutralize_markdown(sut._scrub_verdict_tokens("#1"))
                != sut._neutralize_markdown(sut._scrub_verdict_tokens("#%-1"))), (
            "파이프라인 정의역에서도 충돌한다 — 단사 선언이 실제로 깨졌다"
        )

        # (ㄷ) INV-E 무손상 — 무해화가 verdict 어휘를 되살리지 않는다
        leaked = [c for c in cases if sut.contains_verdict_lexicon(sut._safe_text(c))]
        assert leaked == [], f"INV-E 위반 {len(leaked)}건: {leaked[:3]!r}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
