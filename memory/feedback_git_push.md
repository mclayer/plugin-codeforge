---
name: Git 브랜치 및 push 전략
description: feature 브랜치 사용, main 직접 push 금지, push는 확인 없이 바로 수행
type: feedback
---

항상 feature 브랜치를 만들어서 push한다. main 직접 push는 hook으로 차단되어 있음.

브랜치 네이밍: `feat/`, `fix/`, `chore/` 등 prefix 사용.

push 자체는 확인 없이 바로 수행한다.

**Why:** main 직접 push hook 차단 + 사용자가 feature branch 방식 선택.

**How to apply:** 작업 시작 시 feature 브랜치 생성 → 커밋 → 브랜치 push. MR은 사용자가 별도 요청 시 생성.
