import time
import torch

from models import available_models, get_model
from models.utils import (
    count_parameters,
    model_size_mb,
    benchmark_model,
    print_table,
)
from utils.export import export_model_benchmark


def benchmark_single_model(model_name, device):
    """
    Benchmark one model.
    """

    model = get_model(
        model_name=model_name,
        num_classes=43,
        pretrained=False,
        freeze_backbone=False,
    ).to(device)

    model.eval()

    dummy = torch.randn(4, 3, 64, 64).to(device)

    # warm-up
    with torch.no_grad():
        for _ in range(5):
            _ = model(dummy)

    inference_time = benchmark_model(model, dummy)

    with torch.no_grad():
        output = model(dummy)

    total_params = count_parameters(model, trainable_only=False)
    trainable_params = count_parameters(model, trainable_only=True)

    size_mb = model_size_mb(model)

    images_per_second = 4 / (inference_time / 1000)

    return {
        "Model": model_name,
        "Input": str(tuple(dummy.shape)),
        "Output": str(tuple(output.shape)),
        "Parameters": f"{total_params:,}",
        "Trainable": f"{trainable_params:,}",
        "Size(MB)": f"{size_mb:.2f}",
        "Inference(ms)": f"{inference_time:.2f}",
        "Images/s": f"{images_per_second:.2f}",
        "Device": str(device).upper(),
        "Status": "PASS",
    }


def main():

    print("=" * 70)
    print("MODEL ZOO BENCHMARK")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    results = []

    for model_name in available_models():

        try:
            result = benchmark_single_model(model_name, device)
            results.append(result)

        except Exception as e:

            results.append(
                {
                    "Model": model_name,
                    "Input": "-",
                    "Output": "-",
                    "Parameters": "-",
                    "Trainable": "-",
                    "Size(MB)": "-",
                    "Inference(ms)": "-",
                    "Images/s": "-",
                    "Device": str(device).upper(),
                    "Status": f"FAILED ({e})",
                }
            )

    print_table(results)

    export_model_benchmark(results)

    print("\nBenchmark exported successfully.")


if __name__ == "__main__":
    main()