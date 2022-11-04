from fastapi import APIRouter

from settings import settings

router = APIRouter(prefix=settings.API_ENTRYPOINT, tags=["Default"])


@router.get("/ping")
async def ping():
    """ping/pong endpoint"""
    return {"msg": "pong"}
