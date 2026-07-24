"""
==============================================================
BTSecBench_v2

Blend Backdoor Attack

==============================================================

Reference:
Targeted Backdoor Attacks on Deep Learning Systems
Chen et al.

==============================================================
"""

from __future__ import annotations

import numpy as np
import torch

from attacks.base_attack import BaseAttack


class BlendAttack(BaseAttack):
    """
    Blend Backdoor Attack.

    Blends a trigger pattern with the original image.

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
        alpha=0.20,
        trigger_color=(255, 255, 255),
        seed=42,
    ):

        super().__init__(
            target_class=target_class,
            poison_rate=poison_rate,
            seed=seed,
        )

        self.alpha = alpha

        self.trigger_color = np.array(
            trigger_color,
            dtype=np.uint8,
        )

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

        trigger = np.ones_like(
            image,
            dtype=np.uint8,
        )

        trigger[:] = self.trigger_color

        ########################################################

        poisoned = (

            (1.0 - self.alpha) * image +

            self.alpha * trigger

        )

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

            "BlendAttack("

            f"target_class={self.target_class}, "

            f"poison_rate={self.poison_rate}, "

            f"alpha={self.alpha})"

        )