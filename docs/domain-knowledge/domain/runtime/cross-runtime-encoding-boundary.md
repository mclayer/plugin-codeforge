---
kind: domain_fact
type: domain-knowledge
area: runtime
topic_slug: cross-runtime-encoding-boundary
title: cross-runtime 인코딩 경계 — codex CLI 실행 사슬에서 PYTHONUTF8 / LC_ALL 의 유효역·무효역
status: Active
owner: ArchitectAgent
updated: 2026-08-06
tags:
  - codex-cli
  - encoding
  - utf-8
  - cross-runtime
  - windows-cp949
related_adrs:
  - ADR-081  # Amendment 15 §결정 D16 — promptfile UTF-8 배선 (본 entry 의 carrier 결정)
  - ADR-170  # §결정 21 (= §결정 2 표 entry 7) — argv=ASCII path / 한국어 실값=UTF-8 파일 내부 (동형 승계 원형)
  - ADR-061  # Python script convention — scripts/lib 명시 encoding='utf-8' de facto 관행
  - ADR-119  # research-before-claims — 정직 ceiling 어휘 ("완전 차단" 단정 금지)
  - ADR-161  # domain-knowledge dir separation (path = domain/<area>/<topic>.md)
carrier_story: CFP-2884
date: 2026-08-06
---

# cross-runtime 인코딩 경계 — codex CLI 실행 사슬에서 PYTHONUTF8 / LC_ALL 의 유효역·무효역

## 정의

**cross-runtime 인코딩 경계** = 하나의 논리적 명령(예: `codex exec ... - < promptfile`)이 **여러 런타임을 거쳐** 실행될 때, 각 런타임이 서로 다른 규칙으로 텍스트를 인코딩·디코딩하면서 생기는 경계면.

이 경계에서 흔한 오류는 **"환경변수를 걸었으니 전 구간이 UTF-8"** 이라는 추정이다. 환경변수의 실효 범위는 **런타임 종류별로 다르며**, 우리가 소유하지 않은 런타임(외부 CLI의 native binary)에는 도달하지 않는다. 본 entry 는 codex CLI 를 표본으로 그 유효역/무효역을 고정한다.

## 컨텍스트

발단 = 요구사항리뷰 lane 의 Codex dispatch promptfile 이 한글 mojibake 로 깨진 채 관측된 사고 (UTF-8 byte 를 cp949 로 오해석 — CFP-2884 §1). 대응 설계 과정에서 "인코딩 env export 를 걸면 되는가" 가 쟁점이 되었고, 계층별 실효 여부를 실측해야 판정 가능한 문제로 드러났다.

이 지식이 필요한 상황:

- 외부 CLI(codex 등)에 **한글이 포함된 텍스트를 파일/stdin 으로 넘기는** 조립 코드를 작성할 때
- `LC_ALL=C.UTF-8` / `PYTHONUTF8=1` 같은 env export 로 인코딩 문제를 "해결했다" 고 판단하려 할 때
- Windows(cp949 ANSI 코드페이지) 개발 환경과 Linux CI 사이에서 인코딩 결함이 **CI 에서 재현되지 않을** 때

## 핵심 규칙

### 규칙 1 — codex CLI 실행 사슬은 3 런타임을 건넌다 (우리 소유 = 0 구간)

`codex` 호출 1회는 아래 3개 런타임을 순차로 통과한다 [verified: codex-cli 0.144.5 firsthand 프로브, 2026-08-06, Windows-11-10.0.26200 / npm global 설치본]:

| # | 구간 | 실체 | 실측 근거 |
|---|---|---|---|
| L-a | sh wrapper | `%APPDATA%/npm/codex` = `POSIX shell script, ASCII text executable` — `#!/bin/sh` npm bin shim. `exec "$basedir/node" "$basedir/node_modules/@openai/codex/bin/codex.js" "$@"` | `file $(which codex)` + `head` |
| L-b | node launcher | `@openai/codex/bin/codex.js` = Node ESM. `import { spawn } from "node:child_process"` + `PLATFORM_PACKAGE_BY_TARGET` (target triple → `@openai/codex-<platform>`) 로 플랫폼 패키지 해석 후 child 를 spawn, exit code/signal 을 부모에 미러 | `bin/codex.js` 실독 |
| L-c | native binary | `@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe` = `PE32+ executable for MS Windows (console), x86-64` (약 341 MB). 동 디렉터리에 `codex-code-mode-host.exe` 동반 | `find` + `file` |

