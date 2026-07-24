from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
JSON_DIR = REPORTS / "json"
ASSETS = ROOT / "docs" / "assets"


st.set_page_config(
    page_title="BTSecBench_v2 Dashboard",
    page_icon="BT",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    if path.suffix.lower() == ".json":
        data = load_json(path, [])
        return pd.DataFrame(data if isinstance(data, list) else [data])
    return pd.read_csv(path)


def show_image(path: Path, caption: str | None = None, use_container_width: bool = True) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=use_container_width)
    else:
        st.info(f"Missing image: {path.relative_to(ROOT)}")


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if 0 <= number <= 1:
        number *= 100
    return f"{number:.2f}%"


def number(value: Any, suffix: str = "") -> str:
    try:
        return f"{float(value):.2f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label=label, value=value, help=help_text)


def page_header(title: str, description: str) -> None:
    st.title(title)
    st.caption(description)


attack_results = load_json(JSON_DIR / "attack_success_rate.json", {})
strip_results = load_json(JSON_DIR / "strip_final_results.json", {})
fine_tuning_results = load_json(REPORTS / "fine_tuning" / "fine_tuning_results.json", {})
training_history = load_json(REPORTS / "training_history.json", {})
model_benchmark = load_table(REPORTS / "model_benchmark.json")


with st.sidebar:
    st.title("BTSecBench_v2")
    st.caption("Backdoor Security Benchmark Dashboard")
    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Architecture",
            "Attack Pipeline",
            "STRIP Detection",
            "Fine-Tuning Defense",
            "Results",
            "Examples",
            "Raw Artifacts",
        ],
    )
    st.divider()
    st.caption("Project paths")
    st.code(str(ROOT), language="text")


