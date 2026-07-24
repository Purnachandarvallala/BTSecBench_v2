"""
==============================================================
BTSecBench_v2

SIG Backdoor Attack

==============================================================

Reference:
Invisible Backdoor Attacks on Deep Neural Networks via
Steganography and Sinusoidal Signal Trigger

==============================================================
"""

from __future__ import annotations

import numpy as np
import torch

from attacks.base_attack import BaseAttack


class SIGAttack(BaseAttack):
    """
    Sinusoidal Trigger Attack.

    Adds a sinusoidal perturbation across the image.

    Supports

    ✓ NumPy images
    ✓ Torch tensors
    ✓ RGB images
    """

    ############################################################

    def __init__(
        self,
        target_class=0,
        poison_rate=0.10,
        delta=20,
        frequency=6,
        seed=42,
    ):

        super().__init__(
            target_class=target_class,
            poison_rate=poison_rate,
            seed=seed,
        )

        self.delta = delta
        self.frequency = frequency

    ############################################################

    def _tensor_to_numpy(self, image):

        image = image.detach().cpu()

        image = image.permute(1, 2, 0).numpy()

        image = np.clip(image * 255.0, 0, 255)

        return image.astype(np.uint8)

    ############################################################

    def _numpy_to_tensor(self, image):

        image = image.astype(np.float32) / 255.0

        image = torch.from_numpy(image)

        image = image.permute(2, 0, 1)

        return image

    ############################################################

    def apply_trigger(
        self,
        image,
    ):

        tensor_input = isinstance(
            image,
            torch.Tensor,
        )

        ########################################################

        if tensor_input:

            image = self._tensor_to_numpy(image)

        else:

            image = np.asarray(image).copy()

        ########################################################

        image = image.astype(np.float32)

        h, w = image.shape[:2]

        x = np.arange(w)

        signal = self.delta * np.sin(
            2 * np.pi * self.frequency * x / w
        )

        signal = np.tile(
            signal,
            (h, 1),
        )

        signal = signal[:, :, np.newaxis]

        poisoned = image + signal

        poisoned = np.clip(
            poisoned,
            0,
            255,
        ).astype(np.uint8)

        ########################################################

        if tensor_input:

            return self._numpy_to_tensor(
                poisoned
            )

        return poisoned

    ############################################################

    def __repr__(self):

        return (

            "SIGAttack("

            f"target_class={self.target_class}, "

            f"poison_rate={self.poison_rate}, "

            f"delta={self.delta}, "

            f"frequency={self.frequency})"

        )