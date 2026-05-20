# CFP-1104 Phase 2 Spec Verify Report

**작성일**: 2026-05-20  
**담당**: Claude Code Exploration (READ-ONLY)  
**상태**: 완료 (전수 File Read 기반)

---

## Task A — plugin-codeforge-design 현 ArchitectLane 10 agent file 어휘 verify

**위치**: `/c/workspace/mclayer/plugin-codeforge-design/agents/` (10 file 전수 확인)

### Frontmatter + 어휘 현황

| Agent | Current vocabulary (literal) | DDD Hit | Proposed DDD role |
|-------|---|---|---|
| ArchitectPLAgent | "deputy 6인 + chief author 1인을 조율" | 0 | Authority Pair (PL) |
| ArchitectAgent | "Change Plan §1-§11 author" | 0 | Authority Pair (chief author) |
| CodebaseMapperAgent | "사실 변호자" | 0 | Domain Service |
| RefactorAgent | "리팩터링 옹호자" | 0 | Domain Service |
| SecurityArchitectAgent | "보안 변호자" | 0 | Domain Service |
| TestContractArchitectAgent | "QA perspective contributor" | 0 | Domain Service |
| DataMigrationArchitectAgent | "데이터 무결성 advocate" | 0 | Domain Service |
| OperationalRiskArchitectAgent | "운영 리스크 advocate" | 0 | Domain Service |
| LiveOpsDeputyAgent | "Live ops discipline deputy" | 0 | Subdomain Specialist |
| LiveOrderingDeputyAgent | "Live order lifecycle deputy" | 0 | Subdomain Specialist |

**분석**: DDD 어휘 0건 — 현 vocabulary 절차적 강화 구조 유지 + DDD metaphor layer 별도 추가 권고.

---

## Task B — mctrader-hub ADR-031 golden-path 시연 적합성

**위치**: `/c/workspace/mclayer/mctrader-hub/docs/adr/ADR-031-data-domain-decoupling.md` (623 lines)

### Verify 항목

| 항목 | Result | Value | Note |
|------|--------|-------|------|
| File 실재 | ✅ | 존재 | 623 lines |
| 4-Layer section | ✅ | L499-524 | "4-Layer 의존 모델" 명확 |
| OHS 패턴 | ⚠️ | 부분 | adapters.py factory (OHS equivalent) |
| ACL 패턴 | ❌ | 부재 | data REST boundary (ACL equivalent but unlabeled) |
| Cross-ref ADR | ✅ | 44회 | ADR-029/030/032 abundance |

**적합도**: ⭐⭐⭐⭐⭐ (4-Layer 명확, OHS/ACL refinement 기회)

---

## Task C — plugin-codeforge CFP 번호 검사

### 최신 issue

| CFP | Status |
|-----|--------|
| 1106 | Used |
| 1105 | Unknown |
| 1104 | ✅ AVAILABLE (current worktree) |
| 1103 | Used |

### counters.json

**Result**: ❌ NOT FOUND (manual tracking 중)

**권고**: CFP-1104 예약 확정 + counter 재도입 검토.

---

## Task D — ADR amendment 대상 7건 검사

| ADR | Status | Amendment | Deputy Hit | Impact |
|-----|--------|-----------|-----------|--------|
| **004** | Accepted | 0 | 7회 | ⭐⭐⭐⭐⭐ Foundation |
| **006** | Accepted | 0 | 11회 | ⭐⭐⭐⭐⭐ High |
| **007** | Accepted | 0 | 9회 | ⭐⭐⭐⭐⭐ High |
| **014** | Adopted | 0 | 38회 | ⭐⭐⭐⭐⭐ Critical |
| **064** | Accepted | 4 amend | 0회 | ⭐⭐⭐ Medium |
| **068** | Accepted | 1 amend | 0회 | ⭐⭐⭐ Medium |
| **080** | Active | 0 | 37회 | ⭐⭐⭐⭐ Terminology |

**핵심 발견**:
- ADR-004/006/007: 기초 구조 확정 ✅
- ADR-014: **Amendment 2 필수** (OpRiskArch role clarify + LiveOps/LiveOrdering CONDITIONAL trigger)
- ADR-080: terminology standard 적용 의무

---

## 최종 권고

**CFP-1104 Phase 2 GO**: ✅ **YES with 2 preconditions**

1. **ADR-014 Amendment 2 (Pre-spec or concurrent)**:
   - OperationalRiskArchitectAgent role boundary 확정
   - LiveOps/LiveOrdering CONDITIONAL spawn trigger 명문화

2. **Phase 2 Spec Scope**:
   - Agent file vocabulary → DDD metaphor layer integration
   - ADR-031 4-Layer → golden-path annotation
   - Deputy mandate matrix v2 (current state capture)
   - Amendment batch (ADR-004/006/007/014/080 touch-up)

**예상 labor**: 6-9h (concurrent 시 4-5h)

---

**Report Generated**: 2026-05-20 / Verified via direct Read + Grep operations

