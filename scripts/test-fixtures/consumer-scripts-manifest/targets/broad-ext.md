# CFP-2408 fixture target — 광역확장자 .md (non-exec, git index 100644)

말단확장자 = `.md` 는 allowlist(`.tsv`/`.mjs` 2종)에 없음 → 면제 안 됨 →
Check 4 strict branch → non-exec FAIL. 광역 allowlist(`.md`/`.txt`/`.json` 등)
면제 회귀를 부정하는 mutation-kill fixture (`fail-broad-ext-md`).
