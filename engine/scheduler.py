"""
==============================================================
BTSecBench_v2

Learning Rate Scheduler Factory

Author : Shivaprasad Aredla
==============================================================
"""

import torch


def get_scheduler(
    optimizer,
    name="step",
    epochs=30,
    steps_per_epoch=100,
    step_size=10,
    gamma=0.1,
    milestones=None,
    eta_min=1e-6,
    patience=5,
):

    name = name.lower()

    if milestones is None:
        milestones = [15, 25]

    # --------------------------------------------------------

    if name == "none":
        return None

    # --------------------------------------------------------

    elif name == "step":

        return torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=step_size,
            gamma=gamma,
        )

    # --------------------------------------------------------

    elif name == "multistep":

        return torch.optim.lr_scheduler.MultiStepLR(
            optimizer,
            milestones=milestones,
            gamma=gamma,
        )

    # --------------------------------------------------------

    elif name == "cosine":

        return torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=epochs,
            eta_min=eta_min,
        )

    # --------------------------------------------------------

    elif name == "plateau":

        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="max",
            factor=gamma,
            patience=patience,
        )

    # --------------------------------------------------------

    elif name == "onecycle":

        return torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=optimizer.param_groups[0]["lr"],
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
        )

    # --------------------------------------------------------

    else:

        raise ValueError(
            f"Unknown scheduler : {name}"
        )