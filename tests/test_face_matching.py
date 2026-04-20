import pytest
import numpy as np
from unittest.mock import patch
from app.services.face_matching import FaceMatchingService


KNOWN_ENC = [0.1] * 128
UNKNOWN_ENC = [0.1] * 128
FAR_ENC = [0.9] * 128


@patch("app.services.face_matching.face_recognition")
def test_compare_faces_match(mock_fr):
    mock_fr.face_distance.return_value = np.array([0.3])
    svc = FaceMatchingService()
    result = svc.compare_faces(KNOWN_ENC, UNKNOWN_ENC)
    assert result["match"] is True
    assert result["distance"] == 0.3


@patch("app.services.face_matching.face_recognition")
def test_compare_faces_no_match(mock_fr):
    mock_fr.face_distance.return_value = np.array([0.7])
    svc = FaceMatchingService()
    result = svc.compare_faces(KNOWN_ENC, FAR_ENC)
    assert result["match"] is False


@patch("app.services.face_matching.face_recognition")
def test_find_best_match_returns_none_when_empty(mock_fr):
    svc = FaceMatchingService()
    result = svc.find_best_match(UNKNOWN_ENC, [])
    assert result is None


@patch("app.services.face_matching.face_recognition")
def test_find_best_match_found(mock_fr):
    mock_fr.face_distance.return_value = np.array([0.3])
    svc = FaceMatchingService()
    known = [{"id": 1, "name": "Juan", "encoding": KNOWN_ENC}]
    result = svc.find_best_match(UNKNOWN_ENC, known)
    assert result is not None
    assert result["id"] == 1
    assert result["name"] == "Juan"


@patch("app.services.face_matching.face_recognition")
def test_find_best_match_no_match_above_tolerance(mock_fr):
    mock_fr.face_distance.return_value = np.array([0.8])
    svc = FaceMatchingService()
    known = [{"id": 1, "name": "Juan", "encoding": KNOWN_ENC}]
    result = svc.find_best_match(FAR_ENC, known)
    assert result is None
