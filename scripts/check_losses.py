import torch

from engine.losses import get_loss


def main():

    print("=" * 60)
    print("LOSS FUNCTIONS TEST")
    print("=" * 60)

    logits = torch.randn(8, 43)

    labels = torch.randint(
        0,
        43,
        (8,)
    )

    losses = [

        "cross_entropy",

        "label_smoothing",

        "focal",

    ]

    for loss_name in losses:

        criterion = get_loss(loss_name)

        loss = criterion(
            logits,
            labels,
        )

        print()

        print(loss_name)

        print(f"Loss : {loss.item():.4f}")

    print()

    print("=" * 60)

    print("STATUS : PASS")

    print("=" * 60)


if __name__ == "__main__":

    main()