if page == "Overview":
    page_header(
        "BTSecBench_v2",
        "A Streamlit dashboard for traffic-sign backdoor attacks, defenses, metrics, and generated artifacts.",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Model", str(attack_results.get("model", fine_tuning_results.get("model", "N/A"))))
    with c2:
        metric_card("Attack", str(attack_results.get("attack", strip_results.get("attack", "N/A"))))
    with c3:
        metric_card("Attack Success Rate", pct(attack_results.get("attack_success_rate")))
    with c4:
        metric_card("Fine-Tuned Accuracy", pct(fine_tuning_results.get("validation_accuracy")))

    st.subheader("Benchmark Summary")
    left, right = st.columns([1.2, 1])
    with left:
        show_image(FIGURES / "benchmark_summary.png")
    with right:
        st.markdown(
            """
            This dashboard summarizes the local BTSecBench_v2 artifacts:

            - Backdoor attack pipeline and trigger examples
            - STRIP detection workflow and metrics
            - Fine-tuning defense workflow and validation results
            - Model benchmark and training-history outputs
            """
        )

    st.subheader("Model Benchmark")
    if model_benchmark.empty:
        st.info("No model benchmark table was found.")
    else:
        st.dataframe(model_benchmark, use_container_width=True, hide_index=True)


elif page == "Architecture":
    page_header(
        "System Architecture",
        "High-level project structure and runtime relationships.",
    )
    st.markdown(
        """
        BTSecBench_v2 is organized around data preparation, attack injection,
        model training, evaluation, defenses, explainability, tracking, and reports.
        """
    )
    architecture_md = ROOT / "docs" / "system_architecture.md"
    if architecture_md.exists():
        with st.expander("Open architecture notes"):
            st.markdown(architecture_md.read_text(encoding="utf-8"))
    else:
        st.info("Architecture Markdown file was not found.")


elif page == "Attack Pipeline":
    page_header(
        "Backdoor Attack Pipeline",
        "Workflow for poisoning validation/training samples and measuring attack success.",
    )
    show_image(ASSETS / "backdoor_attack_pipeline_vertical.png")

    st.subheader("Attack Success Rate")
    cols = st.columns(5)
    with cols[0]:
        metric_card("ASR", pct(attack_results.get("attack_success_rate")))
    with cols[1]:
        metric_card("Accuracy", pct(attack_results.get("accuracy")))
    with cols[2]:
        metric_card("Precision", pct(attack_results.get("precision")))
    with cols[3]:
        metric_card("Recall", pct(attack_results.get("recall")))
    with cols[4]:
        metric_card("Samples", str(attack_results.get("samples", "N/A")))

    st.subheader("Attack Figures")
    c1, c2 = st.columns(2)
    with c1:
        show_image(FIGURES / "asr_comparison.png")
    with c2:
        show_image(FIGURES / "accuracy_comparison.png")


elif page == "STRIP Detection":
    page_header(
        "STRIP Detection Workflow",
        "Runtime detection using prediction entropy under random perturbations.",
    )
    show_image(ASSETS / "strip_detection_workflow.svg")

    st.subheader("STRIP Metrics")
    cols = st.columns(5)
    with cols[0]:
        metric_card("Accuracy", pct(strip_results.get("accuracy")))
    with cols[1]:
        metric_card("Precision", pct(strip_results.get("precision")))
    with cols[2]:
        metric_card("Recall", pct(strip_results.get("recall")))
    with cols[3]:
        metric_card("F1", pct(strip_results.get("f1")))
    with cols[4]:
        metric_card("AUC", number(strip_results.get("auc")))

    c1, c2 = st.columns(2)
    with c1:
        show_image(FIGURES / "strip_metrics.png")
        show_image(FIGURES / "strip_entropy_histogram.png")
    with c2:
        show_image(FIGURES / "strip_confusion_matrix.png")
        show_image(FIGURES / "strip_roc_curve.png")


elif page == "Fine-Tuning Defense":
    page_header(
        "Fine-Tuning Defense Workflow",
        "Clean recovery training from a backdoored checkpoint.",
    )
    show_image(ASSETS / "fine_tuning_defense_workflow_vertical.png")

    st.subheader("Fine-Tuning Results")
    cols = st.columns(5)
    with cols[0]:
        metric_card("Validation Accuracy", pct(fine_tuning_results.get("validation_accuracy")))
    with cols[1]:
        metric_card("Validation Loss", number(fine_tuning_results.get("validation_loss")))
    with cols[2]:
        metric_card("F1", pct(fine_tuning_results.get("f1_score")))
    with cols[3]:
        metric_card("MCC", number(fine_tuning_results.get("mcc")))
    with cols[4]:
        metric_card("Epochs", str(fine_tuning_results.get("epochs", "N/A")))

    if training_history:
        st.subheader("Training History")
        history_df = pd.DataFrame(training_history)
        st.line_chart(
            history_df.set_index("epoch")[["train_accuracy", "val_accuracy"]],
            use_container_width=True,
        )
        st.line_chart(
            history_df.set_index("epoch")[["train_loss", "val_loss"]],
            use_container_width=True,
        )


elif page == "Results":
    page_header(
        "Results Dashboard",
        "Consolidated benchmark, attack, defense, and detection outputs.",
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Attack", "STRIP", "Fine-Tuning", "Model Benchmark"]
    )
    with tab1:
        st.json(attack_results)
    with tab2:
        st.json(strip_results)
    with tab3:
        st.json(fine_tuning_results)
    with tab4:
        if model_benchmark.empty:
            st.info("No model benchmark table was found.")
        else:
            st.dataframe(model_benchmark, use_container_width=True, hide_index=True)


elif page == "Examples":
    page_header(
        "Image Examples",
        "Clean validation examples and trigger patterns generated from local GTSRB samples.",
    )
    st.subheader("Correctly Classified Examples")
    show_image(ASSETS / "correctly_classified_examples.png")

    st.subheader("Trigger Pattern Examples")
    show_image(ASSETS / "trigger_pattern_examples.png")


elif page == "Raw Artifacts":
    page_header(
        "Raw Artifacts",
        "Browse available local files used by the dashboard.",
    )
    artifact_dirs = {
        "Report JSON": JSON_DIR,
        "Figures": FIGURES,
        "Generated Assets": ASSETS,
        "Fine-Tuning Reports": REPORTS / "fine_tuning",
    }

    for name, folder in artifact_dirs.items():
        st.subheader(name)
        if not folder.exists():
            st.info(f"Missing folder: {folder.relative_to(ROOT)}")
            continue
        rows = [
            {
                "file": str(path.relative_to(ROOT)),
                "size_kb": round(path.stat().st_size / 1024, 2),
            }
            for path in sorted(folder.iterdir())
            if path.is_file()
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
