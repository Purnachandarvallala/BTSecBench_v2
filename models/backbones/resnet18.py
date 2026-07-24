"""
ResNet18 Backbone
=================

Transfer Learning Backbone
"""

import torch.nn as nn
from torchvision.models import (
    resnet18,
    ResNet18_Weights,
)

from models.backbones.base_model import BaseModel


class ResNet18(BaseModel):

    def __init__(
        self,
        num_classes=43,
        pretrained=True,
        freeze_backbone=False,
    ):

        super().__init__(num_classes)

        weights = (
            ResNet18_Weights.DEFAULT
            if pretrained
            else None
        )

        self.model = resnet18(weights=weights)

        if freeze_backbone:
            for param in self.model.parameters():
                param.requires_grad = False

        self.model.fc = nn.Linear(
            self.model.fc.in_features,
            num_classes,
        )

    def forward(self, x):
        return self.model(x)