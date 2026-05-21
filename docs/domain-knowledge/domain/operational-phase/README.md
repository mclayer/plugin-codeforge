---
kind: domain_fact
type: domain-knowledge
area: operational-phase
topic_slug: operational-phase-readme
title: 운영 phase — narrative SSOT hub
status: Active
tags:
  - operational-phase
  - mechanism-layer
  - narrative-ssot-hub
  - release-lifecycle
  - cfp-1190
related_adrs:
  - ADR-104  # 운영 phase 1st-class 정의 normative SSOT — 본 디렉토리 전체의 referent
  - ADR-087  # Deploy lane 신설 (lane lifecycle 6→8 — 운영 phase 의 release lifecycle 선행 단계)
  - ADR-088  # Deploy Review lane 신설 ("한 번 끝나는" 검증 = 운영 phase 의 선행 단계, §결정 3 + L81 운영 phase 별 Epic origin)
  - ADR-023  # lane plugin lifecycle — lane count invariant (운영 phase = 9번째 lane 아님)
  - ADR-083  # filesystem-only signal invariant (0 API call constraint 의 동형 source)
  - ADR-045  # §D-9 cross-Story pattern → ADR escalation forcing function (self-improving loop 답습 source)
related_stories:
  - CFP-1190  # 본 carrier Story (Epic CFP-1187 Story-1 — 운영 phase 1st-class 정의)
  - CFP-1187  # umbrella Epic — 운영 phase 신설
created: 2026-05-22
updated: 2026-05-22
---

# 운영 phase — narrative SSOT hub

본 디렉토리 = codeforge 의 **운영 phase 서술적 elaboration narrative SSOT** (CFP-1190 carrier, Epic CFP-1187 Story-1). ADR-104 가 normative SSOT 이고 본 4 파일 은 그 해설 (서술) 이다 — ADR 이 결정, domain-knowledge 가 해설.

## 운영 phase 정의 (1-2 문단)

**운영 phase** = 배포검토(deploy-review) lane 이 끝난 *이후* 시간축에서 **지속(ongoing)** 으로 배포 때 약속한 성능·안정성이 실제 지켜지는지 신호를 회수하는 단계. "한 번 끝나는" 배포검토와 달리, 운영 phase 는 **계속 도는** 구조다 (ADR-104 §결정 1).

운영 phase 는 codeforge 의 **9번째 lane 이 아니다**. lane 은 "Story 가 들어가 종료 게이트를 통과하고 끝나는" Story-scoped delta 구조인데, 운영 phase 의 시간축 ongoing 성격은 이 구조에 들어맞지 않는다. 따라서 운영 phase 는 **mechanism layer** (monitor / alert / 자동 Issue 생성 — cron workflow / filesystem signal) 로 실현된다 (ADR-104 §결정 2). "운영 phase" 라는 이름이 붙어 있지만, lane plugin 신설 없이 mechanism 으로 존재한다.

## 이 디렉토리의 3 파일

| 파일 | 핵심 주제 |
|---|---|
| [`operational-phase-definition.md`](operational-phase-definition.md) | release lifecycle 위치 + "한 번 끝나는" vs "계속 도는" 경계 + lane 아님(mechanism layer) + ongoing ↔ Story flow mismatch 해소 + scope |
| [`measurement-channel.md`](measurement-channel.md) | 0 API call constraint + 측정 신호 enum (에러율 / latency burn rate / regression / smoke·health) + wrapper-self-app N/A invariant |
| [`self-improving-loop.md`](self-improving-loop.md) | 운영 신호 → 자동 Issue → PMOAgent escalation → 다음 Epic 후보 회로 + 무한 발산 위험 식별 + loop closure gate (S6 carrier) |

## ADR-104 cross-ref

본 디렉토리 전체의 normative SSOT = [`docs/adr/ADR-104-operational-phase-definition.md`](../../../adr/ADR-104-operational-phase-definition.md).

- §결정 1 — release lifecycle 위치 (배포 → 배포검토 → 운영 phase) → `operational-phase-definition.md §1`
- §결정 2 — lane 아님 (mechanism layer) → `operational-phase-definition.md §3`
- §결정 3 — 0 API call constraint → `measurement-channel.md §1`
- §결정 4 — wrapper-self-app N/A invariant → `measurement-channel.md §3`
- §결정 5 — self-improving loop + loop closure gate 위험 → `self-improving-loop.md §1·§4`

## 운영 phase = mechanism layer (lane 아님) — 한 줄 anchor

> **운영 phase 는 lane 이 아니라 mechanism layer 다** — monitor / alert / 자동 Issue 생성 mechanism (cron workflow / filesystem signal) 으로 실현된다. lane count 변경 0, `phase:운영` label 신설 불요 (ADR-104 §결정 2, ADR-023 lane count invariant 정합).
