import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.models.schemas import VerifyResponse, KnownEncoding
from app.services.face_detection import FaceDetectionService
from app.services.face_encoding import FaceEncodingService
from app.services.face_matching import FaceMatchingService
from app.config import settings
from typing import List

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

detection_svc = FaceDetectionService()
encoding_svc = FaceEncodingService()
matching_svc = FaceMatchingService()


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


@router.post("/api/v1/verify/", response_model=VerifyResponse)
async def verify(
    school_id: int = Form(...),
    known_encodings: str = Form(...),
    image: UploadFile = File(...),
    _: str = Security(verify_api_key),
):
    from app.utils.image_processing import validate_image

    try:
        parsed = json.loads(known_encodings)
        known = [KnownEncoding(**item) for item in parsed]
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid known_encodings format")

    image_bytes = await validate_image(image)
    faces = detection_svc.detect_faces(image_bytes)

    if not faces:
        return VerifyResponse(success=True, matched=False, faces_detected=0, message="No face detected in image")

    encoding = encoding_svc.generate_encoding(image_bytes)
    if encoding is None:
        return VerifyResponse(success=False, matched=False, faces_detected=len(faces), message="Failed to generate face encoding")

    known_list = [{"id": k.id, "name": k.name, "encoding": k.encoding} for k in known]
    match = matching_svc.find_best_match(encoding, known_list)

    if match is None:
        return VerifyResponse(success=True, matched=False, faces_detected=len(faces), message="No match found")

    return VerifyResponse(
        success=True,
        matched=True,
        student_id=match["id"],
        student_name=match["name"],
        confidence=match["confidence"],
        distance=match["distance"],
        faces_detected=len(faces),
        message="Match found",
    )