- **L-c 는 Node 도 Python 도 아닌 네이티브 컴파일 산출물**이다. 상류 구현 언어 = Rust [ADR-081 Amendment 15 Context 4 승계 인용 — 본 프로브는 "PE32+ 네이티브"까지만 직접 확인했고 언어 자체를 바이너리에서 확인하지는 않았다].
- 세 구간 **전부 외부 소유**다. 우리가 소유하는 것은 이 사슬을 **호출하는 쪽**(우리 bash + 우리 Python helper)뿐이다.

### 규칙 2 — `PYTHONUTF8` 의 유효역 = Python 프로세스 한정 (codex 사슬 전 구간 무효)

`PYTHONUTF8=1` 은 CPython 인터프리터의 UTF-8 모드 스위치다. 따라서:

- **유효**: 우리가 실행하는 Python 조립·검증 helper (`scripts/lib/*.py`). [verified firsthand: `PYTHONUTF8=1 python3 -c "..."` → `locale.getpreferredencoding(False)` = `utf-8`, `open(...).encoding` = `utf-8` / Python 3.14.4 MSC v.1944 64bit, Windows-11-10.0.26200]
- **무효**: 위 규칙 1 의 L-a(sh) · L-b(node) · L-c(native). Python 인터프리터가 그 사슬에 존재하지 않으므로 스위치가 참조될 지점 자체가 없다.

→ `PYTHONUTF8=1` 을 dispatch 표면에 export 하는 것은 **codex 를 UTF-8 로 만들지 않는다**. 그것은 우리 helper 가 파일을 UTF-8 로 읽고 쓰게 하는 스위치다.

### 규칙 3 — `LC_ALL`/`LANG` 은 Python-on-Windows 파일 I/O 에 무효 (2급 방어선)

POSIX locale 변수는 Windows CPython 의 파일 I/O 기본 인코딩을 바꾸지 못한다 [verified firsthand: `LC_ALL=C.UTF-8` 만 설정하고 `PYTHONUTF8` 미설정 → `locale.getpreferredencoding(False)` = **`cp949`**, `open(...).encoding` = **`cp949`** — ambient(env 무설정)와 동일. 동일 셸에서 `PYTHONUTF8=1` 로 바꾸면 `utf-8` 로 전환되어 대조 성립].

따라서 인코딩 방어선의 **등급을 분리**해야 한다:

| 등급 | 수단 | 보증 |
|---|---|---|
| **1급** | 코드계층 명시 `encoding='utf-8'` (+ write→re-read 내용 동일성 round-trip assert) | 우리 Python 계층 파일 I/O 의 인코딩 결정론 |
| **2급 (defense-in-depth)** | `export LC_ALL=C.UTF-8` / `export PYTHONUTF8=1` — MSYS2 default pin + Python 프로세스 pin | ambient 환경 drift 완화. **단독으로는 보증 아님** |

- **금지 서술**: "env 를 걸었으니 write 안전". 2급이 GREEN 인 것과 산출물이 UTF-8 인 것은 별개 명제다.
- env export 는 **별도 줄**로 쓴다 — inline env-prefix(`LC_ALL=C.UTF-8 codex exec ...`)는 dispatch lint 의 first-token 판정을 파괴한다 (SSOT = ADR-081 §결정 D16 3항).

### 규칙 4 — 경계 통과 데이터는 argv 가 아니라 파일 내부로 (ADR-170 동형)

우리가 제어 가능한 유일한 방어선은 **경계에 넘기는 byte 자체의 정합**이다. 규범 형태 = ADR-170 §결정 21 (= §결정 2 표 entry 7) 의 "argv 는 ASCII path 만, 한국어 실값·content 는 UTF-8 파일 내부" 를 promptfile 에 동형 적용:

- 경로/argv = ASCII (`- < "$PROMPTFILE"` file-redirect 가 argv 축을 이미 차단)
- 한글 실값 = UTF-8 파일 내부 + **write 직후 round-trip 내용 동일성 assert** (byte 문법 유효성 단독 검사 금지 — cp949 mojibake 는 그 자체로 valid UTF-8 이라 문법 검사를 통과한다)

### 규칙 5 — 검증 환경(Linux CI) ≠ 사고 환경(한국어 Windows)

wrapper CI 러너는 사실상 전량 Linux 이고 codex 를 실행하는 workflow 는 0건이다. 즉 **CI GREEN 은 fixture class 의 증거이지 로컬(한국어 Windows, cp949 ANSI) 환경 무결성의 증거가 아니다.** 인코딩 판별 테스트는 ambient locale 에 의존하지 말고 fixture 로 **명시 codec 주입**해야 결정론이 성립한다.

## 경계

### 본 entry 가 보증하지 않는 것

