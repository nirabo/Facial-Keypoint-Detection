#!/usr/bin/env python3
"""Command-line script for downloading facial keypoint data.

Usage:
    # Download from Kaggle (requires API credentials)
    python scripts/download_data.py --kaggle

    # Generate synthetic sample data for testing
    python scripts/download_data.py --sample --n-samples 100

    # Extract nested zip files (training.zip, test.zip)
    python scripts/download_data.py --extract

    # Verify existing data
    python scripts/download_data.py --verify

    # Show data info
    python scripts/download_data.py --info
"""

import argparse
import sys
from pathlib import Path


# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from facial_keypoints.data.download import (
    check_kaggle_credentials,
    download_from_kaggle,
    download_sample_data,
    extract_nested_zips,
    get_data_info,
    verify_data,
)


def handle_verify(data_dir: Path | None) -> int:
    """Handle --verify command."""
    print("Verifying data files...")
    status = verify_data(data_dir)
    all_valid = True
    for filename, valid in status.items():
        symbol = "✓" if valid else "✗"
        status_text = "OK" if valid else "MISSING/INVALID"
        print(f"  {symbol} {filename}: {status_text}")
        if not valid:
            all_valid = False

    if all_valid:
        print("\nAll data files present and valid!")
        return 0
    print("\nSome data files are missing. Run with --kaggle or --sample.")
    return 1


def handle_info(data_dir: Path | None) -> int:
    """Handle --info command."""
    print("Data Information")
    print("=" * 40)
    try:
        info = get_data_info(data_dir)
        for key, value in info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  Error: {e}")
        print("\n  Data may not be downloaded yet.")
        return 1
    return 0


def handle_kaggle(data_dir: Path | None) -> int:
    """Handle --kaggle command."""
    if not check_kaggle_credentials():
        print("Kaggle credentials not found!")
        print("\nOption 1: Environment variables (recommended for CI/scripts)")
        print("  export KAGGLE_USERNAME=your_username")
        print("  export KAGGLE_KEY=your_api_key")
        print("\nOption 2: Credentials file")
        print("  1. Go to https://www.kaggle.com/account")
        print("  2. Click 'Create New API Token'")
        print("  3. Save kaggle.json to ~/.kaggle/")
        print("  4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return 1

    download_from_kaggle(data_dir)
    print("\nDownload complete!")
    return 0


def handle_sample(data_dir: Path | None, n_samples: int) -> int:
    """Handle --sample command."""
    download_sample_data(data_dir, n_samples=n_samples)
    print("\nSample data generated!")
    print("Note: This is synthetic data for testing only.")
    return 0


def handle_extract(data_dir: Path | None) -> int:
    """Handle --extract command."""
    print("Extracting nested zip files...")
    extract_nested_zips(data_dir)
    print("\nExtraction complete!")
    return 0


def main() -> int:  # noqa: PLR0911
    """Main entry point for the data download script."""
    parser = argparse.ArgumentParser(
        description="Download or generate facial keypoint data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --kaggle              Download from Kaggle
  %(prog)s --sample              Generate sample data
  %(prog)s --verify              Check if data exists
  %(prog)s --info                Show data information

Kaggle Setup:
  1. Create account at kaggle.com
  2. Go to Settings -> API -> Create New Token
     (NOT the new KGAT tokens - they don't work with the CLI)
  3. Save kaggle.json to ~/.kaggle/
  4. chmod 600 ~/.kaggle/kaggle.json

Note: The kaggle CLI requires legacy API credentials (username + key),
not the new KGAT_* tokens which are for Kaggle API v2.
        """,
    )

    parser.add_argument(
        "--kaggle",
        action="store_true",
        help="Download dataset from Kaggle (requires API credentials)",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate synthetic sample data for testing",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify that required data files exist",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about downloaded data",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract nested zip files (training.zip, test.zip)",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=100,
        help="Number of samples for synthetic data (default: 100)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Data directory (default: data/)",
    )

    args = parser.parse_args()

    # Default action is to show help
    if not any([args.kaggle, args.sample, args.verify, args.info, args.extract]):
        parser.print_help()
        return 0

    try:
        if args.verify:
            return handle_verify(args.data_dir)
        if args.info:
            return handle_info(args.data_dir)
        if args.extract:
            return handle_extract(args.data_dir)
        if args.kaggle:
            return handle_kaggle(args.data_dir)
        if args.sample:
            return handle_sample(args.data_dir, args.n_samples)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
