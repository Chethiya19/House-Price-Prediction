import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load the data
train_data = pd.read_csv('New_train.csv')
train_data = train_data[['MSSubClass', 'LotArea', 'HouseStyle', 'RoofStyle', 
                         'TotalBsmtSF', 'FullBath', 'BedroomAbvGr', 'GarageCars', 'SalePrice']]

# Encode categorical columns
label_encoders = {}
categorical_columns = ['MSSubClass', 'HouseStyle', 'RoofStyle']

for col in categorical_columns:
    le = LabelEncoder()
    train_data[col] = le.fit_transform(train_data[col])
    label_encoders[col] = le

# Features and target variable
X = train_data.drop('SalePrice', axis=1)
y = train_data['SalePrice']

# Scale numerical features
scaler = StandardScaler()
numeric_columns = ['LotArea', 'TotalBsmtSF', 'FullBath', 'BedroomAbvGr', 'GarageCars']
X[numeric_columns] = scaler.fit_transform(X[numeric_columns])

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R-squared (R²): {r2}")

# Save the model, scaler, and label encoders
with open('random_forest_model.pkl', 'wb') as file:
    pickle.dump(model, file)

with open('scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

with open('label_encoders.pkl', 'wb') as file:
    pickle.dump(label_encoders, file)

print("Model, scaler, and label encoders saved.")
