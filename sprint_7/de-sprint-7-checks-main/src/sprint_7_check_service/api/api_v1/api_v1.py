from fastapi import APIRouter

from sprint_7_check_service.api.api_v1.endpoints import checks_api


router = APIRouter()
router.include_router(checks_api.router,
                      prefix="/checks",
                      tags=["checks", "db"])
