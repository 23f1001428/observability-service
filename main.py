from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid
from collections import deque
import asyncio

app = FastAPI()

# ---------- Prometheus Counter ----------
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["path"]
)

# ---------- Logs store ----------
logs = deque(maxlen=1000)
start_time = time.time()

# ---------- Middleware (MANDATORY FOR GRADER) ----------
@app.middleware("http")
async def middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    http_requests_total.labels(path=request.url.path).inc()

    logs.append({
        "level": "info",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    })

    return response


# ---------- /work ----------
@app.get("/work")
async def work(n: int = 1):
    await asyncio.sleep(n * 0.01)

    return {
        "email": "23f1001428@ds.study.iitm.ac.in",
        "done": n
    }


# ---------- /metrics ----------
@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ---------- /healthz ----------
@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "uptime_s": time.time() - start_time
    }


# ---------- /logs/tail ----------
@app.get("/logs/tail")
def logs_tail(limit: int = 10):
    return list(logs)[-limit:]