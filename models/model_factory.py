from models.registry import MODEL_REGISTRY


def get_model(
    model_name,
    num_classes=43,
    pretrained=True,
    freeze_backbone=False,
):

    model_name = model_name.lower()

    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Available models: {list(MODEL_REGISTRY.keys())}"
        )

    # -------------------------------
    # Baseline CNN
    # -------------------------------
    if model_name == "cnn":
        return MODEL_REGISTRY[model_name](
            num_classes=num_classes
        )

    # -------------------------------
    # Transfer Learning Models
    # -------------------------------
    return MODEL_REGISTRY[model_name](
        num_classes=num_classes,
        pretrained=pretrained,
        freeze_backbone=freeze_backbone,
    )


def available_models():
    return list(MODEL_REGISTRY.keys())