"""Configuration management for facial keypoint detection.

This module provides centralized configuration using Pydantic settings,
supporting environment variables and .env files.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env files.
    Environment variables are case-insensitive.

    Attributes:
        project_root: Root directory of the project.
        cascade_path: Path to Haar Cascade XML file for face detection.
        model_path: Path to trained Keras model file.
        train_data_path: Path to training CSV file.
        test_data_path: Path to test CSV file.
        image_size: Input image size (square).
        num_keypoints: Number of facial keypoints to detect.
        epochs: Number of training epochs.
        batch_size: Training batch size.
        learning_rate: Training learning rate.
        validation_split: Fraction of data for validation.
        scale_factor: Scale factor for face detection.
        min_neighbors: Minimum neighbors for face detection filtering.
        log_level: Logging level.

    Example:
        >>> from facial_keypoints.config import settings
        >>> print(settings.image_size)
        96
        >>> print(settings.model_path)
        models/model.keras
    """

    # Paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
    )
    cascade_path: Path = Field(
        default=Path("detector_architectures/haarcascade_frontalface_default.xml"),
        description="Path to Haar Cascade XML file",
    )
    model_path: Path = Field(
        default=Path("models/model.keras"),
        description="Path to trained model file",
    )
    train_data_path: Path = Field(
        default=Path("data/training.csv"),
        description="Path to training data CSV",
    )
    test_data_path: Path = Field(
        default=Path("data/test.csv"),
        description="Path to test data CSV",
    )

    # Image settings
    image_size: int = Field(
        default=96,
        ge=32,
        le=512,
        description="Input image size (square)",
    )
    num_keypoints: int = Field(
        default=15,
        ge=1,
        description="Number of facial keypoints",
    )

    # Training settings
    epochs: int = Field(default=50, ge=1, description="Number of training epochs")
    batch_size: int = Field(default=64, ge=1, description="Training batch size")
    learning_rate: float = Field(default=0.001, gt=0, description="Learning rate")
    validation_split: float = Field(
        default=0.2,
        ge=0,
        le=1,
        description="Validation data fraction",
    )

    # Face detection settings
    scale_factor: float = Field(
        default=1.2,
        gt=1.0,
        description="Scale factor for detectMultiScale",
    )
    min_neighbors: int = Field(
        default=5,
        ge=1,
        description="Minimum neighbors for detection filtering",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
