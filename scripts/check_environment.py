from utils.device import get_device
from utils.seed import set_seed
from utils.config import load_config

print("=" * 60)
print("BTSecBench_v2 Environment Check")
print("=" * 60)

config = load_config("configs/config.yaml")

set_seed(config["project"]["seed"])

print("Project :", config["project"]["name"])
print("Seed    :", config["project"]["seed"])
print("Device  :", get_device())

print("\nEnvironment Ready.")