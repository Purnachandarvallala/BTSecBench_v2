from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"

REPORT_DIR = PROJECT_ROOT / "reports"

LOG_DIR = PROJECT_ROOT / "logs"

RESULT_DIR = PROJECT_ROOT / "results"

for folder in [

    CHECKPOINT_DIR,

    REPORT_DIR,

    LOG_DIR,

    RESULT_DIR

]:

    folder.mkdir(exist_ok=True)