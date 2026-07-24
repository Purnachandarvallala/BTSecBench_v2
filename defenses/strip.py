"""
==============================================================
BTSecBench_v2

FINAL STRIP BACKDOOR DETECTION DEFENSE

Purpose:
Detect poisoned inputs before inference.

Evaluation:
- Detection Accuracy
- Precision
- Recall
- F1 Score
- FPR
- FNR
- AUC

Model:
Backdoored checkpoint

checkpoint:
checkpoints/best_model.pth

==============================================================
"""


from __future__ import annotations


import argparse
import json
import random


from pathlib import Path


import numpy as np
import pandas as pd


import torch
import torch.nn.functional as F


from torch.utils.data import DataLoader


from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)



import matplotlib.pyplot as plt



from attacks import get_attack, PoisonedDataset

from data.dataloader import create_dataset

from models import get_model





# =============================================================
# STRIP Detector
# =============================================================


class STRIPDetector:



    def __init__(

        self,

        model_name="efficientnet_b0",

        checkpoint="checkpoints/best_model.pth",

        attack_name="badnets",

        target_class=0,

        poison_rate=1.0,

        batch_size=32,

        perturbations=30,

        alpha=0.7,


    ):


        self.model_name = model_name


        self.checkpoint = checkpoint


        self.attack_name = attack_name


        self.target_class = target_class


        self.poison_rate = poison_rate


        self.batch_size = batch_size


        self.perturbations = perturbations


        # trigger preservation
        self.alpha = alpha



        self.device = torch.device(

            "cuda"

            if torch.cuda.is_available()

            else "cpu"

        )



        self.model = None


        self.clean_dataset = None


        self.poison_dataset = None


        self.clean_bank = None


        self.threshold = None



        self.results = {}



        # Output folders


        self.report_dir = Path(

            "reports"

        )


        self.json_dir = (

            self.report_dir / "json"

        )


        self.csv_dir = (

            self.report_dir / "csv"

        )


        self.figure_dir = (

            self.report_dir / "figures"

        )



        self.json_dir.mkdir(

            parents=True,

            exist_ok=True

        )


        self.csv_dir.mkdir(

            parents=True,

            exist_ok=True

        )


        self.figure_dir.mkdir(

            parents=True,

            exist_ok=True

        )





    # =========================================================
    # Load Backdoored Model
    # =========================================================


    def load_model(self):


        print()

        print("=" * 70)

        print("LOADING BACKDOORED MODEL")

        print("=" * 70)



        self.model = get_model(

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


                checkpoint = checkpoint[

                    "model_state_dict"

                ]



        self.model.load_state_dict(

            checkpoint

        )


        self.model.to(

            self.device

        )


        self.model.eval()



        print(

            "✓ Model loaded"

        )


        print(

            f"Device : {self.device}"

        )
    # =========================================================
    # Build STRIP Datasets
    # =========================================================


    def build_datasets(self):


        print()

        print("=" * 70)

        print("BUILDING STRIP DATASETS")

        print("=" * 70)



        # Clean validation data

        self.clean_dataset = create_dataset(

            csv_file="data/splits/val.csv",

            mode="strip",

        )



        # Backdoor attack

        attack = get_attack(

            attack_name=self.attack_name,

            poison_rate=self.poison_rate,

            target_class=self.target_class,

        )



        # Create poisoned validation set

        self.poison_dataset = PoisonedDataset(

            dataset=self.clean_dataset,

            attack=attack,

            poison_all=True,

        )



        print(

            f"Clean samples    : {len(self.clean_dataset)}"

        )


        print(

            f"Poison samples   : {len(self.poison_dataset)}"

        )



        return (

            self.clean_dataset,

            self.poison_dataset,

        )



    # =========================================================
    # Create Clean Reference Bank
    # =========================================================


    def create_clean_bank(self):


        print()

        print("=" * 70)

        print("CREATING CLEAN IMAGE BANK")

        print("=" * 70)



        bank_size = min(

            1000,

            len(self.clean_dataset)

        )



        indexes = random.sample(

            range(len(self.clean_dataset)),

            bank_size

        )



        images = []



        for idx in indexes:


            sample = self.clean_dataset[idx]


            images.append(

                sample["image"]

            )



        self.clean_bank = torch.stack(

            images

        )



        print(

            f"Reference images : {len(self.clean_bank)}"

        )



        return self.clean_bank




    # =========================================================
    # Data Loader
    # =========================================================


    def create_loader(self, dataset):


        return DataLoader(

            dataset,

            batch_size=self.batch_size,

            shuffle=False,

            num_workers=0,

        )




    # =========================================================
    # Normalize Image
    # =========================================================


    def normalize(self, image):


        mean = torch.tensor(

            [0.3337, 0.3064, 0.3171]

        ).view(

            3,1,1

        ).to(

            image.device

        )



        std = torch.tensor(

            [0.2672, 0.2564, 0.2629]

        ).view(

            3,1,1

        ).to(

            image.device

        )


        return (

            image - mean

        ) / std





    # =========================================================
    # Generate STRIP Perturbations
    # =========================================================


    def generate_perturbations(self, image):


        perturbations = []



        for _ in range(self.perturbations):


            index = random.randint(

                0,

                len(self.clean_bank)-1

            )



            clean_image = self.clean_bank[index]



            # Image space blending

            mixed = (

                self.alpha * image

                +

                (1-self.alpha) * clean_image

            )



            mixed = torch.clamp(

                mixed,

                0,

                1

            )



            mixed = self.normalize(

                mixed

            )



            perturbations.append(

                mixed

            )



        return torch.stack(

            perturbations

        )
        # =========================================================
    # Model Prediction
    # =========================================================


    @torch.no_grad()
    def predict(self, images):


        images = images.to(

            self.device

        )



        outputs = self.model(

            images

        )



        probabilities = F.softmax(

            outputs,

            dim=1

        )



        return probabilities




    # =========================================================
    # Shannon Entropy
    # =========================================================


    def calculate_entropy(self, probabilities):


        """

        Shannon entropy:

        H(p) = -sum(p log(p))


        Lower entropy:
            Stable prediction
            Possible poisoned input


        Higher entropy:
            Unstable prediction
            Clean input


        """



        entropy = -(

            probabilities *

            torch.log(

                probabilities + 1e-12

            )

        ).sum(

            dim=1

        )



        return entropy





    # =========================================================
    # STRIP Score For One Image
    # =========================================================


    @torch.no_grad()
    def strip_score(self, image):


        perturbations = self.generate_perturbations(

            image

        )



        probabilities = self.predict(

            perturbations

        )



        entropy_values = self.calculate_entropy(

            probabilities

        )



        # average entropy over perturbations

        score = entropy_values.mean()



        return score.item()





    # =========================================================
    # Calculate Entropy Distribution
    # =========================================================


    def calculate_dataset_entropy(

        self,

        loader,

        label,

    ):



        scores = []

        labels = []



        print(

            "Calculating entropy..."

        )



        for batch in loader:



            images = batch["image"]



            for image in images:



                score = self.strip_score(

                    image

                )



                scores.append(

                    score

                )



                labels.append(

                    label

                )



        return (

            np.array(scores),

            np.array(labels),

        )





    # =========================================================
    # Optimize Detection Threshold
    # =========================================================


    def optimize_threshold(

        self,

        scores,

        labels,

    ):


        best_threshold = None

        best_f1 = 0



        minimum = scores.min()

        maximum = scores.max()



        thresholds = np.linspace(

            minimum,

            maximum,

            200

        )



        for threshold in thresholds:



            # Low entropy = poisoned

            predictions = (

                scores < threshold

            ).astype(int)



            f1 = f1_score(

                labels,

                predictions,

                zero_division=0

            )



            if f1 > best_f1:


                best_f1 = f1


                best_threshold = threshold




        self.threshold = best_threshold



        print()

        print("=" * 70)

        print("THRESHOLD OPTIMIZATION")

        print("=" * 70)


        print(

            f"Best threshold : {self.threshold:.4f}"

        )


        print(

            f"Best F1        : {best_f1:.4f}"

        )


        print("=" * 70)



        return self.threshold
        # =========================================================
    # Complete Evaluation
    # =========================================================


    def evaluate(self):


        print()

        print("=" * 70)

        print("RUNNING FINAL STRIP EVALUATION")

        print("=" * 70)



        if self.model is None:

            self.load_model()



        self.build_datasets()



        self.create_clean_bank()



        clean_loader = self.create_loader(

            self.clean_dataset

        )


        poison_loader = self.create_loader(

            self.poison_dataset

        )



        # -----------------------------------------------------
        # Entropy scores
        # -----------------------------------------------------


        clean_scores, clean_labels = (

            self.calculate_dataset_entropy(

                clean_loader,

                0

            )

        )



        poison_scores, poison_labels = (

            self.calculate_dataset_entropy(

                poison_loader,

                1

            )

        )



        scores = np.concatenate(

            [

                clean_scores,

                poison_scores

            ]

        )


        labels = np.concatenate(

            [

                clean_labels,

                poison_labels

            ]

        )



        # -----------------------------------------------------
        # Threshold
        # -----------------------------------------------------


        self.optimize_threshold(

            scores,

            labels

        )



        # -----------------------------------------------------
        # Predictions
        # -----------------------------------------------------


        predictions = (

            scores < self.threshold

        ).astype(int)



        # -----------------------------------------------------
        # Metrics
        # -----------------------------------------------------


        accuracy = accuracy_score(

            labels,

            predictions

        )


        precision = precision_score(

            labels,

            predictions,

            zero_division=0

        )


        recall = recall_score(

            labels,

            predictions,

            zero_division=0

        )


        f1 = f1_score(

            labels,

            predictions,

            zero_division=0

        )



        cm = confusion_matrix(

            labels,

            predictions

        )



        tn, fp, fn, tp = cm.ravel()



        fpr = fp / max(

            tn + fp,

            1

        )


        fnr = fn / max(

            fn + tp,

            1

        )



        auc = roc_auc_score(

            labels,

            -scores

        )



        self.results = {


            "threshold":

                float(self.threshold),


            "accuracy":

                float(accuracy),


            "precision":

                float(precision),


            "recall":

                float(recall),


            "f1":

                float(f1),


            "false_positive_rate":

                float(fpr),


            "false_negative_rate":

                float(fnr),


            "auc":

                float(auc),


            "confusion_matrix":

                cm.tolist(),


        }



        print()

        print("=" * 70)

        print("FINAL STRIP RESULTS")

        print("=" * 70)



        print(

            f"Threshold          : {self.threshold:.4f}"

        )


        print(

            f"Accuracy           : {accuracy*100:.2f}%"

        )


        print(

            f"Precision          : {precision*100:.2f}%"

        )


        print(

            f"Recall             : {recall*100:.2f}%"

        )


        print(

            f"F1 Score           : {f1*100:.2f}%"

        )


        print(

            f"False Positive Rate: {fpr*100:.2f}%"

        )


        print(

            f"False Negative Rate: {fnr*100:.2f}%"

        )


        print(

            f"AUC                : {auc:.4f}"

        )


        print("=" * 70)



        return self.results





    # =========================================================
    # Save Results
    # =========================================================


    def save_results(self):


        json_path = (

            self.json_dir /

            "strip_results.json"

        )


        with open(

            json_path,

            "w"

        ) as f:


            json.dump(

                self.results,

                f,

                indent=4

            )



        print()

        print(

            f"Saved report: {json_path}"

        )





# =============================================================
# Main
# =============================================================


def main():


    parser = argparse.ArgumentParser(

        description="Final STRIP Detector"

    )



    parser.add_argument(

        "--model",

        default="efficientnet_b0"

    )


    parser.add_argument(

        "--attack",

        default="badnets"

    )


    parser.add_argument(

        "--checkpoint",

        default="checkpoints/best_model.pth"

    )



    args = parser.parse_args()



    detector = STRIPDetector(

        model_name=args.model,

        attack_name=args.attack,

        checkpoint=args.checkpoint,

    )



    detector.load_model()



    detector.evaluate()



    detector.save_results()




if __name__ == "__main__":

    main()