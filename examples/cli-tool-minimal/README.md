# cli-tool-minimal — CLI 툴 consumer 예시

단일 바이너리 CLI 툴 프로젝트를 `codeforge` 플러그인으로 개발할 때의 overlay 구성 예시. 가상 도메인은 **Log Parser** (로그 파일 → 구조화 이벤트 추출), 기술 스택은 consumer가 채움.

## Dev roster

**preset 미사용**. Core의 generic agent만으로 구성:
- `DeveloperAgent` (core) — CLI 명령·파서·도메인 로직
- `InfraEngineerAgent` (core) — 패키징·릴리스 자동화
- `QADeveloperAgent` (core) — tests/**

프론트엔드·데이터 파이프라인 에이전트 **불필요** → DevPL은 roster에 포함 안 함 (동적 discovery).

## 구조

```
cli-tool-minimal/
├── README.md
├── .claude/
│   ├── settings.json                          # SessionStart hook 등록
│   └── _overlay/
│       ├── CLAUDE.md                          # 프로젝트 SSOT 상수
│       └── agents/
│           ├── DomainAgent.md                 # CLI 도메인 용어·로그 포맷 제약
│           └── DeveloperAgent.md              # CLI 경로 관습
└── .gitignore
```

## 적용 단계

### 1. 복사 · 플레이스홀더 치환

```bash
cp -r examples/cli-tool-minimal/ ~/my-cli/
cd ~/my-cli
```

`.claude/_overlay/CLAUDE.md`의 `<REPLACE: ...>` 치환 (프로젝트명·기술 스택). GitHub·labels 등 objective 상수는 `.claude/_overlay/project.yaml` 별도 편집.

### 2. Overlay 커스터마이즈

`DeveloperAgent` overlay에 본인 CLI 프레임워크 명시 (click/typer/clap/cobra 등), 경로 관습 반영.

### 3. 세션 시작

```bash
claude
ls .claude/agents/
# DeveloperAgent.md, InfraEngineerAgent.md, QADeveloperAgent.md + process agents
# Backend/Frontend/DataEng 없음 확인
```

## 생성 결과 예측

- `.claude/agents/DeveloperAgent.md` → core body + overlay body (CLI 경로 관습)
- `.claude/agents/InfraEngineerAgent.md` → core body (overlay 없음 — 기본으로 충분)
- `.claude/agents/DataEngineerAgent.md` → core body (존재하지만 DevPL이 Change Plan에서 해당 경로 변경 없으면 스폰 안 함)
- Backend/Frontend preset agent → 없음 (consumer가 복사 안 했음)

## CLI 툴 특화 포인트

- **Frontend 없음** → UI/UX 리뷰는 CLI help text·에러 메시지 품질로 대체 (CodeReview에서 체크)
- **DB/저장소 선택적** → 상태 유지 CLI는 `~/.config/<tool>/` 같은 설정 파일만 쓰는 경우가 많음. DataEng 개입 불필요
- **배포 = 패키징** → InfraEng이 systemd 대신 pyproject/Cargo/homebrew/release 자동화 담당

## 다른 shape로 확장

- Library (임포트 가능 모듈): `InfraEng`을 빼고 `DeveloperAgent` + `QADev`만으로 운영
- TUI (curses 기반 인터랙티브): `DeveloperAgent`에 화면 렌더링 경로 추가
- 시스템 데몬: `InfraEng` 역할 확대 (systemd unit·로그 로테이션 등)
