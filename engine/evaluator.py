"""
==============================================================
BTSecBench_v2

Professional Evaluation Engine


==============================================================
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from tqdm import tqdm

from engine.metrics import ClassificationMetrics


class Evaluator:
    """
    Universal evaluator for BTSecBench_v2.

    Responsible for

    ✓ Validation
    ✓ Testing
    ✓ Metrics
    ✓ Reports
    ✓ Predictions

    NOT responsible for

    ✗ Training
    ✗ Optimizer
    ✗ Scheduler
    """

    ####################################################################
    # Constructor
    ####################################################################

    def __init__(
        self,
        device,
        output_dir="reports",
    ):

        self.device = device

        self.metrics = ClassificationMetrics()

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    ####################################################################
    # Move Batch
    ####################################################################

    def _move_batch(
        self,
        batch,
    ):

        images = batch["image"].to(
            self.device,
            non_blocking=True,
        )

        labels = batch["label"].to(
            self.device,
            non_blocking=True,
        )

        return images, labels

    ####################################################################
    # Forward
    ####################################################################

    @torch.no_grad()

    def _forward(
        self,
        model,
        criterion,
        batch,
    ):

        images, labels = self._move_batch(batch)

        outputs = model(images)

        loss = criterion(
            outputs,
            labels,
        )

        predictions = outputs.argmax(dim=1)

        return {

            "loss": loss,

            "predictions": predictions,

            "labels": labels,

            "batch_size": labels.size(0),

        }
        ####################################################################
    # Validate
    ####################################################################

    @torch.no_grad()
    def validate(
        self,
        model,
        dataloader,
        criterion,
    ):

        model.eval()

        self.metrics.reset()

        running_loss = 0.0
        total_samples = 0

        start_time = time.time()

        progress_bar = tqdm(
            dataloader,
            desc="Validation",
            dynamic_ncols=True,
            leave=False,
        )

        for batch in progress_bar:

            result = self._forward(
                model,
                criterion,
                batch,
            )

            loss = result["loss"]
            predictions = result["predictions"]
            labels = result["labels"]
            batch_size = result["batch_size"]

            running_loss += loss.item() * batch_size
            total_samples += batch_size

            self.metrics.update(
                predictions,
                labels,
            )

            progress_bar.set_postfix(
                Loss=f"{running_loss / total_samples:.4f}"
            )

        elapsed = time.time() - start_time

        metric_results = self.metrics.compute()

        validation_results = {

            "loss":
                running_loss / total_samples,

            "accuracy":
                metric_results["accuracy"] * 100,

            "precision":
                metric_results["precision"] * 100,

            "recall":
                metric_results["recall"] * 100,

            "f1":
                metric_results["f1"] * 100,

            "balanced_accuracy":
                metric_results["balanced_accuracy"] * 100,

            "mcc":
                metric_results["mcc"],

            "confusion_matrix":
                metric_results["confusion_matrix"],

            "classification_report":
                metric_results[
                    "classification_report"
                ],

            "samples":
                total_samples,

            "time":
                elapsed,

            "images_per_second":
                total_samples / elapsed,

            "status":
                "PASS",

        }

        return validation_results

    ####################################################################
    # Print Validation Summary
    ####################################################################

    def print_summary(
        self,
        results,
    ):

        print()

        print("=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)

        print(
            f"Loss                 : {results['loss']:.4f}"
        )

        print(
            f"Accuracy             : {results['accuracy']:.2f}%"
        )

        print(
            f"Precision            : {results['precision']:.2f}%"
        )

        print(
            f"Recall               : {results['recall']:.2f}%"
        )

        print(
            f"F1 Score             : {results['f1']:.2f}%"
        )

        print(
            "Balanced Accuracy    : "
            f"{results['balanced_accuracy']:.2f}%"
        )

        print(
            f"MCC                  : {results['mcc']:.4f}"
        )

        print(
            f"Samples              : {results['samples']:,}"
        )

        print(
            "Images / Second      : "
            f"{results['images_per_second']:.2f}"
        )

        print(
            f"Validation Time      : {results['time']:.2f} sec"
        )

        print(
            f"Status               : {results['status']}"
        )

        print("=" * 70)

    ####################################################################
    # Export Metrics
    ####################################################################

    def export_metrics(
        self,
        results,
        filename="validation_metrics.json",
    ):

        export = results.copy()

        # Convert numpy arrays to lists for JSON serialization
        if isinstance(export["confusion_matrix"], np.ndarray):
            export["confusion_matrix"] = (
                export["confusion_matrix"].tolist()
            )

        report_path = self.output_dir / filename

        with open(report_path, "w") as f:
            json.dump(
                export,
                f,
                indent=4,
            )

        print()

        print(f"Validation metrics saved: {report_path}")
            ####################################################################
    # Test
    ####################################################################

    @torch.no_grad()
    def test(
        self,
        model,
        dataloader,
        criterion,
    ):
        """
        Test is identical to validation.
        Kept separate for cleaner architecture.
        """

        print()

        print("=" * 70)
        print("TESTING MODEL")
        print("=" * 70)

        results = self.validate(
            model=model,
            dataloader=dataloader,
            criterion=criterion,
        )

        self.print_summary(results)

        return results

    ####################################################################
    # Predict Batch
    ####################################################################

    @torch.no_grad()
    def predict_batch(
        self,
        model,
        images,
    ):

        model.eval()

        images = images.to(self.device)

        outputs = model(images)

        probabilities = torch.softmax(
            outputs,
            dim=1,
        )

        confidence, predictions = torch.max(
            probabilities,
            dim=1,
        )

        return {

            "predictions": predictions,

            "confidence": confidence,

            "probabilities": probabilities,

        }

    ####################################################################
    # Predict Single
    ####################################################################

    @torch.no_grad()
    def predict_single(
        self,
        model,
        image,
    ):

        model.eval()

        if image.dim() == 3:
            image = image.unsqueeze(0)

        results = self.predict_batch(
            model,
            image,
        )

        return {

            "prediction":
                results["predictions"][0].item(),

            "confidence":
                results["confidence"][0].item(),

            "probabilities":
                results["probabilities"][0],

        }

    ####################################################################
    # Save Confusion Matrix
    ####################################################################

    def save_confusion_matrix(
        self,
        results,
        filename="confusion_matrix.npy",
    ):

        save_path = self.output_dir / filename

        np.save(
            save_path,
            results["confusion_matrix"],
        )

        print()

        print(
            f"Confusion Matrix saved : {save_path}"
        )

    ####################################################################
    # Save Classification Report
    ####################################################################

    def save_classification_report(
        self,
        results,
        filename="classification_report.json",
    ):

        save_path = self.output_dir / filename

        with open(
            save_path,
            "w",
        ) as f:

            json.dump(

                results["classification_report"],

                f,

                indent=4,

            )

        print()

        print(
            f"Classification Report saved : {save_path}"
        )

    ####################################################################
    # Export Complete Results
    ####################################################################

    def export_results(
        self,
        results,
    ):

        self.export_metrics(results)

        self.save_confusion_matrix(results)

        self.save_classification_report(results)

        print()

        print("=" * 70)
        print("EVALUATION RESULTS EXPORTED")
        print("=" * 70)