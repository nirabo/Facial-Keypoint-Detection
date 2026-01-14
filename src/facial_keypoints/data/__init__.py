"""Data loading and processing utilities.

This subpackage provides functions for loading, downloading, and preprocessing
facial keypoint training and test data.
"""

from facial_keypoints.data.download import (
    download_from_kaggle,
    download_sample_data,
    get_data_info,
    verify_data,
)
from facial_keypoints.data.loader import get_data_statistics, load_data


__all__ = [
    "download_from_kaggle",
    "download_sample_data",
    "get_data_info",
    "get_data_statistics",
    "load_data",
    "verify_data",
]
