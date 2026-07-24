\# BTSecBench\_v2

\## A Comprehensive Benchmark Framework for Backdoor Attack Detection and Defense in Traffic Sign Recognition



!\[Python](https://img.shields.io/badge/Python-3.10-blue)

!\[PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)

!\[License](https://img.shields.io/badge/License-MIT-green)

!\[Status](https://img.shields.io/badge/Status-Completed-success)



\---



\# Project Overview



BTSecBench\_v2 is a comprehensive benchmark framework developed to evaluate the robustness of Deep Learning based Traffic Sign Recognition (TSR) systems against Backdoor Attacks.



Unlike traditional image classification projects that only measure classification accuracy, BTSecBench\_v2 provides a complete security evaluation pipeline including:



\- Deep Learning Model Comparison

\- Backdoor Attack Implementation

\- Runtime Detection

\- Defense Mechanisms

\- Automated Benchmark Generation

\- Visualization

\- Performance Reporting



The framework is designed for reproducible research in AI Security and Adversarial Machine Learning.



\---



\# Objectives



The main objectives of this project are:



\- Develop a high-performance Traffic Sign Recognition model.

\- Compare multiple CNN architectures.

\- Implement multiple Backdoor Attacks.

\- Detect poisoned inputs using STRIP.

\- Recover compromised models using Fine-Tuning.

\- Generate automated benchmark reports.

\- Provide reproducible experiments for AI security research.



\---



\# Features



\## Deep Learning Models



✔ Baseline CNN



✔ ResNet18



✔ MobileNetV3



✔ EfficientNet-B0



\---



\## Backdoor Attacks



Implemented attacks include:



\- BadNets

\- Blend Attack

\- SIG Attack

\- WaNet



\---



\## Detection



Implemented detection:



\- STRIP (STRong Intentional Perturbation)



\---



\## Defense



Implemented defense:



\- Fine-Tuning



\---



\## Benchmarking



Automatically generates:



\- CSV reports

\- JSON reports

\- Excel reports

\- Markdown reports

\- Performance Figures



\---



\# Project Workflow



```text

GTSRB Dataset





       ▼



Data Preprocessing






       ▼



Model Training






       ▼



Model Comparison






       ▼



EfficientNet-B0






       ▼



Backdoor Attack Generation






       ▼



BadNets

Blend

SIG

WaNet



&#x20;       │



&#x20;       ▼



STRIP Detection



&#x20;       │



&#x20;       ▼



Fine-Tuning Defense



&#x20;       │



&#x20;       ▼



Benchmark Generation



&#x20;       │



&#x20;       ▼



Reports

Figures

Metrics

```



\---



\# Project Structure



```text

BTSecBench\_v2/



│



├── analysis/

│

├── attacks/

│

├── configs/

│

├── data/

│

├── datasets/

│

├── defenses/

│

├── evaluation/

│

├── models/

│

├── reports/

│

├── trainer/

│

├── utils/

│

├── checkpoints/

│

├── app.py

│

├── benchmark.py

│

├── train.py

│

├── requirements.txt

│

└── README.md

```



\---



\# Dataset



Dataset Used:



German Traffic Sign Recognition Benchmark (GTSRB)



Properties:



\- 43 Traffic Sign Classes

\- Real-world traffic images

\- Different lighting conditions

\- Multiple viewpoints

\- Multiple image sizes



Preprocessing:



\- Resize to 224×224

\- Image normalization

\- Data augmentation

\- Train/Validation/Test split



\---



\# Deep Learning Models



| Model | Purpose |

|---------|----------|

| Baseline CNN | Initial benchmark |

| ResNet18 | Residual learning |

| MobileNetV3 | Lightweight comparison |

| EfficientNet-B0 | Final selected model |



EfficientNet-B0 was selected due to its excellent trade-off between:



\- Accuracy

\- Speed

\- Parameters

\- Computational efficiency



\---



\# Implemented Backdoor Attacks



\## BadNets



\- Visible trigger patch

\- Simple implementation

\- High attack effectiveness



\---



\## Blend Attack



\- Transparent trigger

\- Improved stealth

\- Harder to detect



\---



\## SIG Attack



\- Sinusoidal trigger

\- Global perturbation

\- High stealth



\---



\## WaNet



\- Geometric warping

\- Nearly invisible trigger

\- Advanced attack



\---



\# Detection



Implemented:



\## STRIP



Detection Process:



\- Apply perturbations

\- Multiple predictions

\- Entropy computation

\- Threshold comparison

\- Clean / Suspicious decision



\---



\# Defense



Implemented:



\## Fine-Tuning



Defense Pipeline:



\- Load compromised model

\- Train using clean dataset

\- Reduce trigger influence

\- Preserve clean accuracy



\---



\# Evaluation Metrics



Classification



\- Accuracy

\- Precision

\- Recall

\- F1 Score

\- MCC



Security



\- Attack Success Rate (ASR)

\- Detection Accuracy

\- ROC-AUC



\---



\# Results



The framework successfully:



✔ Compared multiple CNN models



✔ Selected EfficientNet-B0



✔ Implemented four Backdoor Attacks



✔ Detected attacks using STRIP



✔ Defended model using Fine-Tuning



✔ Generated automated benchmark reports



\---



\# Generated Outputs



Reports:



\- CSV

\- JSON

\- Excel

\- Markdown



Figures:



\- Accuracy Comparison

\- Attack Success Rate Comparison

\- STRIP Metrics

\- Benchmark Summary

\- Confusion Matrix

\- ROC Curve



\---



\# Example Figures



```

reports/figures/



accuracy\_comparison.png



asr\_comparison.png



benchmark\_summary.png



strip\_metrics.png



strip\_confusion\_matrix.png



strip\_entropy\_distribution.png



strip\_roc\_curve.png

```



\---



\# Installation



Clone repository



```bash

git clone https://github.com/purnachandarvallala/BTSecBench\_v2.git



cd BTSecBench\_v2

```



Create environment



```bash

conda create -n btsecbench python=3.10



conda activate btsecbench

```



Install packages



```bash

pip install -r requirements.txt

```



\---



\# Training



Train model



```bash

python train.py

```



\---



\# Backdoor Attack



Example



```bash

python attacks/badnets.py

```



\---



\# STRIP Detection



```bash

python defenses/strip.py

```



\---



\# Fine-Tuning Defense



```bash

python defenses/fine\_tuning.py

```



\---



\# Generate Benchmark



```bash

python benchmark.py

```



or



```bash

python -m analysis.final\_benchmark

```



\---



\# Generate Figures



```bash

python -m analysis.generate\_plots

```



\---



\# Technologies Used



\- Python

\- PyTorch

\- TorchVision

\- NumPy

\- Pandas

\- Matplotlib

\- OpenCV

\- Scikit-Learn

\- Streamlit



\---



\# Applications



\- Autonomous Driving

\- Traffic Sign Recognition

\- AI Security

\- Adversarial Machine Learning

\- Cybersecurity Research

\- Benchmark Frameworks



\---



\# Future Improvements



\- Neural Attention Distillation (NAD)

\- Neural Cleanse

\- Fine-Pruning

\- Vision Transformers

\- Physical Trigger Attacks

\- Adaptive STRIP

\- Real-Time Deployment



\---



\# Author



Purnachandar Vallala



Master of Science



Data Science



Germany



\---



\# License



This project is released under the MIT License.



\---



\# Citation



If you use this project in your research, please cite:



```

Purnachandar Vallala



BTSecBench\_v2:

A Comprehensive Benchmark Framework for Backdoor Attack Detection and Defense in Traffic Sign Recognition.



2026\.

```



\---



\# Acknowledgements



\- German Traffic Sign Recognition Benchmark (GTSRB)

\- PyTorch

\- TorchVision

\- OpenCV

\- Scikit-Learn

\- EfficientNet Authors

\- STRIP Authors

\- BadNets Authors



\---



⭐ If you found this project useful, consider giving it a star.

