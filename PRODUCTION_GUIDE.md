# Waiter Production Guide

This document is designed for both:

- non-technical stakeholders (owners, managers, operations teams)
- technical stakeholders (developers, DevOps, SRE, security reviewers)

---

## 1) Executive Summary (Non-Technical)

`Waiter` is a QR-based restaurant ordering platform with:

- contactless customer ordering from table QR codes
- live kitchen/order updates
- dashboard for staff operations
- optional AI assistants for customer/staff interactions

### What this means for business

- Faster order intake
- Fewer manual errors
- Better table turnaround visibility
- Live status transparency for guests
- Operational visibility from one dashboard

### Go-Live Checklist (Business)

- Menu data finalized and reviewed
- Tables created and QR codes printed/tested
- Staff trained on dashboard workflow
- Order status SOP defined (Pending -> Accepted -> Making -> Completed/Rejected)
- AI usage policy approved (if enabled)
- Support contacts and escalation matrix prepared

---

## 2) System Overview (Technical + Business)

### Primary user flows

1. Staff creates restaurant/tables/categories/menu
2. Customer scans table QR and browses menu
3. Customer places order
4. Staff receives order live and updates status
5. Customer receives status updates in real time
6. AI (optional) assists both sides via constrained tools

### What we are building

This project is an operational platform for dine-in restaurants:

- guests order from table QR codes
- kitchen/staff get live order signals
- order lifecycle is standardized and trackable
- AI assists both customer and staff workflows

### How the system works end-to-end

Customer journey:

1. Scan table QR
2. Open table menu page
3. Add items to cart and place order
4. Receive live order updates in browser

Staff journey:

1. Open dashboard order board
2. See incoming orders in real time
3. Update status (`PENDING -> ACCEPTED -> MAKING -> COMPLETED/REJECTED`)
4. Customer receives status update instantly

AI journey:

1. Chat endpoint receives message
2. Application service builds menu/order context
3. LLM may call restricted tools
4. Tool executes DB/realtime action
5. Response returns to UI; session-safe history is persisted

### Engineering approach used in this project

- app-level domain boundaries (`accounts`, `restaurants`, `orders`, `agent`)
- layered architecture (`interfaces`, `application`, `domain`, `infrastructure`)
- compatibility-first migration (legacy `common` facades preserved temporarily)
- non-breaking refactor policy (behavior parity before cleanup)

### Core modules

- `accounts`: auth, profiles, chain context
- `restaurants`: restaurant/table/category/menu management
- `orders`: order lifecycle + websocket broadcast
- `agent`: AI orchestration and tool calls
- `shared`: cross-cutting reusable contracts/utilities
- `common`: compatibility shell and route namespace during migration

---

## 3) Production Architecture (Technical)

Recommended production topology:

- Web app: Django ASGI app (served by `daphne`/ASGI runtime)
- Reverse proxy: Nginx / managed ingress
- Database: PostgreSQL
- Channel layer: Redis (required for multi-instance realtime)
- Background workers: optional Celery workers + Redis broker
- Vector store (AI): Qdrant (managed or self-hosted)
- Object storage: S3-compatible bucket for media
- Static files: collected and served via CDN or web tier

### Minimal reliable deployment stack

- 2+ app instances behind load balancer
- Managed PostgreSQL with backups
- Managed Redis for channels
- Health checks + restart policy
- Centralized logs and alerts

---

## 4) Environment Variables (Production)

Required:

- `DJANGO_SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=<comma-separated>`
- `BASE_URL=<public-domain>`
- `GEMINI_API_KEY` (if AI endpoints are enabled)

Strongly recommended:

- `CSRF_TRUSTED_ORIGINS=https://<domain>`
- storage credentials (`AWS_STORAGE_*`) when using object storage
- observability keys (Sentry/APM) if configured

Operational note:

- do not commit `.env`
- use secret manager (Vault, AWS Secrets Manager, Render secrets, etc.)

---

## 5) Pre-Production Validation (Technical)

Before release:

```bash
python3 manage.py check
python3 manage.py migrate --plan
python3 manage.py test
python3 manage.py collectstatic --no-input
```

