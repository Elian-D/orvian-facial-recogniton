import face_recognition
import numpy as np
from typing import List, Dict, Optional, Any
from app.config import settings


class FaceMatchingService:
    def __init__(self):
        self.tolerance = settings.TOLERANCE

    def compare_faces(self, known: List[float], unknown: List[float]) -> Dict[str, Any]:
        known_enc = np.array(known)
        unknown_enc = np.array(unknown)
        distance = face_recognition.face_distance([known_enc], unknown_enc)[0]
        match = bool(distance <= self.tolerance)
        confidence = round(max(0.0, (1 - distance) * 100), 2)
        return {"match": match, "distance": round(float(distance), 4), "confidence": confidence}

    def find_best_match(
        self,
        unknown_encoding: List[float],
        known_encodings: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if not known_encodings:
            return None

        unknown_enc = np.array(unknown_encoding)
        known_arrays = [np.array(k["encoding"]) for k in known_encodings]
        distances = face_recognition.face_distance(known_arrays, unknown_enc)

        best_idx = int(np.argmin(distances))
        best_distance = float(distances[best_idx])

        if best_distance > self.tolerance:
            return None

        best = known_encodings[best_idx]
        confidence = round(max(0.0, (1 - best_distance) * 100), 2)
        return {
            "id": best["id"],
            "name": best["name"],
            "distance": round(best_distance, 4),
            "confidence": confidence,
        }
