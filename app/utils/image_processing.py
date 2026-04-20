from fastapi import HTTPException, UploadFile
from app.config import settings


async def validate_image(file: UploadFile) -> bytes:
    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE // (1024 * 1024)}MB",
        )
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="File must be an image")
    return contents
