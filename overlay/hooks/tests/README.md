# merge.py tests

`overlay/hooks/merge.py`의 core+overlay 병합 계약 검증.

## 실행

```bash
pip install pyyaml pytest
pytest overlay/hooks/tests/ -v
```

## 커버리지

- `split_frontmatter` / `dedup_list` / `deep_merge` / `merge_frontmatter` 헬퍼
- `render_frontmatter` / `auto_header` 렌더러
- E2E (subprocess 호출): 정상 flow · 식별 스칼라 mismatch abort · overlay 없음/빈 본문 · malformed frontmatter · idempotency · 사용법 오류

계약 상세는 [`../../../docs/plugin-design.md`](../../../docs/plugin-design.md) §4 참조.
