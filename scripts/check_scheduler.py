import torch

from models import get_model

from engine.scheduler import get_scheduler


def main():

    print("=" * 60)
    print("SCHEDULER FACTORY TEST")
    print("=" * 60)

    model = get_model("cnn")

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.001,
    )

    schedulers = [

        "step",

        "multistep",

        "cosine",

        "plateau",

        "onecycle",

    ]

    for scheduler_name in schedulers:

        scheduler = get_scheduler(

            optimizer,

            name=scheduler_name,

            epochs=30,

            steps_per_epoch=100,

        )

        print()

        print(f"{scheduler_name}")

        print(type(scheduler).__name__)

    print()

    print("=" * 60)

    print("STATUS : PASS")

    print("=" * 60)


if __name__ == "__main__":

    main()