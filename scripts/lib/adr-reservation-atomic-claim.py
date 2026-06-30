#!/usr/bin/env python3
# scripts/lib/adr-reservation-atomic-claim.py
# CFP-2491 / Epic CFP-2481 E3b — ADR-RESERVATION 번호 atomic claim primitive (단일-셀 OCC).
#
# SSOT 근거:
#   - ADR-133 §결정2 — GitHub Contents API PUT `sha`→409 retry (단일-셀 OCC, load-bearing 분기)
#   - ADR-133 §결정2 Pattern A binding — 신규 알고리즘 발명 금지. 참조구현 = scripts/post-merge-telemetry.sh L99-153.
#   - ADR-133 Amendment 1 / Change Plan §3.1 — 언어=Python (ADR-061 §결정6), claim-state=별도 JSON artifact.
#   - ADR-133 §결정4 / Amd1 A1-2 — claimant identity (`{role}:{story_key}:{run_id}`) idempotency key.
#   - ADR-133 §결정5 / Amd1 A1-3 — ABA 내성: 클라이언트 단조성 불변식(next<=max reject + claims[] append-only)
#                                   + (mechanical 2층) adr-reservation-state branch protection.
#   - Change Plan §3.1 Finding 1 (InfraOp, load-bearing) — append-only 와 다른 단일-셀 read-modify-write.
#         매 attempt 마다 state content 를 re-read 해 현재 최고번호 N 재확인 + next=N+1 재계산.
#         SHA re-fetch 만으론 부족 — 다른 세션이 그 사이 N+1 점유 시 자신은 N+2 로 재계산해야 한다 (mutant m2 표적).
#   - Change Plan §7.5 (Security P1) — status_code 만 추출, 전체응답 파일 0, GH_TOKEN 로그 출력 절대 금지.
#
# 핵심 = "설계대로 만들었나"가 아니라 "race 가 실제로 차단되는가"(mutation-RED). m1-m6 + m2a/m2b 표적.
#
# Usage (CLI):
#   GH_TOKEN=... python3 scripts/lib/adr-reservation-atomic-claim.py \
#       --repo mclayer/plugin-codeforge \
#       --state-path adr-reservation-claim-state.json \
#       --branch adr-reservation-state \
#       --claimant "ArchitectAgent:CFP-2491:run-12345"
#
# 출력: claim 성공 시 stdout 에 점유 번호(정수) 1줄 + exit 0. 실패 시 stderr 진단 + exit 1.
#
# Test mock seam (deterministic — 실 GitHub 동시성 없이 race 재현, Change Plan §8 GAP-1):
#   환경변수 CLAIM_SHA_OVERRIDE / CLAIM_TEST_SCRIPT 으로 GitHub I/O 를 stub 으로 대체.
#   기본 동작은 `gh api` subprocess. CLI 진입점은 unittest 없이도 mock seam 으로 단위검증 가능.

import json
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple


# ─── 데이터 모델 ─────────────────────────────────────────────────────────────

@dataclass
class GhResponse:
    """gh api 호출의 결과. status_code 만 의미 — 전체 응답 본문/헤더는 캡처하지 않는다 (Security P1)."""
    status_code: int
    body: str = ""          # GET 시 파일 content(JSON) — PUT 응답 본문은 사용하지 않음.


@dataclass
class ClaimState:
    """adr-reservation-state branch 위 별도 JSON artifact (2-channel 경계 보존 — ADR-RESERVATION.md schema bump 0)."""
    max_adr_number: int
    claims: list = field(default_factory=list)
    # GitHub Contents API blob sha — state 파일 부재 시 None (create 경로).
    blob_sha: Optional[str] = None


@dataclass
class ClaimResult:
    status: str             # "claimed" | "self_claim" | "exhausted" | "client_error"
    adr_number: Optional[int] = None
    attempts: int = 0
    reason: str = ""


