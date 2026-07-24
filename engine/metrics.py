"""
==============================================================
BTSecBench_v2

Classification Metrics Engine


==============================================================
"""

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    matthews_corrcoef,
    confusion_matrix,
    classification_report,
)

import numpy as np


class ClassificationMetrics:
    """
    Universal classification metrics for BTSecBench.
    """

    def __init__(self, num_classes=43):

        self.num_classes = num_classes

        self.reset()

    def reset(self):

        self.targets = []
        self.predictions = []

    def update(self, predictions, targets):
        """
        predictions : torch.Tensor or numpy array
        targets     : torch.Tensor or numpy array
        """

        try:
            predictions = predictions.detach().cpu().numpy()
        except AttributeError:
            predictions = np.asarray(predictions)

        try:
            targets = targets.detach().cpu().numpy()
        except AttributeError:
            targets = np.asarray(targets)

        # logits -> class index
        if predictions.ndim > 1:
            predictions = predictions.argmax(axis=1)

        self.predictions.extend(predictions.tolist())
        self.targets.extend(targets.tolist())

    def compute(self):

        results = {

            "accuracy": accuracy_score(
                self.targets,
                self.predictions,
            ),

            "precision": precision_score(
                self.targets,
                self.predictions,
                average="macro",
                zero_division=0,
            ),

            "recall": recall_score(
                self.targets,
                self.predictions,
                average="macro",
                zero_division=0,
            ),

            "f1": f1_score(
                self.targets,
                self.predictions,
                average="macro",
                zero_division=0,
            ),

            "balanced_accuracy": balanced_accuracy_score(
                self.targets,
                self.predictions,
            ),

            "mcc": matthews_corrcoef(
                self.targets,
                self.predictions,
            ),

            "confusion_matrix": confusion_matrix(
                self.targets,
                self.predictions,
            ),

            "classification_report": classification_report(
                self.targets,
                self.predictions,
                zero_division=0,
                output_dict=True,
            ),
        }

        return results