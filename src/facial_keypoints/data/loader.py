"""Data loading utilities for facial keypoint detection.

This module provides functions for loading training and test data
from CSV files containing facial images and keypoint annotations.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from sklearn.utils import shuffle

from facial_keypoints.config import settings
from facial_keypoints.exceptions import DataLoadError


if TYPE_CHECKING:
    from numpy.typing import NDArray


def load_data(
    test: bool = False,
    data_path: Path | str | None = None,
    random_state: int = 42,
) -> tuple["NDArray[np.float32]", "NDArray[np.float32] | None"]:
    """Load facial keypoint data from CSV files.

    Loads training or test data from CSV files containing facial images
    and their corresponding keypoint annotations. Images are 96x96 grayscale.

    Args:
        test: If True, load test data; otherwise load training data.
        data_path: Optional custom path to data file. If None, uses default
            paths from settings.
        random_state: Random seed for shuffling training data.

    Returns:
        A tuple of (X, y) where:
            - X: Image array of shape (n_samples, 96, 96, 1), values in [0, 1]
            - y: Keypoint array of shape (n_samples, 30), values in [-1, 1]
                 Returns None for test data.

    Raises:
        DataLoadError: If the data file cannot be loaded or parsed.

    Example:
        >>> X_train, y_train = load_data()
        >>> print(f"Training samples: {X_train.shape[0]}")
        >>> X_test, _ = load_data(test=True)
    """
    if data_path is None:
        data_path = settings.test_data_path if test else settings.train_data_path

    data_path = Path(data_path)

    if not data_path.exists():
        raise DataLoadError(str(data_path), "Data file not found")

    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise DataLoadError(str(data_path), f"Failed to parse CSV: {e}") from e

    if "Image" not in df.columns:
        raise DataLoadError(str(data_path), "Missing 'Image' column in CSV")

    # Convert pixel string to numpy array
    # Using list comprehension instead of deprecated np.fromstring
    def parse_image(image_str: str) -> "NDArray[np.float64]":
        """Parse space-separated pixel values to numpy array."""
        return np.array([float(x) for x in image_str.split()])

    df["Image"] = df["Image"].apply(parse_image)

    # Drop rows with missing values
    df = df.dropna()

    if len(df) == 0:
        raise DataLoadError(str(data_path), "No valid samples after dropping NaN")

    # Stack images and normalize to [0, 1]
    X = np.vstack(df["Image"].values) / 255.0
    X = X.astype(np.float32)
    X = X.reshape(-1, settings.image_size, settings.image_size, 1)

    if not test:
        # Extract keypoint columns (all except last 'Image' column)
        y = df[df.columns[:-1]].values
        # Normalize coordinates to [-1, 1]
        # Original coords are in [0, 96], center is at 48
        y = (y - 48) / 48
        y = y.astype(np.float32)

        # Shuffle training data
        X, y = shuffle(X, y, random_state=random_state)

        return X, y

    return X, None


def get_data_statistics(
    X: "NDArray[np.float32]",
    y: "NDArray[np.float32] | None" = None,
) -> dict[str, float | int]:
    """Compute statistics for loaded data.

    Useful for data exploration and validation.

    Args:
        X: Image array of shape (n_samples, height, width, channels).
        y: Optional keypoint array of shape (n_samples, n_keypoints * 2).

    Returns:
        Dictionary containing data statistics including:
            - n_samples: Number of samples
            - image_height: Image height
            - image_width: Image width
            - x_min, x_max, x_mean, x_std: Image value statistics
            - n_keypoints, y_min, y_max, y_mean, y_std: Keypoint statistics (if y provided)

    Example:
        >>> X, y = load_data()
        >>> stats = get_data_statistics(X, y)
        >>> print(f"Samples: {stats['n_samples']}, Keypoints: {stats['n_keypoints']}")
    """
    stats: dict[str, float | int] = {
        "n_samples": int(X.shape[0]),
        "image_height": int(X.shape[1]),
        "image_width": int(X.shape[2]),
        "x_min": float(X.min()),
        "x_max": float(X.max()),
        "x_mean": float(X.mean()),
        "x_std": float(X.std()),
    }

    if y is not None:
        stats.update({
            "n_keypoints": int(y.shape[1] // 2),
            "y_min": float(y.min()),
            "y_max": float(y.max()),
            "y_mean": float(y.mean()),
            "y_std": float(y.std()),
        })

    return stats
