"""
==============================================================
BTSecBench_v2

Base Backdoor Attack
==============================================================

Abstract base class for all backdoor attacks.

All attacks inherit from this class.

Implemented attacks:
    • BadNets
    • Blend
    • SIG
    • WaNet

==============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import random

import numpy as np
import torch


class BaseAttack(ABC):
    """
    Base class for all backdoor attacks.

    Parameters
    ----------
    target_class : int
        Target label after poisoning.

    poison_rate : float
        Fraction of samples to poison.

    seed : int
        Random seed.
    """

    ############################################################

    def __init__(
        self,
        target_class: int = 0,
        poison_rate: float = 0.10,
        seed: int = 42,
    ):

        self.target_class = target_class

        self.poison_rate = poison_rate

        self.seed = seed

        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    ############################################################

    @abstractmethod
    def apply_trigger(
        self,
        image,
    ):
        """
        Apply trigger to ONE image.

        Must return image with same type.

        Parameters
        ----------
        image
            numpy.ndarray
            or torch.Tensor

        Returns
        -------
        image
        """
        raise NotImplementedError

    ############################################################

    def should_poison(self):

        """
        Decide whether current sample
        should be poisoned.
        """

        return random.random() < self.poison_rate

    ############################################################

    def poison_sample(
        self,
        image,
        label,
    ):

        """
        Poison one sample.

        Returns
        -------
        poisoned_image

        poisoned_label

        poison_flag
        """

        poison_flag = self.should_poison()

        if poison_flag:

            image = self.apply_trigger(image)

            label = self.target_class

        return image, label, poison_flag

    ############################################################

    def poison_batch(
        self,
        images,
        labels,
    ):

        """
        Poison an entire batch.

        Parameters
        ----------
        images

        labels

        Returns
        -------
        images

        labels

        poison_flags
        """

        poisoned_images = []

        poisoned_labels = []

        poison_flags = []

        for image, label in zip(images, labels):

            img, lbl, flag = self.poison_sample(
                image,
                int(label),
            )

            poisoned_images.append(img)

            poisoned_labels.append(lbl)

            poison_flags.append(flag)

        ########################################################

        if isinstance(labels, torch.Tensor):

            poisoned_labels = torch.tensor(
                poisoned_labels,
                dtype=labels.dtype,
                device=labels.device,
            )

        return (

            poisoned_images,

            poisoned_labels,

            poison_flags,

        )

    ############################################################

    def __call__(
        self,
        image,
        label,
    ):

        return self.poison_sample(
            image=image,
            label=label,
        )

    ############################################################

    def __repr__(self):

        return (

            f"{self.__class__.__name__}("

            f"target_class={self.target_class}, "

            f"poison_rate={self.poison_rate})"

        )