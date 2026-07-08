from fastapi import FastAPI

from app.routers import users, images

app = FastAPI(title="Image Metadata API")

app.include_router(users.router)
app.include_router(images.router)

@app.get("/")
def health_check():
    return {"status": "ok"}