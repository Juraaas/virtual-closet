import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models.models import ClothingItem, User
from services import storage
from services.warp import WarpError, overlay_multiple

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
def try_on(user_id: uuid.UUID, item_ids: list[uuid.UUID] = Query(
        default=[],
        description="One or more clothing item IDs to composite (e.g. one top, one bottom," \
        " one pair of shoes).",
    ), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.silhouette_image_path or not user.silhouette_keypoints:
        raise HTTPException(status_code=422, detail="User has no silhouette/pose data yet")

    if not item_ids:
        raise HTTPException(status_code=400, detail="At least one item_ids value is required")
    items = db.query(ClothingItem).filter(ClothingItem.id.in_(item_ids)).all()
    found_ids = {item.id for item in items}
    missing = set(item_ids) - found_ids
    if missing:
        raise HTTPException(status_code=404, detail=f"Clothing items not found: {missing}")

    garments = []
    for item in items:
        if not item.segmented_image_path:
            raise HTTPException(
                status_code=422, detail=f"Clothing item '{item.name}' has no segmented image yet"
            )
        garments.append(
            {
                "category": item.category.value,
                "image_bytes": _download_bytes(item.segmented_image_path),
            }
        )

    silhouette_bytes = _download_bytes(user.silhouette_image_path)

    try:
        result_bytes = overlay_multiple(
            silhouette_bytes=silhouette_bytes,
            silhouette_keypoints=user.silhouette_keypoints["keypoints"],
            garments=garments,
        )
    except WarpError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return Response(content=result_bytes, media_type="image/png")