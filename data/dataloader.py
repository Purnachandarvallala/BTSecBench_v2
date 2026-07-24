import torch
from torch.utils.data import DataLoader

from data.dataset import GTSRBDataset
from data.transforms import (
    get_train_transforms,
    get_val_transforms,
    get_test_transforms,
    get_strip_transforms,
)


def build_dataloader(csv_file, batch_size, shuffle, mode):

    if mode == "train":
        transform = get_train_transforms()
    elif mode == "val":
        transform = get_val_transforms()
    elif mode == "strip":
        transform = get_strip_transforms()
    else:
        transform = get_test_transforms()

    dataset = GTSRBDataset(
        csv_file=csv_file,
        transform=transform,
        mode=mode,
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=False,
    )

    return loader


# ============================================================
# Convenience wrapper
# ============================================================

def create_dataloaders(
    train_csv="data/splits/train.csv",
    val_csv="data/splits/val.csv",
    batch_size=32,
):

    train_loader = build_dataloader(
        csv_file=train_csv,
        batch_size=batch_size,
        shuffle=True,
        mode="train",
    )

    val_loader = build_dataloader(
        csv_file=val_csv,
        batch_size=batch_size,
        shuffle=False,
        mode="val",
    )

    return train_loader, val_loader
# ============================================================
# Dataset Factory
# ============================================================

def create_dataset(
    csv_file,
    mode="train",
):
    """
    Create a dataset without wrapping it in a DataLoader.

    This is used for:
        - Clean training
        - Backdoor attacks
        - Explainability
        - Future research modules
    """

    if mode == "train":
        transform = get_train_transforms()

    elif mode == "val":
        transform = get_val_transforms()

    else:
        transform = get_test_transforms()

    dataset = GTSRBDataset(
        csv_file=csv_file,
        transform=transform,
        mode=mode,
    )

    return dataset