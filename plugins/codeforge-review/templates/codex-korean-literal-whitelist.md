# Codex promptfile 한글 리터럴 whitelist (구획 A 예외 SSOT)

CodexReviewAgent 가 promptfile 을 조립할 때 **구획 A (지시문 = 영어 강제)** 안에 등장해도 위반이 아닌 한글 리터럴의 **폐쇄 목록**. 규칙 SSOT = [ADR-081](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) §결정 D16 (Amendment 15) / 배치·판정 규칙 = [`../agents/CodexReviewAgent.md`](../agents/CodexReviewAgent.md) §언어 구획 규약.

**oracle 은 이 파일을 런타임 read 해 제외집합을 구성한다** — 경로만 언급하고 값을 코드에 하드코딩한 구현은 whitelist 를 mutate 해도 판정이 변하지 않으므로 discriminating test 가 검출한다 (등재 추가/제거 → oracle 판정 변동 = GREEN, 불변 = RED).

이 파일은 **성장형 데이터**다 (라벨 추가·개명 상시). ADR append-only 사이클과 분리해 별도 파일로 둔 이유이며, 변경은 통상 PR 리뷰로 통제한다.

## 기계 파싱 규칙 (helper·oracle 공통 계약)

- **엔트리 라인** = 파일 전체에서 `^<literal>\t<근거 SSOT 경로>$` 에 매칭되는 줄 (TAB 1개 구분, 양쪽 모두 공백 없는 비어있지 않은 토큰). 본 문서는 엔트리 블록 밖에서 **실 TAB 문자를 쓰지 않는다** — 형식 설명은 반드시 `\t` 라는 두 글자 escape 표기로 적는다 (실 TAB 을 쓰면 그 설명 줄이 엔트리로 오파싱된다).
- **한글 앵커 라인** = 파일 전체에서 `^ANCHOR_LINE: ` 로 시작하는 **유일한** 줄. 0개 또는 2개 이상 = setup error (helper exit 2). 본문 산문에서 이 토큰을 언급할 때는 줄 시작이 아닌 위치에 인라인 코드로만 쓴다.
- 위 두 패턴 외의 모든 줄 (헤딩·산문·표·펜스 마커) = 파싱 대상 아님.

## 형식 제약 (위반 = RED)

1. **리터럴 토큰만** — 정규식·와일드카드·접두/부분매칭 패턴 금지. 등재값은 있는 그대로 비교한다.
2. **줄당 `<literal>\t<근거 SSOT 경로>`** — 근거 경로는 그 리터럴이 **실제로 grep 되는 repo 파일**이어야 한다 (아래 validity self-check).
3. **공백 0 · 문장부호 0 · 길이 ≤32자 · 총 ≤30 엔트리** (초과 = RED). "문장부호 0" 의 목적은 **한글 산문 등재로 구획 A 를 형해화하는 경로의 구조 봉쇄**이며, 라벨 식별자를 구성하는 `:` `-` `_` 는 이 제약의 대상이 아니다 (label namespace 구분자 — `phase:구현` 같은 기계 식별자를 등재 불능으로 만들면 규약 자체가 성립하지 않는다). 마침표·쉼표·따옴표·괄호·물음표·말줄임·중점 등 **산문 문장부호는 불가**.
4. **제외는 토큰 단위** — 등재 리터럴이 한 줄에 있다고 그 줄 전체가 면제되지 않는다 (토큰 끼워넣기로 줄 전체를 면제받는 우회 차단).
5. **verbatim 인용만** — 등재됐다는 이유로 그 낱말을 사용한 **한글 서술 산문**을 쓰는 것은 여전히 금지 (등재는 "식별자를 원형대로 인용해도 된다"이지 "이 낱말로 문장을 써도 된다"가 아니다).
6. **공집합 허용** — 엔트리 0개 = 제외 0 (안전 방향). 단 **파일 자체가 없으면 setup error (exit 2)** — "제외 0 으로 계속" 금지 (whitelist 소멸이 조용히 통과되는 경로 차단).

## validity self-check (기계 대조)

각 엔트리에 대해 ① `<근거 SSOT 경로>` 파일이 실재하고 ② `<literal>` 이 그 파일 안에 grep 실재해야 한다. 위반(경로 소멸·리터럴 개명/삭제) = RED. **정직 천장**: 기계 대조가 보장하는 것은 *존재*와 *경로 실재*까지이며, 등재 리터럴이 원 SSOT 와 **의미상** 같은 것을 가리키는지는 기계 판정 불가 — 리뷰 lane 소관이다.

