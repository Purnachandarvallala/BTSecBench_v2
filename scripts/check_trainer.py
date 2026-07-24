import torch

from data.dataloader import create_dataloaders

from models import get_model

from engine.losses import get_loss
from engine.scheduler import get_scheduler
from engine.trainer import Trainer


def main():

    print("=" * 60)
    print("TRAINER TEST")
    print("=" * 60)

    train_loader, val_loader = create_dataloaders()

    model = get_model("cnn")

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.001,
    )

    criterion = get_loss()

    scheduler = get_scheduler(
        optimizer,
        name="step",
    )

    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        scheduler=scheduler,
        train_loader=train_loader,
        val_loader=val_loader,
        device=torch.device("cpu"),
        epochs=30,
    )

    trainer.summary()

    print()

    print("Running one training epoch...")

    results = trainer.train_one_epoch()

    print()

    print("=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)

    for key, value in results.items():

        if isinstance(value, float):
            print(f"{key:12}: {value:.4f}")
        else:
            print(f"{key:12}: {value}")

    print()
    print("STATUS : PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()