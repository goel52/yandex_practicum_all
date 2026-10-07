from fastapi import FastAPI
from sprint_7_check_service.api import api


app = FastAPI(
    title='Practicum DE - Sprint 7 Check Service',
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/api/v1/health/healthcheck", include_in_schema=False)
def healthcheck():
    """Process health only: do not start Spark for Kubernetes probes."""
    return {"status": "ok"}
