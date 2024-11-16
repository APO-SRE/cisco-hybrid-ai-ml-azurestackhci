import os
import pandas as pd
import mlflow
from mlflow.exceptions import MlflowException

def init():
    global model
    try:
        print('Initializing model loading...')
        
        # Azure ML sets the AZUREML_MODEL_DIR environment variable to point to the downloaded model directory.
        model_dir = os.environ.get('AZUREML_MODEL_DIR', None)
        if model_dir is None:
            raise ValueError("AZUREML_MODEL_DIR environment variable is not set.")
        
        print(f"Model directory from environment variable: {model_dir}")

        # Construct the model path for MLflow
        model_path = os.path.join(model_dir, 'trained_models')  # Path inside the AZUREML_MODEL_DIR
        mlmodel_file_path = os.path.join(model_path, "MLmodel")

        # Check if the MLmodel configuration file exists
        if not os.path.exists(mlmodel_file_path):
            raise FileNotFoundError(f"MLmodel file not found at: {mlmodel_file_path}")
        
        # Load the model using MLflow
        model = mlflow.pyfunc.load_model(model_path)
        print(f"Model loaded successfully from: {model_path}")
    except MlflowException as e:
        print(f"MlflowException while loading model: {str(e)}")
        raise
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def run(mini_batch):
    print(f"run method start: {__file__}, run({len(mini_batch)} files)")
    try:
        # Log the paths of the files in the mini_batch
        print(f"Files in mini_batch: {mini_batch}")
        
        # Load the data from the mini_batch and print a preview
        data_frames = []
        for fp in mini_batch:
            print(f"Preview of file {fp}:")
            df = pd.read_csv(fp)
            print(df.head())
            data_frames.append(df)

        # Concatenate all data frames
        data = pd.concat(data_frames)
        print(f"Loaded data shape: {data.shape}, Columns: {data.columns}")

        # Preprocess data if necessary
        # Example: data = preprocess(data)

        # Make predictions using the loaded model
        pred = model.predict(data)
        print(f"Prediction completed. Predictions: {pred}")

        # Prepare the result by adding the predictions to the input data
        result = data.copy()
        result['PaymentIsOutstanding'] = pred
        return result
    except Exception as e:
        print(f"Error during batch prediction: {str(e)}")
        raise
