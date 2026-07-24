# 🚦 BTSecBench_v2
### A Comprehensive Benchmark Framework for Backdoor Attack Detection and Defense in Traffic Sign Recognition

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red?style=for-the-badge&logo=pytorch)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</p>

---

## 📌 Project Overview

**BTSecBench_v2** is a comprehensive benchmark framework developed to evaluate the robustness of **Deep Learning-based Traffic Sign Recognition (TSR)** systems against **Backdoor Attacks**.

Deep learning-based TSR systems are widely used in Autonomous Vehicles and Advanced Driver Assistance Systems (ADAS). Modern convolutional neural networks achieve excellent classification accuracy, but they remain vulnerable to backdoor attacks — where poisoned samples injected during training cause a model to behave normally on clean images while predicting an attacker-selected target class whenever a hidden trigger appears.

This is a serious security concern because:

- High classification accuracy does **not** guarantee a secure model.
- Traditional evaluation methods cannot detect hidden backdoors.
- A compromised TSR model may misclassify critical traffic signs, potentially leading to unsafe driving decisions.

Unlike conventional image classification projects that focus only on classification accuracy, BTSecBench_v2 integrates:

- 🚀 Multiple Deep Learning Models
- 🎯 Multiple Backdoor Attacks
- 🔍 Runtime Detection
- 🛡 Defense Mechanisms
- 📊 Automated Benchmarking
- 📈 Visualization
- 📑 Report Generation

The framework provides an end-to-end pipeline that evaluates not only how accurate a model is, but also how secure and robust it is against adversarial manipulation — making it a reproducible benchmark for AI security research.

---

## 🎯 Why This Project?

Most existing implementations focus on only one aspect of backdoor security, such as:

- A single attack
- A single defense
- Classification accuracy only
- Manual evaluation
- Limited reporting

There is no unified benchmark that allows researchers to compare multiple attacks, detection methods, defenses, and performance metrics within one reproducible workflow. **BTSecBench_v2 addresses this gap** by integrating all these components into a single benchmark framework.

---

## 🎯 Objectives

The primary objectives of this project are to:

- Develop a robust Traffic Sign Recognition system.
- Compare multiple CNN architectures.
- Implement multiple backdoor attacks.
- Evaluate Attack Success Rate (ASR).
- Detect poisoned inputs using STRIP.
- Defend compromised models using Fine-Tuning.
- Automatically generate benchmark reports.
- Provide a reproducible framework for AI Security research.

---

## 🏆 Key Contributions

- Compared **four** deep learning architectures: Baseline CNN, ResNet18, MobileNetV3, and EfficientNet-B0.
- Selected **EfficientNet-B0** as the backbone based on its accuracy–efficiency trade-off.
- Implemented **four** representative backdoor attacks: BadNets, Blend, SIG, and WaNet.
- Integrated **STRIP** for runtime detection of poisoned inputs.
- Implemented **Fine-Tuning** as the defense and recovery mechanism.
- Developed an automated benchmarking system that generates CSV, JSON, and Excel reports, Markdown summaries, and performance figures.

---

## 🏗 Project Architecture

```text
                     GTSRB Dataset
                           │
                           ▼
                  Data Preprocessing
                           │
                           ▼
                Deep Learning Models
                           │
     ┌────────────┬──────────────┬──────────────┐
     ▼            ▼              ▼              ▼
Baseline CNN   ResNet18   MobileNetV3   EfficientNet-B0
                           │
                           ▼
               Selected Backbone Model
                           │
                           ▼
             Backdoor Attack Generation
                           │
     ┌────────────┬────────────┬────────────┬────────────┐
     ▼            ▼            ▼            ▼
   BadNets      Blend         SIG         WaNet
                           │
                           ▼
                 STRIP Runtime Detection
                           │
                           ▼
                 Fine-Tuning Defense
                           │
                           ▼
               Benchmark Generation
                           │
                           ▼
      CSV • JSON • Excel • Markdown • Figures
```

---

## 🆚 Improvements Over a Conventional TSR Pipeline

| Conventional TSR | BTSecBench_v2 |
|---|---|
| Focuses only on classification accuracy | Evaluates both accuracy and security |
| Single CNN model | Four CNN architectures compared |
| No attack evaluation | Four representative backdoor attacks implemented |
| No runtime detection | STRIP-based detection integrated |
| No defense mechanism | Fine-Tuning defense implemented |
| Manual evaluation | Automated benchmark generation |
| Limited reporting | CSV, JSON, Excel, Markdown, and visualization outputs |

---

## 📂 Project Structure

