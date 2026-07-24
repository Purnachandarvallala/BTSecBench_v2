import json
from pathlib import Path

import pandas as pd


def export_model_benchmark(results):
    """
    Export benchmark results.
    """

    reports = Path("reports")
    reports.mkdir(exist_ok=True)

    pd.DataFrame(results).to_csv(
        reports / "model_benchmark.csv",
        index=False,
    )

    pd.DataFrame(results).to_excel(
        reports / "model_benchmark.xlsx",
        index=False,
    )

    with open(
        reports / "model_benchmark.json",
        "w",
    ) as f:
        json.dump(results, f, indent=4)

    pd.DataFrame(results).to_markdown(
        reports / "model_benchmark.md",
        index=False,
    )