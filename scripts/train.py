"""
==============================================================
BTSecBench_v2

Training Script

Author : Shivaprasad Aredla

==============================================================
"""

import argparse
import random
import numpy as np
import torch

from data.dataloader import create_dataloaders

from models import get_model

from engine import (
    Trainer,
    Evaluator,
    get_loss,
    get_scheduler,
)


# ============================================================
# Seed
# ============================================================

def set_seed(seed=42):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True

    torch.backends.cudnn.benchmark = False


# ============================================================
# Argument Parser
# ============================================================

def get_args():

    parser = argparse.ArgumentParser(
        description="BTSecBench Training"
    )

    parser.add_argument(
        "--model",
        default="cnn",
        type=str,
    )

    parser.add_argument(
        "--epochs",
        default=30,
        type=int,
    )

    parser.add_argument(
        "--batch-size",
        default=64,
        type=int,
    )

    parser.add_argument(
        "--lr",
        default=3e-4,
        type=float,
    )

    parser.add_argument(
        "--loss",
        default="label_smoothing",
        type=str,
    )

    parser.add_argument(
        "--scheduler",
        default="cosine",
        type=str,
    )

    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
    )

    return parser.parse_args()
# ============================================================
# Main
# ============================================================

def main():

    args = get_args()

    set_seed(42)

    device = torch.device(args.device)

    print("=" * 70)
    print("BTSecBench_v2 Training")
    print("=" * 70)

    print(f"Model      : {args.model}")
    print(f"Device     : {device}")
    print(f"Epochs     : {args.epochs}")
    print(f"Batch Size : {args.batch_size}")
    print(f"LR         : {args.lr}")
    print(f"Loss       : {args.loss}")
    print(f"Scheduler  : {args.scheduler}")

    print("=" * 70)

    ###########################################################
    # Data
    ###########################################################

    train_loader, val_loader = create_dataloaders(
        batch_size=args.batch_size,
    )

    ###########################################################
    # Model
    ###########################################################

    model = get_model(
        model_name=args.model,
        num_classes=43,
        pretrained=True,
        freeze_backbone=False,
    )

    ###########################################################
    # Optimizer
    ###########################################################

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=1e-4,
    )

    ###########################################################
    # Loss
    ###########################################################

    criterion = get_loss(
        name=args.loss,
    )

    ###########################################################
    # Scheduler
    ###########################################################

    scheduler = get_scheduler(
        optimizer=optimizer,
        name=args.scheduler,
        epochs=args.epochs,
        steps_per_epoch=len(train_loader),
    )

    ###########################################################
    # Trainer
    ###########################################################

    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        scheduler=scheduler,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        epochs=args.epochs,
    )

    ###########################################################
    # Evaluator
    ###########################################################

    evaluator = Evaluator(
        device=device,
    )

    ###########################################################
    # Summary
    ###########################################################

    trainer.summary()

    ###########################################################
    # Train
    ###########################################################

    trainer.fit(
        evaluator=evaluator,
    )

    ###########################################################
    # Finished
    ###########################################################

    print()

    print("=" * 70)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 70)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()