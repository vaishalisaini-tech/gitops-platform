"""
Sample FastAPI service for the GitOps delivery platform.

Exposes:
  GET /            -> basic JSON, app metadata
  GET /healthz     -> liveness probe (process is up)
  GET /readyz      -> readiness probe (can serve traffic)
  GET /api/items   -> trivial demo endpoint
  GET /metrics     -> Prometheus metrics

The app is deliberately small but production-shaped: structured config via
environment variables, Prometheus instrumentation, and probe endpoints that
Kubernetes can use independently.
"""
import os
import time

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

APP_NAME = os.getenv("APP_NAME", "gitops-demo")
APP_ENV = os.getenv("APP_ENV", "dev")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# --- Prometheus metrics -----------------------------------------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["path"],
)

# Readiness flag so we can simulate "not ready yet" on startup.
_STARTED_AT = time.time()
_READY_AFTER_SECONDS = float(os.getenv("READY_AFTER_SECONDS", "0"))


@app.middleware("http")
async def track_metrics(request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    REQUEST_LATENCY.labels(path=request.url.path).observe(elapsed)
    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    ).inc()
    return response


@app.get("/")
def root():
    return {"app": APP_NAME, "env": APP_ENV, "version": APP_VERSION}


@app.get("/healthz")
def healthz():
    """Liveness: the process is alive. Cheap and dependency-free."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness: only ready once warm-up window has elapsed."""
    ready = (time.time() - _STARTED_AT) >= _READY_AFTER_SECONDS
    if not ready:
        return Response(content='{"status":"warming-up"}', status_code=503,
                        media_type="application/json")
    return {"status": "ready"}


@app.get("/api/items")
def items():
    return {"items": [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
