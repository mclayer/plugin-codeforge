---
kind: concept_definition
type: domain-knowledge
slug: text-encoding-layer-model
title: Text-encoding layer model — 텍스트 파이프라인 인코딩 5계층 (저작→write→전송→소비→표시) + 방어수단-계층 매핑 + ASCII 구조 불변
status: Active
updated: 2026-08-03
carrier_story: CFP-2884
related_adrs:
  - ADR-081  # Codex dispatch 계보 — promptfile 조립·codex exec 주입 경로의 인코딩 취약면
  - ADR-119  # research-before-claims — 본 개념의 출처 인용 규율
related_files:
  - plugins/codeforge-review/agents/CodexReviewAgent.md  # dispatch 템플릿 (promptfile 조립 지점)
tags:
  - encoding
  - utf-8
  - cp949
  - mojibake
  - windows
  - layer-model
  - ascii-invariance
---

# Text-encoding layer model (텍스트 파이프라인 인코딩 5계층 모델)

## 정의

`text-encoding layer model` = **텍스트가 저작에서 최종 소비까지 흐르는 파이프라인을 인코딩 관점에서 5계층으로 분해하고, 각 방어 수단이 어느 계층만 방어하는지 매핑하는 분석 모델**.

## 컨텍스트

mojibake(문자 깨짐)는 "어딘가 깨졌다"가 아니라 "특정 계층에서 byte↔문자 해석 계약이 어긋났다"로 특정해야 올바른 방어 수단을 선택할 수 있다. 본 개념은 CFP-2884 발단 사건 탐구 과정에서 요구사항 lane 이 정립했다 (변경 이력 참조).

## 핵심 규칙

### 5계층

| 계층 | 내용 | 깨짐 발생 조건 |
|---|---|---|
| L0 저작 | 프롬프트 텍스트가 heredoc/echo 인자로 shell 에 전달 | harness→shell 인자 인코딩 불일치 |
| L1 파일 write | promptfile 등 파일로 기록 | writer 런타임이 locale 인코딩(cp949)으로 기록 |
| L2 전송 | `cmd - < file` stdin redirect / pipe | **깨지지 않음** — kernel fd 레벨 byte 투명 |
| L3 소비 | 자식 프로세스가 byte 를 문자로 디코딩 | 소비자의 가정 인코딩 ≠ 실제 byte 인코딩 |
| L4 표시 | 콘솔/터미널 렌더 | 콘솔 코드페이지 ≠ 스트림 인코딩 (표시만 깨짐, 데이터 무손상) |

**L2 불변 사실**: POSIX shell 의 `< file` redirect 는 `open()`+`dup2()` 로 fd 를 연결하는 kernel 연산 — shell 은 내용을 읽지도 변환하지도 않는다 (byte-transparent). [source: POSIX dup/dup2 — pubs.opengroup.org/onlinepubs/9799919799/functions/dup.html]. 따라서 "redirect 가 깨뜨렸다"는 진단은 항상 오진 — 깨짐은 L1(기록 시점) 또는 L3(디코딩 시점)이다.

### 방어수단 → 계층 매핑

