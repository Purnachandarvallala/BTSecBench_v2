from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import json


class DatasetStatistics:

    def __init__(self, dataset_root):

        self.root = Path(dataset_root)

        self.train_root = (
            self.root /
            "Final_Training" /
            "Images"
        )

        self.output_dir = Path("data/statistics")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------

    def class_distribution(self):

        classes = []
        counts = []

        for folder in sorted(self.train_root.iterdir()):

            if not folder.is_dir():
                continue

            csv_file = folder / f"GT-{folder.name}.csv"

            df = pd.read_csv(csv_file, sep=";")

            classes.append(int(folder.name))
            counts.append(len(df))

        distribution = pd.DataFrame(
            {
                "Class": classes,
                "Images": counts
            }
        )

        distribution.to_csv(
            self.output_dir / "class_distribution.csv",
            index=False
        )

        plt.figure(figsize=(14,5))
        plt.bar(distribution["Class"], distribution["Images"])
        plt.xlabel("Class")
        plt.ylabel("Images")
        plt.title("GTSRB Class Distribution")
        plt.tight_layout()

        plt.savefig(
            self.output_dir /
            "class_distribution.png",
            dpi=300
        )

        plt.close()

        return distribution

    # --------------------------------------------------

    def image_resolution(self):

        widths = []
        heights = []

        for folder in sorted(self.train_root.iterdir()):

            if not folder.is_dir():
                continue

            csv_file = folder / f"GT-{folder.name}.csv"

            df = pd.read_csv(csv_file, sep=";")

            for filename in df["Filename"]:

                image = Image.open(folder / filename)

                w, h = image.size

                widths.append(w)
                heights.append(h)

        return {
            "min_width": int(np.min(widths)),
            "max_width": int(np.max(widths)),
            "avg_width": float(np.mean(widths)),
            "min_height": int(np.min(heights)),
            "max_height": int(np.max(heights)),
            "avg_height": float(np.mean(heights))
        }

    # --------------------------------------------------

    def compute_mean_std(self):

        print("Computing Mean / Std (may take a few minutes)...")

        pixels = []

        for folder in sorted(self.train_root.iterdir()):

            if not folder.is_dir():
                continue

            csv_file = folder / f"GT-{folder.name}.csv"

            df = pd.read_csv(csv_file, sep=";")

            for filename in df["Filename"]:

                img = Image.open(folder / filename)

                img = img.resize((64,64))

                arr = np.asarray(img).astype(np.float32) / 255.0

                pixels.append(arr.reshape(-1,3))

        pixels = np.concatenate(pixels, axis=0)

        mean = pixels.mean(axis=0)
        std = pixels.std(axis=0)

        return mean.tolist(), std.tolist()

    # --------------------------------------------------

    def save_summary(self, distribution, resolution, mean, std):

        summary = {

            "dataset": "GTSRB",

            "num_classes": len(distribution),

            "num_images": int(distribution.Images.sum()),

            "mean": mean,

            "std": std,

            "resolution": resolution

        }

        with open(
            self.output_dir / "statistics.json",
            "w"
        ) as f:

            json.dump(summary, f, indent=4)

    # --------------------------------------------------

    def run(self):

        print("="*60)
        print("Dataset Statistics")
        print("="*60)

        distribution = self.class_distribution()

        resolution = self.image_resolution()

        mean, std = self.compute_mean_std()

        self.save_summary(
            distribution,
            resolution,
            mean,
            std
        )

        print()

        print("Dataset Statistics Generated Successfully.")