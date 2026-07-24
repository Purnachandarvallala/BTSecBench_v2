"""
==============================================================
BTSecBench_v2

Training History Manager

Author : Shivaprasad Aredla
==============================================================
"""

from pathlib import Path
import json
import pandas as pd


class History:

    def __init__(self):

        self.history = {
            "epoch": [],
            "train_loss": [],
            "train_accuracy": [],
            "val_loss": [],
            "val_accuracy": [],
            "learning_rate": [],
        }

    def update(
        self,
        epoch,
        train_loss,
        train_accuracy,
        val_loss,
        val_accuracy,
        learning_rate,
    ):

        self.history["epoch"].append(epoch)
        self.history["train_loss"].append(train_loss)
        self.history["train_accuracy"].append(train_accuracy)
        self.history["val_loss"].append(val_loss)
        self.history["val_accuracy"].append(val_accuracy)
        self.history["learning_rate"].append(learning_rate)

    def dataframe(self):

        return pd.DataFrame(self.history)

    def save_csv(self, save_path):

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        self.dataframe().to_csv(save_path, index=False)

    def save_json(self, save_path):

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            json.dump(self.history, f, indent=4)

    def __len__(self):

        return len(self.history["epoch"])