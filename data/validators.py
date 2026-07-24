"""
=========================================================
BTSecBench_v2

Dataset Validator

=========================================================
"""

from pathlib import Path
from PIL import Image
import pandas as pd


class DatasetValidator:

    def __init__(self, dataset_root):

        self.dataset_root = Path(dataset_root)

        self.training_root = (
            self.dataset_root /
            "Final_Training" /
            "Images"
        )

        self.test_root = (
            self.dataset_root /
            "Final_Test" /
            "Images"
        )

    # ----------------------------------------------------

    def validate_structure(self):

        print("\nChecking folder structure...")

        assert self.training_root.exists(), \
            "Training folder missing."

        assert self.test_root.exists(), \
            "Test folder missing."

        print("✓ Folder structure OK")

    # ----------------------------------------------------

    def validate_class_folders(self):

        print("Checking class folders...")

        folders = sorted(self.training_root.iterdir())

        classes = [
            x for x in folders
            if x.is_dir()
        ]

        assert len(classes) == 43, \
            f"Expected 43 classes, got {len(classes)}"

        print("✓ 43 class folders found.")

    # ----------------------------------------------------

    def validate_csv_files(self):

        print("Checking annotation CSV files...")

        for class_dir in sorted(self.training_root.iterdir()):

            if not class_dir.is_dir():
                continue

            csv_file = class_dir / f"GT-{class_dir.name}.csv"

            assert csv_file.exists(), \
                f"Missing {csv_file}"

        print("✓ All annotation files found.")

    # ----------------------------------------------------

    def validate_images(self):

        print("Checking images...")

        image_count = 0

        for class_dir in sorted(self.training_root.iterdir()):

            if not class_dir.is_dir():
                continue

            csv_file = class_dir / f"GT-{class_dir.name}.csv"

            df = pd.read_csv(csv_file, sep=";")

            for _, row in df.iterrows():

                image_path = class_dir / row["Filename"]

                assert image_path.exists(), \
                    f"Missing image {image_path}"

                try:

                    img = Image.open(image_path)

                    img.verify()

                except Exception:

                    raise RuntimeError(
                        f"Corrupted image: {image_path}"
                    )

                image_count += 1

        print(f"✓ {image_count} images verified.")

    # ----------------------------------------------------

    def run(self):

        print("=" * 60)
        print("DATASET VALIDATION")
        print("=" * 60)

        self.validate_structure()

        self.validate_class_folders()

        self.validate_csv_files()

        self.validate_images()

        print()

        print("=" * 60)
        print("DATASET VALIDATION PASSED")
        print("=" * 60)