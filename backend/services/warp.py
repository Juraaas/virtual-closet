from io import BytesIO
from PIL import Image

class WarpError(Exception):
    pass


CATEGORY_ANCHOR_KEYPOINTS = {
    "top": {
        "top_left": "left_shoulder",
        "top_right": "right_shoulder",
        "bottom_left": "left_hip",
        "bottom_right": "right_hip",
        "padding_top": 0.35,
        "padding_bottom": 0.15,
        "padding_sides": 0.55,
    },
    "bottom": {
        "top_left": "left_hip",
        "top_right": "right_hip",
        "bottom_left": "left_ankle",
        "bottom_right": "right_ankle",
        "padding_top": 0.6,
        "padding_bottom": 0.05,
        "padding_sides": 0.6,
    },
    "shoes": {
        "top_left": "left_ankle",
        "top_right": "right_ankle",
        "bottom_left": "left_ankle",
        "bottom_right": "right_ankle",
        "padding_top": 0.3,
        "padding_bottom": 0.6,
        "padding_sides": 0.6,
    },
}


def _bounding_box_from_keypoints(keypoints: dict, category: str) -> tuple[int, int, int, int]:
    if category not in CATEGORY_ANCHOR_KEYPOINTS:
        raise WarpError(f"No overlay logic defined for category '{category}' yet")

    anchors = CATEGORY_ANCHOR_KEYPOINTS[category]

    try:
        tl = keypoints[anchors["top_left"]]
        tr = keypoints[anchors["top_right"]]
        bl = keypoints[anchors["bottom_left"]]
        br = keypoints[anchors["bottom_right"]]
    except KeyError as e:
        raise WarpError(f"Missing required keypoint: {e}")

    all_x = [tl["x_px"], tr["x_px"], bl["x_px"], br["x_px"]]
    all_y = [tl["y_px"], tr["y_px"], bl["y_px"], br["y_px"]]

    left = min(all_x)
    right = max(all_x)
    top = min(all_y)
    bottom = max(all_y)

    width = right - left
    height = bottom - top

    left -= int(width * anchors["padding_sides"])
    right += int(width * anchors["padding_sides"])
    top -= int(height * anchors["padding_top"])
    bottom += int(height * anchors["padding_bottom"])

    return left, top, right, bottom


def overlay_clothing(
    silhouette_bytes: bytes,
    silhouette_keypoints: dict,
    clothing_png_bytes: bytes,
    category: str,
) -> bytes:
    silhouette = Image.open(BytesIO(silhouette_bytes)).convert("RGBA")
    garment = Image.open(BytesIO(clothing_png_bytes)).convert("RGBA")

    left, top, right, bottom = _bounding_box_from_keypoints(silhouette_keypoints, category)

    target_width = max(right - left, 1)
    target_height = max(bottom - top, 1)

    garment_ratio = garment.width / garment.height
    box_ratio = target_width / target_height

    if garment_ratio > box_ratio:
        new_width = target_width
        new_height = int(target_width / garment_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * garment_ratio)

    garment_resized = garment.resize((max(new_width, 1), max(new_height, 1)))

    paste_x = left + (target_width - new_width) // 2
    paste_y = top + (target_height - new_height) // 2

    composite = silhouette.copy()
    composite.paste(garment_resized, (paste_x, paste_y), garment_resized)

    output = BytesIO()
    composite.save(output, format="PNG")
    return output.getvalue()


def overlay_multiple(
    silhouette_bytes: bytes,
    silhouette_keypoints: dict,
    garments: list[dict],
) -> bytes:
    silhouette = Image.open(BytesIO(silhouette_bytes)).convert("RGBA")

    z_order = {"shoes": 0, "bottom": 1, "top": 2}
    sorted_garments = sorted(garments, key=lambda g: z_order.get(g["category"], 99))

    composite = silhouette.copy()

    for garment_entry in sorted_garments:
        category = garment_entry["category"]
        garment_bytes = garment_entry["image_bytes"]

        garment = Image.open(BytesIO(garment_bytes)).convert("RGBA")
        left, top, right, bottom = _bounding_box_from_keypoints(silhouette_keypoints, category)

        target_width = max(right - left, 1)
        target_height = max(bottom - top, 1)

        garment_ratio = garment.width / garment.height
        box_ratio = target_width / target_height

        if garment_ratio > box_ratio:
            new_width = target_width
            new_height = int(target_width / garment_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * garment_ratio)

        garment_resized = garment.resize((max(new_width, 1), max(new_height, 1)))

        paste_x = left + (target_width - new_width) // 2
        paste_y = top + (target_height - new_height) // 2

        composite.paste(garment_resized, (paste_x, paste_y), garment_resized)

    output = BytesIO()
    composite.save(output, format="PNG")
    return output.getvalue()