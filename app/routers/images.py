import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user
from app.storage import save_file_locally, delete_file_locally

router = APIRouter(prefix="/images", tags=["images"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=schemas.ImageOut, status_code=status.HTTP_201_CREATED)
def upload_image(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    saved_filename = save_file_locally(file)

    new_image = models.Image(
        title=title,
        description=description,
        filename=saved_filename,
        user_id=current_user.id,
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    logger.info(f"Image uploaded: id={new_image.id}, user_id={current_user.id}, filename={saved_filename}")
    return new_image


@router.get("/", response_model=list[schemas.ImageOut])
def list_images(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Image)
        .filter(models.Image.user_id == current_user.id)
        .order_by(models.Image.created_at.desc())
        .all()
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    image = (
        db.query(models.Image)
        .filter(models.Image.id == image_id, models.Image.user_id == current_user.id)
        .first()
    )
    if image is None:
        logger.warning(f"Delete attempted on nonexistent/unowned image: id={image_id}, user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="Image not found")

    delete_file_locally(image.filename)
    db.delete(image)
    db.commit()
    logger.info(f"Image deleted: id={image_id}, user_id={current_user.id}")