"""Data download utilities for facial keypoint detection.

This module provides functions for downloading the facial keypoint
dataset from Kaggle or alternative sources.

The dataset is from the Kaggle Facial Keypoints Detection competition:
https://www.kaggle.com/c/facial-keypoints-detection

Requirements:
    - Kaggle API credentials (~/.kaggle/kaggle.json)
    - Or manual download from Kaggle website
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

from facial_keypoints.config import settings


def check_kaggle_credentials() -> bool:
    """Check if Kaggle API credentials are configured.

    Returns:
        True if credentials file exists, False otherwise.
    """
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    return kaggle_json.exists()


def download_from_kaggle(
    data_dir: Path | str | None = None,
    competition: str = "facial-keypoints-detection",
) -> Path:
    """Download dataset from Kaggle using the Kaggle API.

    Requires Kaggle API credentials to be configured.
    See: https://github.com/Kaggle/kaggle-api#api-credentials

    Args:
        data_dir: Directory to save the data. Defaults to project data/ dir.
        competition: Kaggle competition name.

    Returns:
        Path to the data directory containing the CSV files.

    Raises:
        RuntimeError: If Kaggle API is not installed or credentials missing.
        subprocess.CalledProcessError: If download fails.

    Example:
        >>> data_path = download_from_kaggle()
        >>> print(f"Data saved to: {data_path}")
    """
    if data_dir is None:
        data_dir = settings.data_dir
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Check for kaggle credentials
    if not check_kaggle_credentials():
        msg = (
            "Kaggle API credentials not found.\n"
            "Please set up your credentials:\n"
            "1. Go to https://www.kaggle.com/account\n"
            "2. Click 'Create New API Token'\n"
            "3. Save kaggle.json to ~/.kaggle/kaggle.json\n"
            "4. Run: chmod 600 ~/.kaggle/kaggle.json"
        )
        raise RuntimeError(msg)

    # Check if kaggle CLI is available
    if shutil.which("kaggle") is None:
        msg = (
            "Kaggle CLI not found. Install it with:\n"
            "  pip install kaggle\n"
            "  # or\n"
            "  uv add kaggle"
        )
        raise RuntimeError(msg)

    print(f"Downloading {competition} dataset...")
    print(f"Destination: {data_dir}")

    # Download competition data
    subprocess.run(
        [
            "kaggle",
            "competitions",
            "download",
            "-c",
            competition,
            "-p",
            str(data_dir),
        ],
        check=True,
    )

    # Extract zip file if present
    zip_path = data_dir / f"{competition}.zip"
    if zip_path.exists():
        print(f"Extracting {zip_path.name}...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(data_dir)
        zip_path.unlink()  # Remove zip after extraction
        print("Extraction complete!")

    # Verify expected files exist
    expected_files = ["training.csv", "test.csv"]
    for filename in expected_files:
        filepath = data_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / 1024 / 1024
            print(f"  ✓ {filename} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ {filename} (not found)")

    return data_dir


def download_sample_data(
    data_dir: Path | str | None = None,
    n_samples: int = 100,
) -> Path:
    """Create sample training data for testing (without full download).

    Generates synthetic sample data matching the expected format.
    Useful for testing the pipeline without downloading the full dataset.

    Args:
        data_dir: Directory to save the data.
        n_samples: Number of synthetic samples to generate.

    Returns:
        Path to the data directory.

    Example:
        >>> data_path = download_sample_data(n_samples=50)
        >>> # Now you can test: X, y = load_data()
    """
    import numpy as np  # noqa: PLC0415
    import pandas as pd  # noqa: PLC0415

    if data_dir is None:
        data_dir = settings.data_dir
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {n_samples} synthetic samples...")

    # Keypoint column names (15 keypoints x 2 coordinates)
    keypoint_columns = [
        "left_eye_center_x",
        "left_eye_center_y",
        "right_eye_center_x",
        "right_eye_center_y",
        "left_eye_inner_corner_x",
        "left_eye_inner_corner_y",
        "left_eye_outer_corner_x",
        "left_eye_outer_corner_y",
        "right_eye_inner_corner_x",
        "right_eye_inner_corner_y",
        "right_eye_outer_corner_x",
        "right_eye_outer_corner_y",
        "left_eyebrow_inner_end_x",
        "left_eyebrow_inner_end_y",
        "left_eyebrow_outer_end_x",
        "left_eyebrow_outer_end_y",
        "right_eyebrow_inner_end_x",
        "right_eyebrow_inner_end_y",
        "right_eyebrow_outer_end_x",
        "right_eyebrow_outer_end_y",
        "nose_tip_x",
        "nose_tip_y",
        "mouth_left_corner_x",
        "mouth_left_corner_y",
        "mouth_right_corner_x",
        "mouth_right_corner_y",
        "mouth_center_top_lip_x",
        "mouth_center_top_lip_y",
        "mouth_center_bottom_lip_x",
        "mouth_center_bottom_lip_y",
    ]

    rng = np.random.default_rng(42)

    # Generate synthetic data
    data: dict[str, list] = {col: [] for col in keypoint_columns}
    data["Image"] = []

    for _ in range(n_samples):
        # Generate random face-like keypoints (roughly centered)
        keypoints = rng.uniform(20, 76, size=30)

        for i, col in enumerate(keypoint_columns):
            data[col].append(keypoints[i])

        # Generate random grayscale image (96x96 = 9216 pixels)
        pixels = rng.integers(0, 256, size=9216)
        data["Image"].append(" ".join(map(str, pixels)))

    df = pd.DataFrame(data)
    train_path = data_dir / "training.csv"
    df.to_csv(train_path, index=False)

    # Create smaller test set (no keypoints)
    test_data = {"Image": data["Image"][: n_samples // 5]}
    test_df = pd.DataFrame(test_data)
    test_path = data_dir / "test.csv"
    test_df.to_csv(test_path, index=False)

    print(f"  ✓ training.csv ({len(df)} samples)")
    print(f"  ✓ test.csv ({len(test_df)} samples)")
    print(f"Data saved to: {data_dir}")

    return data_dir


def verify_data(data_dir: Path | str | None = None) -> dict[str, bool]:
    """Verify that required data files exist and are valid.

    Args:
        data_dir: Directory containing the data files.

    Returns:
        Dictionary with file names as keys and validity as values.

    Example:
        >>> status = verify_data()
        >>> if all(status.values()):
        ...     print("All data files present!")
    """
    import pandas as pd  # noqa: PLC0415

    if data_dir is None:
        data_dir = settings.data_dir
    data_dir = Path(data_dir)

    results = {}

    # Check training.csv
    train_path = data_dir / "training.csv"
    if train_path.exists():
        try:
            df = pd.read_csv(train_path, nrows=5)
            has_image = "Image" in df.columns
            has_keypoints = len(df.columns) > 1
            results["training.csv"] = has_image and has_keypoints
        except Exception:
            results["training.csv"] = False
    else:
        results["training.csv"] = False

    # Check test.csv
    test_path = data_dir / "test.csv"
    if test_path.exists():
        try:
            df = pd.read_csv(test_path, nrows=5)
            results["test.csv"] = "Image" in df.columns
        except Exception:
            results["test.csv"] = False
    else:
        results["test.csv"] = False

    return results


def get_data_info(data_dir: Path | str | None = None) -> dict[str, str | int]:
    """Get information about the downloaded data.

    Args:
        data_dir: Directory containing the data files.

    Returns:
        Dictionary with data information.
    """
    import pandas as pd  # noqa: PLC0415

    if data_dir is None:
        data_dir = settings.data_dir
    data_dir = Path(data_dir)

    info: dict[str, str | int] = {"data_dir": str(data_dir)}

    # Training data info
    train_path = data_dir / "training.csv"
    if train_path.exists():
        df = pd.read_csv(train_path)
        info["train_samples"] = len(df)
        info["train_size_mb"] = round(train_path.stat().st_size / 1024 / 1024, 2)
        info["n_keypoint_columns"] = len(df.columns) - 1  # Exclude 'Image'

        # Count samples with all keypoints present
        keypoint_cols = [c for c in df.columns if c != "Image"]
        complete_samples = df[keypoint_cols].dropna().shape[0]
        info["complete_samples"] = complete_samples

    # Test data info
    test_path = data_dir / "test.csv"
    if test_path.exists():
        df = pd.read_csv(test_path)
        info["test_samples"] = len(df)
        info["test_size_mb"] = round(test_path.stat().st_size / 1024 / 1024, 2)

    return info
