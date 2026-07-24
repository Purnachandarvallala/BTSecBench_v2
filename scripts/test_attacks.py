"""
==============================================================
BTSecBench_v2

Attack Engine Test
==============================================================
"""

import matplotlib.pyplot as plt

from data.dataset import GTSRBDataset

from attacks import (
    BadNetsAttack,
    BlendAttack,
    SIGAttack,
    WaNetAttack,
)


def show_attack(dataset, attack, title):

    sample = dataset[0]

    image = sample["image"]
    label = sample["label"]

    poisoned_image, poisoned_label, poisoned = attack.poison_sample(
        image=image,
        label=int(label),
    )

    print("=" * 60)
    print(title)
    print("=" * 60)

    print(f"Original Label : {label}")
    print(f"Poisoned Label : {poisoned_label}")
    print(f"Poison Applied : {poisoned}")

    plt.figure(figsize=(8,4))

    plt.subplot(1,2,1)
    plt.imshow(image.permute(1,2,0))
    plt.title("Original")
    plt.axis("off")

    plt.subplot(1,2,2)
    plt.imshow(poisoned_image.permute(1,2,0))
    plt.title(title)
    plt.axis("off")

    plt.show()


def main():

    dataset = GTSRBDataset(
        csv_file="data/splits/train.csv",
        transform=None,
    )

    attacks = [

        ("BadNets",
         BadNetsAttack()),

        ("Blend",
         BlendAttack()),

        ("SIG",
         SIGAttack()),

        ("WaNet",
         WaNetAttack()),

    ]

    for title, attack in attacks:

        show_attack(
            dataset,
            attack,
            title,
        )


if __name__ == "__main__":
    main()