Manual smoke test matrix:

- login/logout
- dashboard creation/edit flows
- table menu and cart flow
- order placement and live websocket updates
- staff status transitions
- AI customer/staff endpoints (if enabled)

### "Done" checklist for any feature/change

A change is considered complete only when:

- user-facing behavior remains correct
- no duplicate ownership is introduced
- module boundaries are respected
- legacy compatibility is preserved where required
- validation commands and smoke checks pass
- docs are updated (`README.md` + this guide)

---

## 6) Reliability and Scaling

### Critical production requirements

- Replace in-memory channel layer with Redis channel layer
- Replace SQLite with PostgreSQL
- Run multiple app instances behind LB

### Scaling knobs

- Horizontal app instance count
- Redis sizing for websocket fanout
- DB connection pooling
- Static/media CDN
- Qdrant resource scaling (if AI traffic grows)

---

## 7) Security Requirements

### Access and authentication

- enforce strong admin/staff passwords
- restrict admin endpoint exposure
- least-privilege IAM for storage/infra

### App and data protection

- HTTPS only
- secure headers and CSRF trusted origins
- secret rotation policy
- regular dependency patching
- backups and tested restore process

### AI safety controls

- treat AI outputs as assistant suggestions, not authority
- keep tool scope minimal (already constrained to defined tool functions)
- monitor for prompt abuse patterns

---

## 8) Monitoring and Operations

Track at minimum:

- request latency, error rate, throughput
- websocket connection count/failure rate
- DB CPU/connections/slow queries
- Redis memory/latency
- app exceptions (Sentry/log aggregation)
- deployment health checks

Alert on:

- elevated 5xx responses
- websocket disconnect spikes
- migration failures
- queue backlog (if Celery enabled)

---

## 9) Deployment Strategy

Recommended release approach:

1. Staging deployment
2. Migrate DB
3. Run smoke tests
4. Gradual production rollout (canary/rolling)
5. Post-deploy verification

Rollback plan:

- keep previous image/version ready
- reversible migrations where possible
- fast route rollback in orchestrator/platform

---

## 10) Business Runbook (Non-Technical)

Daily:

- verify dashboard loads
- verify test order end-to-end once per shift
- verify QR scan at sample tables

When issues occur:

- capture table number + timestamp + screenshot
- check if issue is customer-only or all tables
- escalate to technical contact with exact steps

Change governance:

- no production menu schema changes during peak hours
- schedule releases off-peak
- announce staff-facing changes before rollout

### Quick way to understand project health

- Can customers place orders? (core business continuity)
- Are staff receiving live updates? (operational continuity)
- Are status updates reflected to customers? (service continuity)
- If AI is down, can manual workflow still run? (fallback continuity)

---

## 11) Known Production Caveats

- In-memory channels are not production-safe for multi-instance deployments
- SQLite is for local/dev only
- AI endpoints depend on external provider availability and token limits
- Qdrant local storage should not be source-controlled

---

## 12) Definition of Production Readiness

You are production-ready when all are true:

- PostgreSQL and Redis are in production
- `DEBUG=False` and secrets managed securely
- health checks, logs, and alerts are active
- backups and restore are tested
- smoke tests and load sanity checks pass
- on-call/escalation ownership is clear

---

## 13) Suggested Next Documents

For enterprise readiness, add:

- `RUNBOOK.md` (incident and operational SOP)
- `SECURITY.md` (threat model and controls)
- `DEPLOYMENT.md` (exact infra commands/pipeline)
- `API_CONTRACTS.md` (stable request/response schemas)

---

## 14) Ownership and Change Map

Who typically owns what:

- Product/Operations:
  - menu policy, SOPs, rollout timing, staff training
- Backend engineering:
  - app modules, APIs, signals, migrations, architecture
- DevOps/SRE:
  - deployment, scaling, monitoring, backups, incident response
- QA:
  - smoke/regression validation and release confidence

Where to implement new logic:

1. Find the owning app (`accounts`, `restaurants`, `orders`, `agent`)
2. Add/update behavior in app layer first
3. Keep `common` changes minimal (compatibility only)
4. Validate end-to-end flows after every change

