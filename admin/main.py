from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.routes import router


app = FastAPI(
    title="Challenge Admin Panel"
)


app.include_router(router)