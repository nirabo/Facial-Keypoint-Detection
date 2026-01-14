"""Data loading and processing utilities.

This subpackage provides functions for loading and preprocessing
facial keypoint training and test data.
"""

from facial_keypoints.data.loader import get_data_statistics, load_data

__all__ = ["load_data", "get_data_statistics"]
