from fastapi import APIRouter
from starlette.responses import RedirectResponse

router = APIRouter()

@router.get("/")
async def index():
    return RedirectResponse('/docs')

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "DSpaces API is running"}