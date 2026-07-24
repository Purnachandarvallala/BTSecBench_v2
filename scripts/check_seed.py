from engine.seed import set_seed

import torch

import random

import numpy as np


def main():

    set_seed(42)

    print("=" * 60)

    print("SEED VERIFICATION")

    print("=" * 60)

    print()

    print("Python")

    print(random.randint(1,100))

    print()

    print("NumPy")

    print(np.random.randint(1,100))

    print()

    print("PyTorch")

    print(torch.randint(1,100,(5,)))

    print()

    print("SUCCESS")

    print("=" * 60)


if __name__ == "__main__":

    main()