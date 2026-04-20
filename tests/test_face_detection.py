import pytest
from unittest.mock import patch, MagicMock
from app.services.face_detection import FaceDetectionService


@patch("app.services.face_detection.face_recognition")
def test_detect_faces_returns_list(mock_fr):
    mock_fr.face_locations.return_value = [(10, 100, 90, 20)]
    svc = FaceDetectionService()
    result = svc.detect_faces(b"fake_image_bytes")
    assert isinstance(result, list)


@patch("app.services.face_detection.face_recognition")
def test_has_single_face_true(mock_fr):
    mock_fr.face_locations.return_value = [(10, 100, 90, 20)]
    svc = FaceDetectionService()
    assert svc.has_single_face(b"fake") is True


@patch("app.services.face_detection.face_recognition")
def test_has_single_face_false_when_multiple(mock_fr):
    mock_fr.face_locations.return_value = [(10, 100, 90, 20), (50, 200, 130, 110)]
    svc = FaceDetectionService()
    assert svc.has_single_face(b"fake") is False


@patch("app.services.face_detection.face_recognition")
def test_get_largest_face_returns_none_when_no_faces(mock_fr):
    mock_fr.face_locations.return_value = []
    svc = FaceDetectionService()
    assert svc.get_largest_face(b"fake") is None
