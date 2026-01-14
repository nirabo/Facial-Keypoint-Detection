"""
Facial Keypoint Detection package.

This package provides tools for detecting facial keypoints using
CNN models and OpenCV-based face detection.

Example:
    >>> from facial_keypoints.pipeline import FacialKeypointsPipeline
    >>> pipeline = FacialKeypointsPipeline()
    >>> result = pipeline.process("image.jpg")
    >>> print(f"Detected {result.n_faces} faces")
"""

__version__ = "1.0.0"
__author__ = "L. Petrov"

from facial_keypoints.config import settings


__all__ = ["__version__", "settings"]
