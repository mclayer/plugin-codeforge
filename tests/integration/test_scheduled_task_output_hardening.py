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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
