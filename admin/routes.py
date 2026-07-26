from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return """
    <h1>Challenge Admin Panel</h1>
    <p>Panel is running successfully.</p>
    """