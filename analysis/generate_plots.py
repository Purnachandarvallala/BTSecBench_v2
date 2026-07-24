"""
==============================================================

BTSecBench_v2

Generate Performance Figures


==============================================================
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


class PlotGenerator:

    def __init__(self):

        self.report_dir = Path("reports")

        self.json_dir = self.report_dir / "json"

        self.fine_tuning_dir = self.report_dir / "fine_tuning"

        self.figure_dir = self.report_dir / "figures"

        self.figure_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        print("=" * 70)
        print("GENERATING PERFORMANCE FIGURES")
        print("=" * 70)

    # ---------------------------------------------------------

    def load_json(self, path):

        if not path.exists():

            raise FileNotFoundError(path)

        with open(path, "r") as f:

            return json.load(f)

    # ---------------------------------------------------------

    def load_results(self):

        self.attack = self.load_json(

            self.json_dir /

            "attack_success_rate.json"

        )

        self.strip = self.load_json(

            self.json_dir /

            "strip_final_results.json"

        )

        self.ft = self.load_json(

            self.fine_tuning_dir /

            "fine_tuning_results.json"

        )

    # ---------------------------------------------------------

    def plot_accuracy(self):

        labels = [

            "Clean",

            "Fine-Tuning",

        ]

        values = [

            99.97,

            self.ft["validation_accuracy"],

        ]

        plt.figure(figsize=(7,5))

        bars = plt.bar(

            labels,

            values,

        )

        plt.ylim(95,100)

        plt.ylabel("Accuracy (%)")

        plt.title("Model Accuracy Comparison")

        for bar,value in zip(bars,values):

            plt.text(

                bar.get_x()+bar.get_width()/2,

                value+0.2,

                f"{value:.2f}%",

                ha="center",

            )

        plt.grid(

            axis="y",

            linestyle="--",

            alpha=0.4,

        )

        plt.tight_layout()

        plt.savefig(

            self.figure_dir /

            "accuracy_comparison.png",

            dpi=300,

        )

        plt.close()

        print("✓ accuracy_comparison.png")

    # ---------------------------------------------------------

    def plot_asr(self):

        labels=[

            "Before Defense",

            "After Defense",

        ]

        values=[

            99.97,

            self.attack["attack_success_rate"],

        ]

        plt.figure(figsize=(7,5))

        bars=plt.bar(

            labels,

            values,

        )

        plt.ylabel(

            "Attack Success Rate (%)"

        )

        plt.title(

            "ASR Before vs After Defense"

        )

        plt.ylim(0,100)

        for bar,value in zip(bars,values):

            plt.text(

                bar.get_x()+bar.get_width()/2,

                value+1,

                f"{value:.2f}%",

                ha="center",

            )

        plt.grid(

            axis="y",

            linestyle="--",

            alpha=0.4,

        )

        plt.tight_layout()

        plt.savefig(

            self.figure_dir/

            "asr_comparison.png",

            dpi=300,

        )

        plt.close()

        print("✓ asr_comparison.png")
            # ---------------------------------------------------------
    # STRIP Metrics
    # ---------------------------------------------------------

    def plot_strip_metrics(self):

        labels = [

            "Accuracy",
            "Precision",
            "Recall",
            "F1",

        ]

        values = [

            self.strip["accuracy"] * 100,
            self.strip["precision"] * 100,
            self.strip["recall"] * 100,
            self.strip["f1"] * 100,

        ]

        plt.figure(figsize=(8,5))

        bars = plt.bar(

            labels,

            values,

        )

        plt.ylim(0,100)

        plt.ylabel("Percentage (%)")

        plt.title("STRIP Detection Performance")

        for bar,value in zip(bars,values):

            plt.text(

                bar.get_x()+bar.get_width()/2,

                value+1,

                f"{value:.2f}%",

                ha="center",

            )

        plt.grid(

            axis="y",

            linestyle="--",

            alpha=0.4,

        )

        plt.tight_layout()

        plt.savefig(

            self.figure_dir/

            "strip_metrics.png",

            dpi=300,

        )

        plt.close()

        print("✓ strip_metrics.png")


    # ---------------------------------------------------------
    # Benchmark Summary
    # ---------------------------------------------------------

    def plot_benchmark_summary(self):

        labels = [

            "Fine-Tuning\nAccuracy",

            "BadNets\nASR",

            "STRIP\nAccuracy",

            "STRIP\nPrecision",

            "STRIP\nRecall",

            "STRIP\nF1",

        ]

        values = [

            self.ft["validation_accuracy"],

            self.attack["attack_success_rate"],

            self.strip["accuracy"] * 100,

            self.strip["precision"] * 100,

            self.strip["recall"] * 100,

            self.strip["f1"] * 100,

        ]

        plt.figure(figsize=(10,6))

        bars = plt.bar(

            labels,

            values,

        )

        plt.ylim(0,100)

        plt.ylabel("Percentage (%)")

        plt.title("BTSecBench_v2 Benchmark Summary")

        for bar,value in zip(bars,values):

            plt.text(

                bar.get_x()+bar.get_width()/2,

                value+1,

                f"{value:.2f}",

                ha="center",

                fontsize=9,

            )

        plt.grid(

            axis="y",

            linestyle="--",

            alpha=0.4,

        )

        plt.tight_layout()

        plt.savefig(

            self.figure_dir/

            "benchmark_summary.png",

            dpi=300,

        )

        plt.close()

        print("✓ benchmark_summary.png")


    # ---------------------------------------------------------
    # Generate All
    # ---------------------------------------------------------

    def generate_all(self):

        self.load_results()

        self.plot_accuracy()

        self.plot_asr()

        self.plot_strip_metrics()

        self.plot_benchmark_summary()

        print()

        print("="*70)

        print("ALL FIGURES GENERATED")

        print("="*70)

        print(self.figure_dir)

        print("="*70)


# ==========================================================
# Main
# ==========================================================

def main():

    generator = PlotGenerator()

    generator.generate_all()


if __name__ == "__main__":

    main()