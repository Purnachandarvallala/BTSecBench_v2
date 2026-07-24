"""
Base Model
==========

Base class for all neural network models used in BTSecBench_v2.
"""

import torch
import torch.nn as nn


class BaseModel(nn.Module):
    """
    Base class for all models.
    """

    def __init__(self, num_classes: int):
        super().__init__()

        self.num_classes = num_classes

    def forward(self, x):
        raise NotImplementedError("Forward method must be implemented.")

    # --------------------------------------------------------
    # Parameter Information
    # --------------------------------------------------------

    def total_parameters(self):
        """
        Returns total number of parameters.
        """
        return sum(p.numel() for p in self.parameters())

    def trainable_parameters(self):
        """
        Returns number of trainable parameters.
        """
        return sum(
            p.numel()
            for p in self.parameters()
            if p.requires_grad
        )

    # --------------------------------------------------------
    # Model Size
    # --------------------------------------------------------

    def model_size_mb(self):
        """
        Approximate model size in MB.
        """
        param_bytes = sum(
            p.numel() * p.element_size()
            for p in self.parameters()
        )

        buffer_bytes = sum(
            b.numel() * b.element_size()
            for b in self.buffers()
        )

        total_bytes = param_bytes + buffer_bytes

        return total_bytes / (1024 ** 2)

    # --------------------------------------------------------
    # Freeze / Unfreeze
    # --------------------------------------------------------

    def freeze(self):
        """
        Freeze all model parameters.
        """
        for param in self.parameters():
            param.requires_grad = False

    def unfreeze(self):
        """
        Unfreeze all model parameters.
        """
        for param in self.parameters():
            param.requires_grad = True

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    def get_device(self):
        """
        Returns current device.
        """
        return next(self.parameters()).device

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def summary(self):
        """
        Returns model information.
        """
        return {
            "Model": self.__class__.__name__,
            "Classes": self.num_classes,
            "Total Parameters": self.total_parameters(),
            "Trainable Parameters": self.trainable_parameters(),
            "Model Size (MB)": round(self.model_size_mb(), 2),
            "Device": str(self.get_device())
        }