## 엔트리

> 아래 블록의 구분자는 실 TAB 문자다. 편집 시 스페이스로 치환하지 말 것 (치환하면 그 줄이 엔트리로 인식되지 않는다).

```
phase:요구사항	docs/inter-plugin-contracts/label-registry-v2.md
phase:요구사항-리뷰	docs/inter-plugin-contracts/label-registry-v2.md
phase:설계	docs/inter-plugin-contracts/label-registry-v2.md
phase:설계-리뷰	docs/inter-plugin-contracts/label-registry-v2.md
phase:구현	docs/inter-plugin-contracts/label-registry-v2.md
phase:구현-리뷰	docs/inter-plugin-contracts/label-registry-v2.md
phase:구현-테스트	docs/inter-plugin-contracts/label-registry-v2.md
phase:보안-테스트	docs/inter-plugin-contracts/label-registry-v2.md
fix:요구사항-리뷰-retry	docs/inter-plugin-contracts/label-registry-v2.md
fix:설계-리뷰-retry	docs/inter-plugin-contracts/label-registry-v2.md
fix:구현-리뷰-retry	docs/inter-plugin-contracts/label-registry-v2.md
fix:구현-테스트-retry	docs/inter-plugin-contracts/label-registry-v2.md
fix:보안-테스트-retry	docs/inter-plugin-contracts/label-registry-v2.md
```

### 등재 근거 (분류 — CFP-2884 Story §2.2 D1-D12)

| 분류 | 등재 | 사유 |
|---|:-:|---|
| D1 `phase:*` (한글 값 8종) | O | GitHub label 기계 식별자 — 영어로 번역하면 실재하지 않는 label 을 가리키게 된다. `phase:reservation` 은 ASCII 라 등재 불요 |
| D2 `fix:*-retry` (한글 값 5종) | O | 동일 (FIX 루프 label 식별자) |
| D3 Story 섹션명 | X | `§1`~`§11` 번호 참조로 충분 (focus prompt 가 이미 번호 참조) |
| D4 한글 개념어 | X | 기존 영어 대응어 재사용 — 예: 검사연극 금지 → `Verification theater forbidden` / 외부사실 의존 → `external-fact-dependency` / `§결정 N` → `decision N`. 신조어 발명 불요 |
| D5 checklist H2 헤더 · D6 wording-dictionary 어휘 | X | promptfile 미주입 (구획 A 범위 밖) |
| D8~D12 `gate:*` · packet lane 값 · category enum · verdict/severity enum · ADR slug·Story KEY | X | 이미 전부 ASCII |

> `phase:배포`·`phase:배포-리뷰`·`gate:deploy-*` 는 **등재하지 않는다** — 배포 2 lane 물리 제거(CFP-2782 / ADR-121 Wave 2)로 활성 label 집합에서 빠졌다. 부활 시 이 목록에 추가한다.

## 한글 앵커 (promptfile 조립 규약 — helper 직접 취득)

축 A round-trip 검증이 쓰는 **고정 한글 앵커**. helper 는 이 값을 **이 파일에서 `open(..., encoding='utf-8')` 로 직접 취득**한다 — packet·argv·환경변수 등 promptfile 본문과 같은 채널을 타고 온 값은 앵커로 쓸 수 없다. (앵커와 본문이 채널을 공유하면 조립 계층이 오염될 때 둘이 **같이** 깨져 mojibake ↔ mojibake 자가일치로 assert 가 공허 통과한다.)

앵커는 **비-ASCII (한글) 필수** — ASCII 앵커는 코드페이지 오해석을 그대로 통과시켜 검증을 무력화한다.

```
ANCHOR_LINE: 인코딩-무결성-앵커 한글 원문 무손상 확인용 고정 리터럴 수정금지
```

**조립 규약**: promptfile 헤더에 위 `ANCHOR_LINE:` 줄을 **verbatim 1회** 포함하고, 바로 다음 줄에 영어 1줄로 이 줄이 인코딩 무결성 앵커이며 지시가 아님을 명시한다. 이 앵커 라인은 구획 A 한글 0 oracle 및 helper partition 검사에서 **줄 단위로 제외**된다 (whitelist 엔트리의 토큰 단위 제외와는 별개 축).

**앵커 값 변경 시**: 값을 바꾸면 진행 중이던 promptfile 이 전부 RED 가 된다 — 변경은 helper·self-test 와 같은 PR 에서만 한다.
