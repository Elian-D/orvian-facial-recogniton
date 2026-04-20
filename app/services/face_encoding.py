import face_recognition
import numpy as np
from PIL import Image
import io
from typing import Optional, List
from app.config import settings


class FaceEncodingService:
    def __init__(self):
        self.model = settings.FACE_ENCODING_MODEL

    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return np.array(image)

    def generate_encoding(self, image_bytes: bytes) -> Optional[List[float]]:
        image = self._load_image(image_bytes)
        encodings = face_recognition.face_encodings(image, model=self.model)
        if not encodings:
            return None
        return encodings[0].tolist()

    def generate_multiple_encodings(self, image_bytes: bytes, num_jitters: int = 10) -> List[List[float]]:
        image = self._load_image(image_bytes)
        encodings = face_recognition.face_encodings(image, num_jitters=num_jitters, model=self.model)
        return [enc.tolist() for enc in encodings]
