"""
==============================================================
BTSecBench_v2

Backdoor Training Script


==============================================================

Train any model using any supported backdoor attack.

Supported Models
----------------
- cnn
- resnet18
- mobilenet_v3
- efficientnet_b0

Supported Attacks
-----------------
- badnets
- blend
- sig
- wanet

Example
-------

python -m scripts.train_backdoor \
    --model efficientnet_b0 \
    --attack badnets \
    --poison-rate 0.10 \
    --target-class 0

==============================================================
"""

from __future__ import annotations

import argparse
import random
import numpy as np

import torch

from torch.utils.data import DataLoader

from data.dataloader import create_dataset

from attacks import (
    PoisonedDataset,
    get_attack,
    available_attacks,
)

from models import get_model

from engine import (
    Trainer,
    Evaluator,
    get_loss,
    get_scheduler,
)

###############################################################
# Seed
###############################################################

def set_seed(seed=42):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True

    torch.backends.cudnn.benchmark = False


###############################################################
# Arguments
###############################################################

def get_args():

    parser = argparse.ArgumentParser(
        description="Backdoor Training"
    )

    ###########################################################
    # Model
    ###########################################################

    parser.add_argument(
        "--model",
        default="efficientnet_b0",
        type=str,
    )

    ###########################################################
    # Attack
    ###########################################################

    parser.add_argument(
        "--attack",
        default="badnets",
        choices=available_attacks(),
    )

    parser.add_argument(
        "--poison-rate",
        default=0.10,
        type=float,
    )

    parser.add_argument(
        "--target-class",
        default=0,
        type=int,
    )

    ###########################################################
    # Training
    ###########################################################

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

    ###########################################################
    # Loss
    ###########################################################

    parser.add_argument(
        "--loss",
        default="label_smoothing",
        type=str,
    )

    ###########################################################
    # Scheduler
    ###########################################################

    parser.add_argument(
        "--scheduler",
        default="cosine",
        type=str,
    )

    ###########################################################
    # Device
    ###########################################################

    parser.add_argument(

        "--device",

        default="cuda"
        if torch.cuda.is_available()
        else "cpu",

    )

    return parser.parse_args()
###############################################################
# Main
###############################################################

def main():

    args = get_args()

    set_seed()

    device = torch.device(args.device)

    ###########################################################
    # Configuration
    ###########################################################

    print("=" * 70)
    print("BTSecBench_v2")
    print("BACKDOOR TRAINING")
    print("=" * 70)

    print(f"Model          : {args.model}")
    print(f"Attack         : {args.attack}")
    print(f"Poison Rate    : {args.poison_rate}")
    print(f"Target Class   : {args.target_class}")
    print(f"Epochs         : {args.epochs}")
    print(f"Batch Size     : {args.batch_size}")
    print(f"Learning Rate  : {args.lr}")
    print(f"Device         : {device}")

    print("=" * 70)

    ###########################################################
    # Dataset
    ###########################################################

    clean_train_dataset = create_dataset(
        csv_file="data/splits/train.csv",
        mode="train",
    )

    clean_val_dataset = create_dataset(
        csv_file="data/splits/val.csv",
        mode="val",
    )

    ###########################################################
    # Create Attack
    ###########################################################

    attack = get_attack(
        attack_name=args.attack,
        poison_rate=args.poison_rate,
        target_class=args.target_class,
    )

    ###########################################################
    # Poisoned Dataset
    ###########################################################

    train_dataset = PoisonedDataset(
        dataset=clean_train_dataset,
        attack=attack,
        poison_all=False,
    )

    val_dataset = PoisonedDataset(
        dataset=clean_val_dataset,
        attack=None,
        poison_all=False,
    )

    ###########################################################
    # DataLoaders
    ###########################################################

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
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
        output_dir=f"reports/{args.model}_{args.attack}",
    )

    ###########################################################
    # Summary
    ###########################################################

    trainer.summary()

    print()

    print("=" * 70)
    print("BACKDOOR CONFIGURATION")
    print("=" * 70)

    print(f"Attack         : {args.attack}")
    print(f"Poison Rate    : {args.poison_rate:.2f}")
    print(f"Target Class   : {args.target_class}")

    print("=" * 70)
    print()

    ###########################################################
    # Train
    ###########################################################

    trainer.fit(
        evaluator=evaluator,
    )

    ###########################################################
    # Final Evaluation
    ###########################################################

    print()

    print("=" * 70)
    print("FINAL VALIDATION")
    print("=" * 70)

    results = evaluator.validate(
        model=model,
        dataloader=val_loader,
        criterion=criterion,
    )

    evaluator.print_summary(results)

    evaluator.export_metrics(
        results,
        filename="backdoor_validation.json",
    )

    ###########################################################
    # Finished
    ###########################################################

    print()

    print("=" * 70)
    print("BACKDOOR TRAINING COMPLETED")
    print("=" * 70)

    print(f"Model        : {args.model}")
    print(f"Attack       : {args.attack}")
    print(f"Poison Rate  : {args.poison_rate}")
    print(f"Target Class : {args.target_class}")

    print("=" * 70)


###############################################################
# Entry Point
###############################################################

if __name__ == "__main__":
    main()