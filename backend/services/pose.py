import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

RELEVANT_LANDMARKS = {
    "left_shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER,
    "right_shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER,
    "left_hip": mp_pose.PoseLandmark.LEFT_HIP,
    "right_hip": mp_pose.PoseLandmark.RIGHT_HIP,
    "left_elbow": mp_pose.PoseLandmark.LEFT_ELBOW,
    "right_elbow": mp_pose.PoseLandmark.RIGHT_ELBOW,
    "left_wrist": mp_pose.PoseLandmark.LEFT_WRIST,
    "right_wrist": mp_pose.PoseLandmark.RIGHT_WRIST,
    "left_knee": mp_pose.PoseLandmark.LEFT_KNEE,
    "right_knee": mp_pose.PoseLandmark.RIGHT_KNEE,
    "left_ankle": mp_pose.PoseLandmark.LEFT_ANKLE,
    "right_ankle": mp_pose.PoseLandmark.RIGHT_ANKLE,
    "nose": mp_pose.PoseLandmark.NOSE,
}

class PoseDetectionError(Exception):
    """Raised when no person/pose could be detected in the image."""


def extract_keypoints(image_bytes: bytes) -> dict:
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if image is None:
        raise PoseDetectionError("Could not decode image")

    height, width = image.shape[:2]
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(image_rgb)

    if not results.pose_landmarks:
        raise PoseDetectionError("No person detected in the image")

    landmarks = results.pose_landmarks.landmark

    keypoints = {}
    for name, landmark_id in RELEVANT_LANDMARKS.items():
        lm = landmarks[landmark_id]
        keypoints[name] = {
            "x": lm.x,
            "y": lm.y,
            "x_px": round(lm.x * width),
            "y_px": round(lm.y * height),
            "visibility": round(lm.visibility, 3),
        }

    return {
        "image_width": width,
        "image_height": height,
        "keypoints": keypoints,
    }