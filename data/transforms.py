"""
BTSecBench_v2
Professional Image Transformation Pipeline

Supports:
- Training
- Validation
- Testing
- Explainability
- Inference
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2


# ==========================================================
# Dataset Statistics (Computed from GTSRB)
# ==========================================================

MEAN = (
    0.3403,
    0.3121,
    0.3214,
)

STD = (
    0.2724,
    0.2608,
    0.2669,
)

IMAGE_SIZE = 64


# ==========================================================
# Training Transforms
# ==========================================================

def get_train_transforms():

    return A.Compose([

        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE
        ),

        A.Affine(
            scale=(0.90, 1.10),
            translate_percent=(-0.05, 0.05),
            rotate=(-15, 15),
            shear=(-5, 5),
            p=0.50,
        ),

        A.RandomBrightnessContrast(
            brightness_limit=0.20,
            contrast_limit=0.20,
            p=0.50,
        ),

        A.GaussNoise(
            p=0.20,
        ),

        A.Normalize(
            mean=MEAN,
            std=STD,
        ),

        ToTensorV2(),

    ])


# ==========================================================
# Validation Transforms
# ==========================================================

def get_val_transforms():

    return A.Compose([

        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE,
        ),

        A.Normalize(
            mean=MEAN,
            std=STD,
        ),

        ToTensorV2(),

    ])


# ==========================================================
# Test Transforms
# ==========================================================

def get_test_transforms():

    return A.Compose([

        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE,
        ),

        A.Normalize(
            mean=MEAN,
            std=STD,
        ),

        ToTensorV2(),

    ])


# ==========================================================
# Explainability Transforms
# (No Normalization)
# ==========================================================

def get_xai_transforms():

    return A.Compose([

        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE,
        ),

        ToTensorV2(),

    ])
# ==========================================================
# STRIP Transform (Resize + Tensor ONLY)
# ==========================================================

def get_strip_transforms():

    return A.Compose([

        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE,
        ),

        ToTensorV2(),

    ])


# ==========================================================
# Inference Transforms
# ==========================================================

def get_inference_transforms():

    return A.Compose([

        A.Resize(
            IMAGE_SIZE,
            IMAGE_SIZE,
        ),

        A.Normalize(
            mean=MEAN,
            std=STD,
        ),

        ToTensorV2(),

    ])