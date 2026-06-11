# K8s preset (CFP-128 / ADR-033)

InfraEngineerAgent 가 consumer overlay project.yaml 의 `infra_strategy_extras.k8s_preset_enabled: true` 일 때 활성.

## 활성 절차

1. consumer project.yaml 에 추가:
   ```yaml
   infra_strategy: docker_first  # 1st-class Dockerfile + compose
   infra_strategy_extras:
     k8s_preset_enabled: true    # K8s manifests 동반 산출
   ```

2. consumer repo 의 `k8s/` 또는 `deploy/k8s/` directory 에 본 preset 의 3 template 복사:
   ```bash
   cp ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/k8s/*.yaml.template k8s/
   ```

3. 각 template 의 placeholder 치환:
   - `{app_name}` — service name
   - `{namespace}` — K8s namespace
   - `{image_ref}` — registry image (e.g. `ghcr.io/org/repo:tag`)
   - `{replicas}` — replica count
   - `{host}` — Ingress hostname

4. `kubectl apply -f k8s/`

## 파일 목록

- `deployment.yaml.template` — Deployment with liveness/readiness probes + resource limits
- `service.yaml.template` — ClusterIP Service
- `ingress.yaml.template` — NGINX Ingress

## InfraEngineerAgent 책임

- Story §3 도입할 설계 에 K8s preset 활성 명시 시 본 preset 의 template 을 consumer repo 에 복사
- placeholder 치환 (consumer overlay context 활용)
- consumer-specific 변경 (resource limits / replica count / probe path) 적용
- `compose.yml` (dev) + `k8s/*.yaml` (prod) 짝꿍 maintain

## 거부된 대안

- Helm chart 형태 — 학습 곡선 + dependency, 단순 K8s manifest preferred
- Kustomize overlay — overlay-on-overlay 복잡도, single template + placeholder 채택
