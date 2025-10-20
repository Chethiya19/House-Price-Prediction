# House Price Prediction Flask Application

This project is a web-based application built with Flask that predicts house prices using a trained Random Forest model. The project includes a script (`train_model.py`) for training the model and a Flask app for serving the predictions.

## Project Structure

- **`train_model.py`**: A script for training the Random Forest model. It handles data loading, preprocessing, model training, evaluation, and saving the model, scaler, and label encoders.
- **`app.py`**: The main Flask application file that handles routes and prediction logic.
- **`templates/index.html`**: The HTML template for the web interface where users input house features and view predictions.
- **`New_train.csv`**: The dataset used for training the model.
- **`random_forest_model.pkl`**: The trained Random Forest model saved as a pickle file.
- **`scaler.pkl`**: The `StandardScaler` object used to scale numerical features, also saved as a pickle file.
- **`label_encoders.pkl`**: A dictionary containing `LabelEncoder` objects for encoding categorical features.

## Prerequisites

- Python 3.x
- Flask
- pandas
- scikit-learn
- pickle

You can install the necessary dependencies using:

```bash
pip install Flask pandas scikit-learn

#Create a Virtual Environment
python -m venv venv

## Activate the Virtual Environment
.\venv\Scripts\activate


## Model is Alreadt Trauned. If want Train the Model
python train_model.py

#Running the Flask Application
python app.py

Open the Url -  http://127.0.0.1:5000 


This `README.md` file provides a comprehensive overview of the project, including instructions on how to train the model, run the Flask application, and use the web interface to predict house prices.
