# ADR 번호 예약 레지스트리

**Write 주체**: GitOpsAgent 전용 (sequential append).
**충돌 해소**: 두 세션 동시 append → git merge positional conflict → GitOpsAgent가 adr_number 오름차순 re-sort.

```yaml
reservations: []
# 형식:
# - adr_number: NNN
#   epic: CFP-XXX
#   status: reserved   # reserved | active | archived
#   reserved_at: ISO8601
```

## 예약 절차

1. ArchitectAgent가 ADR 필요 신호 발신
2. GitOpsAgent가 마지막 `adr_number` + 1을 append → commit
3. ArchitectAgent가 예약된 번호로 `ADR-NNN-*.md` 생성
4. ADR merge 완료 후 `status: reserved → active`로 갱신

## 현재 예약 목록

| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 50 | CFP-344 | active | 2026-05-09 |

## 번호 해제 (archived)

ADR deprecated/superseded 시 해당 row `status: archived`. 번호 재사용 금지.
