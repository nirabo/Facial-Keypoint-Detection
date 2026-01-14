"""Model inference for facial keypoint prediction.

This module provides a high-level interface for loading trained
CNN models and predicting facial keypoints on cropped face images.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from facial_keypoints.config import settings
from facial_keypoints.exceptions import ModelLoadError

if TYPE_CHECKING:
    from numpy.typing import NDArray

# Import keras - support both TensorFlow's keras and standalone keras
try:
    from tensorflow import keras
except ImportError:
    import keras


@dataclass(frozen=True, slots=True)
class KeypointPrediction:
    """Container for keypoint predictions.

    Attributes:
        keypoints: Array of shape (n_keypoints, 2) with (x, y) coordinates
            in pixel space (denormalized).
        raw_output: Raw model output before denormalization, shape (n_keypoints * 2,).
    """

    keypoints: "NDArray[np.float32]"
    raw_output: "NDArray[np.float32]"


class KeypointPredictor:
    """Predictor for facial keypoints using a trained CNN model.

    This class loads a trained Keras model and provides methods for
    predicting facial keypoints on preprocessed face images.

    Attributes:
        model_path: Path to the trained model file.
        image_size: Expected input image size (square).

    Example:
        >>> predictor = KeypointPredictor("models/model.keras")
        >>> face_crop = cv2.imread("face.jpg")
        >>> prediction = predictor.predict(face_crop)
        >>> print(f"Detected {len(prediction.keypoints)} keypoints")
        >>> for i, (x, y) in enumerate(prediction.keypoints):
        ...     print(f"Keypoint {i}: ({x:.1f}, {y:.1f})")
    """

    def __init__(
        self,
        model_path: Path | str | None = None,
        image_size: int | None = None,
    ) -> None:
        """Initialize the keypoint predictor.

        Args:
            model_path: Path to trained Keras model (.h5, .keras, or SavedModel).
                If None, uses default from settings.
            image_size: Expected input image size (default: 96).

        Raises:
            ModelLoadError: If model cannot be loaded.
        """
        self.model_path = Path(model_path or settings.model_path)
        self.image_size = image_size if image_size is not None else settings.image_size

        if not self.model_path.exists():
            raise ModelLoadError(str(self.model_path), "Model file not found")

        try:
            self._model = keras.models.load_model(str(self.model_path))
        except Exception as e:
            raise ModelLoadError(str(self.model_path), str(e)) from e

    def preprocess(self, image: "NDArray[np.uint8]") -> "NDArray[np.float32]":
        """Preprocess an image for model input.

        Converts image to grayscale, resizes to expected dimensions,
        normalizes to [0, 1], and adds batch/channel dimensions.

        Args:
            image: Input image (grayscale or color, any size).

        Returns:
            Preprocessed image array of shape (1, size, size, 1).
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Resize to expected input size
        resized = cv2.resize(gray, (self.image_size, self.image_size))

        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0

        # Add batch and channel dimensions: (H, W) -> (1, H, W, 1)
        return np.expand_dims(np.expand_dims(normalized, axis=-1), axis=0)

    def predict(
        self,
        image: "NDArray[np.uint8]",
        denormalize: bool = True,
    ) -> KeypointPrediction:
        """Predict facial keypoints on an image.

        Args:
            image: Input face image (cropped, grayscale or color).
            denormalize: If True, convert coordinates from [-1, 1] to
                pixel space [0, image_size].

        Returns:
            KeypointPrediction with (x, y) coordinates for each keypoint.
        """
        preprocessed = self.preprocess(image)
        raw_output = self._model.predict(preprocessed, verbose=0)
        raw_output = np.squeeze(raw_output).astype(np.float32)

        if denormalize:
            # Convert from [-1, 1] to pixel coordinates [0, 96]
            keypoints = raw_output * 48 + 48
        else:
            keypoints = raw_output

        # Reshape to (n_keypoints, 2) for (x, y) pairs
        keypoints_reshaped = keypoints.reshape(-1, 2)

        return KeypointPrediction(keypoints=keypoints_reshaped, raw_output=raw_output)

    def predict_on_original(
        self,
        face_crop: "NDArray[np.uint8]",
        bbox_x: int,
        bbox_y: int,
        original_shape: tuple[int, int],
    ) -> "NDArray[np.float32]":
        """Predict keypoints and map back to original image coordinates.

        This method handles the coordinate transformation from the
        96x96 model input space back to the original image space.

        Args:
            face_crop: Cropped face image from original.
            bbox_x: X coordinate of crop origin in original image.
            bbox_y: Y coordinate of crop origin in original image.
            original_shape: (height, width) of the cropped region
                in the original image.

        Returns:
            Keypoints array of shape (n_keypoints, 2) in original image coordinates.

        Example:
            >>> keypoints = predictor.predict_on_original(
            ...     face_crop,
            ...     bbox_x=100,
            ...     bbox_y=50,
            ...     original_shape=(200, 200),
            ... )
        """
        prediction = self.predict(face_crop, denormalize=True)

        # Scale keypoints from 96x96 to original crop size
        scale_x = original_shape[1] / self.image_size
        scale_y = original_shape[0] / self.image_size

        keypoints = prediction.keypoints.copy()
        keypoints[:, 0] = keypoints[:, 0] * scale_x + bbox_x
        keypoints[:, 1] = keypoints[:, 1] * scale_y + bbox_y

        return keypoints
