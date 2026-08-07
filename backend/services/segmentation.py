import os
from io import BytesIO
import numpy as np
import onnxruntime as ort
import requests
from PIL import Image

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml", "weights")
_MODEL_PATH = os.path.join(_MODEL_DIR, "silueta.onnx")
_MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/silueta.onnx"

_INPUT_SIZE = 320
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_session: ort.InferenceSession | None = None


class SegmentationError(Exception):
    """Raised when background removal fails or produces an unusable result."""

def _ensure_model_downloaded() -> None:
    if os.path.exists(_MODEL_PATH):
        return

    os.makedirs(_MODEL_DIR, exist_ok=True)
    try:
        response = requests.get(_MODEL_URL, stream=True, timeout=60)
        response.raise_for_status()
        tmp_path = _MODEL_PATH + ".tmp"
        with open(tmp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        os.replace(tmp_path, _MODEL_PATH)
    except Exception as e:
        raise SegmentationError(f"Failed to download silueta model: {e}")


def _get_session() -> ort.InferenceSession:
    global _session
    if _session is None:
        _ensure_model_downloaded()
        _session = ort.InferenceSession(_MODEL_PATH, providers=["CPUExecutionProvider"])
    return _session


def _preprocess(image: Image.Image) -> np.ndarray:
    resized = image.resize((_INPUT_SIZE, _INPUT_SIZE), Image.LANCZOS)
    array = np.array(resized, dtype=np.float32) / 255.0
    array = (array - _MEAN) / _STD
    array = array.transpose(2, 0, 1)
    return np.expand_dims(array, axis=0).astype(np.float32)


def remove_background(image_bytes: bytes) -> bytes:
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise SegmentationError(f"Could not open input image: {e}")

    original_size = image.size

    try:
        session = _get_session()
        input_tensor = _preprocess(image)
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: input_tensor})
    except Exception as e:
        raise SegmentationError(f"Model inference failed: {e}")

    mask = outputs[0][0][0]
    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)

    mask_image = Image.fromarray((mask * 255).astype(np.uint8)).resize(
        original_size, Image.LANCZOS
    )

    result = image.convert("RGBA")
    result.putalpha(mask_image)

    output = BytesIO()
    result.save(output, format="PNG")
    return output.getvalue()