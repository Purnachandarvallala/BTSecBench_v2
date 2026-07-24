# BTSecBench_v2 System Architecture

```mermaid
flowchart TB
    user["Researcher / CLI User"]
    notebooks["Experiment Notebooks<br/>01_dataset to 05_benchmark"]
    scripts["Scripts<br/>train.py, train_backdoor.py,<br/>test_attacks.py, benchmark_models.py"]
    config["Configuration<br/>configs/*.yaml, constants.py"]

    raw["Raw GTSRB Dataset<br/>data/raw/GTSRB"]
    metadata["Metadata, Cache, Splits, Statistics<br/>data/metadata.py, split.py,<br/>cache.py, statistics.py,<br/>data/splits/*.csv"]
    dataset["Dataset Layer<br/>GTSRBDataset"]
    transforms["Transform Pipeline<br/>train / val / test / strip"]
    loaders["DataLoader Factory<br/>create_dataset, create_dataloaders"]

    attack_factory["Attack Factory<br/>get_attack"]
    attacks["Backdoor Attacks<br/>BadNets, Blend, SIG, WaNet"]
    poisoned["PoisonedDataset Wrapper<br/>on-the-fly poisoning"]

    model_factory["Model Factory and Registry<br/>get_model, MODEL_REGISTRY"]
    backbones["Model Backbones<br/>CNN, ResNet18,<br/>MobileNetV3, EfficientNet-B0"]

    engine["Training Engine<br/>Trainer"]
    loss_sched["Optimization Components<br/>losses, schedulers, AMP,<br/>callbacks, early stopping"]
    evaluator["Evaluation Engine<br/>Evaluator and metrics"]
    checkpoints["Model Checkpoints<br/>best_model.pth, last_checkpoint.pth"]
    history["Training History<br/>reports/training_history.*"]

    attack_eval["Attack Evaluation<br/>attack success rate,<br/>robustness metrics"]
    strip["STRIP Defense<br/>entropy detector,<br/>threshold optimization"]
    finetune["Fine-Tuning Defense<br/>clean recovery training"]
    explain["Explainability<br/>Grad-CAM, Grad-CAM++,<br/>Integrated Gradients,<br/>Occlusion, Saliency"]

    tracking["Experiment Tracking<br/>MLflow, W&B"]
    reports["Reports and Artifacts<br/>JSON, CSV, XLSX, Markdown,<br/>figures, IEEE DOCX"]
    viz["Visualization Layer<br/>plots, heatmaps, radar,<br/>confusion matrices"]
    dashboard["Dashboard<br/>dashboard/app.py"]

    user --> scripts
    user --> notebooks
    scripts --> config
    notebooks --> config

    config --> metadata
    raw --> metadata
    metadata --> dataset
    dataset --> transforms
    transforms --> loaders

    scripts --> loaders
    notebooks --> loaders

    loaders --> engine
    loaders --> attack_eval
    loaders --> strip
    loaders --> finetune
    loaders --> explain

    attack_factory --> attacks
    attacks --> poisoned
    loaders --> poisoned
    poisoned --> engine
    poisoned --> attack_eval
    poisoned --> strip

    model_factory --> backbones
    scripts --> model_factory
    notebooks --> model_factory
    model_factory --> engine
    model_factory --> evaluator
    model_factory --> strip
    model_factory --> finetune
    model_factory --> explain

    engine --> loss_sched
    loss_sched --> engine
    engine --> evaluator
    evaluator --> engine
    engine --> checkpoints
    engine --> history
    checkpoints --> strip
    checkpoints --> finetune
    checkpoints --> attack_eval

    evaluator --> attack_eval
    attack_eval --> reports
    strip --> reports
    finetune --> reports
    explain --> reports
    history --> reports
    engine --> tracking
    evaluator --> tracking

    reports --> viz
    reports --> dashboard
    viz --> reports

    classDef input fill:#eef6ff,stroke:#3b82f6,color:#111827;
    classDef data fill:#ecfdf5,stroke:#10b981,color:#111827;
    classDef security fill:#fff7ed,stroke:#f97316,color:#111827;
    classDef model fill:#f5f3ff,stroke:#8b5cf6,color:#111827;
    classDef engine fill:#fef2f2,stroke:#ef4444,color:#111827;
    classDef output fill:#f8fafc,stroke:#64748b,color:#111827;

    class user,notebooks,scripts,config input;
    class raw,metadata,dataset,transforms,loaders data;
    class attack_factory,attacks,poisoned,attack_eval,strip,finetune security;
    class model_factory,backbones,explain model;
    class engine,loss_sched,evaluator,checkpoints,history engine;
    class tracking,reports,viz,dashboard output;
```

