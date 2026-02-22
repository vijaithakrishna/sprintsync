from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import LoggingMiddleware, metrics
from app.routers import auth, users, tasks, ai
from app.config import settings

app = FastAPI(
    title="SprintSync API",
    description="Lean sprint management tool with AI assist",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": "SprintSync", "version": "1.0.0"}


@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    total = metrics["http_requests_total"]
    avg_latency = (
        round(metrics["total_latency_ms"] / total, 2) if total > 0 else 0
    )
    return {
        "http_requests_total": total,
        "errors_total": metrics["errors_total"],
        "ai_suggest_calls_total": metrics["ai_suggest_calls_total"],
        "avg_latency_ms": avg_latency,
        "routes": metrics["routes"],
    }