"""
==============================================================
BTSecBench_v2

Attack Success Rate (ASR) Evaluation

==============================================================

Evaluates a trained backdoor model on a fully poisoned
test dataset.

Outputs
-------
✓ Attack Success Rate (ASR)
✓ Accuracy
✓ Precision
✓ Recall
✓ F1 Score
✓ MCC
✓ Confusion Matrix
✓ JSON Report

==============================================================
"""

from __future__ import annotations

import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from attacks import (
    PoisonedDataset,
    get_attack,
)

from data.dataloader import create_dataset

from engine import (
    Evaluator,
    get_loss,
)

from models import get_model


class AttackSuccessRate:

    def __init__(

        self,

        model_name="efficientnet_b0",

        checkpoint="checkpoints/best_model.pth",

        attack_name="badnets",

        poison_rate=1.0,

        target_class=0,

        batch_size=64,

        device=None,

    ):

        self.model_name = model_name

        self.checkpoint = checkpoint

        self.attack_name = attack_name

        self.poison_rate = poison_rate

        self.target_class = target_class

        self.batch_size = batch_size

        self.device = torch.device(

            device if device

            else "cuda"

            if torch.cuda.is_available()

            else "cpu"

        )

        self.output_dir = Path(

            "reports/json"

        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

    ############################################################

    def build_model(self):

        model = get_model(

            model_name=self.model_name,

            num_classes=43,

            pretrained=False,

        )

        checkpoint = torch.load(

            self.checkpoint,

            map_location=self.device,
            weights_only=False,

        )

        if isinstance(checkpoint, dict):

            if "model_state_dict" in checkpoint:

                checkpoint = checkpoint["model_state_dict"]

        model.load_state_dict(checkpoint)

        model.to(self.device)

        model.eval()

        return model
        ############################################################
    # Build Poisoned Test Loader
    ############################################################

    def build_dataloader(self):

        clean_dataset = create_dataset(

            csv_file="data/splits/val.csv",

            mode="test",

        )

        attack = get_attack(

            attack_name=self.attack_name,

            poison_rate=self.poison_rate,

            target_class=self.target_class,

        )

        poisoned_dataset = PoisonedDataset(

            dataset=clean_dataset,

            attack=attack,

            poison_all=True,

        )

        loader = DataLoader(

            poisoned_dataset,

            batch_size=self.batch_size,

            shuffle=False,

            num_workers=0,

            pin_memory=torch.cuda.is_available(),

        )

        return loader

    ############################################################
    # Evaluate
    ############################################################

    def evaluate(self):

        print()

        print("=" * 70)

        print("ATTACK SUCCESS RATE EVALUATION")

        print("=" * 70)

        model = self.build_model()

        dataloader = self.build_dataloader()

        criterion = get_loss("cross_entropy")

        evaluator = Evaluator(

            device=self.device,

            output_dir="reports/json",

        )

        results = evaluator.validate(

            model=model,

            dataloader=dataloader,

            criterion=criterion,

        )

        ########################################################

        asr = results["accuracy"]

        report = {

            "model": self.model_name,

            "attack": self.attack_name,

            "target_class": self.target_class,

            "poison_rate": self.poison_rate,

            "attack_success_rate": round(asr, 2),

            "accuracy": round(results["accuracy"], 2),

            "precision": round(results["precision"], 2),

            "recall": round(results["recall"], 2),

            "f1_score": round(results["f1"], 2),

            "balanced_accuracy": round(

                results["balanced_accuracy"],

                2,

            ),

            "mcc": round(results["mcc"], 4),

            "samples": results["samples"],

            "validation_time": round(

                results["time"],

                2,

            ),

        }

        ########################################################

        output_file = (

            self.output_dir /

            "attack_success_rate.json"

        )

        with open(

            output_file,

            "w",

        ) as f:

            json.dump(

                report,

                f,

                indent=4,

            )

        ########################################################

        print()

        print("=" * 70)

        print("ATTACK SUCCESS RATE")

        print("=" * 70)

        print(f"Model             : {self.model_name}")

        print(f"Attack            : {self.attack_name}")

        print(f"Target Class      : {self.target_class}")

        print(f"Poison Rate       : {self.poison_rate:.2f}")

        print(f"Attack Success    : {asr:.2f}%")

        print(f"Precision         : {results['precision']:.2f}%")

        print(f"Recall            : {results['recall']:.2f}%")

        print(f"F1 Score          : {results['f1']:.2f}%")

        print(f"MCC               : {results['mcc']:.4f}")

        print()

        print(f"Report Saved      : {output_file}")

        print("=" * 70)

        return report
    ############################################################
# Main
############################################################

def main():

    import argparse

    parser = argparse.ArgumentParser(

        description="Attack Success Rate Evaluation"

    )

    parser.add_argument(
        "--model",
        default="efficientnet_b0",
        type=str,
    )

    parser.add_argument(
        "--checkpoint",
        default="checkpoints/best_model.pth",
        type=str,
    )

    parser.add_argument(
        "--attack",
        default="badnets",
        type=str,
    )

    parser.add_argument(
        "--target-class",
        default=0,
        type=int,
    )

    parser.add_argument(
        "--batch-size",
        default=64,
        type=int,
    )

    args = parser.parse_args()

    evaluator = AttackSuccessRate(

        model_name=args.model,

        checkpoint=args.checkpoint,

        attack_name=args.attack,

        poison_rate=1.0,

        target_class=args.target_class,

        batch_size=args.batch_size,

    )

    report = evaluator.evaluate()

    print()

    print("=" * 70)

    print("SUMMARY")

    print("=" * 70)

    print(f"Model                : {report['model']}")

    print(f"Attack               : {report['attack']}")

    print(f"Attack Success Rate  : {report['attack_success_rate']:.2f}%")

    print(f"Accuracy             : {report['accuracy']:.2f}%")

    print(f"Precision            : {report['precision']:.2f}%")

    print(f"Recall               : {report['recall']:.2f}%")

    print(f"F1 Score             : {report['f1_score']:.2f}%")

    print(f"MCC                  : {report['mcc']:.4f}")

    print("=" * 70)


############################################################
# Entry Point
############################################################

if __name__ == "__main__":

    main()