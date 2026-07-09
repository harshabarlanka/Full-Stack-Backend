import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        logger.warning(f"Signup attempted with existing email: {user_in.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user_in.email,
        hashed_password=auth.hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user created: id={new_user.id}, email={new_user.email}")
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = auth.create_access_token(data={"sub": str(user.id)})
    logger.info(f"User logged in: id={user.id}, email={user.email}")
    return schemas.Token(access_token=access_token)