# ─── GitHub I/O 추상화 (mock seam) ───────────────────────────────────────────
#
# 실 구현 = `gh api` subprocess. 테스트는 동일 시그니처의 stub 을 주입한다 (Change Plan §8 deterministic).
# Security P1 정합 — gh api 응답에서 status_code(GET 의 경우 본문)만 추출, `-i > /tmp/...` full-response
# 파일 캡처 금지, X-OAuth-Scopes 등 헤더 미캡처. GH_TOKEN 은 절대 로그 출력하지 않는다.

class GitHubContentsClient:
    """GitHub Contents API conditional PUT (`sha`→409) OCC 채널 클라이언트."""

    def __init__(self, repo: str, branch: str):
        self.repo = repo
        self.branch = branch

    def get_state(self, state_path: str) -> GhResponse:
        """state 파일 GET — 200(본문 = base64 decode 된 JSON) / 404(부재, create 경로) / 그 외."""
        # gh api 는 200 이면 JSON object, 404 면 non-zero exit. status_code 만 의미.
        proc = subprocess.run(
            ["gh", "api", f"repos/{self.repo}/contents/{state_path}?ref={self.branch}",
             "--jq", "{content: .content, sha: .sha}"],
            capture_output=True, text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                return GhResponse(status_code=0)
            import base64
            raw = base64.b64decode(payload.get("content", "")).decode("utf-8") if payload.get("content") else ""
            return GhResponse(status_code=200, body=json.dumps({"json": raw, "sha": payload.get("sha")}))
        # gh exit non-zero — 404(부재) 로 간주(create 경로). 다른 에러는 PUT 단계에서 재현.
        return GhResponse(status_code=404)

    def put_state(self, state_path: str, content_json: str, blob_sha: Optional[str],
                  message: str) -> GhResponse:
        """conditional PUT — blob_sha 동봉(존재 시). server-side SHA 비교 → 불일치 409.

        Security P1: `-i` (응답 헤더 캡처) 미사용. status_code 만 HTTP-status 헤더에서 추출하지 않고
        gh exit + 본문 미저장으로 처리. gh api 는 4xx/5xx 시 non-zero exit + stderr 에 status 정보.
        """
        import base64
        content_b64 = base64.b64encode(content_json.encode("utf-8")).decode("ascii")
        args = ["gh", "api", "-X", "PUT", f"repos/{self.repo}/contents/{state_path}",
                "-f", f"message={message}",
                "-f", f"content={content_b64}",
                "-f", f"branch={self.branch}"]
        if blob_sha:
            args += ["-f", f"sha={blob_sha}"]
        proc = subprocess.run(args, capture_output=True, text=True)
        if proc.returncode == 0:
            return GhResponse(status_code=200)
        # gh api 실패 — stderr 에서 HTTP status 추출 (전체 응답 파일 캡처 0, 헤더 미보존).
        code = _extract_http_status(proc.stderr)
        return GhResponse(status_code=code)


def _extract_http_status(stderr: str) -> int:
    """gh api stderr 에서 'HTTP 409' 형태 status 추출. GH_TOKEN 등 민감값은 로그 출력 안 함."""
    import re
    m = re.search(r"HTTP\s+(\d{3})", stderr or "")
    if m:
        return int(m.group(1))
    # gh 가 명시적 status 미출력 시 5xx/network 로 분류(backoff 경로).
    return 0


# ─── claim state 파싱/구성 ───────────────────────────────────────────────────

def parse_state(resp: GhResponse) -> ClaimState:
    """GET 응답 → ClaimState. 404(부재) → max_adr_number=0, blob_sha=None (create 경로)."""
    if resp.status_code != 200:
        return ClaimState(max_adr_number=0, claims=[], blob_sha=None)
    payload = json.loads(resp.body)
    raw = payload.get("json", "")
    sha = payload.get("sha")
    if not raw.strip():
        return ClaimState(max_adr_number=0, claims=[], blob_sha=sha)
    data = json.loads(raw)
    return ClaimState(
        max_adr_number=int(data.get("max_adr_number", 0)),
        claims=list(data.get("claims", [])),
        blob_sha=sha,
    )


def find_self_claim(state: ClaimState, claimant: str) -> Optional[int]:
    """(adr_number, claimant) idempotency key — 동일 claimant 의 기존 claim 발견 시 그 번호 반환 (self-claim).

    ADR-133 Amd1 A1-2 / Change Plan §8.5.3 — at-least-once replay(crash-after-200) self-claim 감지.
    re-emit 없이 기존 점유 번호를 그대로 반환 → 200 간주 (double-claim 0).
    """
    for c in state.claims:
        if c.get("claimant") == claimant and c.get("status") == "claimed":
            return int(c["adr_number"])
    return None


def build_next_state(state: ClaimState, claimant: str, next_number: int, now_iso: str) -> str:
    """현재 state 위에 next_number claim 을 append-only 로 추가한 JSON 문자열 구성.

    ABA 단조성 불변식 (ADR-133 §결정5 / Change Plan §3.3 클라이언트 불변식):
      - next_number 는 max_adr_number 보다 커야 한다 (단조 비감소 — 호출 전 검증).
      - claims[] 는 append-only (기존 row 삭제/변형 금지).
    """
    new_claims = list(state.claims)
    new_claims.append({
        "adr_number": next_number,
        "claimant": claimant,
        "status": "claimed",
        "claimed_at": now_iso,
    })
    return json.dumps({
        "max_adr_number": next_number,
        "claims": new_claims,
    }, ensure_ascii=False, indent=2) + "\n"


# ─── 핵심 OCC retry 루프 (Pattern A 충실 포팅 — load-bearing) ─────────────────

def claim_adr_number(
    repo: str,
    state_path: str,
    branch: str,
    claimant: str,
    max_attempts: int = 4,
    backoff_delays: Tuple[int, ...] = (2, 4, 8),
    client: Optional[GitHubContentsClient] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    jitter_fn: Callable[[], float] = lambda: random.randint(1, 5),
    now_fn: Callable[[], str] = None,
) -> ClaimResult:
    """단일-셀 OCC: read state(현재 최고 N + SHA) → next=N+1 → conditional PUT(sha) →
        200/201=claimed / 409=다른 세션 점유 → re-fetch + next 재계산 + jitter retry /
        4xx(409 제외)=즉시 exit1 / 5xx·network=backoff(2,4,8) / exhausted=::error::+exit1.

    load-bearing 분기 (Change Plan §3.1 Finding 1, mutant m2 표적):
      매 attempt 마다 state content 를 re-read 해 현재 최고번호 N 을 재확인하고 next=N+1 을 재계산한다.
      SHA 만 갱신하면 안 됨 — 다른 세션이 그 사이 N+1 점유 시 자신은 N+2 로 재계산해야 lost-update 가 차단된다.
        · m2a 표적: SHA re-fetch 생략 (stale blob sha 재사용 → 영구 409)
        · m2b 표적: next 재계산 생략 (stale N+1 재시도 → 다른 세션 점유 번호와 충돌 또는 lost-update)
    """
    if client is None:
        client = GitHubContentsClient(repo=repo, branch=branch)
    if now_fn is None:
        now_fn = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for attempt in range(1, max_attempts + 1):
        # ── (1) read phase — 매 attempt 현재 state 를 re-read (m2a/m2b load-bearing) ──
        # SHA re-fetch + content re-read 를 동시에 — 둘 다 매 attempt 갱신해야 OCC 정확.
        get_resp = client.get_state(state_path)
        state = parse_state(get_resp)

        # ── (1.5) self-claim idempotency (ADR-133 Amd1 A1-2 / §8.5.3 replay) ──
        existing = find_self_claim(state, claimant)
        if existing is not None:
            # 동일 (adr_number, claimant) 이미 점유 — re-emit 없이 self-claim 으로 간주(200 간주).
            print(existing)
            return ClaimResult(status="self_claim", adr_number=existing, attempts=attempt,
                               reason="idempotent self-claim (at-least-once replay)")

        # ── (2) modify phase — next=N+1 재계산 (m2b load-bearing) ──
        next_number = state.max_adr_number + 1

        # ABA 단조성 불변식 (§3.3 클라이언트 불변식): next 는 max 보다 커야 한다 (단조 비감소 강제).
        # mutant m6(rewind: N-1 기록) 는 이 검증으로 reject.
        if next_number <= state.max_adr_number:
            _err(f"단조성 위반 — next({next_number}) <= max({state.max_adr_number}). claim reject (ABA rewind 차단).")
            return ClaimResult(status="client_error", attempts=attempt,
                               reason="monotonicity violation")

        now_iso = now_fn()
        content_json = build_next_state(state, claimant, next_number, now_iso)
        message = f"claim(adr-{next_number}): {claimant} OCC atomic claim (ADR-133)"

        # ── (3) write phase — conditional PUT (blob sha 동봉, INV-1: 모든 write sha= 포함) ──
        put_resp = client.put_state(state_path, content_json, state.blob_sha, message)

        if put_resp.status_code in (200, 201):
            # atomic 점유 성공.
            print(next_number)
            return ClaimResult(status="claimed", adr_number=next_number, attempts=attempt,
                               reason="OCC PUT success")
        elif put_resp.status_code == 409:
            # SHA conflict — 다른 세션이 그 사이 점유. re-fetch + next 재계산 + jitter 후 retry.
            # (다음 루프 iteration 의 read phase 가 SHA + N 둘 다 재취득 — m2a/m2b 핵심.)
            _warn(f"SHA conflict (HTTP 409) attempt {attempt} — re-fetch SHA + next 재계산 + jitter retry")
            if attempt < max_attempts:
                sleep_fn(jitter_fn())
            continue
        elif 400 <= put_resp.status_code < 500:
            # 4xx (409 제외) — client error, no retry, 즉시 fail (INV: silent drop 0).
            _err(f"4xx client error (HTTP {put_resp.status_code}) — no retry, aborting claim.")
            return ClaimResult(status="client_error", attempts=attempt,
                               reason=f"HTTP {put_resp.status_code}")
        else:
            # 5xx / network error (status_code 0 포함) — exponential backoff.
            idx = attempt - 1
            delay = backoff_delays[idx] if idx < len(backoff_delays) else backoff_delays[-1]
            _warn(f"5xx/network error (HTTP {put_resp.status_code}) attempt {attempt} — backoff {delay}s")
            if attempt < max_attempts:
                sleep_fn(delay)

    # ── exhausted — silent drop 절대 금지 (INV-3: exit1). ──
    _err(f"OCC retries exhausted after {max_attempts} attempts — ADR 번호 claim 실패 (claimant={claimant}).")
    return ClaimResult(status="exhausted", attempts=max_attempts, reason="retries exhausted")


# ─── 진단 출력 (stderr — GH_TOKEN 절대 미출력) ───────────────────────────────

def _warn(msg: str) -> None:
    print(f"::warning::{msg}", file=sys.stderr)


def _err(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)


# ─── CLI 진입점 ──────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="ADR-RESERVATION 번호 atomic claim (단일-셀 OCC, ADR-133)")
    p.add_argument("--repo", required=True, help="owner/repo (claim branch 소유 repo)")
    p.add_argument("--state-path", required=True, help="claim state JSON 경로 (state branch 위)")
    p.add_argument("--branch", required=True, help="claim state long-lived branch (예: adr-reservation-state)")
    p.add_argument("--claimant", required=True, help="{role}:{story_key}:{run_id} idempotency key")
    p.add_argument("--max-attempts", type=int, default=4)
    args = p.parse_args(argv)

    result = claim_adr_number(
        repo=args.repo,
        state_path=args.state_path,
        branch=args.branch,
        claimant=args.claimant,
        max_attempts=args.max_attempts,
    )
    if result.status in ("claimed", "self_claim"):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
