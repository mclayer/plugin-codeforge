## 10. Hotfix 경로 (운영 장애 대응)

정상 7-레인 full flow 는 Story 1건당 반나절~수일 소요. 운영 장애로 즉시 대응 필요한 경우 **Minimal Path** (`severity:bug`, ≤30 lines) 또는 **Medium Path** (`severity:critical`, multi-file) 중 하나 선택. 어느 경로든 **사후 감사 (next working session 자동 수행) 의무**.

상세 = [`docs/hotfix-playbook.md`](hotfix-playbook.md) (CFP-93, P2-9 follow-up — cognitive overhead reduction 목적으로 별도 분리). mctrader debut audit (Issue #181 P2-9) 까지 사용 사례 0 — 본 경로는 첫 운영 장애 발생 시 활성화.

---

