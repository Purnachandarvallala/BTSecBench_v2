"""
==========================================================
BTSecBench_v2
Dataset Split Generator
==========================================================

Creates reproducible train/validation CSV files from the
official GTSRB training dataset.

Output:
--------
data/splits/train.csv
data/splits/val.csv

Author:
Shivaprasad Aredla

==========================================================
"""

from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
import yaml


def load_config():
    with open("configs/config.yaml", "r") as f:
        return yaml.safe_load(f)


def scan_training_dataset(training_root: Path):
    """
    Scan GTSRB training dataset.

    Returns
    -------
    DataFrame

    columns:
        image
        label
    """

    images = []
    labels = []

    class_dirs = sorted(training_root.iterdir())

    for class_dir in class_dirs:

        if not class_dir.is_dir():
            continue

        class_id = int(class_dir.name)

        csv_path = class_dir / f"GT-{class_dir.name}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(csv_path)

        df = pd.read_csv(csv_path, sep=";")

        for _, row in df.iterrows():

            image_path = class_dir / row["Filename"]

            images.append(str(image_path))

            labels.append(class_id)

    return pd.DataFrame(
        {
            "image": images,
            "label": labels
        }
    )


def create_splits():

    config = load_config()

    dataset_root = (
        Path(config["dataset"]["root"])
        / config["dataset"]["train_dir"]
    )

    output_dir = Path("data/splits")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = scan_training_dataset(dataset_root)

    train_df, val_df = train_test_split(
        df,
        test_size=config["dataset"]["val_split"],
        stratify=df["label"],
        random_state=config["project"]["seed"],
        shuffle=True
    )

    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)

    train_df.to_csv(
        output_dir / "train.csv",
        index=False
    )

    val_df.to_csv(
        output_dir / "val.csv",
        index=False
    )

    print("=" * 60)
    print("Dataset Split Completed")
    print("=" * 60)

    print(f"Training Samples : {len(train_df)}")
    print(f"Validation Samples : {len(val_df)}")

    print()

    print("Files Saved")

    print(output_dir / "train.csv")
    print(output_dir / "val.csv")


if __name__ == "__main__":
    create_splits()