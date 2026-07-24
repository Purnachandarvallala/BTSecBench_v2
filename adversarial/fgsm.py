"""
==============================================================

BTSecBench_v2

Fast Gradient Sign Method (FGSM)

Reference:
Goodfellow et al.
Explaining and Harnessing Adversarial Examples (2015)

==============================================================
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn as nn

from torch.utils.data import DataLoader

from tqdm import tqdm

from data.dataloader import create_dataset

from models import get_model


class FGSMAttack:

    """
    Fast Gradient Sign Method.

    x_adv = x + ε * sign(∇x J)

    """

    def __init__(
        self,
        model_name="efficientnet_b0",
        checkpoint="checkpoints/best_model.pth",
        epsilon=8 / 255,
        batch_size=64,
        device=None,
    ):

        self.model_name = model_name
        self.checkpoint = checkpoint
        self.epsilon = epsilon
        self.batch_size = batch_size

        self.device = (
            torch.device(device)
            if device
            else torch.device(
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )
        )

        self.output_dir = Path(
            "reports/adversarial/fgsm"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model = None

        self.criterion = nn.CrossEntropyLoss()

        print("=" * 60)
        print("FAST GRADIENT SIGN METHOD")
        print("=" * 60)
        print(f"Model      : {model_name}")
        print(f"Checkpoint : {checkpoint}")
        print(f"Epsilon    : {epsilon:.6f}")
        print(f"Device      : {self.device}")
        print("=" * 60)

    ############################################################

    def load_model(self):

        print("\nLoading model...")

        model = get_model(
            model_name=self.model_name,
            num_classes=43,
            pretrained=False,
        )

        checkpoint = torch.load(
            self.checkpoint,
            map_location=self.device,
            weights_only=False,
        )

        if isinstance(checkpoint, dict):

            if "model_state_dict" in checkpoint:

                checkpoint = checkpoint[
                    "model_state_dict"
                ]

        model.load_state_dict(checkpoint)

        model.to(self.device)

        model.eval()

        self.model = model

        print("✓ Model loaded")

    ############################################################

    def build_dataloader(self):

        dataset = create_dataset(

            csv_file="data/splits/test.csv",

            mode="test",

        )

        loader = DataLoader(

            dataset,

            batch_size=self.batch_size,

            shuffle=False,

            num_workers=4,

            pin_memory=True,

        )

        print(
            f"Test Samples : {len(dataset)}"
        )

        return loader
    