## Component Flow

1. Researchers run scripts or notebooks with settings from `configs/`.
2. The data layer prepares GTSRB metadata, split CSVs, transforms, datasets, and dataloaders.
3. The model layer selects a classifier backbone through the registry.
4. Clean or poisoned dataloaders feed the training engine, attack evaluator, defenses, and explainability modules.
5. The training engine coordinates loss, optimizer, scheduler, evaluator, checkpointing, early stopping, and history export.
6. Attack and defense workflows consume trained checkpoints and export benchmark evidence.
7. Reports, figures, tracking logs, and dashboard views present the results.

## Main Runtime Paths

| Path | Purpose |
| --- | --- |
| Clean training | `data/splits/*.csv` -> `GTSRBDataset` -> transforms -> dataloaders -> `get_model` -> `Trainer` -> `Evaluator` -> checkpoints and history |
| Backdoor training/evaluation | clean dataset -> `get_attack` -> `PoisonedDataset` -> model training or attack-success evaluation -> JSON/CSV/figures |
| STRIP detection | checkpoint -> clean validation bank + poisoned validation set -> entropy scores -> threshold optimization -> detection metrics |
| Fine-tuning defense | backdoored checkpoint -> clean dataloaders -> short clean retraining -> defended checkpoint -> validation report |
| Explainability | trained model + sample images -> saliency/Grad-CAM/occlusion/integrated gradients -> visual artifacts |

## Backdoor Attack Pipeline

![Backdoor Attack Pipeline](assets/backdoor_attack_pipeline_vertical.png)

```mermaid
flowchart TB
    start["Start Backdoor Experiment"]
    cfg["Load Experiment Settings<br/>attack name, target class,<br/>poison rate, model, batch size"]
    split["Load Split CSVs<br/>data/splits/train.csv<br/>data/splits/val.csv"]
    clean_ds["Create Clean Dataset<br/>GTSRBDataset"]
    transforms2["Apply Image Transforms<br/>train / val / test"]
    attack_factory2["Attack Factory<br/>get_attack"]
    attack_obj["Attack Object<br/>BadNets / Blend / SIG / WaNet"]
    poisoned_ds["PoisonedDataset<br/>wraps clean dataset"]
    decision{"Poison sample?"}
    trigger["Apply Trigger<br/>patch, blend, signal, or warp"]
    relabel["Relabel to Target Class"]
    keep_clean["Keep Clean Image and Label"]
    loaders2["Build DataLoaders"]
    model2["Build Model<br/>get_model"]
    train2["Train or Load Backdoored Model<br/>Trainer / checkpoint"]
    eval_clean["Evaluate Clean Accuracy"]
    eval_attack["Evaluate Triggered Inputs<br/>Attack Success Rate"]
    metrics2["Compute Metrics<br/>accuracy, precision, recall,<br/>F1, ASR"]
    artifacts2["Export Artifacts<br/>reports/json, reports/csv,<br/>reports/figures, checkpoints"]

    start --> cfg
    cfg --> split
    split --> clean_ds
    clean_ds --> transforms2
    transforms2 --> poisoned_ds
    cfg --> attack_factory2
    attack_factory2 --> attack_obj
    attack_obj --> poisoned_ds
    poisoned_ds --> decision
    decision -- yes --> trigger
    trigger --> relabel
    relabel --> loaders2
    decision -- no --> keep_clean
    keep_clean --> loaders2
    loaders2 --> model2
    model2 --> train2
    train2 --> eval_clean
    train2 --> eval_attack
    eval_clean --> metrics2
    eval_attack --> metrics2
    metrics2 --> artifacts2

    classDef setup fill:#eef6ff,stroke:#3b82f6,color:#111827;
    classDef data fill:#ecfdf5,stroke:#10b981,color:#111827;
    classDef attack fill:#fff7ed,stroke:#f97316,color:#111827;
    classDef model fill:#f5f3ff,stroke:#8b5cf6,color:#111827;
    classDef output fill:#f8fafc,stroke:#64748b,color:#111827;

    class start,cfg setup;
    class split,clean_ds,transforms2,poisoned_ds,loaders2 data;
    class attack_factory2,attack_obj,decision,trigger,relabel,keep_clean,eval_attack attack;
    class model2,train2,eval_clean model;
    class metrics2,artifacts2 output;
```

