from fastapi import FastAPI

from app.admin.views import setup_admin


app = FastAPI(
    title="Omid Challenge Bot"
)


setup_admin(app)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Omid Challenge Bot"
    }