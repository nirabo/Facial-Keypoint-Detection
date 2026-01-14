# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-14

### Added

- Modern project structure with `src/` layout following Python packaging best practices
- Type hints for all public functions and classes
- Google-style docstrings throughout the codebase
- `FacialKeypointsPipeline` class for end-to-end face detection and keypoint prediction
- `FaceDetector` class wrapping OpenCV Haar Cascade classifiers
- `KeypointPredictor` class for CNN-based keypoint inference
- `BoundingBox` immutable dataclass for face detection results
- Custom exception hierarchy (`FacialKeypointsError`, `DataLoadError`, `ModelLoadError`, etc.)
- Pydantic-based configuration management with environment variable support
- pytest test suite with fixtures for unit testing
- Docker support with multi-stage builds:
  - Development stage with Jupyter Lab
  - Training stage (CPU)
  - Training stage with NVIDIA CUDA support (GPU)
  - Inference stage
- Docker Compose configuration with profiles for different workflows
- Makefile with standard targets: help, up, down, logs, ps, build, restart, clean, shell, test, lint, format, check-env
- Comprehensive `.gitignore` and `.dockerignore` files
- Environment configuration templates (`.env.example`)

### Changed

- Migrated from standalone `keras` to `tensorflow.keras` (TensorFlow 2.16+)
- Updated deprecated `numpy.fromstring()` to list comprehension pattern
- Fixed mutable default arguments in function signatures (e.g., `plot_keypoints`)
- Reorganized code into logical subpackages:
  - `facial_keypoints.data` - Data loading and preprocessing
  - `facial_keypoints.detection` - Face detection
  - `facial_keypoints.models` - Keypoint prediction
  - `facial_keypoints.visualization` - Plotting utilities
- Updated all dependencies to modern versions (Python 3.12+, numpy 2.0+, etc.)
- Moved notebook to `notebooks/` directory
- Cleared notebook outputs to reduce repository size

### Removed

- Legacy `utils.py` file (functionality migrated to new package structure)

### Fixed

- Deprecated `numpy.fromstring()` usage causing warnings
- Mutable default arguments causing potential bugs
- Missing type annotations throughout codebase
- Inconsistent error handling

### Security

- Added non-root user in Docker images
- Environment-based configuration for sensitive values

## [0.1.0] - 2019-XX-XX (Original)

### Added

- Initial implementation as Udacity course project
- Jupyter notebook with OpenCV face detection
- CNN model for facial keypoint regression
- Basic utility functions in `utils.py`

[Unreleased]: https://github.com/yourusername/Facial-Keypoint-Detection/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/Facial-Keypoint-Detection/releases/tag/v1.0.0
[0.1.0]: https://github.com/yourusername/Facial-Keypoint-Detection/releases/tag/v0.1.0
