"""Visualization utilities for facial keypoint detection.

This module provides functions for visualizing facial keypoints,
face detections, and training data.
"""

from typing import TYPE_CHECKING

import cv2
import matplotlib.pyplot as plt
import numpy as np


# Constants for image channel detection
_GRAYSCALE_DIMS = 2
_COLOR_CHANNELS = 3

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from numpy.typing import NDArray

    from facial_keypoints.detection.face_detector import BoundingBox


def plot_keypoints(
    image: "NDArray[np.float32 | np.uint8]",
    keypoints: "NDArray[np.float32]",
    ax: "Axes | None" = None,
    marker_color: str = "cyan",
    marker_size: int = 40,
    title: str | None = None,
    denormalize: bool = False,
) -> "Axes":
    """Plot facial keypoints on an image.

    Args:
        image: Image array (grayscale or RGB).
        keypoints: Keypoints as (n_points, 2) or flat (n_points*2,) array.
            If denormalize=True, expects values in [-1, 1].
            Otherwise expects pixel coordinates.
        ax: Matplotlib axes to plot on. If None, creates new figure.
        marker_color: Color for keypoint markers.
        marker_size: Size of keypoint markers.
        title: Optional title for the plot.
        denormalize: If True, convert keypoints from [-1, 1] to pixel coords.

    Returns:
        The matplotlib Axes object.

    Example:
        >>> fig, ax = plt.subplots()
        >>> plot_keypoints(image, keypoints, ax=ax)
        >>> plt.show()
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 8))

    # Squeeze extra dimensions
    img = np.squeeze(image)

    # Display image
    if len(img.shape) == _GRAYSCALE_DIMS:
        ax.imshow(img, cmap="gray")
    else:
        ax.imshow(img)

    # Flatten keypoints if needed
    kp = keypoints.flatten().astype(np.float32)

    # Denormalize if needed
    if denormalize:
        kp = kp * 48 + 48

    # Plot keypoints (x values at even indices, y at odd)
    ax.scatter(
        kp[0::2],
        kp[1::2],
        marker="o",
        c=marker_color,
        s=marker_size,
        edgecolors="black",
        linewidths=0.5,
        zorder=10,
    )

    ax.set_xticks([])
    ax.set_yticks([])

    if title:
        ax.set_title(title)

    return ax


def plot_training_samples(
    images: "NDArray[np.float32]",
    keypoints: "NDArray[np.float32]",
    n_samples: int = 9,
    figsize: tuple[int, int] = (12, 12),
) -> "Figure":
    """Plot a grid of training samples with keypoints.

    Useful for visualizing training data quality and distribution.

    Args:
        images: Image array of shape (n, height, width, 1).
        keypoints: Keypoint array of shape (n, 30) in normalized [-1, 1] range.
        n_samples: Number of samples to display (will be arranged in grid).
        figsize: Figure size as (width, height) in inches.

    Returns:
        The matplotlib Figure object.

    Example:
        >>> X, y = load_data()
        >>> fig = plot_training_samples(X, y, n_samples=16)
        >>> plt.savefig("training_samples.png")
    """
    n_cols = int(np.ceil(np.sqrt(n_samples)))
    n_rows = int(np.ceil(n_samples / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98, hspace=0.05, wspace=0.05)

    # Handle single subplot case
    axes_flat = [axes] if n_samples == 1 else axes.flatten()

    for i in range(min(n_samples, len(images))):
        # Denormalize keypoints from [-1, 1] to pixel coordinates
        kp_denorm = keypoints[i] * 48 + 48
        plot_keypoints(images[i], kp_denorm, ax=axes_flat[i])

    # Hide unused axes
    for i in range(n_samples, len(axes_flat)):
        axes_flat[i].axis("off")

    return fig


def plot_face_detections(
    image: "NDArray[np.uint8]",
    boxes: "list[BoundingBox]",
    ax: "Axes | None" = None,
    box_color: tuple[int, int, int] = (255, 0, 0),
    box_thickness: int = 3,
    title: str | None = None,
) -> "Axes":
    """Plot face detection bounding boxes on an image.

    Args:
        image: Image array (BGR or RGB).
        boxes: List of BoundingBox objects from face detection.
        ax: Matplotlib axes to plot on.
        box_color: RGB color for bounding boxes.
        box_thickness: Line thickness for boxes in pixels.
        title: Optional title for the plot.

    Returns:
        The matplotlib Axes object.

    Example:
        >>> detector = FaceDetector()
        >>> boxes = detector.detect(image)
        >>> plot_face_detections(image, boxes, title=f"Found {len(boxes)} faces")
        >>> plt.show()
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 10))

    # Make a copy to draw on
    img_copy = image.copy()

    for box in boxes:
        cv2.rectangle(
            img_copy,
            (box.x, box.y),
            (box.x + box.width, box.y + box.height),
            box_color,
            box_thickness,
        )

    # Convert BGR to RGB if needed
    if len(img_copy.shape) == _COLOR_CHANNELS and img_copy.shape[2] == _COLOR_CHANNELS:
        img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)

    ax.imshow(img_copy)
    ax.set_xticks([])
    ax.set_yticks([])

    if title:
        ax.set_title(title)

    return ax


def plot_pipeline_result(
    image: "NDArray[np.uint8]",
    faces: list,
    figsize: tuple[int, int] = (10, 10),
    show_boxes: bool = True,
    show_keypoints: bool = True,
    keypoint_color: str = "cyan",
    keypoint_size: int = 40,
) -> "Figure":
    """Plot results from the facial keypoints pipeline.

    Args:
        image: Original image (BGR format).
        faces: List of FaceKeypointsResult objects from pipeline.
        figsize: Figure size.
        show_boxes: Whether to draw bounding boxes.
        show_keypoints: Whether to draw keypoints.
        keypoint_color: Color for keypoint markers.
        keypoint_size: Size of keypoint markers.

    Returns:
        The matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Make a copy and convert to RGB
    img_rgb = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)

    if show_boxes:
        for face in faces:
            box = face.bounding_box
            cv2.rectangle(
                img_rgb,
                (box.x, box.y),
                (box.x + box.width, box.y + box.height),
                (255, 0, 0),
                3,
            )

    ax.imshow(img_rgb)

    if show_keypoints:
        for face in faces:
            ax.scatter(
                face.keypoints[:, 0],
                face.keypoints[:, 1],
                marker="o",
                c=keypoint_color,
                s=keypoint_size,
                edgecolors="black",
                linewidths=0.5,
                zorder=10,
            )

    ax.set_title(f"Detected {len(faces)} face(s)")
    ax.set_xticks([])
    ax.set_yticks([])

    plt.tight_layout()
    return fig
