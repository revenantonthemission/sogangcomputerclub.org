# SGCC Memo Service: Memo Saving Fix & 24/7 Port-Forwarding Setup

## Date: 2025-09-24

## Issues Resolved

### 1. Memo Saving Issue ✅ **FIXED**

**Problem:** Memo creation was hanging indefinitely due to Kafka timeout in FastAPI service.

**Root Cause:**
- `kafka_producer.send_and_wait()` in `/home/rvnnt/production/app/main.py:195` was blocking indefinitely
- Kafka service was unhealthy, causing infinite timeout on memo creation

**Solution Applied:**
```python
# Before (line 195):
await kafka_producer.send_and_wait("memo_events", event_data)

# After (with timeout):
await asyncio.wait_for(
    kafka_producer.send_and_wait("memo_events", event_data),
    timeout=5.0
)
```

**Files Modified:**
- `/home/rvnnt/production/app/main.py` - Added `import asyncio` and timeout wrapper

**Verification:**
- ✅ Memo creation now works: Created test memo ID 36
- ✅ Kafka errors no longer block operations
- ✅ FastAPI service responds within 5 seconds

### 2. 24/7 Port-Forwarding Setup ✅ **IMPLEMENTED**

**Challenge:** Maintain persistent Kubernetes port-forwarding for external service access.

**Solution: Unified Ingress Controller Approach**

Instead of managing separate port-forwards for frontend and backend services, we implemented a single port-forward to the Kubernetes ingress controller, which handles all internal routing.

#### System Configuration

**systemd Service:** `/etc/systemd/system/kubectl-port-forward.service`
```ini
[Unit]
Description=Kubernetes Port Forward for SGCC Memo Services
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Environment="KUBECONFIG=/root/.kube/config"
ExecStart=/usr/bin/kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8090:80
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**nginx Upstream Configuration:** `/etc/nginx/nginx.conf`
```nginx
# Kubernetes Ingress Controller upstream (handles both frontend and backend)
upstream kubernetes_ingress {
    server 127.0.0.1:8090;
    keepalive 32;
}

# FastAPI backend upstream (alias to ingress)
upstream fastapi_backend {
    server 127.0.0.1:8090;
    keepalive 32;
}

# SvelteKit Node.js app upstream (alias to ingress)
upstream sveltekit_app {
    server 127.0.0.1:8090;
    keepalive 32;
}
```

#### Service Management Commands

```bash
# Check service status
sudo systemctl status kubectl-port-forward.service

# View logs
sudo journalctl -u kubectl-port-forward.service -f

# Restart if needed
sudo systemctl restart kubectl-port-forward.service
```

## Final Service Status

### External Access Points
- **IP Address:** `http://163.239.88.120/`
- **Domain:** `http://sogangcomputerclub.org/`

### Service Health Check Results
```json
{
  "status": "degraded",
  "timestamp": "2025-09-23T16:31:21.376125+00:00",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "kafka": "unhealthy"
  }
}
```

### Functional Verification
- ✅ **Frontend:** Returns HTML page properly
- ✅ **Backend API:** All endpoints responding
- ✅ **Memo Operations:** Create, read, update, delete working
- ✅ **Database:** Connected and operational
- ✅ **24/7 Operation:** systemd service with auto-restart
- ⚠️ **Kafka:** Unhealthy but not blocking operations (timeout fix applied)

### API Endpoints Working
- `GET /health` - Service health check
- `GET /docs` - API documentation
- `GET /memos/` - List all memos
- `POST /memos/` - Create new memo
- `PUT /memos/{id}` - Update memo
- `DELETE /memos/{id}` - Delete memo

### Architecture Benefits
1. **Simplified Management:** Single port-forward instead of multiple services
2. **Internal Routing:** Kubernetes ingress handles all routing logic
3. **Reliability:** Auto-restart on failure, boot persistence
4. **Performance:** Leverages existing ingress controller load balancing
5. **Maintainability:** Centralized configuration and monitoring

## Network Flow
```
External Request → nginx (host) → localhost:8090 →
Kubernetes Ingress Controller → Internal Services (frontend/backend)
```

## Files Modified Summary
1. `/home/rvnnt/production/app/main.py` - Added Kafka timeout fix
2. `/etc/systemd/system/kubectl-port-forward.service` - Created systemd service
3. `/etc/nginx/nginx.conf` - Updated upstream configuration

## Monitoring & Maintenance

### Health Monitoring
```bash
# Check external service
curl http://163.239.88.120/health

# Check port-forward service
sudo systemctl status kubectl-port-forward.service

# Check pod status
kubectl get pods -n sgcc-memo
kubectl get pods -n ingress-nginx
```

### Log Monitoring
```bash
# Service logs
sudo journalctl -u kubectl-port-forward.service --since="1 hour ago"

# FastAPI logs
kubectl logs -n sgcc-memo -l app=fastapi --tail=50

# Frontend logs
kubectl logs -n sgcc-memo -l app=frontend --tail=50
```

## Recovery Procedures

### If Port-Forward Fails
```bash
sudo systemctl restart kubectl-port-forward.service
```

### If Service Unavailable
```bash
# Check pod status
kubectl get pods -n sgcc-memo

# Restart failed pods
kubectl rollout restart deployment/fastapi -n sgcc-memo
kubectl rollout restart deployment/frontend -n sgcc-memo
```

### If Nginx Issues
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

**Implementation Date:** September 24, 2025
**Status:** Production Ready ✅
**Uptime Target:** 24/7 Continuous Operation