from fastapi.routing import APIRouter

from src.api.v1.handlers.campaign import router as campaign_router

router = APIRouter()

router.include_router(campaign_router, prefix="/v1", tags=["Кампании"])
