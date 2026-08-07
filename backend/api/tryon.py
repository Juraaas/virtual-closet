import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models.models import ClothingItem, User
from services import storage
from services.warp import WarpError, overlay_clothing

router = APIRouter(prefix="/tryon", tags=["tryon"])

_s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
)

def _download_bytes(object_key: str) -> bytes:
    obj = _s3_client.get_object(Bucket=settings.s3_bucket_name, Key=object_key)
    return obj["Body"].read()

@router.get("/{user_id}/{clothing_item_id}")
def try_on(user_id: uuid.UUID, clothing_item_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.silhouette_image_path or not user.silhouette_keypoints:
        raise HTTPException(status_code=422, detail="User has no silhouette/pose data yet")

    item = db.query(ClothingItem).filter(ClothingItem.id == clothing_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")
    if not item.segmented_image_path:
        raise HTTPException(status_code=422, detail="Clothing item has no segmented image yet")

    silhouette_bytes = _download_bytes(user.silhouette_image_path)
    garment_bytes = _download_bytes(item.segmented_image_path)

    try:
        result_bytes = overlay_clothing(
            silhouette_bytes=silhouette_bytes,
            silhouette_keypoints=user.silhouette_keypoints["keypoints"],
            clothing_png_bytes=garment_bytes,
            category=item.category.value,
        )
    except WarpError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return Response(content=result_bytes, media_type="image/png")