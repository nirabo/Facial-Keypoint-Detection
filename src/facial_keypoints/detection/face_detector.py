"""Face detection using OpenCV Haar Cascade classifiers.

This module provides face detection functionality using pre-trained
Haar Cascade classifiers from OpenCV.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from facial_keypoints.config import settings
from facial_keypoints.exceptions import (
    FaceDetectionError,
    InvalidImageError,
    NoFaceDetectedError,
)


# Constants for image channel detection
_COLOR_CHANNELS = 3

if TYPE_CHECKING:
    from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Represents a face bounding box.

    This is an immutable dataclass containing the coordinates and
    dimensions of a detected face region.

    Attributes:
        x: Left coordinate of the bounding box.
        y: Top coordinate of the bounding box.
        width: Width of the bounding box.
        height: Height of the bounding box.

    Example:
        >>> box = BoundingBox(x=100, y=50, width=200, height=200)
        >>> print(f"Face at ({box.x}, {box.y}), size: {box.width}x{box.height}")
        >>> print(f"Center: {box.center}, Area: {box.area}")
    """

    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        """Return center coordinates of bounding box.

        Returns:
            Tuple of (center_x, center_y) coordinates.
        """
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        """Return area of bounding box in pixels.

        Returns:
            Area as width * height.
        """
        return self.width * self.height

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Convert to tuple format (x, y, w, h).

        Returns:
            Tuple of (x, y, width, height).
        """
        return (self.x, self.y, self.width, self.height)


class FaceDetector:
    """Face detector using OpenCV Haar Cascade classifier.

    This class wraps OpenCV's CascadeClassifier for detecting faces
    in images using pre-trained Haar Cascade models.

    Attributes:
        cascade_path: Path to the Haar Cascade XML file.
        scale_factor: Scale factor for multi-scale detection.
        min_neighbors: Minimum neighbors for detection filtering.

    Example:
        >>> detector = FaceDetector()
        >>> image = cv2.imread("photo.jpg")
        >>> faces = detector.detect(image)
        >>> for box in faces:
        ...     print(f"Face at ({box.x}, {box.y}), size: {box.width}x{box.height}")
    """

    def __init__(
        self,
        cascade_path: Path | str | None = None,
        scale_factor: float | None = None,
        min_neighbors: int | None = None,
    ) -> None:
        """Initialize the face detector.

        Args:
            cascade_path: Path to Haar Cascade XML file.
                If None, uses default from settings.
            scale_factor: Scale factor for detectMultiScale.
                If None, uses default from settings (1.2).
            min_neighbors: Minimum neighbors for filtering.
                If None, uses default from settings (5).

        Raises:
            FaceDetectionError: If cascade file cannot be loaded.
        """
        self.cascade_path = Path(cascade_path or settings.cascade_path)
        self.scale_factor = scale_factor if scale_factor is not None else settings.scale_factor
        self.min_neighbors = min_neighbors if min_neighbors is not None else settings.min_neighbors

        if not self.cascade_path.exists():
            msg = f"Cascade file not found: {self.cascade_path}"
            raise FaceDetectionError(msg)

        self._cascade = cv2.CascadeClassifier(str(self.cascade_path))

        if self._cascade.empty():
            msg = f"Failed to load cascade: {self.cascade_path}"
            raise FaceDetectionError(msg)

    def detect(
        self,
        image: "NDArray[np.uint8]",
        scale_factor: float | None = None,
        min_neighbors: int | None = None,
    ) -> list[BoundingBox]:
        """Detect faces in an image.

        Args:
            image: Input image as numpy array (BGR or grayscale).
            scale_factor: Override default scale factor for this detection.
            min_neighbors: Override default min neighbors for this detection.

        Returns:
            List of BoundingBox objects for detected faces.
            Returns empty list if no faces are detected.

        Raises:
            InvalidImageError: If input image is invalid (None or empty).
        """
        if image is None or image.size == 0:
            msg = "Empty image provided"
            raise InvalidImageError(msg)

        # Convert to grayscale if needed
        if len(image.shape) == _COLOR_CHANNELS:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        scale = scale_factor if scale_factor is not None else self.scale_factor
        neighbors = min_neighbors if min_neighbors is not None else self.min_neighbors

        faces = self._cascade.detectMultiScale(gray, scale, neighbors)

        return [
            BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h))
            for (x, y, w, h) in faces
        ]

    def detect_single(
        self,
        image: "NDArray[np.uint8]",
        scale_factor: float | None = None,
        min_neighbors: int | None = None,
    ) -> BoundingBox:
        """Detect a single face in an image.

        Useful when you expect exactly one face in the image.
        If multiple faces are detected, returns the largest one.

        Args:
            image: Input image as numpy array.
            scale_factor: Override default scale factor.
            min_neighbors: Override default min neighbors.

        Returns:
            BoundingBox for the largest detected face.

        Raises:
            NoFaceDetectedError: If no face is detected.
        """
        faces = self.detect(image, scale_factor, min_neighbors)

        if not faces:
            raise NoFaceDetectedError

        # Return largest face by area
        return max(faces, key=lambda f: f.area)

    def crop_face(
        self,
        image: "NDArray[np.uint8]",
        box: BoundingBox,
        padding: float = 0.0,
    ) -> "NDArray[np.uint8]":
        """Crop a face region from an image.

        Args:
            image: Source image.
            box: Bounding box of the face to crop.
            padding: Optional padding as fraction of box size (0.0-1.0).

        Returns:
            Cropped face image.
        """
        h, w = image.shape[:2]

        # Apply padding
        pad_x = int(box.width * padding)
        pad_y = int(box.height * padding)

        x1 = max(0, box.x - pad_x)
        y1 = max(0, box.y - pad_y)
        x2 = min(w, box.x + box.width + pad_x)
        y2 = min(h, box.y + box.height + pad_y)

        return image[y1:y2, x1:x2]
