from data.dataloader import build_dataloader


def main():

    loader = build_dataloader(
        csv_file="data/splits/train.csv",
        batch_size=32,
        shuffle=True,
        mode="train"
    )

    batch = next(iter(loader))

    print("=" * 60)
    print("DataLoader Test")
    print("=" * 60)

    print()

    print("Images :", batch["image"].shape)
    print("Labels :", batch["label"].shape)

    print()

    print("First Label :", batch["label"][0].item())
    print("First Image :", batch["path"][0])

    print()

    print("Everything OK.")


if __name__ == "__main__":
    main()