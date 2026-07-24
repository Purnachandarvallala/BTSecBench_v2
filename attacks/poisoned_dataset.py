"""
==============================================================
BTSecBench_v2

Poisoned Dataset Wrapper

==============================================================

Wraps an existing dataset and applies
backdoor attacks on-the-fly.

Supports

✓ Clean Dataset
✓ BadNets
✓ Blend
✓ SIG
✓ WaNet

==============================================================
"""

from __future__ import annotations

from torch.utils.data import Dataset


class PoisonedDataset(Dataset):
    """
    Dataset wrapper that applies a backdoor attack
    during data loading.

    Parameters
    ----------
    dataset : Dataset
        Original dataset.

    attack : BaseAttack
        Backdoor attack instance.

    poison_all : bool
        If True, every sample is poisoned.
        Useful for Attack Success Rate evaluation.
    """

    ############################################################

    def __init__(
        self,
        dataset,
        attack=None,
        poison_all=False,
    ):

        self.dataset = dataset

        self.attack = attack

        self.poison_all = poison_all

    ############################################################

    def __len__(self):

        return len(self.dataset)

    ############################################################

    def __getitem__(
        self,
        index,
    ):

        sample = self.dataset[index]

        image = sample["image"]

        label = sample["label"]

        path = sample.get("path", "")

        poisoned = False

        ########################################################
        # Clean dataset
        ########################################################

        if self.attack is None:

            return {

                "image": image,

                "label": label,

                "path": path,

                "poisoned": False,

            }

        ########################################################
        # Force poison every sample
        ########################################################

        if self.poison_all:

            original_rate = self.attack.poison_rate

            self.attack.poison_rate = 1.0

            image, label, poisoned = self.attack(
                image,
                int(label),
            )

            self.attack.poison_rate = original_rate

        ########################################################
        # Normal poisoning
        ########################################################

        else:

            image, label, poisoned = self.attack(
                image,
                int(label),
            )

        ########################################################

        return {

            "image": image,

            "label": label,

            "path": path,

            "poisoned": poisoned,

        }

    ############################################################

    def summary(self):

        print("=" * 60)

        print("POISONED DATASET")

        print("=" * 60)

        print(f"Samples      : {len(self)}")

        print(
            f"Attack       : "
            f"{type(self.attack).__name__ if self.attack else 'None'}"
        )

        print(
            f"Poison Rate  : "
            f"{self.attack.poison_rate if self.attack else 0.0}"
        )

        print(
            f"Target Class : "
            f"{self.attack.target_class if self.attack else '-'}"
        )

        print(
            f"Poison All   : {self.poison_all}"
        )

        print("=" * 60)