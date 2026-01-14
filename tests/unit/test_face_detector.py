"""Unit tests for face detection functionality."""

from pathlib import Path

import numpy as np
import pytest

from facial_keypoints.detection.face_detector import BoundingBox, FaceDetector
from facial_keypoints.exceptions import FaceDetectionError, InvalidImageError, NoFaceDetectedError


class TestBoundingBox:
    """Tests for BoundingBox dataclass."""

    def test_creation(self) -> None:
        """Test bounding box creation."""
        box = BoundingBox(x=10, y=20, width=100, height=80)
        assert box.x == 10
        assert box.y == 20
        assert box.width == 100
        assert box.height == 80

    def test_center_calculation(self) -> None:
        """Test bounding box center calculation."""
        box = BoundingBox(x=10, y=20, width=100, height=80)
        assert box.center == (60, 60)

    def test_center_calculation_zero_origin(self) -> None:
        """Test center calculation with zero origin."""
        box = BoundingBox(x=0, y=0, width=100, height=100)
        assert box.center == (50, 50)

    def test_area_calculation(self) -> None:
        """Test bounding box area calculation."""
        box = BoundingBox(x=0, y=0, width=100, height=50)
        assert box.area == 5000

    def test_area_calculation_square(self) -> None:
        """Test area calculation for square box."""
        box = BoundingBox(x=0, y=0, width=64, height=64)
        assert box.area == 4096

    def test_immutable(self) -> None:
        """Test that BoundingBox is immutable (frozen dataclass)."""
        box = BoundingBox(x=10, y=20, width=100, height=80)
        with pytest.raises(AttributeError):
            box.x = 50  # type: ignore[misc]

    def test_to_tuple(self) -> None:
        """Test conversion to tuple."""
        box = BoundingBox(x=10, y=20, width=100, height=80)
        assert box.to_tuple() == (10, 20, 100, 80)

    def test_slots_memory_efficiency(self) -> None:
        """Test that BoundingBox uses slots for memory efficiency."""
        box = BoundingBox(x=10, y=20, width=100, height=80)
        assert hasattr(box, "__slots__") or not hasattr(box, "__dict__")


class TestFaceDetector:
    """Tests for FaceDetector class."""

    def test_init_raises_on_missing_cascade(self, tmp_path: Path) -> None:
        """Test that initialization fails with missing cascade file."""
        with pytest.raises(FaceDetectionError, match="not found"):
            FaceDetector(cascade_path=tmp_path / "nonexistent.xml")

    def test_init_with_valid_cascade(self, cascade_path: Path) -> None:
        """Test initialization with valid cascade file."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)
        assert detector.cascade_path == cascade_path

    def test_init_default_parameters(self, cascade_path: Path) -> None:
        """Test that default parameters are set from settings."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)
        assert detector.scale_factor > 1.0
        assert detector.min_neighbors >= 1

    def test_init_custom_parameters(self, cascade_path: Path) -> None:
        """Test initialization with custom parameters."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(
            cascade_path=cascade_path,
            scale_factor=1.5,
            min_neighbors=10,
        )
        assert detector.scale_factor == 1.5
        assert detector.min_neighbors == 10

    def test_detect_raises_on_none_image(self, cascade_path: Path) -> None:
        """Test that detect raises on None image."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)
        with pytest.raises(InvalidImageError, match="Empty"):
            detector.detect(None)  # type: ignore[arg-type]

    def test_detect_raises_on_empty_image(self, cascade_path: Path) -> None:
        """Test that detect raises on empty image."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)
        with pytest.raises(InvalidImageError, match="Empty"):
            detector.detect(np.array([]))

    def test_detect_returns_list(
        self,
        cascade_path: Path,
        sample_image_color: np.ndarray,
    ) -> None:
        """Test that detect returns a list."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)
        result = detector.detect(sample_image_color)

        assert isinstance(result, list)

    def test_detect_accepts_grayscale(
        self,
        cascade_path: Path,
        sample_image_gray: np.ndarray,
    ) -> None:
        """Test that detect accepts grayscale images."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)
        result = detector.detect(sample_image_gray)

        assert isinstance(result, list)

    def test_detect_single_raises_on_no_face(
        self,
        cascade_path: Path,
        sample_image_gray: np.ndarray,
    ) -> None:
        """Test that detect_single raises when no face found."""
        if not cascade_path.exists():
            pytest.skip("Cascade file not available")

        detector = FaceDetector(cascade_path=cascade_path)

        # Random noise image unlikely to contain face
        with pytest.raises(NoFaceDetectedError):
            detector.detect_single(sample_image_gray)


class TestNoFaceDetectedError:
    """Tests for NoFaceDetectedError exception."""

    def test_error_message_without_path(self) -> None:
        """Test error message when no path provided."""
        error = NoFaceDetectedError()
        assert "No face detected" in str(error)
        assert error.image_path is None

    def test_error_message_with_path(self) -> None:
        """Test error message includes image path."""
        error = NoFaceDetectedError("/path/to/image.jpg")
        assert "No face detected" in str(error)
        assert "/path/to/image.jpg" in str(error)
        assert error.image_path == "/path/to/image.jpg"
