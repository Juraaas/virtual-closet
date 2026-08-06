from io import BytesIO
from PIL import Image
from rembg import remove

class SegmentationError(Exception):
    """Raised when background removal fails or produces an unusable result."""


def remove_background(image_bytes: bytes) -> bytes:
    try:
        output_bytes = remove(image_bytes)
    except Exception as e:
        raise SegmentationError(f"Background removal failed: {e}")

    try:
        image = Image.open(BytesIO(output_bytes))
        image.verify()
    except Exception as e:
        raise SegmentationError(f"Produced invalid image: {e}")

    return output_bytes