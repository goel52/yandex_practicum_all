from fastapi import APIRouter

from sprint_7_check_service.api.api_v1 import api_v1

router = APIRouter()
router.include_router(api_v1.router, prefix="/v1", tags=["v1"])
