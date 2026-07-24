"""
==============================================================
BTSecBench_v2

WaNet Inspired Backdoor Attack

==============================================================

Research-inspired implementation based on:

WaNet: Imperceptible Warping-based Backdoor Attack

==============================================================
"""

from __future__ import annotations

import cv2
import numpy as np
import torch

from attacks.base_attack import BaseAttack


class WaNetAttack(BaseAttack):
    """
    WaNet-inspired smooth geometric warping attack.

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
        warp_strength=2.0,
        grid_size=4,
        seed=42,
    ):

        super().__init__(
            target_class=target_class,
            poison_rate=poison_rate,
            seed=seed,
        )

        self.warp_strength = warp_strength

        self.grid_size = grid_size

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

        h, w = image.shape[:2]

        ########################################################
        # Smooth displacement field
        ########################################################

        dx = np.random.uniform(
            -1,
            1,
            (
                self.grid_size,
                self.grid_size,
            ),
        )

        dy = np.random.uniform(
            -1,
            1,
            (
                self.grid_size,
                self.grid_size,
            ),
        )

        dx = cv2.resize(
            dx,
            (w, h),
            interpolation=cv2.INTER_CUBIC,
        )

        dy = cv2.resize(
            dy,
            (w, h),
            interpolation=cv2.INTER_CUBIC,
        )

        dx *= self.warp_strength

        dy *= self.warp_strength

        ########################################################
        # Pixel mapping
        ########################################################

        xx, yy = np.meshgrid(
            np.arange(w),
            np.arange(h),
        )

        map_x = (
            xx + dx
        ).astype(np.float32)

        map_y = (
            yy + dy
        ).astype(np.float32)

        ########################################################
        # Warp image
        ########################################################

        warped = cv2.remap(

            image,

            map_x,

            map_y,

            interpolation=cv2.INTER_LINEAR,

            borderMode=cv2.BORDER_REFLECT,

        )

        ########################################################

        if tensor_input:

            return self._numpy_to_tensor(
                warped
            )

        return warped

    ############################################################

    def __repr__(self):

        return (

            "WaNetAttack("

            f"target_class={self.target_class}, "

            f"poison_rate={self.poison_rate}, "

            f"warp_strength={self.warp_strength}, "

            f"grid_size={self.grid_size})"

        )