import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from schemas.schemas import UserCreateSimple, UserOut
from services import storage
from services.pose import PoseDetectionError, extract_keypoints

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
def create_user(payload: UserCreateSimple, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = User(email=payload.email, hashed_password="unset")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/{user_id}/silhouette", response_model=UserOut)
async def upload_silhouette(user_id: uuid.UUID,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    image_bytes = await file.read()

    try:
        pose_result = extract_keypoints(image_bytes)
    except PoseDetectionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    file.file.seek(0)
    object_key = storage.upload_file(file, folder="silhouettes")

    user.silhouette_image_path = object_key
    user.silhouette_keypoints = pose_result
    db.commit()
    db.refresh(user)

    return user