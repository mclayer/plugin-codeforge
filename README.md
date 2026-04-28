# codeforge-requirements

[`codeforge`](https://github.com/mclayer/plugin-codeforge) ζ arc CFP-37 — Requirements lane plugin.

4 sub-agent 병렬 (Domain · Analyst · Researcher) → RequirementsPLAgent 통합. ζ arc writer-distributed 모델로 Story §2/§5/§6 + Domain Knowledge 직접 write.

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 2.0.0). 단독 동작 불가 — codeforge wrapper 의 Orchestrator 가 RequirementsPLAgent 를 스폰.

**필수 CLI**: `codex` — RequirementsAnalystAgent 가 `codex exec -m gpt-5.4` 호출.

본 plugin SessionStart hook 이 codeforge core 설치 + codex CLI 가용성 verify.

## 설치

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-review@mclayer": true,
    "codeforge-pmo@mclayer": true,
    "codeforge-requirements@mclayer": true
  }
}
```

## Architecture

RequirementsPLAgent 는 다음을 PL 산하 sub-agent 병렬 dispatch:
- **DomainAgent**: docs/domain-knowledge/** + docs/adr/** + 도메인 코드 + Story §1 4소스 → 도메인 지식 공백 분석. 공백 발견 시 KB 파일 직접 write
- **RequirementsAnalystAgent**: codex exec gpt-5.4 호출 → ambiguity / 암묵 가정 / 누락 / AC 도출
- **ResearcherAgent**: 웹 / 논문 / 공급사 문서 → 외부 기술·표준·선행사례 인용

PL 이 dedup·상충 조정 후 Story §2/§5/§6 동시 채움 + [요구사항] prefix comment + phase:요구사항 → phase:설계 transition.

## Inter-plugin Contract

`requirements_output v1` — `docs/inter-plugin-contracts/requirements-output-v1.md` (canonical). codeforge wrapper 측 sibling reference 동기 의무.

## ζ arc 위치

CFP-37 — codeforge ζ arc 세 번째 lane plugin (review v2 retrofit + pmo 다음). 4 agent 추출 + 도메인 KB owner write 이전이 본 plugin 의 특이점.
