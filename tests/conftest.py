"""Shared test fixtures for facial keypoint detection tests.

This module provides common fixtures used across unit and integration tests.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest


if TYPE_CHECKING:
    from numpy.typing import NDArray


@pytest.fixture
def project_root() -> Path:
    """Return project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_image_gray() -> "NDArray[np.uint8]":
    """Create a sample grayscale image for testing.

    Returns:
        Random 96x96 grayscale image.
    """
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (96, 96), dtype=np.uint8)


@pytest.fixture
def sample_image_color() -> "NDArray[np.uint8]":
    """Create a sample color image for testing.

    Returns:
        Random 480x640x3 BGR image.
    """
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def sample_keypoints_normalized() -> "NDArray[np.float32]":
    """Create sample normalized keypoints in [-1, 1] range.

    Returns:
        Array of shape (30,) with 15 (x, y) keypoint pairs.
    """
    rng = np.random.default_rng(42)
    return rng.uniform(-1, 1, (30,)).astype(np.float32)


@pytest.fixture
def sample_keypoints_pixel() -> "NDArray[np.float32]":
    """Create sample keypoints in pixel coordinates [0, 96].

    Returns:
        Array of shape (30,) with 15 (x, y) keypoint pairs.
    """
    rng = np.random.default_rng(42)
    return rng.uniform(0, 96, (30,)).astype(np.float32)


@pytest.fixture
def sample_training_batch() -> tuple["NDArray[np.float32]", "NDArray[np.float32]"]:
    """Create a small batch of training data.

    Returns:
        Tuple of (images, keypoints) where:
            - images: Image array of shape (10, 96, 96, 1)
            - keypoints: Keypoints array of shape (10, 30)
    """
    rng = np.random.default_rng(42)
    n_samples = 10
    images = rng.random((n_samples, 96, 96, 1), dtype=np.float32)
    keypoints = rng.uniform(-1, 1, (n_samples, 30)).astype(np.float32)
    return images, keypoints


@pytest.fixture
def cascade_path(project_root: Path) -> Path:
    """Return path to face cascade file.

    Returns:
        Path to haarcascade_frontalface_default.xml
    """
    return project_root / "detector_architectures" / "haarcascade_frontalface_default.xml"


@pytest.fixture
def test_images_dir(project_root: Path) -> Path:
    """Return path to test images directory.

    Returns:
        Path to images/ directory.
    """
    return project_root / "images"
