---
title: deploy-mechanism plugin sample (parity case — F1 byte-parity fixture)
type: fixture
---

# Deploy Mechanism — plugin declarative seed

## deploy

```yaml
deploy:
  mechanism: blue-green
  swap_window_seconds: 10800
  rollback_enabled: true
  health_check_path: /health
  environment: production
```

### Required fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deploy.mechanism` | string | yes | Deployment mechanism (blue-green / rolling / canary) |
| `deploy.swap_window_seconds` | integer | yes | Retention window in seconds (default: 10800 = 3h) |
| `deploy.rollback_enabled` | boolean | yes | Auto-rollback on health check failure |
| `deploy.health_check_path` | string | yes | Health check endpoint path |
| `deploy.environment` | string | yes | Target environment (production / staging / development) |
