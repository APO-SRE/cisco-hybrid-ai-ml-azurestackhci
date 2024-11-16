# Creating the Custom Azure Machine Learning Environment

This document provides instructions on how to create a custom Azure Machine Learning environment using the provided YAML files. This environment includes MLflow and Azure ML libraries tailored for Cisco's requirements.

## Prerequisites

- **Azure CLI** installed on your machine.
- **Azure Machine Learning CLI extension** installed:
  ```bash
  az extension add -n ml
  ```
- **Access permissions** to the Azure resource group `AI-Expert-Advisor-East-US2-RG` and the Azure Machine Learning workspace `Cisco-Machine-Learning`.

## Files in This Directory

- **`cisco-mfolw-azureml-env.yml`**: The main environment definition file.
- **`conda-env-cisco-mlflow-azureml.yml`**: The Conda environment file specifying dependencies.

### Contents of `cisco-mfolw-azureml-env.yml`:

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/environment.schema.json
name: cisco-mlflow-azureml-env
version: 1
conda_file: conda-env-cisco-mlflow-azureml.yml
image: mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest
description: Custom environment for Cisco with MLflow and Azure ML libraries
```

### Contents of `conda-env-cisco-mlflow-azureml.yml`:

```yaml
name: conda-env-cisco-mlflow-azureml
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.9
  - conda-forge::ncurses
  - pip
  - pip:
      - numpy
      - pandas
      - scikit-learn
      - mlflow
      - azureml-core
      - azureml-defaults
      - azureml-mlflow
      - azureml-telemetry
      - azure-identity
      - azureml-dataprep
      - azureml-dataset-runtime
      - azureml-pipeline-core
      - azureml-pipeline-steps
      - azureml-train-core
      - azureml-train-automl-client
      - azureml-train-automl-runtime
      - azureml-train-restclients-hyperdrive
      - azureml-widgets
      - azure-storage-blob
      - azure-storage-file-share
      - azure-storage-file-datalake
      - azureml
      - requests
```

## Steps to Create the Custom Environment

### 1. Install Azure Machine Learning CLI Extension (If Not Already Installed)

Ensure that the Azure Machine Learning extension for Azure CLI is installed and up-to-date:

```bash
az extension add -n ml
az extension update -n ml
```

### 2. Log In to Azure

Authenticate with your Azure account:

```bash
az login
```

If you have multiple subscriptions, set the desired subscription:

```bash
az account set --subscription "Your Subscription Name or ID"
```

### 3. Create the Custom Environment

Run the following command in your terminal from the directory containing the YAML files:

```bash
az ml environment create --file cisco-mfolw-azureml-env.yml \
  --resource-group Cisco-UCS-RG \
  --workspace-name Cisco-Machine-Learning
```

- **Parameters**:
  - `--file`: Path to the environment definition YAML file (`cisco-mfolw-azureml-env.yml`).
  - `--resource-group`: Name of your Azure resource group.
  - `--workspace-name`: Name of your Azure Machine Learning workspace.

### 4. Verify the Environment Creation

To confirm that the environment has been created successfully, list the environments in your workspace:

```bash
az ml environment list \
  --resource-group Cisco-UCS-RG \
  --workspace-name Cisco-Machine-Learning
```

Look for `cisco-mlflow-azureml-env` in the output.

## Usage

- **Training Scripts**: Reference this custom environment in your training scripts or pipeline definitions to ensure consistency.
- **Deployment**: Use the same environment when deploying models to maintain compatibility between training and inference environments.

## Notes

- The environment uses the Docker base image: `mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest`.
- The Conda environment includes essential Python libraries such as `numpy`, `pandas`, `scikit-learn`, `mlflow`, and various Azure ML packages.

## Troubleshooting

- **Permission Errors**: Ensure you have the necessary permissions for the specified resource group and workspace.
- **Extension Issues**: If you encounter issues with the Azure ML CLI extension, try updating or reinstalling it.
  ```bash
  az extension update -n ml
  ```
- **Authentication Errors**: Make sure you're logged in to Azure CLI with the correct account.

## References

- [Azure Machine Learning Environments](https://learn.microsoft.com/azure/machine-learning/concept-environments)
- [Create and Manage Environments with Azure CLI](https://learn.microsoft.com/azure/machine-learning/how-to-manage-environments-cli)
- [Azure ML CLI Extension](https://learn.microsoft.com/azure/machine-learning/how-to-configure-cli)

