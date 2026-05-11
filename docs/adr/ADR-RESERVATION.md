---
adr_number: null
title: ADR 踰덊샇 ?덉빟 ?덉??ㅽ듃由?(GitOpsAgent ?꾩슜 ?댁쁺 ?덉??ㅽ듃由?
status: Active
category: governance
date: 2026-05-09
carrier_story: CFP-344
related_adrs:
  - ADR-050
related_files:
  - docs/parallel-work/section-ownership.yaml
  - templates/github-workflows/parallel-epic-conflict-check.yml
---

# ADR 踰덊샇 ?덉빟 ?덉??ㅽ듃由?
## ?곹깭

Active (2026-05-09) ??ADR-050 짠寃곗젙 1 援ы쁽. GitOpsAgent ?꾩슜 sequential append ?덉??ㅽ듃由?

## 而⑦뀓?ㅽ듃

蹂듭닔 Orchestrator ?몄뀡???숈떆???쒕줈 ?ㅻⅨ ?먰뵿??吏꾪뻾???????몄뀡??媛숈? ADR 踰덊샇濡??뚯씪???앹꽦?섎뒗 異⑸룎??諛쒖깮?쒕떎 (ADR-048 以묐났 ?щ? ?ㅼ쬆). ADR-050 짠寃곗젙 1?먯꽌 ??臾몄젣瑜??닿껐?섍린 ?꾪빐 蹂??덉??ㅽ듃由щ? ?좎꽕?덈떎.

**Write 二쇱껜**: GitOpsAgent ?꾩슜 (sequential append).
**異⑸룎 ?댁냼**: ???몄뀡 ?숈떆 append ??git merge positional conflict ??GitOpsAgent媛 adr_number ?ㅻ쫫李⑥닚 re-sort.

## 寃곗젙

GitOpsAgent媛 蹂??덉??ㅽ듃由щ? ?듯빐 ADR 踰덊샇瑜??먯옄?곸쑝濡??덉빟?쒕떎.

### ?덉빟 ?덉감

1. ArchitectAgent媛 ADR ?꾩슂 ?좏샇 諛쒖떊
2. GitOpsAgent媛 留덉?留?`adr_number` + 1??append ??commit
3. ArchitectAgent媛 ?덉빟??踰덊샇濡?`ADR-NNN-*.md` ?앹꽦
4. ADR merge ?꾨즺 ??`status: reserved ??active`濡?媛깆떊

### ?덉??ㅽ듃由?YAML ?ㅽ궎留?
```yaml
reservations: []
# ?뺤떇:
# - adr_number: NNN
#   epic: CFP-XXX
#   status: reserved   # reserved | active | archived
#   reserved_at: ISO8601
```

## 寃곌낵

### ?꾩옱 ?덉빟 紐⑸줉

| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 50 | CFP-344 | active | 2026-05-09 |
| 51 | CFP-343 | active | 2026-05-09 |
| 54 | CFP-363 | active | 2026-05-10 |
| 55 | CFP-367 | reserved | 2026-05-10 |
| 56 | CFP-374 | active | 2026-05-11 |

### 踰덊샇 ?댁젣 (archived)

ADR deprecated/superseded ???대떦 row `status: archived`. 踰덊샇 ?ъ궗??湲덉?.

## 愿???뚯씪

- [ADR-050](ADR-050-parallel-epic-conflict-coordination.md) ??蹂??덉??ㅽ듃由?寃곗젙??carrier ADR
- `docs/parallel-work/section-ownership.yaml` ??ADR-050 짠寃곗젙 4 (locked ?뱀뀡 ?좎뼵)
- `templates/github-workflows/parallel-epic-conflict-check.yml` ??ADR-050 짠寃곗젙 3 (?먮룞 異⑸룎 媛먯?)

