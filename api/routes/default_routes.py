from fastapi import APIRouter

from api.config import swagger_settings as settings
from starlette.responses import RedirectResponse 
router = APIRouter()

@router.get("/")
async def index():
    return RedirectResponse('/docs')