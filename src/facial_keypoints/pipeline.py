"""End-to-end facial keypoint detection pipeline.

This module provides a high-level pipeline that combines face detection
and keypoint prediction for complete facial keypoint detection.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from facial_keypoints.detection.face_detector import BoundingBox, FaceDetector
from facial_keypoints.exceptions import InvalidImageError
from facial_keypoints.models.predictor import KeypointPredictor


if TYPE_CHECKING:
    from numpy.typing import NDArray


@dataclass
class FaceKeypointsResult:
    """Result of facial keypoint detection for a single face.

    Attributes:
        bounding_box: Face bounding box in original image coordinates.
        keypoints: Array of shape (n_keypoints, 2) with (x, y) pixel coordinates
            in original image space.
        confidence: Detection confidence (reserved for future use).
    """

    bounding_box: BoundingBox
    keypoints: "NDArray[np.float32]"
    confidence: float = 1.0


@dataclass
class PipelineResult:
    """Result of the complete detection pipeline.

    Attributes:
        image: Original input image (BGR format).
        faces: List of detected faces with their keypoints.
    """

    image: "NDArray[np.uint8]"
    faces: list[FaceKeypointsResult] = field(default_factory=list)

    @property
    def n_faces(self) -> int:
        """Return number of detected faces."""
        return len(self.faces)

    def get_keypoints_flat(self) -> "list[NDArray[np.float32]]":
        """Get keypoints as flat arrays for all faces.

        Returns:
            List of arrays, each of shape (n_keypoints * 2,).
        """
        return [face.keypoints.flatten() for face in self.faces]


class FacialKeypointsPipeline:
    """Complete pipeline for facial keypoint detection.

    This class combines face detection using Haar Cascades with
    CNN-based keypoint prediction to detect facial keypoints
    in arbitrary images containing one or more faces.

    Attributes:
        face_detector: Face detection component.
        keypoint_predictor: Keypoint prediction component.

    Example:
        >>> pipeline = FacialKeypointsPipeline()
        >>> result = pipeline.process("photo.jpg")
        >>> print(f"Found {result.n_faces} faces")
        >>> for face in result.faces:
        ...     print(f"Face at {face.bounding_box.center}")
        ...     print(f"Keypoints: {face.keypoints.shape}")
    """

    def __init__(
        self,
        cascade_path: Path | str | None = None,
        model_path: Path | str | None = None,
        scale_factor: float | None = None,
        min_neighbors: int | None = None,
    ) -> None:
        """Initialize the facial keypoints pipeline.

        Args:
            cascade_path: Path to Haar Cascade XML file for face detection.
            model_path: Path to trained Keras model for keypoint prediction.
            scale_factor: Scale factor for face detection (default: 1.2).
            min_neighbors: Minimum neighbors for face detection (default: 5).

        Raises:
            FaceDetectionError: If cascade file cannot be loaded.
            ModelLoadError: If model cannot be loaded.
        """
        self.face_detector = FaceDetector(
            cascade_path=cascade_path,
            scale_factor=scale_factor,
            min_neighbors=min_neighbors,
        )
        self.keypoint_predictor = KeypointPredictor(model_path=model_path)

    def process(
        self,
        image: "NDArray[np.uint8] | str | Path",
        detect_all: bool = True,
    ) -> PipelineResult:
        """Process an image to detect faces and predict keypoints.

        Args:
            image: Input image as numpy array (BGR) or path to image file.
            detect_all: If True, detect all faces in the image.
                If False, detect only the largest face (raises if none found).

        Returns:
            PipelineResult containing the original image and detected faces
            with their keypoints.

        Raises:
            InvalidImageError: If image cannot be loaded or is invalid.
            NoFaceDetectedError: If detect_all=False and no face is found.

        Example:
            >>> result = pipeline.process("group_photo.jpg")
            >>> for face in result.faces:
            ...     print(f"Face: {face.bounding_box}")
        """
        # Load image if path provided
        if isinstance(image, (str, Path)):
            img = cv2.imread(str(image))
            if img is None:
                msg = f"Could not load image: {image}"
                raise InvalidImageError(msg)
        else:
            img = image

        if img is None or img.size == 0:
            msg = "Empty image provided"
            raise InvalidImageError(msg)

        # Detect faces
        if detect_all:
            boxes = self.face_detector.detect(img)
        else:
            box = self.face_detector.detect_single(img)
            boxes = [box]

        # Predict keypoints for each face
        faces: list[FaceKeypointsResult] = []
        for box in boxes:
            # Crop face region
            face_crop = img[box.y : box.y + box.height, box.x : box.x + box.width]

            # Skip empty crops
            if face_crop.size == 0:
                continue

            # Predict keypoints mapped to original image coordinates
            keypoints = self.keypoint_predictor.predict_on_original(
                face_crop,
                bbox_x=box.x,
                bbox_y=box.y,
                original_shape=(box.height, box.width),
            )

            faces.append(FaceKeypointsResult(bounding_box=box, keypoints=keypoints))

        return PipelineResult(image=img, faces=faces)

    def process_single(
        self,
        image: "NDArray[np.uint8] | str | Path",
    ) -> FaceKeypointsResult:
        """Process an image expecting exactly one face.

        Convenience method for images known to contain a single face.

        Args:
            image: Input image as numpy array or path.

        Returns:
            FaceKeypointsResult for the detected face.

        Raises:
            NoFaceDetectedError: If no face is detected.
            InvalidImageError: If image is invalid.
        """
        result = self.process(image, detect_all=False)
        return result.faces[0]

    def visualize(
        self,
        result: PipelineResult,
        show_boxes: bool = True,
        show_keypoints: bool = True,
        figsize: tuple[int, int] = (10, 10),
    ) -> None:
        """Visualize pipeline results.

        Displays the original image with detected faces and keypoints.

        Args:
            result: PipelineResult to visualize.
            show_boxes: Whether to draw bounding boxes around faces.
            show_keypoints: Whether to draw keypoint markers.
            figsize: Figure size as (width, height) in inches.
        """
        # Lazy imports to avoid importing matplotlib at module load time
        import matplotlib.pyplot as plt  # noqa: PLC0415

        from facial_keypoints.visualization.plotting import plot_pipeline_result  # noqa: PLC0415

        plot_pipeline_result(
            result.image,
            result.faces,
            figsize=figsize,
            show_boxes=show_boxes,
            show_keypoints=show_keypoints,
        )
        plt.show()
