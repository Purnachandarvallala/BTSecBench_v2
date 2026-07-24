"""
=========================================================
BTSecBench_v2

Dataset Metadata Generator
=========================================================
"""

from pathlib import Path
from datetime import datetime
import json
import pandas as pd


def generate_metadata():

    train_csv = Path("data/splits/train.csv")
    val_csv = Path("data/splits/val.csv")
    test_csv = Path("data/raw/GTSRB/GT-final_test.csv")

    train = pd.read_csv(train_csv)
    val = pd.read_csv(val_csv)
    test = pd.read_csv(test_csv, sep=";")

    metadata = {

        "dataset": "GTSRB",

        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "num_classes": 43,

        "image_size": 64,

        "train_samples": len(train),

        "validation_samples": len(val),

        "test_samples": len(test),

        "total_samples":
            len(train) +
            len(val) +
            len(test),

        "image_extension": ".ppm"

    }

    output = Path("data/cache")
    output.mkdir(exist_ok=True)

    with open(output / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print("=" * 60)
    print("Metadata Generated Successfully")
    print("=" * 60)

    for k, v in metadata.items():
        print(f"{k:20}: {v}")


if __name__ == "__main__":
    generate_metadata()