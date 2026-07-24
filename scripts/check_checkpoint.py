import torch

from engine.checkpoint import CheckpointManager

from models import get_model


def main():

    print("=" * 60)
    print("CHECKPOINT TEST")
    print("=" * 60)

    model = get_model("cnn")

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.001,
    )

    manager = CheckpointManager()

    manager.save(

        model=model,

        optimizer=optimizer,

        epoch=10,

        metrics={
            "accuracy":98.7,
            "loss":0.034
        },

        is_best=True,
    )

    checkpoint = manager.load(

        model,

        optimizer,

    )

    print()

    print("Epoch")

    print(checkpoint["epoch"])

    print()

    print("Metrics")

    print(checkpoint["metrics"])

    print()

    print("Latest")

    print(manager.latest_checkpoint())

    print()

    print("="*60)

    print("STATUS : PASS")

    print("="*60)


if __name__=="__main__":

    main()