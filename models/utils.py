import time
import torch
from rich.console import Console
from rich.table import Table

console = Console()


def count_parameters(model, trainable_only=False):
    """
    Count model parameters.
    """
    if trainable_only:
        return sum(
            p.numel()
            for p in model.parameters()
            if p.requires_grad
        )

    return sum(
        p.numel()
        for p in model.parameters()
    )


def model_size_mb(model):
    """
    Approximate model size in MB.
    """
    size = 0

    for p in model.parameters():
        size += p.numel() * p.element_size()

    for b in model.buffers():
        size += b.numel() * b.element_size()

    return size / (1024 ** 2)


def benchmark_model(
    model,
    x,
    device="cpu",
    warmup=10,
    runs=100,
):
    """
    Average inference time in milliseconds.
    """

    model.eval()
    model.to(device)

    x = x.to(device)

    with torch.no_grad():

        for _ in range(warmup):
            model(x)

        if device == "cuda":
            torch.cuda.synchronize()

        start = time.perf_counter()

        for _ in range(runs):
            model(x)

        if device == "cuda":
            torch.cuda.synchronize()

        end = time.perf_counter()

    return ((end - start) / runs) * 1000


def print_table(results):
    """
    Pretty benchmark table using Rich.
    """

    table = Table(
        title="🚀 BTSecBench_v2 Model Zoo Benchmark",
        show_lines=True,
        header_style="bold cyan",
    )

    table.add_column("Model", justify="left")
    table.add_column("Parameters", justify="right")
    table.add_column("Trainable", justify="right")
    table.add_column("Size (MB)", justify="right")
    table.add_column("Time (ms)", justify="right")
    table.add_column("Images/s", justify="right")
    table.add_column("Device", justify="center")
    table.add_column("Status", justify="center")

    for row in results:

        table.add_row(
            row["Model"],
            row["Parameters"],
            row["Trainable"],
            row["Size(MB)"],
            row["Inference(ms)"],
            row["Images/s"],
            row["Device"],
            row["Status"],
        )

    console.print(table)