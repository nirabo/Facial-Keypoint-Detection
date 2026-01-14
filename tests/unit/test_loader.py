"""Unit tests for data loading functionality."""

import numpy as np

from facial_keypoints.data.loader import get_data_statistics
from facial_keypoints.exceptions import DataLoadError


class TestGetDataStatistics:
    """Tests for get_data_statistics function."""

    def test_returns_correct_keys_without_y(
        self,
        sample_training_batch: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test that correct keys are returned when y is None."""
        images, _ = sample_training_batch
        stats = get_data_statistics(images)

        expected_keys = {
            "n_samples",
            "image_height",
            "image_width",
            "x_min",
            "x_max",
            "x_mean",
            "x_std",
        }
        assert set(stats.keys()) == expected_keys

    def test_returns_correct_keys_with_y(
        self,
        sample_training_batch: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test that correct keys are returned when y is provided."""
        images, keypoints = sample_training_batch
        stats = get_data_statistics(images, keypoints)

        assert "n_keypoints" in stats
        assert "y_min" in stats
        assert "y_max" in stats
        assert "y_mean" in stats
        assert "y_std" in stats

    def test_n_samples_correct(
        self,
        sample_training_batch: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test that n_samples is computed correctly."""
        images, keypoints = sample_training_batch
        stats = get_data_statistics(images, keypoints)

        assert stats["n_samples"] == 10
        assert stats["n_keypoints"] == 15  # 30 / 2

    def test_image_dimensions_correct(
        self,
        sample_training_batch: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test that image dimensions are computed correctly."""
        images, _ = sample_training_batch
        stats = get_data_statistics(images)

        assert stats["image_height"] == 96
        assert stats["image_width"] == 96

    def test_x_stats_in_range(
        self,
        sample_training_batch: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test that image statistics are within expected range."""
        images, _ = sample_training_batch
        stats = get_data_statistics(images)

        assert 0 <= stats["x_min"] <= 1
        assert 0 <= stats["x_max"] <= 1
        assert 0 <= stats["x_mean"] <= 1
        assert stats["x_std"] >= 0

    def test_y_stats_in_range(
        self,
        sample_training_batch: tuple[np.ndarray, np.ndarray],
    ) -> None:
        """Test that keypoint statistics are within expected range."""
        images, keypoints = sample_training_batch
        stats = get_data_statistics(images, keypoints)

        # Normalized keypoints should be in [-1, 1]
        assert -1 <= stats["y_min"] <= 1
        assert -1 <= stats["y_max"] <= 1
        assert -1 <= stats["y_mean"] <= 1


class TestDataLoadError:
    """Tests for DataLoadError exception."""

    def test_error_message_includes_path(self) -> None:
        """Test that error message includes file path."""
        error = DataLoadError("/path/to/file.csv", "Custom message")
        assert "/path/to/file.csv" in str(error)
        assert "Custom message" in str(error)

    def test_file_path_attribute(self) -> None:
        """Test that file_path attribute is set correctly."""
        error = DataLoadError("/path/to/file.csv")
        assert error.file_path == "/path/to/file.csv"
