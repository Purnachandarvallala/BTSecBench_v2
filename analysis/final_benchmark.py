"""
==============================================================

BTSecBench_v2

Final Benchmark

Description
-----------
Aggregates all experiment results into a single benchmark.

Reads

• Attack Success Rate
• STRIP Detection
• Fine-Tuning Defense

Outputs

CSV
JSON
Markdown
Excel

==============================================================
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


class FinalBenchmark:

    def __init__(self):

        self.report_dir = Path("reports")

        self.json_dir = self.report_dir / "json"

        self.output_dir = self.report_dir / "benchmark"

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.results = []

        print()

        print("=" * 70)
        print("FINAL BENCHMARK")
        print("=" * 70)

    # ==========================================================
    # Read JSON
    # ==========================================================

    def load_json(self, file_path):

        if not file_path.exists():

            print(f"Missing : {file_path}")

            return {}

        with open(file_path, "r") as file:

            return json.load(file)

    # ==========================================================
    # Attack
    # ==========================================================

    def load_attack_results(self):

        data = self.load_json(

            self.json_dir /

            "attack_success_rate.json"

        )

        if not data:

            return

        self.results.append({

            "Component": "BadNets",

            "Metric": "Attack Success Rate",

            "Value": data.get(

                "attack_success_rate",

                "-"

            )

        })

    # ==========================================================
    # STRIP
    # ==========================================================

    def load_strip_results(self):

        data = self.load_json(

            self.json_dir /

            "strip_final_results.json"

        )

        if not data:

            data = self.load_json(

                self.json_dir /

                "strip_results.json"

            )

        if not data:

            return

        metrics = [

            ("Detection Accuracy", "accuracy"),

            ("Precision", "precision"),

            ("Recall", "recall"),

            ("F1 Score", "f1"),

            ("AUC", "auc"),

            ("False Positive Rate", "false_positive_rate"),

            ("False Negative Rate", "false_negative_rate"),

        ]

        for name, key in metrics:

            if key in data:

                self.results.append({

                    "Component": "STRIP",

                    "Metric": name,

                    "Value": data[key],

                })

    # ==========================================================
    # Fine-Tuning
    # ==========================================================

    def load_fine_tuning_results(self):

        data = self.load_json(

            self.report_dir /

            "fine_tuning" /

            "fine_tuning_results.json"

        )

        if not data:

            return

        for key in [

            "accuracy",

            "precision",

            "recall",

            "f1",

            "loss",

        ]:

            if key in data:

                self.results.append({

                    "Component": "Fine-Tuning",

                    "Metric": key.title(),

                    "Value": data[key],

                })
                    # ==========================================================
    # Build Benchmark Table
    # ==========================================================

    def build_dataframe(self):

        df = pd.DataFrame(self.results)

        return df


    # ==========================================================
    # Save CSV
    # ==========================================================

    def save_csv(self, df):

        path = self.output_dir / "benchmark.csv"

        df.to_csv(

            path,

            index=False,

        )

        print(f"Saved : {path}")


    # ==========================================================
    # Save JSON
    # ==========================================================

    def save_json(self, df):

        path = self.output_dir / "benchmark.json"

        df.to_json(

            path,

            orient="records",

            indent=4,

        )

        print(f"Saved : {path}")


    # ==========================================================
    # Save Markdown
    # ==========================================================

    def save_markdown(self, df):

        path = self.output_dir / "benchmark.md"

        with open(path, "w") as file:

            file.write("# BTSecBench_v2 Benchmark\n\n")

            file.write(

                df.to_markdown(

                    index=False

                )

            )

        print(f"Saved : {path}")


    # ==========================================================
    # Save Excel
    # ==========================================================

    def save_excel(self, df):

        path = self.output_dir / "benchmark.xlsx"

        df.to_excel(

            path,

            index=False,

        )

        print(f"Saved : {path}")


    # ==========================================================
    # Overall Summary
    # ==========================================================

    def summary(self):

        print()
        print("=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)

        for row in self.results:

            value = row["Value"]

            metric = row["Metric"].lower()

            # Metrics stored as fractions
            if (
                isinstance(value, (float, int))
                and metric in [
                    "detection accuracy",
                    "precision",
                    "recall",
                    "f1 score",
                    "false positive rate",
                    "false negative rate",
                ]
                and value <= 1
            ):
                value = value * 100
                value = f"{value:.2f}%"

            # AUC stays between 0 and 1
            elif metric == "auc":
                value = f"{value:.4f}"

            # Already stored as percentage
            elif isinstance(value, (float, int)):
                value = f"{value:.2f}%"

            print(
                f"{row['Component']:<15}"
                f"{row['Metric']:<28}"
                f"{value}"
            )

        print("=" * 70)

    # ==========================================================
    # Export Everything
    # ==========================================================

    def export(self):

        df = self.build_dataframe()

        self.save_csv(df)

        self.save_json(df)

        self.save_markdown(df)

        self.save_excel(df)

        self.summary()

        return df
        # ==========================================================
    # Run Benchmark
    # ==========================================================

    def run(self):

        self.load_attack_results()

        self.load_strip_results()

        self.load_fine_tuning_results()

        self.export()


# ==============================================================
# Main
# ==============================================================

def main():

    benchmark = FinalBenchmark()

    benchmark.run()


if __name__ == "__main__":

    main()