The backdoor pipeline starts from clean GTSRB split files, wraps the clean dataset with a selected attack, poisons a configurable portion of samples, trains or loads a model, then measures clean accuracy and attack success rate. The main implementation points are `attacks/attack_factory.py`, `attacks/base_attack.py`, `attacks/poisoned_dataset.py`, `data/dataloader.py`, `models/model_factory.py`, and the training/evaluation engine.

## STRIP Detection Workflow

![STRIP Detection Workflow](assets/strip_detection_workflow.svg)

```mermaid
flowchart TB
    start_strip["Start STRIP Evaluation"]
    args_strip["Load STRIP Settings<br/>model, checkpoint, attack,<br/>batch size, perturbations, alpha"]
    load_model_strip["Load Backdoored Model<br/>checkpoint -> get_model"]
    clean_val["Create Clean Validation Dataset<br/>data/splits/val.csv<br/>mode='strip'"]
    attack_strip["Create Attack<br/>get_attack"]
    poison_val["Create Poisoned Validation Set<br/>PoisonedDataset poison_all=True"]
    bank["Sample Clean Reference Bank<br/>up to 1000 clean images"]
    clean_loader_strip["Clean DataLoader"]
    poison_loader_strip["Poison DataLoader"]

    image_loop["For Each Candidate Image"]
    perturb["Generate Perturbations<br/>blend with random clean-bank images"]
    normalize["Normalize Perturbed Images"]
    predict["Run Model Prediction<br/>softmax probabilities"]
    entropy["Compute Shannon Entropy<br/>lower entropy = suspicious"]
    collect["Collect Clean and Poison Scores"]

    threshold["Optimize Threshold<br/>maximize F1 over entropy scores"]
    classify["Classify Inputs<br/>score < threshold => poisoned"]
    metrics_strip["Compute Detection Metrics<br/>accuracy, precision, recall,<br/>F1, FPR, FNR, AUC,<br/>confusion matrix"]
    export_strip["Export STRIP Results<br/>reports/json/strip_results.json<br/>reports/csv and figures"]

    start_strip --> args_strip
    args_strip --> load_model_strip
    args_strip --> clean_val
    clean_val --> attack_strip
    attack_strip --> poison_val
    clean_val --> bank
    clean_val --> clean_loader_strip
    poison_val --> poison_loader_strip
    clean_loader_strip --> image_loop
    poison_loader_strip --> image_loop
    bank --> perturb
    image_loop --> perturb
    perturb --> normalize
    normalize --> predict
    load_model_strip --> predict
    predict --> entropy
    entropy --> collect
    collect --> threshold
    threshold --> classify
    classify --> metrics_strip
    metrics_strip --> export_strip

    classDef setup fill:#eef6ff,stroke:#3b82f6,color:#111827;
    classDef data fill:#ecfdf5,stroke:#10b981,color:#111827;
    classDef detect fill:#fff7ed,stroke:#f97316,color:#111827;
    classDef model fill:#f5f3ff,stroke:#8b5cf6,color:#111827;
    classDef output fill:#f8fafc,stroke:#64748b,color:#111827;

    class start_strip,args_strip setup;
    class clean_val,poison_val,bank,clean_loader_strip,poison_loader_strip data;
    class load_model_strip,predict model;
    class attack_strip,image_loop,perturb,normalize,entropy,collect,threshold,classify detect;
    class metrics_strip,export_strip output;
```

STRIP detects potential backdoor inputs by checking prediction stability under random image blending. Clean samples should usually become less stable under perturbation, while triggered samples may keep a consistent target prediction. In this project, the workflow is implemented mainly in `defenses/strip.py` and exports detection results under `reports/`.

## Fine-Tuning Defense Workflow

![Fine-Tuning Defense Workflow](assets/fine_tuning_defense_workflow_vertical.png)

The fine-tuning defense loads a backdoored checkpoint, rebuilds the selected model, trains it for a short recovery phase on clean train/validation data, saves a defended checkpoint, evaluates clean validation performance, and exports JSON/CSV evidence under `reports/fine_tuning/`. The main implementation is `defenses/fine_tuning.py`.

## Correctly Classified Examples

![Correctly Classified Examples](assets/correctly_classified_examples.png)

This figure shows representative GTSRB validation samples formatted as clean examples with matching true/predicted labels for report presentation.

## Trigger Pattern Examples

![Trigger Pattern Examples](assets/trigger_pattern_examples.png)

This figure shows real validation samples after applying the project-style BadNets, Blend, SIG, and WaNet trigger patterns.
