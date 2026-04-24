# library-minimal — 배포 가능 라이브러리 consumer 예시

패키지 매니저로 배포되는 라이브러리 프로젝트를 `codeforge` 플러그인으로 개발할 때의 overlay 구성 예시. 가상 도메인은 **Schema Guard** (데이터 → 스키마 validator 라이브러리), 기술 스택은 consumer가 채움.

## Dev roster

**preset 미사용**. core generic agent만으로 구성:
- `DeveloperAgent` (core) — 공개 API·내부 로직·타입·문서 주석
- `InfraEngineerAgent` (core) — 패키징·릴리스·semver·배포 (PyPI/crates.io/npm/Maven 등)
- `QADeveloperAgent` (core) — tests/**

## Preset이 없는 이유

라이브러리 shape는 **Dev 역할 단일**이 기본. Frontend 없고, 특화된 병렬 분업 포인트 없음. webapp preset의 Backend+Frontend 같은 분할이 이 shape에선 과잉.

필요 시 consumer overlay에서 역할 분할 가능:
- `PublicAPIDeveloperAgent` (공개 API만 담당, semver 의무)
- `InternalImplDeveloperAgent` (내부 구현, 자유롭게 변경 가능)

## 구조

```
library-minimal/
├── README.md
├── .claude/
│   ├── settings.json
│   └── _overlay/
│       ├── project.yaml                     # SSOT 상수
│       ├── CLAUDE.md                        # narrative
│       └── agents/
│           ├── DomainAgent.md               # 라이브러리 도메인·API 안정성 원칙
│           └── DeveloperAgent.md            # 공개/내부 경로 scoping
└── .gitignore
```

## 적용 단계

### 1. 복사 · 플레이스홀더 치환

```bash
cp -r examples/library-minimal/ ~/my-library/
cd ~/my-library
```

`.claude/_overlay/project.yaml`의 `<REPLACE — ...>` 치환.
`.claude/_overlay/CLAUDE.md`의 `<REPLACE: ...>` 치환 (기술 스택·언어).

### 2. 세션 시작

```bash
claude
ls .claude/agents/
# DeveloperAgent.md, InfraEngineerAgent.md, QADeveloperAgent.md + process agents
# Frontend 없음 확인
```

## 라이브러리 특화 포인트

### 공개 API vs 내부 구현 분리

라이브러리의 **공개 API는 semver 계약**이므로 변경 민감도가 높음. DeveloperAgent overlay에서 경로 scoping 권장:
- `src/<lib>/public/**` 또는 `src/<lib>/__init__.py` 등 — 공개 surface
- `src/<lib>/internal/**` — 자유 리팩터링 가능

Change Plan §3에서 "공개 API 변경 시 semver bump 필수 + deprecation path"를 설계 의무로 명시.

### InfraEngineer 범위 = 패키징·릴리스

웹 서비스의 "배포"가 아닌 **릴리스 자동화**:
- `pyproject.toml` / `Cargo.toml` / `package.json` 관리
- `CHANGELOG.md` 자동화
- GitHub Actions `on: release` 워크플로우
- pre-release 지원 (alpha/beta/rc tag)

### Frontend 없음 → UI/UX 관심사 대체

- CodeReview에서 공개 API 디자인 (예: 인자 이름·기본값·에러 타입) 체크
- 문서화 (docstring·README·API reference)를 DocsAgent + CodeReview가 공동 검증
