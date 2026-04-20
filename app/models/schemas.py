from pydantic import BaseModel
from typing import Optional, List


class EnrollResponse(BaseModel):
    success: bool
    student_id: int
    encoding: Optional[List[float]] = None
    faces_detected: int
    message: str


class KnownEncoding(BaseModel):
    id: int
    name: str
    encoding: List[float]


class VerifyResponse(BaseModel):
    success: bool
    matched: bool
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    confidence: Optional[float] = None
    distance: Optional[float] = None
    faces_detected: int
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
