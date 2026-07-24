"""
==============================================================
BTSecBench_v2

BadNets Attack

==============================================================

Reference:
BadNets: Evaluating Backdooring Attacks on Deep Neural Networks
Gu et al., IEEE Access 2019

==============================================================
"""

from __future__ import annotations

import numpy as np
import torch

from attacks.base_attack import BaseAttack


class BadNetsAttack(BaseAttack):
    """
    Classic square trigger attack.

    Supports:

    ✓ NumPy images
    ✓ Torch tensors
    ✓ RGB images
    ✓ Multiple trigger positions
    """

    ############################################################

    def __init__(
        self,
        target_class=0,
        poison_rate=0.10,
        trigger_size=4,
        trigger_color=(255, 255, 255),
        position="bottom_right",
        seed=42,
    ):

        super().__init__(
            target_class=target_class,
            poison_rate=poison_rate,
            seed=seed,
        )

        self.trigger_size = trigger_size

        self.trigger_color = np.array(
            trigger_color,
            dtype=np.uint8,
        )

        self.position = position

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

    def _trigger_location(
        self,
        h,
        w,
    ):

        s = self.trigger_size

        if self.position == "bottom_right":

            return h - s, w - s

        elif self.position == "bottom_left":

            return h - s, 0

        elif self.position == "top_right":

            return 0, w - s

        elif self.position == "top_left":

            return 0, 0

        elif self.position == "center":

            return (

                (h - s) // 2,

                (w - s) // 2,

            )

        else:

            raise ValueError(

                f"Unknown position: {self.position}"

            )

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

        poisoned = image.copy()

        h, w = poisoned.shape[:2]

        y, x = self._trigger_location(
            h,
            w,
        )

        ########################################################

        poisoned[
            y:y + self.trigger_size,
            x:x + self.trigger_size,
        ] = self.trigger_color

        ########################################################

        if tensor_input:

            return self._numpy_to_tensor(
                poisoned
            )

        return poisoned

    ############################################################

    def __repr__(self):

        return (

            "BadNetsAttack("

            f"target_class={self.target_class}, "

            f"poison_rate={self.poison_rate}, "

            f"trigger_size={self.trigger_size}, "

            f"position='{self.position}')"

        )