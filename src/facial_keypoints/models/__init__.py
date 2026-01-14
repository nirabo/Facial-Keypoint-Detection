"""Model inference utilities.

This subpackage provides model loading and prediction functionality
for facial keypoint detection using trained CNN models.
"""

from facial_keypoints.models.predictor import KeypointPredictor

__all__ = ["KeypointPredictor"]
