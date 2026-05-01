import os
import sys
import json
import pickle
import warnings
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

warnings.filterwarnings('ignore')

DATA_PATH = Path(__file__).parent.parent
MODELS_PATH = DATA_PATH / "models"
MODELS_PATH.mkdir(exist_ok=True)

def load_and_merge():
    train_path = DATA_PATH / 'data' / 'train.csv'
    stores_path = DATA_PATH / 'data' / 'stores.csv'
    features_path = DATA_PATH / 'data' / 'features.csv'
    
    train_data = pd.read_csv(train_path)
    stores_data = pd.read_csv(stores_path)
    features_data = pd.read_csv(features_path)
    
    train_data['Date'] = pd.to_datetime(train_data['Date'])
    features_data['Date'] = pd.to_datetime(features_data['Date'])
    
    full_data = train_data.merge(features_data, on=['Store', 'Date'], how='left', suffixes=('_train', '_features'))
    full_data = full_data.merge(stores_data, on='Store', how='left')
    
    if 'IsHoliday_train' in full_data.columns:
        full_data['IsHoliday'] = full_data['IsHoliday_train']
        full_data = full_data.drop(columns=['IsHoliday_train', 'IsHoliday_features'], errors='ignore')
    
    full_data['Weekly_Sales'] = pd.to_numeric(full_data['Weekly_Sales'], errors='coerce')
    full_data = full_data.dropna(subset=['Weekly_Sales'])
    
    return full_data.sort_values('Date').reset_index(drop=True)

def feature_engineering(df):
    data = df.copy()
    data['Year'] = data['Date'].dt.year
    data['Month'] = data['Date'].dt.month
    data['Week'] = data['Date'].dt.isocalendar().week
    data['DayOfWeek'] = data['Date'].dt.dayofweek
    
    data = data.sort_values(['Store', 'Dept', 'Date']).reset_index(drop=True)
    
    for lag in [1, 4, 12, 26, 52]:
        data[f'Sales_Lag_{lag}'] = data.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(lag)
        
    for window in [4, 12, 26]:
        data[f'Sales_MA_{window}'] = data.groupby(['Store', 'Dept'])['Weekly_Sales'].transform(lambda x: x.rolling(window=window, min_periods=1).mean())
        
    data['Sales_EMA_12'] = data.groupby(['Store', 'Dept'])['Weekly_Sales'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
    
    data = data.fillna(data.mean(numeric_only=True))
    
    feature_cols = [
        'Store', 'Dept', 'Type', 'Size',
        'Temperature', 'Fuel_Price', 'CPI', 'Unemployment', 'IsHoliday',
        'Year', 'Month', 'Week', 'DayOfWeek',
        'Sales_Lag_1', 'Sales_Lag_4', 'Sales_Lag_12', 'Sales_Lag_26', 'Sales_Lag_52',
        'Sales_MA_4', 'Sales_MA_12', 'Sales_MA_26',
        'Sales_EMA_12'
    ]
    
    X = data[feature_cols].copy()
    y = data['Weekly_Sales'].copy()
    
    if 'Type' in X.columns:
        X['Type'] = pd.Categorical(X['Type']).codes
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    return X_scaled, y, scaler

def train_and_save(X, y, scaler):
    params = {
        'n_estimators': 200,
        'learning_rate': 0.1,
        'max_depth': 6,
        'random_state': 42,
        'n_jobs': -1
    }
    
    print("Training XGBoost Model...")
    model = xgb.XGBRegressor(**params)
    model.fit(X, y)
    
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    print(f"Model R2 Score: {r2:.4f}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    model_path = MODELS_PATH / "demand_model.pkl"
    scaler_path = MODELS_PATH / "model_scaler.pkl"
    meta_path = MODELS_PATH / "model_metadata.json"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    metadata = {
        'timestamp': timestamp,
        'r2_score': r2,
        'features': list(X.columns)
    }
    
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print("Model and Scaler Saved!")

def main():
    print("Starting Model Training Pipeline...")
    data = load_and_merge()
    X, y, scaler = feature_engineering(data)
    train_and_save(X, y, scaler)
    print("Training Finished Successfully!")

if __name__ == "__main__":
    main()
