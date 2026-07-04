from pydantic import BaseModel, EmailStr
from datetime import datetime


# ---- User schemas ----

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # lets Pydantic read SQLAlchemy objects directly


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ---- Image schemas ----

class ImageOut(BaseModel):
    id: int
    title: str
    description: str | None
    filename: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True