```text
BTSecBench_v2/
│
├── analysis/            # Benchmark generation and analysis
├── attacks/             # Backdoor attack implementations
├── checkpoints/         # Saved trained models
├── configs/             # Configuration files
├── dashboard/           # Dashboard/UI components
├── data/                # Dataset storage
├── defenses/            # STRIP and Fine-Tuning
├── docs/                # Documentation
├── engine/              # Training and inference engine
├── evaluation/          # Evaluation scripts
├── explainability/      # Explainability modules
├── models/              # Deep learning architectures
├── notebooks/           # Jupyter notebooks
├── output/              # Generated outputs
├── reports/
│   ├── csv/
│   ├── figures/
│   ├── json/
│   └── pdf/
├── scripts/             # Utility scripts
├── tests/               # Testing modules
├── tools/               # Helper tools
├── tracking/            # Experiment tracking
├── utils/               # Common utilities
├── visualization/       # Plot generation
├── app.py               # Streamlit application
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 📊 Dataset

**Dataset:** German Traffic Sign Recognition Benchmark (GTSRB)

### Features

- 43 traffic sign classes
- Real-world traffic sign images
- Different viewpoints
- Different lighting conditions
- Multiple backgrounds
- Variable image sizes

### Preprocessing

- Image resize (224×224)
- Normalization
- Data augmentation
- Train / validation / test split

---

## 🤖 Deep Learning Models

| Model | Purpose |
|--------|----------|
| Baseline CNN | Initial performance benchmark |
| ResNet18 | Residual learning comparison |
| MobileNetV3 | Lightweight model comparison |
| ⭐ EfficientNet-B0 | Final selected backbone |

### Why EfficientNet-B0?

- Highest classification accuracy
- Excellent feature extraction
- Fewer parameters
- Better generalization
- Computationally efficient

---

## ⚔ Implemented Backdoor Attacks

These attacks represent different trigger strategies, ranging from visible patches to highly stealthy geometric transformations.

### ✅ BadNets
- Visible trigger patch
- High Attack Success Rate
- Simple implementation

### ✅ Blend Attack
- Transparent trigger
- Improved stealth
- Harder to detect

### ✅ SIG Attack
- Global sinusoidal trigger
- Hidden perturbation
- High stealth

### ✅ WaNet
- Geometric warping
- Nearly invisible trigger
- Advanced attack strategy

---

## 🔍 Runtime Detection — STRIP

The project integrates **STRIP (STRong Intentional Perturbation)** for runtime backdoor detection.

```text
Input Image
      │
      ▼
Generate Perturbations
      │
      ▼
Multiple Predictions
      │
      ▼
Entropy Calculation
      │
      ▼
Threshold Comparison
      │
      ▼
Clean / Suspicious
```

---

## 🛡 Defense Mechanism — Fine-Tuning

Fine-Tuning is used to recover compromised models.

```text
Compromised Model
      │
      ▼
Load Clean Dataset
      │
      ▼
Fine-Tune Model
      │
      ▼
Recovered Model
      │
      ▼
Performance Evaluation
```

---

## 📈 Evaluation Metrics

### Classification Metrics
- Accuracy
- Precision
- Recall
- F1-Score
- Balanced Accuracy
- Matthews Correlation Coefficient (MCC)

### Security Metrics
- Attack Success Rate (ASR)
- STRIP Detection Accuracy
- ROC-AUC

---

## 📊 Generated Outputs

The framework automatically generates:

**Reports**
- CSV
- JSON
- Excel
- Markdown

**Figures**
- Accuracy comparison
- Attack Success Rate comparison
- STRIP metrics
- Benchmark summary
- ROC curve
- Confusion matrix
- Entropy distribution

---

## 🚀 Installation

**Clone the repository**

```bash
git clone https://github.com/<YOUR_USERNAME>/BTSecBench_v2.git
cd BTSecBench_v2
```

**Create environment**

```bash
conda create -n btsecbench python=3.10
conda activate btsecbench
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

**Train model**
```bash
python train.py
```

**Run backdoor attack**
```bash
python attacks/badnets.py
```

**Run STRIP detection**
```bash
python defenses/strip.py
```

**Run Fine-Tuning defense**
```bash
python defenses/fine_tuning.py
```

**Generate benchmark**
```bash
python benchmark.py
```
or
```bash
python -m analysis.final_benchmark
```

**Generate visualizations**
```bash
python -m analysis.generate_plots
```

---

## 📈 Results

The project successfully:

- ✅ Compared four deep learning models.
- ✅ Selected EfficientNet-B0 as the optimal backbone.
- ✅ Implemented four representative backdoor attacks.
- ✅ Evaluated Attack Success Rate (ASR).
- ✅ Detected poisoned inputs using STRIP.
- ✅ Recovered the compromised model using Fine-Tuning.
- ✅ Generated automated benchmark reports and visualizations.

---

## 💻 Technologies Used

- Python
- PyTorch
- TorchVision
- OpenCV
- NumPy
- Pandas
- Matplotlib
- Scikit-learn
- Streamlit
- Jupyter Notebook

---

## 📚 Applications

- Autonomous Driving
- Advanced Driver Assistance Systems (ADAS)
- Traffic Sign Recognition
- Adversarial Machine Learning
- AI Security
- Cybersecurity Research
- Benchmark Framework Development

---

## 🔮 Future Work

- Neural Attention Distillation (NAD)
- Neural Cleanse
- Fine-Pruning
- Vision Transformers (ViTs)
- Physical Trigger Attacks
- Adaptive STRIP
- Real-Time Edge AI Deployment
- Multi-Dataset Benchmarking

---

## 👨‍💻 Author

**Purnachandar Vallala**

Master of Science in Data Science

Germany

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgements

- German Traffic Sign Recognition Benchmark (GTSRB)
- PyTorch
- TorchVision
- OpenCV
- Scikit-learn
- EfficientNet Authors
- STRIP Authors
- BadNets Authors

---

### ⭐ If you found this project useful, please consider giving it a Star.
