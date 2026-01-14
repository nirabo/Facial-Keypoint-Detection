"""Face detection utilities.

This subpackage provides face detection functionality using
OpenCV Haar Cascade classifiers.
"""

from facial_keypoints.detection.face_detector import BoundingBox, FaceDetector


__all__ = ["BoundingBox", "FaceDetector"]
