from pathlib import Path
from PIL import Image

import pandas as pd
import torch
from torch.utils.data import Dataset
import numpy as np

class GTSRBDataset(Dataset):
    """
    Production Dataset for BTSecBench_v2

    Supports

    - Train
    - Validation
    - Test
    - Explainability
    - Backdoor experiments
    """

    def __init__(
        self,
        csv_file,
        transform=None,
        mode="train"
    ):

        self.mode = mode
        self.transform = transform
        
        self.samples = pd.read_csv(csv_file)

        self.samples["image"] = (
            self.samples["image"]
            .apply(Path)
        )

    def __len__(self):

        return len(self.samples)

    def __getitem__(self, index):

        row = self.samples.iloc[index]

        image_path = row["image"]

        label = int(row["label"])

        image = Image.open(image_path).convert("RGB")

        # Albumentations requires numpy array
        image = np.array(image)
        
        if self.transform:

            image = self.transform(image=image)["image"]

        return {

            "image": image,

            "label": torch.tensor(
                label,
                dtype=torch.long
            ),

            "path": str(image_path)
        }