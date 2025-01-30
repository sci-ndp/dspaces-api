from fastapi import APIRouter, Request

from api.config import swagger_settings as settings
from starlette.responses import RedirectResponse 
router = APIRouter()

@router.get("/")
async def index(request: Request):
    return RedirectResponse(f'{request.scope.get("root_path", "")}/docs')