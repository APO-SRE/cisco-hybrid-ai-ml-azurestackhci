# Running Machine Learning Workloads Guide

This guide provides step-by-step instructions to execute the training and scoring scripts, monitor your jobs in Azure ML Workspace, and retrieve the results.

## Prerequisites

Before starting, ensure the following:
1. Azure infrastructure is set up and configured as per the setup documentation.
2. `config/config.json` is properly configured with your Azure subscription, resource group, and workspace details.

---

## 1. Preparing the Training Script (`deploy-train.py`)

Before running `deploy-train.py`, update the following parameters in the script:

- **Compute Target and Managed Identity**:
  ```python
  attach_name = "Cisco-k8s-dfault"  # Update with the registered compute target name
  managed_identity_client_id = "af6bcfce-fec2-4763-b40b-749f298b599b"  # Replace with your managed identity client ID
  ```

- **Pipeline Settings**:
  Update the node pool and environment for the pipeline job:
  ```python
  pipeline_job.settings.node_selector = {"nodepool": "largepool"}  # Ensure the correct node pool is selected
  pipeline_job.environment = "cisco-mlflow-azureml-env:1"  # Specify the correct environment name and version here
  ```

- **Instance Type in `train-model.yml`**:
  In `train-model.yml`, update the `instance_type` as follows:
  ```yaml
  resources:
    instance_type: standardinstancetype  # Update with the correct instance type
  ```

---

## 2. Running the Training Pipeline (`deploy-train.py`)

### Step 1: Execute `deploy-train.py`

Run the training script using the following command:

```bash
python deploy-train.py
```

This script:
- Initializes an Azure ML client and connects to your Azure Kubernetes Service (AKS) cluster.
- Loads and prepares the dataset for training.
- Executes a pipeline to perform data preprocessing, feature engineering, model training, and model registration in Azure ML.

### Step 2: Monitor the Training Job in Azure ML

1. Open the [Azure ML Workspace](https://ml.azure.com/).
2. Navigate to **Jobs** and locate the experiment named `machine-learning-cisco-ucs`.
3. View job details to monitor each pipeline step, including logs and output metrics.

After completion, the model will be registered in Azure ML under a unique name and version.

---

## 3. Updating the Scoring Script (`deploy-score.py`)

Once the model is registered, update `deploy-score.py` with the following:

- **Environment and Model Details**:
  ```python
  environment = ml_client.environments.get(name="cisco-mlflow-azureml-env", version="1")  # Update environment name and version
  model = ml_client.models.get(name="Recievable-Predictor-Cisco-AKS-on-UCS-ML", version="1")  # Update model name and version
  ```

- **Compute Target and Managed Identity**:
  Update these parameters as follows:
  ```python
  attach_name = "Cisco-k8s-dfault"  # Update with the registered compute target name
  managed_identity_client_id = "af6bcfce-fec2-4763-b40b-749f298b599b"  # Replace with your managed identity client ID
  ```

---

## 4. Running the Scoring Pipeline (`deploy-score.py`)

### Step 1: Execute `deploy-score.py`

Run the scoring script with the following command:

```bash
python deploy-score.py
```

This script:
- Connects to the batch scoring endpoint.
- Uses the specified model for batch inference on the input dataset.
- Saves the predictions to a CSV file.

### Step 2: Monitor the Scoring Job in Azure ML

1. In Azure ML Workspace, go to **Jobs** and locate the job started by `deploy-score.py`.
2. Check the job’s logs and status to verify successful completion.

### Step 3: Retrieve Results

Once the scoring job is complete, `deploy-score.py` will save the predictions to a local CSV file. Review the file to verify the prediction results.

---

## Additional Information

For troubleshooting:
- **Logs**: Access logs in Azure ML to check for error messages.
- **Permissions**: Ensure your account has access to the necessary Azure resources.

This guide provides a complete set of instructions to configure, execute, and monitor ML workloads on Azure ML using `deploy-train.py` and `deploy-score.py`. Contact your administrator or consult the setup documentation for further assistance.
```
 