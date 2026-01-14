# Facial Keypoint Detection

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

End-to-end facial keypoint detection system combining OpenCV face detection with CNN-based keypoint regression.

![Facial Keypoint Detection](./images/obamas_with_keypoints.png)

## Overview

This project detects **15 facial keypoints** (eyes, eyebrows, nose, mouth) on faces in images. It combines:

- **Face Detection**: OpenCV Haar Cascade classifiers
- **Keypoint Prediction**: CNN trained on 96x96 grayscale face images
- **End-to-End Pipeline**: Detect faces → crop → predict keypoints → map to original coordinates

Originally developed as part of the Udacity Computer Vision Nanodegree, now modernized with:
- Modern Python 3.12+ with type hints
- Docker containerization with GPU support
- pytest test suite
- Ruff linting and mypy type checking

## Quick Start

### Installation (Local)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/yourusername/Facial-Keypoint-Detection.git
cd Facial-Keypoint-Detection
uv sync --all-extras

# Verify installation
uv run python -c "from facial_keypoints import settings; print(settings)"
```

### Installation (Docker)

```bash
# Copy environment file
cp .env.example .env.dev

# Start Jupyter Lab
make up

# Open http://localhost:8888 (token: facialkeys)
```

## Usage

### Python API

```python
from facial_keypoints.pipeline import FacialKeypointsPipeline

# Initialize pipeline
pipeline = FacialKeypointsPipeline(
    cascade_path="detector_architectures/haarcascade_frontalface_default.xml",
    model_path="models/model.keras",
)

# Process an image
result = pipeline.process("images/james.jpg")

print(f"Detected {result.n_faces} face(s)")
for face in result.faces:
    print(f"  Face at {face.bounding_box.center}")
    print(f"  Keypoints shape: {face.keypoints.shape}")

# Visualize results
pipeline.visualize(result)
```

### Data Loading

```python
from facial_keypoints.data import load_data, get_data_statistics

# Load training data
X_train, y_train = load_data(test=False)
print(f"Training: {X_train.shape}, {y_train.shape}")

# Load test data
X_test, _ = load_data(test=True)
print(f"Test: {X_test.shape}")

# Get statistics
stats = get_data_statistics(X_train, y_train)
print(f"Samples: {stats['n_samples']}, Keypoints: {stats['n_keypoints']}")
```

### Face Detection

```python
from facial_keypoints.detection import FaceDetector
import cv2

detector = FaceDetector()
image = cv2.imread("photo.jpg")

# Detect all faces
boxes = detector.detect(image)
for box in boxes:
    print(f"Face at ({box.x}, {box.y}), size: {box.width}x{box.height}")

# Detect single face (largest)
box = detector.detect_single(image)
```

## Project Structure

```
Facial-Keypoint-Detection/
├── src/facial_keypoints/      # Main package
│   ├── config.py              # Pydantic settings
│   ├── exceptions.py          # Custom exceptions
│   ├── pipeline.py            # End-to-end pipeline
│   ├── data/                  # Data loading
│   ├── detection/             # Face detection
│   ├── models/                # Keypoint prediction
│   └── visualization/         # Plotting utilities
├── tests/                     # pytest test suite
├── notebooks/                 # Jupyter notebooks
├── detector_architectures/    # Haar cascade XML files
├── images/                    # Test images
├── data/                      # Training data (gitignored)
├── models/                    # Trained models (gitignored)
├── pyproject.toml             # Project config & dependencies
├── Dockerfile                 # Multi-stage Docker build
├── compose.yaml               # Docker Compose services
└── Makefile                   # Development commands
```

## Development

### Available Commands

```bash
make help          # Show all commands
make up            # Start Jupyter Lab (Docker)
make down          # Stop services
make install       # Install dependencies locally
make test          # Run tests
make test-coverage # Run tests with coverage
make lint          # Run Ruff linter
make format        # Format code with Ruff
make type-check    # Run mypy type checker
make train         # Run training (CPU)
make train-gpu     # Run training (GPU)
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
uv run pytest tests/unit/test_loader.py -v
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check
```

## Training

### Data Setup

Download the [Kaggle Facial Keypoints Detection dataset](https://www.kaggle.com/c/facial-keypoints-detection/data) and place files in `data/`:

```
data/
├── training.csv   # ~7000 images with 15 keypoints each
└── test.csv       # ~1800 images (no keypoints)
```

### Train Model

```bash
# Using Docker (CPU)
make train

# Using Docker (GPU)
make train-gpu

# Or run the notebook
make up  # Then open notebooks/Facial-Keypoint-Detection.ipynb
```

## Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `jupyter` | JupyterLab for development | 8888 |
| `train` | Training (CPU) | - |
| `train-gpu` | Training (GPU with CUDA) | - |
| `inference` | Model inference | - |

## Configuration

Configuration via environment variables (`.env.dev`):

```bash
# Training
EPOCHS=50
BATCH_SIZE=64
LEARNING_RATE=0.001
VALIDATION_SPLIT=0.2

# Paths
MODEL_PATH=models/model.keras
CASCADE_PATH=detector_architectures/haarcascade_frontalface_default.xml

# Face Detection
SCALE_FACTOR=1.2
MIN_NEIGHBORS=5
```

## Model Architecture

CNN architecture for keypoint regression:

```
Input: 96x96x1 grayscale image

Conv2D(16, 3x3) + ReLU → MaxPool(2x2)
Conv2D(32, 3x3) + ReLU → MaxPool(2x2)
Conv2D(64, 3x3) + ReLU → MaxPool(2x2)
Conv2D(128, 3x3) + ReLU → MaxPool(2x2)

Flatten → Dense(512) + ReLU + Dropout(0.2)
Dense(30)  # 15 keypoints × 2 coordinates

Output: 30 values (x, y for each keypoint)
Total Parameters: ~1.16M
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Udacity Computer Vision Nanodegree](https://www.udacity.com/course/computer-vision-nanodegree--nd891)
- [Kaggle Facial Keypoints Detection](https://www.kaggle.com/c/facial-keypoints-detection)
- OpenCV for Haar Cascade classifiers
