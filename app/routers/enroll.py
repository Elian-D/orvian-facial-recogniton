from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.models.schemas import EnrollResponse
from app.services.face_detection import FaceDetectionService
from app.services.face_encoding import FaceEncodingService
from app.config import settings

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

detection_svc = FaceDetectionService()
encoding_svc = FaceEncodingService()


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


@router.post("/api/v1/enroll/", response_model=EnrollResponse)
async def enroll(
    student_id: int = Form(...),
    school_id: int = Form(...),
    image: UploadFile = File(...),
    _: str = Security(verify_api_key),
):
    from app.utils.image_processing import validate_image

    image_bytes = await validate_image(image)
    faces = detection_svc.detect_faces(image_bytes)

    if not faces:
        return EnrollResponse(success=False, student_id=student_id, faces_detected=0, message="No face detected in image")

    if len(faces) > 1:
        return EnrollResponse(success=False, student_id=student_id, faces_detected=len(faces), message="Multiple faces detected; please provide an image with a single face")

    encoding = encoding_svc.generate_encoding(image_bytes)
    if encoding is None:
        return EnrollResponse(success=False, student_id=student_id, faces_detected=1, message="Failed to generate face encoding")

    return EnrollResponse(success=True, student_id=student_id, encoding=encoding, faces_detected=1, message="Face enrolled successfully")
