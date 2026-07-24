from models.backbones.cnn import CNNBaseline
from models.backbones.resnet18 import ResNet18
from models.backbones.mobilenet_v3 import MobileNetV3
from models.backbones.efficientnet_b0 import EfficientNetB0


MODEL_REGISTRY = {

    "cnn": CNNBaseline,

    "resnet18": ResNet18,

    "mobilenet_v3": MobileNetV3,

    "efficientnet_b0": EfficientNetB0

}