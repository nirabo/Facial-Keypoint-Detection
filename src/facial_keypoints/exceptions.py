"""Custom exceptions for facial keypoint detection.

This module defines a hierarchy of exceptions for handling various
error conditions in the facial keypoint detection pipeline.
"""


class FacialKeypointsError(Exception):
    """Base exception for facial keypoints package.

    All custom exceptions in this package inherit from this class,
    allowing for broad exception handling when needed.
    """


class DataLoadError(FacialKeypointsError):
    """Raised when data loading fails.

    Attributes:
        file_path: Path to the file that failed to load.
    """

    def __init__(self, file_path: str, message: str = "Failed to load data") -> None:
        """Initialize DataLoadError.

        Args:
            file_path: Path to the file that failed to load.
            message: Error message prefix.
        """
        self.file_path = file_path
        super().__init__(f"{message}: {file_path}")


class ModelLoadError(FacialKeypointsError):
    """Raised when model loading fails.

    Attributes:
        model_path: Path to the model that failed to load.
    """

    def __init__(self, model_path: str, message: str = "Failed to load model") -> None:
        """Initialize ModelLoadError.

        Args:
            model_path: Path to the model that failed to load.
            message: Error message prefix.
        """
        self.model_path = model_path
        super().__init__(f"{message}: {model_path}")


class FaceDetectionError(FacialKeypointsError):
    """Raised when face detection fails."""


class NoFaceDetectedError(FaceDetectionError):
    """Raised when no face is detected in an image.

    Attributes:
        image_path: Path to the image (if available).
    """

    def __init__(self, image_path: str | None = None) -> None:
        """Initialize NoFaceDetectedError.

        Args:
            image_path: Optional path to the image where no face was found.
        """
        self.image_path = image_path
        message = "No face detected"
        if image_path:
            message += f" in {image_path}"
        super().__init__(message)


class MultipleFacesDetectedError(FaceDetectionError):
    """Raised when multiple faces are detected but only one was expected.

    Attributes:
        count: Number of faces detected.
        image_path: Path to the image (if available).
    """

    def __init__(self, count: int, image_path: str | None = None) -> None:
        """Initialize MultipleFacesDetectedError.

        Args:
            count: Number of faces detected.
            image_path: Optional path to the image.
        """
        self.count = count
        self.image_path = image_path
        message = f"Multiple faces detected ({count})"
        if image_path:
            message += f" in {image_path}"
        super().__init__(message)


class InvalidImageError(FacialKeypointsError):
    """Raised when an invalid image is provided.

    This can occur when:
    - Image file cannot be read
    - Image array is empty or malformed
    - Image format is not supported
    """

    def __init__(self, reason: str = "Invalid image") -> None:
        """Initialize InvalidImageError.

        Args:
            reason: Description of why the image is invalid.
        """
        super().__init__(reason)


class PreprocessingError(FacialKeypointsError):
    """Raised when image preprocessing fails."""

    def __init__(self, reason: str = "Preprocessing failed") -> None:
        """Initialize PreprocessingError.

        Args:
            reason: Description of why preprocessing failed.
        """
        super().__init__(reason)
