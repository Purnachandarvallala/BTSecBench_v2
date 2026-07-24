"""
==============================================================
BTSecBench_v2

Fine-Tuning Defense


==============================================================

Mitigation of backdoor attacks by fine-tuning the poisoned
model on clean data.

Pipeline

Backdoored Model
        ↓
Load Checkpoint
        ↓
Clean Fine-Tuning
        ↓
Save Defended Model
        ↓
Evaluate
        ↓
Compare Before vs After

==============================================================
"""

from __future__ import annotations

from pathlib import Path

import torch

from data.dataloader import create_dataloaders

from models import get_model

from engine import (
    Trainer,
    Evaluator,
    get_loss,
    get_scheduler,
)

###############################################################
# Fine Tuning Defense
###############################################################

class FineTuningDefense:

    def __init__(

        self,

        model_name="efficientnet_b0",

        checkpoint="checkpoints/best_model.pth",

        epochs=5,

        batch_size=64,

        learning_rate=1e-5,

        device=None,

    ):

        self.model_name = model_name

        self.checkpoint = checkpoint

        self.epochs = epochs

        self.batch_size = batch_size

        self.learning_rate = learning_rate

        self.device = torch.device(

            device if device

            else "cuda"

            if torch.cuda.is_available()

            else "cpu"

        )

        #######################################################

        self.output_dir = Path("reports/fine_tuning")

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

    ###########################################################
    # Load Model
    ###########################################################

    def load_model(self):

        print()

        print("=" * 70)

        print("LOADING BACKDOORED MODEL")

        print("=" * 70)

        model = get_model(

            model_name=self.model_name,

            num_classes=43,

            pretrained=False,

            freeze_backbone=False,

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

        print("Checkpoint Loaded Successfully")

        return model

    ###########################################################
    # Clean Data
    ###########################################################

    def build_dataloaders(self):

        print()

        print("=" * 70)

        print("LOADING CLEAN DATASET")

        print("=" * 70)

        train_loader, val_loader = create_dataloaders(

            batch_size=self.batch_size,

        )

        return train_loader, val_loader

    ###########################################################
    # Optimizer
    ###########################################################

    def build_optimizer(self, model):

        return torch.optim.AdamW(

            model.parameters(),

            lr=self.learning_rate,

            weight_decay=1e-4,

        )

    ###########################################################
    # Loss
    ###########################################################

    def build_loss(self):

        return get_loss(

            name="cross_entropy",

        )

    ###########################################################
    # Scheduler
    ###########################################################

    def build_scheduler(

        self,

        optimizer,

        train_loader,

    ):

        return get_scheduler(

            optimizer=optimizer,

            name="cosine",

            epochs=self.epochs,

            steps_per_epoch=len(train_loader),

        )
        ###########################################################
    # Fine-Tune Defense
    ###########################################################

    def defend(self):

        print()

        print("=" * 70)
        print("STARTING FINE-TUNING DEFENSE")
        print("=" * 70)

        #######################################################
        # Model
        #######################################################

        model = self.load_model()

        #######################################################
        # Data
        #######################################################

        train_loader, val_loader = self.build_dataloaders()

        #######################################################
        # Optimizer
        #######################################################

        optimizer = self.build_optimizer(model)

        #######################################################
        # Loss
        #######################################################

        criterion = self.build_loss()

        #######################################################
        # Scheduler
        #######################################################

        scheduler = self.build_scheduler(

            optimizer,

            train_loader,

        )

        #######################################################
        # Trainer
        #######################################################

        trainer = Trainer(

            model=model,

            optimizer=optimizer,

            criterion=criterion,

            scheduler=scheduler,

            train_loader=train_loader,

            val_loader=val_loader,

            device=self.device,

            epochs=self.epochs,

            checkpoint_dir="checkpoints",

        )

        #######################################################
        # Evaluator
        #######################################################

        evaluator = Evaluator(

            device=self.device,

            output_dir=self.output_dir,

        )

        #######################################################
        # Summary
        #######################################################

        trainer.summary()

        #######################################################
        # Fine-Tune
        #######################################################

        trainer.fit(

            evaluator=evaluator,

        )

        #######################################################
        # Save Defended Model
        #######################################################

        defended_checkpoint = (

            self.output_dir /

            "defended_model.pth"

        )

        torch.save(

            model.state_dict(),

            defended_checkpoint,

        )

        #######################################################
        # Store objects
        #######################################################

        self.model = model

        self.trainer = trainer

        self.evaluator = evaluator

        self.criterion = criterion

        self.train_loader = train_loader

        self.val_loader = val_loader

        self.defended_checkpoint = defended_checkpoint

        print()

        print("=" * 70)
        print("FINE-TUNING COMPLETED")
        print("=" * 70)

        print(f"Defended Model : {defended_checkpoint}")

        print("=" * 70)
            ###########################################################
    # Evaluate Defended Model
    ###########################################################

    def evaluate(self):

        print()

        print("=" * 70)
        print("EVALUATING DEFENDED MODEL")
        print("=" * 70)

        results = self.evaluator.validate(

            model=self.model,

            dataloader=self.val_loader,

            criterion=self.criterion,

        )

        self.evaluator.print_summary(results)

        self.results = results

        return results

    ###########################################################
    # Export Results
    ###########################################################

    def export_results(self):

        print()

        print("=" * 70)
        print("EXPORTING DEFENSE RESULTS")
        print("=" * 70)

        report = {

            "defense": "Fine-Tuning",

            "model": self.model_name,

            "epochs": self.epochs,

            "learning_rate": self.learning_rate,

            "checkpoint": str(self.defended_checkpoint),

            "validation_accuracy": round(

                self.results["accuracy"],

                2,

            ),

            "validation_loss": round(

                self.results["loss"],

                4,

            ),

            "precision": round(

                self.results["precision"],

                2,

            ),

            "recall": round(

                self.results["recall"],

                2,

            ),

            "f1_score": round(

                self.results["f1"],

                2,

            ),

            "balanced_accuracy": round(

                self.results["balanced_accuracy"],

                2,

            ),

            "mcc": round(

                self.results["mcc"],

                4,

            ),

            "samples": self.results["samples"],

            "validation_time": round(

                self.results["time"],

                2,

            )

        }

        #######################################################
        # JSON
        #######################################################

        json_path = (

            self.output_dir /

            "fine_tuning_results.json"

        )

        import json

        with open(

            json_path,

            "w",

        ) as f:

            json.dump(

                report,

                f,

                indent=4,

            )

        #######################################################
        # CSV
        #######################################################

        import pandas as pd

        csv_path = (

            self.output_dir /

            "fine_tuning_results.csv"

        )

        pd.DataFrame(

            [report]

        ).to_csv(

            csv_path,

            index=False,

        )

        #######################################################

        print()

        print("=" * 70)
        print("FINE-TUNING DEFENSE RESULTS")
        print("=" * 70)

        print(

            f"Validation Accuracy : "

            f"{report['validation_accuracy']:.2f}%"

        )

        print(

            f"Validation Loss     : "

            f"{report['validation_loss']:.4f}"

        )

        print()

        print(f"Checkpoint : {self.defended_checkpoint}")

        print(f"JSON       : {json_path}")

        print(f"CSV        : {csv_path}")

        print("=" * 70)

        return report


###############################################################
# Main
###############################################################

def main():

    defense = FineTuningDefense(

        model_name="efficientnet_b0",

        checkpoint="checkpoints/best_model.pth",

        epochs=15,

        learning_rate=1e-4,

    )

    defense.defend()

    defense.evaluate()

    defense.export_results()


###############################################################
# Entry Point
###############################################################

if __name__ == "__main__":

    main()