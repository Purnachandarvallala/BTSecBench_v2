"""
==============================================================
BTSecBench_v2

Reproducibility Utilities

Author : Shivaprasad Aredla
==============================================================
"""

import os
import random

import numpy as np
import torch


def set_seed(seed: int = 42) -> None:
    """
    Set all random seeds for reproducibility.

    Parameters
    ----------
    seed : int
        Random seed.
    """

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    torch.cuda.manual_seed(seed)

    torch.cuda.manual_seed_all(seed)

    os.environ["PYTHONHASHSEED"] = str(seed)

    torch.backends.cudnn.deterministic = True

    torch.backends.cudnn.benchmark = False


def seed_worker(worker_id):
    """
    Seed DataLoader workers.
    """

    worker_seed = torch.initial_seed() % (2**32)

    np.random.seed(worker_seed)

    random.seed(worker_seed)


def get_generator(seed: int = 42):
    """
    Generator for DataLoader.

    Returns
    -------
    torch.Generator
    """

    g = torch.Generator()

    g.manual_seed(seed)

    return g