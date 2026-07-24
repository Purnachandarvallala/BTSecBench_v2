"""
MobileNetV3 Backbone
====================

Transfer Learning Backbone
"""

import torch.nn as nn
from torchvision.models import (
    mobilenet_v3_large,
    MobileNet_V3_Large_Weights,
)

from models.backbones.base_model import BaseModel


class MobileNetV3(BaseModel):

    def __init__(
        self,
        num_classes=43,
        pretrained=True,
        freeze_backbone=False,
    ):

        super().__init__(num_classes)

        weights = (
            MobileNet_V3_Large_Weights.DEFAULT
            if pretrained
            else None
        )

        self.model = mobilenet_v3_large(weights=weights)

        if freeze_backbone:
            for param in self.model.parameters():
                param.requires_grad = False

        in_features = self.model.classifier[-1].in_features

        self.model.classifier[-1] = nn.Linear(
            in_features,
            num_classes
        )

    def forward(self, x):
        return self.model(x)