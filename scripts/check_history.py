from engine.history import History


def main():

    print("=" * 60)
    print("HISTORY ENGINE TEST")
    print("=" * 60)

    history = History()

    history.update(
        epoch=1,
        train_loss=0.42,
        train_accuracy=91.2,
        val_loss=0.39,
        val_accuracy=92.4,
        learning_rate=0.001,
    )

    history.update(
        epoch=2,
        train_loss=0.31,
        train_accuracy=94.6,
        val_loss=0.27,
        val_accuracy=95.1,
        learning_rate=0.0008,
    )

    print(history.dataframe())

    history.save_csv("reports/training_history.csv")
    history.save_json("reports/training_history.json")

    print()
    print("History Length :", len(history))
    print()
    print("STATUS : PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()