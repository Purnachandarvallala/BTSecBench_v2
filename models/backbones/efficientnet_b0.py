"""
EfficientNet-B0 Backbone
"""

import torch.nn as nn
from torchvision.models import (
    efficientnet_b0,
    EfficientNet_B0_Weights,
)

from models.backbones.base_model import BaseModel


class EfficientNetB0(BaseModel):

    def __init__(
        self,
        num_classes=43,
        pretrained=True,
        freeze_backbone=False,
    ):

        super().__init__(num_classes)

        weights = (
            EfficientNet_B0_Weights.DEFAULT
            if pretrained
            else None
        )

        self.model = efficientnet_b0(weights=weights)

        if freeze_backbone:
            for param in self.model.parameters():
                param.requires_grad = False

        in_features = self.model.classifier[-1].in_features

        self.model.classifier[-1] = nn.Linear(
            in_features,
            num_classes,
        )

    def forward(self, x):
        return self.model(x)