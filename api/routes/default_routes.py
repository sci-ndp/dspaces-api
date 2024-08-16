from fastapi import APIRouter

from api.config import swagger_settings as settings

router = APIRouter()

@router.get("/")
async def index():
    return {"message": f"Hello, welcome to {settings.swagger_title}"}