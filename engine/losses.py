"""
==============================================================
BTSecBench_v2

Loss Functions

Author : Shivaprasad Aredla
==============================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================
# Focal Loss
# ============================================================

class FocalLoss(nn.Module):

    def __init__(
        self,
        alpha=1.0,
        gamma=2.0,
        reduction="mean"
    ):

        super().__init__()

        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits, targets):

        ce_loss = F.cross_entropy(
            logits,
            targets,
            reduction="none"
        )

        pt = torch.exp(-ce_loss)

        loss = self.alpha * ((1 - pt) ** self.gamma) * ce_loss

        if self.reduction == "mean":
            return loss.mean()

        if self.reduction == "sum":
            return loss.sum()

        return loss


# ============================================================
# Label Smoothing
# ============================================================

class LabelSmoothingLoss(nn.Module):

    def __init__(
        self,
        smoothing=0.1
    ):

        super().__init__()

        self.smoothing = smoothing

    def forward(self, logits, targets):

        confidence = 1.0 - self.smoothing

        log_probs = F.log_softmax(logits, dim=1)

        n_classes = logits.size(1)

        true_dist = torch.zeros_like(log_probs)

        true_dist.fill_(self.smoothing / (n_classes - 1))

        true_dist.scatter_(1, targets.unsqueeze(1), confidence)

        return torch.mean(
            torch.sum(
                -true_dist * log_probs,
                dim=1
            )
        )


# ============================================================
# Factory
# ============================================================

def get_loss(
    name="cross_entropy",
    class_weights=None,
    smoothing=0.1,
    gamma=2.0,
    alpha=1.0,
):

    name = name.lower()

    if name == "cross_entropy":

        return nn.CrossEntropyLoss(
            weight=class_weights
        )

    elif name == "weighted":

        return nn.CrossEntropyLoss(
            weight=class_weights
        )

    elif name == "label_smoothing":

        return LabelSmoothingLoss(
            smoothing=smoothing
        )

    elif name == "focal":

        return FocalLoss(
            alpha=alpha,
            gamma=gamma
        )

    else:

        raise ValueError(
            f"Unknown loss : {name}"
        )