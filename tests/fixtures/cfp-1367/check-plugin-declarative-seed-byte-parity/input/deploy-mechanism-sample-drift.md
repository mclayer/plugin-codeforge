---
title: deploy-mechanism plugin sample (drift case — F1 byte-parity fixture)
type: fixture
---

# Deploy Mechanism — plugin declarative seed (DRIFTED)

## deploy

```yaml
deploy:
  mechanism: blue-green
  swap_window_seconds: 10800
  rollback_enabled: true
  health_check_path: /health
  environment: production
  extra_field_drift: unexpected_value
```

### Required fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deploy.mechanism` | string | yes | Deployment mechanism (blue-green / rolling / canary) |
| `deploy.swap_window_seconds` | integer | yes | Retention window in seconds |
| `deploy.rollback_enabled` | boolean | yes | Auto-rollback on health check failure |
| `deploy.extra_field_drift` | string | no | DRIFTED field not in wrapper SSOT |
