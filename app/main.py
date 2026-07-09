from fastapi import FastAPI

from app.logging_config import setup_logging
from app.routers import users, images

setup_logging()

app = FastAPI(title="Image Metadata API")

app.include_router(users.router)
app.include_router(images.router)

@app.get("/")
def health_check():
    return {"status": "ok"}