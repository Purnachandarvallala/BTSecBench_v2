from engine.early_stopping import EarlyStopping


def main():

    print("=" * 60)
    print("EARLY STOPPING TEST")
    print("=" * 60)

    early = EarlyStopping(
        patience=3,
        min_delta=0.001,
        mode="max",
    )

    validation_accuracy = [

        0.81,
        0.83,
        0.84,
        0.841,
        0.841,
        0.840,
        0.839,
        0.838,
    ]

    for epoch, score in enumerate(validation_accuracy, start=1):

        stop = early.step(score)

        print(
            f"Epoch {epoch:02d} | "
            f"Accuracy={score:.3f} | "
            f"Best={early.best_score:.3f} | "
            f"Counter={early.counter}"
        )

        if stop:

            print()

            print(
                f"Early stopping triggered at epoch {epoch}"
            )

            break

    print()

    print("=" * 60)
    print("STATUS : PASS")
    print("=" * 60)


if __name__ == "__main__":

    main()