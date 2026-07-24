"""
==============================================================
BTSecBench_v2

Attack Factory


==============================================================
"""

from attacks.badnets import BadNetsAttack
from attacks.blend import BlendAttack
from attacks.sig import SIGAttack
from attacks.wanet import WaNetAttack


ATTACK_REGISTRY = {

    "badnets": BadNetsAttack,

    "blend": BlendAttack,

    "sig": SIGAttack,

    "wanet": WaNetAttack,

}


def available_attacks():

    return sorted(ATTACK_REGISTRY.keys())


def get_attack(
    attack_name,
    target_class=0,
    poison_rate=0.10,
    **kwargs,
):

    attack_name = attack_name.lower()

    if attack_name not in ATTACK_REGISTRY:

        raise ValueError(

            f"Unknown attack '{attack_name}'. "

            f"Available attacks: "

            f"{available_attacks()}"

        )

    attack_class = ATTACK_REGISTRY[attack_name]

    return attack_class(

        target_class=target_class,

        poison_rate=poison_rate,

        **kwargs,

    )