import face_recognition
import numpy as np
from PIL import Image
import io
from typing import List, Tuple, Optional
from app.config import settings


class FaceDetectionService:
    def __init__(self):
        self.model = settings.FACE_DETECTION_MODEL

    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return np.array(image)

    def detect_faces(self, image_bytes: bytes) -> List[Tuple]:
        image = self._load_image(image_bytes)
        return face_recognition.face_locations(image, model=self.model)

    def has_single_face(self, image_bytes: bytes) -> bool:
        return len(self.detect_faces(image_bytes)) == 1

    def get_largest_face(self, image_bytes: bytes) -> Optional[Tuple]:
        locations = self.detect_faces(image_bytes)
        if not locations:
            return None
        return max(locations, key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]))
