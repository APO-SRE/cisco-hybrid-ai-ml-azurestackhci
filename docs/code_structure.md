# Code Structure Documentation

This document provides an overview of the code structure in the repository, explaining the purpose of each directory and key files. It serves as a guide to help users understand how to navigate the codebase, set up the environment, and execute the training and scoring pipelines.

---

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Key Files and Scripts](#key-files-and-scripts)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
- [Running the Pipelines](#running-the-pipelines)
- [Dependencies and Requirements](#dependencies-and-requirements)
- [Best Practices](#best-practices)
- [Additional Resources](#additional-resources)

---

## Overview

The code in this repository is designed to facilitate the deployment of a hybrid AI/ML solution on Azure Stack HCI with Cisco UCS hardware. It primarily focuses on:

- **Training Pipeline**: Scripts and configurations for training machine learning models.
- **Scoring Pipeline**: Scripts for model inference and scoring.
- **Component Definitions**: Reusable components used in the pipelines.
- **Environment Definitions**: Specifications of the computational environments required for the pipelines.
- **Data Handling**: Scripts and configurations for data preprocessing and management.

---

## Directory Structure

Below is the hierarchical structure of the `code` directory and related scripts:

```

/code
├── config                               # Shared configurations
│   ├── feature-engineering.yml
│   ├── feature-replace-missing-values.yml
│   ├── feature-selection.yml
│   ├── split-data.yml
│   ├── train-model.yml
│   ├── register-model.yml
│   └── config.json
├── environment                          # Environment configurations
│   ├── cisco-mlflow-azureml-env.yml
│   ├── conda-env-cisco-mlflow-azureml.yml
│  
├── scripts                              # Shared Python scripts
│   ├── feature_engineering.py
│   ├── replace_missing_values.py
│   ├── feature_selection.py
│   ├── split_data.py
│   ├── train_model.py
│   └── register_model.py
├── deploy-train.py                      # Main script for training pipeline
│                     
├── deploy-score.py                      # Main script for scoring pipeline
│                  
├── data
|    ├── ChicagoParkingTickets1.csv      # raw data to be scored
|    ├── ChicagoParkingTickets2.csv
|
└── README.md                            # Project documentation


```

### `/code` Directory

## Key Files and Scripts

### Training Pipeline Scripts

- **`train_pipeline.py`**: The main script to initiate the training pipeline.
- **`score_pipeline.py`**: The main script to initiate the scoring pipeline.

### Component Definitions

- YAML files in the `config/` directories define the inputs, outputs, and configurations for each component.
  - **Example**: `feature-engineering.yml` defines how the feature engineering component is executed within the pipeline.

### Environment Definitions

- **Azure ML Environment Files**:
  - **`cisco-mlflow-azureml-env.yml`**: Defines the Azure ML environment with required packages.
- **Conda Environment Files**:
  - **`conda-env-cisco-mlflow-azureml.yml`**: Specifies the Conda environment dependencies.

---

## Setup and Installation

To set up the environment and prepare for running the pipelines, follow the steps in each of these sections:

1. **[Azure Stack HCI Install]**.(/deployments/hci_deployment_guide.md).
2. **[AKS Deployment Install]**.(/deployments/aks_deployment_guide.md).
3. **[Azure Machine Learning Deployment]**.(/deployments/ml_deployment_guide.md).


### Environment Setup

- Follow the Enviroment steps listed in the /enviroment/README.md file (/environment/README.md)

## Run Pipelines

- Follow the Running ML Workloads Guide to run Training and Scoring Pipelines. (/docs/running_ml_workloads_guide.md)

**Note**: For any questions or issues, please refer to the [Contributing](../README.md#contributing) section in the main `README.md` or open an issue in the repository.