| 수단 | 방어 계층 | 적용 범위 한계 | 출처 |
|---|---|---|---|
| `PYTHONUTF8=1` (PEP 540) | L1+L3 | **Python 프로세스만** — 파일 open/stdio 기본 인코딩을 locale(cp949) 대신 UTF-8 로 | PEP 686 (Python 3.15 부터 default 화 확정) — peps.python.org/pep-0686 |
| `PYTHONIOENCODING` | L3 (stdio 한정) | Python stdio 만, 파일 open 미방어 | Python docs |
| `LC_ALL`/`LANG=*.UTF-8` | L1/L3 (POSIX tool 층) | MSYS2/Cygwin 런타임 charset + locale-aware tool 만 — Git Bash 는 LANG 으로 locale 결정 | msys2 setup-locale 문서 |
| `chcp 65001` | L4 (+console-API 프로그램 L3) | 콘솔 코드페이지만 — 파일/파이프 경로 무관 | MSYS2 이슈 (#698: bash 가 chcp 변경을 honor 하는지 불확실) |
| UTF-8 BOM | L3 힌트 | Unicode 표준상 UTF-8 에 BOM 은 "neither required nor recommended" — PowerShell 5.1 잔재 관행 | Unicode Standard |
| **ASCII-화 (영어 지시문)** | **전 계층 불변** | cp949·CP1252·UTF-8 전부 ASCII superset — 코드페이지 오해석이 일어나도 ASCII 7-bit 구간은 byte 동일 → 구조적 면역 | 구조적 사실 (인코딩 표준 정의) |

### 핵심 통찰 (CFP-2884 발단 사건 적용)

1. **env-var 수단은 전부 partial** — 각각 특정 런타임·특정 계층만 방어. 파이프라인에 Python/PowerShell/Rust CLI 가 혼재하면 단일 env-var 로 전 계층을 닫을 수 없다.
2. **소비자(codex CLI) 측 상류 결함은 우리 배선으로 못 닫는다** — openai/codex Windows 인코딩 이슈 중 현재 open = **#4013 "Cannot force UTF-8" 단독** (open/reopened, updated 2026-07-26 [verified: gh api 2026-08-03]). #7290 "non-Latin characters can still become garbled **even when everything is configured to UTF-8**"·#4498 (PowerShell stdio 재인코딩 mojibake)·#4574 (CJK 깨짐 회귀) 는 **종결(closed/completed)** — "이 class 결함이 반복 발생·회귀해 온 패턴"의 이력 근거로만 인용한다. **증거 성격 한정 (입력측 직접 증거 부재)**: 위 4건은 전부 codex 의 **출력·콘솔(write) 축** 실측이며, 입력 promptfile 오디코딩(L3 입력 소비)의 직접 증거가 아니다 — 입력측 리스크 = 동종 class 추정 [hypothesis]. 그럼에도 결론은 유지된다 (보수 방향): 축 A(UTF-8 배선)를 완벽히 해도 잔여 리스크 잔존 → 비-ASCII 표면 자체를 줄이는 축 B(지시문 영어화)가 **defense-in-depth 이지 중복이 아니다**.
3. mojibake 진단 시 "깨진 출력"이 아니라 **어느 계층의 byte 를 실측했는가**부터 — L4 표시 깨짐(데이터 무손상)과 L1/L3 데이터 깨짐은 대응이 전혀 다르다.

## 경계

- 본 개념 = 외부 표준·선행사례 기반 계층 모델 (ResearcherAgent 소유). CFP-2884 사건의 실제 깨짐 계층 특정 = 설계 lane 실측 영역.
- consumer 프로젝트 일반 적용 가능 (Windows + 비-ASCII 주 언어 환경 공통).

## 관련 ADR

- **ADR-081 (Codex dispatch 계보)** — promptfile 조립·`codex exec` 주입 경로의 인코딩 취약면 (본 모델의 주 적용 지점).
- **ADR-119 (research-before-claims)** — 본 개념의 출처 인용 규율.

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-08-03 | 신규 작성 — CFP-2884 요구사항 lane 탐구 산출 | CFP-2884 |
| 2026-08-03 | FIX Iter 1 정정 — 상류 이슈 open 산정 정정 (open = #4013 단독, 종결 3건 = 재발·회귀 패턴 이력 근거) + 증거 성격 한정 (출력·콘솔 축 실측 / 입력측 = 동종 class 추정) (RF-6·RF-7) | CFP-2884 |
| 2026-08-04 | 헤딩 구조 재배치 — concept doc-section-schema 필수 헤딩(컨텍스트·핵심 규칙·관련 ADR) 정합. 내용 무손실 (정의 2문장 분리 이동 + 기존 절 3종을 핵심 규칙 하위 `###` 로 강등 + frontmatter 인용 ADR 2건 목록화) | CFP-2884 |
