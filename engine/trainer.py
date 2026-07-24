"""
==============================================================
BTSecBench_v2

Training Engine


==============================================================
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Any, Optional

import torch
import torch.nn as nn
import torch.nn.utils as nn_utils
from tqdm import tqdm

from engine.history import History
from engine.metrics import ClassificationMetrics
from engine.checkpoint import CheckpointManager
from engine.early_stopping import EarlyStopping


class Trainer:
    """
    Universal Trainer for BTSecBench_v2

    Supports
    --------
    ✓ CNN Baseline
    ✓ ResNet18
    ✓ MobileNetV3
    ✓ EfficientNet-B0

    Future Support
    --------------
    ✓ BadNets
    ✓ Blend
    ✓ SIG
    ✓ WaNet
    ✓ Neural Cleanse
    ✓ STRIP
    ✓ Fine-Pruning
    ✓ NAD
    """

    ####################################################################
    # Constructor
    ####################################################################

    def __init__(
        self,
        model: nn.Module,
        optimizer,
        criterion,
        scheduler,
        train_loader,
        val_loader,
        device,
        epochs: int = 30,
        checkpoint_dir: str = "checkpoints",
        patience: int = 10,
    ):

        self.model = model.to(device)

        self.optimizer = optimizer

        self.criterion = criterion

        self.scheduler = scheduler

        self.train_loader = train_loader

        self.val_loader = val_loader

        self.device = device

        self.epochs = epochs

        ################################################################

        self.history = History()

        self.metrics = ClassificationMetrics()

        self.checkpoint = CheckpointManager(
            checkpoint_dir=checkpoint_dir
        )

        self.early_stopping = EarlyStopping(
            patience=patience,
            mode="max",
        )

        ################################################################

        self.best_accuracy = 0.0

        self.best_loss = float("inf")

        self.current_epoch = 0

        self.start_epoch = 1

        ################################################################

        self.train_batches = len(train_loader)

        self.val_batches = len(val_loader)

        ################################################################

        self.output_dir = Path("reports")

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    ####################################################################
    # Summary
    ####################################################################

    def summary(self):

        print("=" * 70)
        print("TRAINER SUMMARY")
        print("=" * 70)

        print(f"Model            : {self.model.__class__.__name__}")
        print(f"Device           : {self.device}")
        print(f"Epochs           : {self.epochs}")
        print(f"Train Batches    : {self.train_batches}")
        print(f"Validation Batch : {self.val_batches}")
        print(f"Optimizer        : {self.optimizer.__class__.__name__}")

        scheduler_name = (
            type(self.scheduler).__name__
            if self.scheduler is not None
            else "None"
        )

        print(f"Scheduler        : {scheduler_name}")
        print(f"Criterion        : {self.criterion.__class__.__name__}")
        print(f"Checkpoint Dir   : {self.checkpoint.checkpoint_dir}")

        print("=" * 70)

    ####################################################################
    # Helper
    ####################################################################

    def get_learning_rate(self):

        return self.optimizer.param_groups[0]["lr"]

    ####################################################################
    # Move Batch
    ####################################################################

    def _move_batch_to_device(
        self,
        batch: Dict[str, Any],
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

    def _forward_pass(
        self,
        batch: Dict[str, Any],
    ):

        images, labels = self._move_batch_to_device(
            batch
        )

        outputs = self.model(images)

        loss = self.criterion(
            outputs,
            labels,
        )

        return {
            "loss": loss,
            "outputs": outputs,
            "labels": labels,
            "batch_size": labels.size(0),
        }

    ####################################################################
    # Backward
    ####################################################################

    def _backward_pass(
        self,
        loss,
    ):

        self.optimizer.zero_grad()

        loss.backward()

        nn_utils.clip_grad_norm_(
            self.model.parameters(),
            max_norm=5.0,
        )

        self.optimizer.step()

    ####################################################################
    # Scheduler
    ####################################################################

    def _scheduler_step(
        self,
        validation_accuracy: Optional[float] = None,
    ):

        if self.scheduler is None:
            return

        if self.scheduler.__class__.__name__ == "ReduceLROnPlateau":

            self.scheduler.step(validation_accuracy)

        else:

            self.scheduler.step()

    ####################################################################
    # Save Best Model
    ####################################################################

    def _save_best_model(
        self,
        validation_results,
    ):

        current_accuracy = validation_results["accuracy"]

        if current_accuracy > self.best_accuracy:

            self.best_accuracy = current_accuracy

            self.checkpoint.save(
                model=self.model,
                optimizer=self.optimizer,
                scheduler=self.scheduler,
                epoch=self.current_epoch,
                metrics=validation_results,
                filename="best_model.pth",
                is_best=True,
            )

    ####################################################################
    # Save Last Checkpoint
    ####################################################################

    def save_last_checkpoint(
        self,
        validation_results=None,
    ):

        if validation_results is None:
            validation_results = {}

        self.checkpoint.save(
            model=self.model,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            epoch=self.current_epoch,
            metrics=validation_results,
            filename="last_checkpoint.pth",
        )

    ####################################################################
    # Resume Training
    ####################################################################

    def load_checkpoint(
        self,
        filename="last_checkpoint.pth",
    ):

        checkpoint = self.checkpoint.load(
            model=self.model,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            filename=filename,
        )

        self.start_epoch = checkpoint["epoch"] + 1

        return checkpoint
        ####################################################################
    # Train One Epoch
    ####################################################################

    def train_one_epoch(self):

        self.model.train()

        self.metrics.reset()

        running_loss = 0.0
        running_correct = 0
        total_samples = 0

        epoch_start = time.time()

        progress_bar = tqdm(
            self.train_loader,
            desc=f"Epoch {self.current_epoch}/{self.epochs}",
            dynamic_ncols=True,
            leave=False,
        )

        for batch in progress_bar:

            ############################################################
            # Forward
            ############################################################

            result = self._forward_pass(batch)

            loss = result["loss"]

            outputs = result["outputs"]

            labels = result["labels"]

            batch_size = result["batch_size"]

            ############################################################
            # Backward
            ############################################################

            self._backward_pass(loss)

            ############################################################
            # Statistics
            ############################################################

            predictions = outputs.argmax(dim=1)

            running_loss += loss.item() * batch_size

            running_correct += (
                predictions == labels
            ).sum().item()

            total_samples += batch_size

            ############################################################
            # Metrics Engine
            ############################################################

            self.metrics.update(
                predictions,
                labels,
            )

            ############################################################
            # Progress Bar
            ############################################################

            progress_bar.set_postfix(

                Loss=f"{running_loss / total_samples:.4f}",

                Acc=f"{100 * running_correct / total_samples:.2f}%",

                LR=f"{self.get_learning_rate():.6f}",

            )

        ############################################################
        # Epoch Statistics
        ############################################################

        elapsed = time.time() - epoch_start

        metric_results = self.metrics.compute()

        train_results = {

            "epoch":
                self.current_epoch,

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

            "learning_rate":
                self.get_learning_rate(),

            "samples":
                total_samples,

            "time":
                elapsed,

            "images_per_second":
                total_samples / elapsed,

            "status":
                "PASS",

        }

        return train_results

    ####################################################################
    # Print Training Summary
    ####################################################################

    def print_train_summary(
        self,
        results,
    ):

        print()

        print("=" * 70)

        print("TRAINING RESULTS")

        print("=" * 70)

        print(
            f"Epoch                : {results['epoch']}"
        )

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
            "Learning Rate        : "
            f"{results['learning_rate']:.6f}"
        )

        print(
            f"Samples              : {results['samples']:,}"
        )

        print(
            "Images / Second      : "
            f"{results['images_per_second']:.2f}"
        )

        print(
            f"Epoch Time           : {results['time']:.2f} sec"
        )

        print(
            f"Status               : {results['status']}"
        )

        print("=" * 70)

    ####################################################################
    # History
    ####################################################################

    def update_history(
        self,
        train_results,
        validation_results,
    ):

        self.history.update(

            epoch=train_results["epoch"],

            train_loss=train_results["loss"],

            train_accuracy=train_results["accuracy"],

            val_loss=validation_results["loss"],

            val_accuracy=validation_results["accuracy"],

            learning_rate=train_results[
                "learning_rate"
            ],

        )

    ####################################################################
    # Export History
    ####################################################################

    def export_history(self):

        csv_path = (
            self.output_dir /
            "training_history.csv"
        )

        json_path = (
            self.output_dir /
            "training_history.json"
        )

        self.history.save_csv(csv_path)

        self.history.save_json(json_path)

        print()

        print("=" * 70)

        print("History Exported")

        print("=" * 70)

        print(csv_path)

        print(json_path)

        print("=" * 70)
            ####################################################################
    # Fit
    ####################################################################

    def fit(
        self,
        evaluator,
    ):
        """
        Complete training loop.

        Parameters
        ----------
        evaluator : Evaluator
            Validation engine.
        """

        print()
        print("=" * 70)
        print("TRAINING STARTED")
        print("=" * 70)

        overall_start = time.time()

        for epoch in range(
            self.start_epoch,
            self.epochs + 1,
        ):

            self.current_epoch = epoch

            ########################################################
            # Train
            ########################################################

            train_results = self.train_one_epoch()

            ########################################################
            # Validate
            ########################################################

            validation_results = evaluator.validate(
                model=self.model,
                dataloader=self.val_loader,
                criterion=self.criterion,
            )

            ########################################################
            # Display
            ########################################################

            self.print_train_summary(train_results)

            evaluator.print_summary(validation_results)

            ########################################################
            # Scheduler
            ########################################################

            self._scheduler_step(
                validation_results["accuracy"]
            )

            ########################################################
            # History
            ########################################################

            self.update_history(
                train_results,
                validation_results,
            )

            ########################################################
            # Save Best Model
            ########################################################

            self._save_best_model(
                validation_results,
            )

            ########################################################
            # Save Last Checkpoint
            ########################################################

            self.save_last_checkpoint(
                validation_results,
            )

            ########################################################
            # Early Stopping
            ########################################################

            stop = self.early_stopping.step(
                validation_results["accuracy"]
            )

            if stop:

                print()

                print("=" * 70)
                print("EARLY STOPPING")
                print("=" * 70)

                break

        ############################################################
        # Export History
        ############################################################

        self.export_history()

        ############################################################

        total_time = time.time() - overall_start

        print()

        print("=" * 70)
        print("TRAINING FINISHED")
        print("=" * 70)

        print(
            f"Best Validation Accuracy : "
            f"{self.best_accuracy:.2f}%"
        )

        print(
            f"Total Training Time      : "
            f"{total_time / 60:.2f} minutes"
        )

        print("=" * 70)