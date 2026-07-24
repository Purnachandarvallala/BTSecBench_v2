import torch

from engine.metrics import ClassificationMetrics


def main():

    print("=" * 60)
    print("CLASSIFICATION METRICS TEST")
    print("=" * 60)

    metrics = ClassificationMetrics(num_classes=5)

    predictions = torch.tensor([
        [0.1, 0.8, 0.1, 0.0, 0.0],
        [0.2, 0.1, 0.6, 0.1, 0.0],
        [0.9, 0.1, 0.0, 0.0, 0.0],
        [0.0, 0.1, 0.2, 0.6, 0.1],
        [0.1, 0.0, 0.1, 0.1, 0.7],
        [0.2, 0.5, 0.2, 0.1, 0.0],
    ])

    labels = torch.tensor([1, 2, 0, 3, 4, 2])

    metrics.update(predictions, labels)

    results = metrics.compute()

    print(f"Accuracy            : {results['accuracy']:.4f}")
    print(f"Precision (Macro)  : {results['precision']:.4f}")
    print(f"Recall (Macro)     : {results['recall']:.4f}")
    print(f"F1 Score           : {results['f1']:.4f}")
    print(f"Balanced Accuracy  : {results['balanced_accuracy']:.4f}")
    print(f"MCC                : {results['mcc']:.4f}")

    print("\nConfusion Matrix")
    print(results["confusion_matrix"])

    print("\nSTATUS : PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()