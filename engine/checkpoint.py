"""
=========================================================
BTSecBench_v2

Checkpoint Manager

=========================================================
"""

from pathlib import Path
from datetime import datetime

import torch


class CheckpointManager:
    """
    Professional checkpoint manager.
    """

    def __init__(self, checkpoint_dir="checkpoints"):

        self.checkpoint_dir = Path(checkpoint_dir)

        self.checkpoint_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    ######################################################

    def save(
        self,
        model,
        optimizer=None,
        scheduler=None,
        epoch=0,
        metrics=None,
        filename="last_checkpoint.pth",
        is_best=False,
    ):

        if metrics is None:
            metrics = {}

        checkpoint = {

            "epoch": epoch,

            "model_state_dict":
                model.state_dict(),

            "optimizer_state_dict":
                optimizer.state_dict()
                if optimizer is not None else None,

            "scheduler_state_dict":
                scheduler.state_dict()
                if scheduler is not None else None,

            "metrics": metrics,

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        }

        save_path = self.checkpoint_dir / filename

        torch.save(
            checkpoint,
            save_path,
        )

        print(f"\nCheckpoint saved : {save_path}")

        if is_best:

            best_path = (
                self.checkpoint_dir /
                "best_model.pth"
            )

            torch.save(
                checkpoint,
                best_path,
            )

            print(
                f"Best model updated : {best_path}"
            )

    ######################################################

    def load(
        self,
        model,
        optimizer=None,
        scheduler=None,
        filename="last_checkpoint.pth",
    ):

        load_path = self.checkpoint_dir / filename

        if not load_path.exists():

            raise FileNotFoundError(load_path)

        checkpoint = torch.load(
            load_path,
            map_location="cpu",
        )

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        if (
            optimizer is not None
            and checkpoint["optimizer_state_dict"] is not None
        ):
            optimizer.load_state_dict(
                checkpoint["optimizer_state_dict"]
            )

        if (
            scheduler is not None
            and checkpoint["scheduler_state_dict"] is not None
        ):
            scheduler.load_state_dict(
                checkpoint["scheduler_state_dict"]
            )

        print(f"\nLoaded checkpoint : {load_path}")

        return checkpoint

    ######################################################

    def latest_checkpoint(self):

        files = sorted(
            self.checkpoint_dir.glob("*.pth")
        )

        if len(files) == 0:
            return None

        return files[-1]