- **상류 codex 자신의 입력 오디코딩** — openai/codex Windows 인코딩 결함 #4013 은 **open 상태**다. 우리 배선의 보증은 "L1(우리 조립 계층) 산출물의 내용 동일성 + 한글 노출 표면 축소"까지이며, **"완전 차단"이 아니다** (ADR-119 정직 ceiling — 단정 서술 금지).
- **L-c native binary 내부 동작** — env 로 인코딩 제어 불가. 관측 가능한 것은 입력 byte 와 출력뿐이다.
- **codex→model shell env 전달 계층** — promptfile 은 model-generated shell 을 경유하지 않고 우리 bash 가 `- <` 로 fd 0 을 연결하므로 이 계층은 본 결함 class 의 경로 밖이다 (scope-out — ADR-081 §결정 D16 7항).

### 버전 고정 프로브 + 재검증 의무

본 entry 의 규칙 1 (실행 사슬 3 구간) 은 **codex-cli 0.144.5 에 고정된 프로브 결과**다. 사슬 구조는 상류 패키징 결정이라 마이너 릴리스에서도 바뀔 수 있다.

- **재검증 trigger**: codex CLI 버전 갱신 (`codex --version` 이 0.144.5 가 아닐 때) — 규칙 1 표의 3 구간을 `file`/실독으로 재확인하고 본 entry 의 `updated` 를 갱신할 의무.
- 규칙 2·3 (Python 인터프리터 스위치의 유효역) 은 codex 버전과 무관하며 CPython 동작에 의존한다 — 재검증 trigger 는 **Python major/minor 갱신**이다.

## 관련 ADR

- [ADR-081](../../../../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) Amendment 15 §결정 D16 — promptfile 3-구획 언어 규약 + UTF-8 round-trip fail-closed 배선. 본 entry 의 carrier 결정 (env 계층 재배치 = D16 3항).
- [ADR-170](../../../../archive/adr/ADR-170-orchestrator-subagent-default-inline-whitelist.md) §결정 21 (= §결정 2 표 entry 7) — argv=ASCII path / 한국어 실값=UTF-8 파일 내부. 규칙 4 의 원형 (구 ADR-039 §결정 7 (b) 재제정 — ADR-039 직접 인용 금지).
- [ADR-061](../../../../archive/adr/ADR-061-python-script-writing-convention.md) — Python script convention. `scripts/lib` 의 명시 `encoding='utf-8'` de facto 관행이 규칙 3 의 1급 방어선.
- [ADR-119](../../../../archive/adr/ADR-119-research-before-claims.md) — 검증 후 단언. 본 entry 의 실측 표기·"완전 차단 금지" 어휘 규율.

## 변경 이력

- **2026-08-06** — CFP-2884 carrier — initial entry (ADR-081 Amendment 15 §결정 D16 / Change Plan §7.4 ⓓ 도입). codex CLI 3-런타임 사슬 실측 + `PYTHONUTF8`/`LC_ALL` 유효역·무효역 고정 + 1급/2급 방어선 등급 분리 + CLI 버전 재검증 의무 배치.

---

**관찰 source**:
- codex-cli 0.144.5 로컬 설치본 firsthand 프로브 (2026-08-06 KST, Windows-11-10.0.26200 / npm global) — `which codex` → `file` → `bin/codex.js` 실독 → 플랫폼 패키지 `vendor/.../bin/codex.exe` `file` 판정
- Python 3.14.4 (MSC v.1944 64bit) 에서 `locale.getpreferredencoding(False)` + `open().encoding` 3-조건 대조 실측 (ambient / `LC_ALL=C.UTF-8` 단독 / `PYTHONUTF8=1`)
- ADR-081 Amendment 15 Context 4 (InfraOperationalArchitect deputy 실측 승계 — 본 프로브가 독립 재현)

**Acknowledged gaps**:
- L-c native binary 의 구현 언어(Rust)는 상류 공개 사실 승계 인용이며 본 프로브가 바이너리에서 직접 확인한 값이 아니다 (프로브 확인 범위 = PE32+ 네이티브까지)
- 상류 #4013 (Cannot force UTF-8) open — codex 자신의 입력측 오디코딩 유무는 미확정 [hypothesis]. 입력 promptfile 오디코딩의 직접 증거는 부재하며 동종 class 추정에 머문다
- 프로브 표본 = win32-x64 1종. linux/darwin 플랫폼 패키지의 사슬 동일성은 `PLATFORM_PACKAGE_BY_TARGET` 매핑 실독에 근거한 구조 추론이며 각 플랫폼 실행 실측이 아니다
- codex CLI 버전 갱신 시 규칙 1 재검증 의무 (위 "버전 고정 프로브 + 재검증 의무")
