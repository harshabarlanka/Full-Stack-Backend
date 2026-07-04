from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routers import users, images

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Image Metadata API")

app.include_router(users.router)
app.include_router(images.router)

@app.get("/")
def health_check():
    return {"status": "ok"}