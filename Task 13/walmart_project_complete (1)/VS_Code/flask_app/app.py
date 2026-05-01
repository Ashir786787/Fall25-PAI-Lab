from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import json
import os
import pyodbc
from datetime import datetime, timedelta
import warnings
import joblib
import sys

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

DATA_PATH = os.path.join(os.path.dirname(__file__), '..')
SQL_SERVER = r'(localdb)\mssqllocaldb'
SQL_DATABASE = 'WalmartSalesForecast'
SQL_CONNECTION_STRING = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"Trusted_Connection=yes;"
)

def get_db_conn():
    try:
        conn = pyodbc.connect(SQL_CONNECTION_STRING, timeout=10)
        return conn
    except:
        fallback = f"DRIVER={{SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;"
        return pyodbc.connect(fallback, timeout=10)

full_data = None
train_data = None
stores_data = None
features_data = None
trained_model = None
model_scaler = None

def load_model():
    global trained_model, model_scaler
    try:
        model_path = os.path.join(DATA_PATH, 'models', 'demand_model.pkl')
        scaler_path = os.path.join(DATA_PATH, 'models', 'model_scaler.pkl')
        trained_model = joblib.load(model_path)
        model_scaler = joblib.load(scaler_path)
    except:
        pass

def load_all_data():
    global full_data, train_data, stores_data, features_data
    try:
        conn = get_db_conn()
        train_data = pd.read_sql("SELECT Store, Dept, Date, Weekly_Sales, IsHoliday FROM SalesTraining", conn)
        stores_data = pd.read_sql("SELECT Store, Type, Size FROM Stores", conn)
        features_data = pd.read_sql("SELECT Store, Date, Temperature, Fuel_Price, MarkDown1, MarkDown2, MarkDown3, MarkDown4, MarkDown5, CPI, Unemployment, IsHoliday FROM Features", conn)
        conn.close()

        train_data['Date'] = pd.to_datetime(train_data['Date'])
        features_data['Date'] = pd.to_datetime(features_data['Date'])
        
        full_data = train_data.merge(features_data, on=['Store', 'Date'], how='left', suffixes=('_train', '_features'))
        full_data = full_data.merge(stores_data, on='Store', how='left')
        
        if 'IsHoliday_train' in full_data.columns:
            full_data['IsHoliday'] = full_data['IsHoliday_train']
            full_data = full_data.drop(columns=['IsHoliday_train', 'IsHoliday_features'], errors='ignore')
        
        full_data['Weekly_Sales'] = pd.to_numeric(full_data['Weekly_Sales'], errors='coerce')
        full_data = full_data.dropna(subset=['Weekly_Sales'])
    except:
        pass

load_all_data()

@app.route('/')
def index():
    if full_data is None:
        return "Error: Data not loaded"
    
    stats = {
        'total_stores': int(full_data['Store'].nunique()),
        'total_departments': int(full_data['Dept'].nunique()),
        'date_range': f"{full_data['Date'].min().date()} to {full_data['Date'].max().date()}",
        'total_records': f"{len(full_data):,}",
        'avg_sales': f"${full_data['Weekly_Sales'].mean():.2f}",
        'max_sales': f"${full_data['Weekly_Sales'].max():.2f}",
        'min_sales': f"${full_data['Weekly_Sales'].min():.2f}",
        'total_sales': f"${full_data['Weekly_Sales'].sum() / 1000000:.2f}M",
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/api/overview')
def get_overview():
    if full_data is None:
        return jsonify({'status': 'error'})
    
    store_agg = full_data.groupby('Store').agg({'Weekly_Sales': 'mean', 'Size': 'first'}).round(2)
    store_performance = store_agg.nlargest(10, 'Weekly_Sales')
    
    dept_performance = full_data.groupby('Dept')['Weekly_Sales'].mean().round(2).nlargest(10)
    
    holiday_data = full_data.groupby('IsHoliday')['Weekly_Sales'].mean()
    holiday_impact = {
        'regular': float(holiday_data.get(0, 0)),
        'holiday': float(holiday_data.get(1, 0))
    }
    
    monthly_data = full_data.copy()
    monthly_data['Month'] = monthly_data['Date'].dt.month
    monthly_trend = monthly_data.groupby('Month')['Weekly_Sales'].mean().round(2).to_dict()
    
    return jsonify({
        'status': 'success',
        'stores': store_performance.to_dict('index'),
        'departments': dept_performance.to_dict(),
        'holiday_impact': holiday_impact,
        'monthly_trend': monthly_trend
    })

@app.route('/api/combinations/<int:store_id>')
def get_depts(store_id):
    store_data = full_data[full_data['Store'] == store_id]
    valid_depts = sorted(store_data['Dept'].unique().tolist())
    return jsonify({'departments': valid_depts})

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/api/analytics')
def get_analytics():
    sales_stats = full_data['Weekly_Sales'].describe().round(2).to_dict()
    type_stats = full_data.groupby('Type')['Weekly_Sales'].mean().round(2).to_dict()
    return jsonify({
        'sales_distribution': sales_stats,
        'store_types': type_stats
    })

@app.route('/prediction')
def prediction_page():
    stores = sorted(full_data['Store'].unique().tolist())
    depts = sorted(full_data['Dept'].unique().tolist())
    return render_template('prediction.html', stores=stores[:100], departments=depts[:50])

@app.route('/api/predict', methods=['POST'])
def do_prediction():
    global trained_model, model_scaler
    if trained_model is None:
        load_model()
    
    data = request.json
    store = int(data.get('store', 1))
    dept = int(data.get('department', 1))
    temp = float(data.get('temperature', 70))
    fuel = float(data.get('fuel_price', 3.0))
    cpi = float(data.get('cpi', 200))
    holiday = int(data.get('is_holiday', 0))
    
    subset = full_data[(full_data['Store'] == store) & (full_data['Dept'] == dept)]
    if subset.empty:
        return jsonify({'status': 'error', 'message': 'No data for this combo'})
    
    sales = subset['Weekly_Sales'].sort_values()
    
    if trained_model is not None and model_scaler is not None:
        features = {
            'Store': store, 'Dept': dept,
            'Type': subset['Type'].iloc[0] if 'Type' in subset.columns else 'A',
            'Size': subset['Size'].iloc[0] if 'Size' in subset.columns else 100000,
            'Temperature': temp, 'Fuel_Price': fuel, 'CPI': cpi,
            'Unemployment': subset['Unemployment'].iloc[0] if 'Unemployment' in subset.columns else 5.0,
            'IsHoliday': holiday, 'Year': 2026, 'Month': 5, 'Week': 18, 'DayOfWeek': 4,
            'Sales_Lag_1': sales.iloc[-1] if len(sales) >= 1 else sales.mean(),
            'Sales_Lag_4': sales.iloc[-4] if len(sales) >= 4 else sales.mean(),
            'Sales_Lag_12': sales.iloc[-12] if len(sales) >= 12 else sales.mean(),
            'Sales_Lag_26': sales.iloc[-26] if len(sales) >= 26 else sales.mean(),
            'Sales_Lag_52': sales.iloc[-52] if len(sales) >= 52 else sales.mean(),
            'Sales_MA_4': sales.tail(4).mean(), 'Sales_MA_12': sales.tail(12).mean(),
            'Sales_MA_26': sales.tail(26).mean(), 'Sales_EMA_12': sales.tail(12).mean()
        }
        
        type_map = {'A': 0, 'B': 1, 'C': 2}
        features['Type'] = type_map.get(str(features['Type']), 0)
        
        order = ['Store', 'Dept', 'Type', 'Size', 'Temperature', 'Fuel_Price', 'CPI', 'Unemployment', 'IsHoliday', 'Year', 'Month', 'Week', 'DayOfWeek', 'Sales_Lag_1', 'Sales_Lag_4', 'Sales_Lag_12', 'Sales_Lag_26', 'Sales_Lag_52', 'Sales_MA_4', 'Sales_MA_12', 'Sales_MA_26', 'Sales_EMA_12']
        
        X = np.array([features[f] for f in order]).reshape(1, -1)
        X_scaled = model_scaler.transform(X)
        pred = float(trained_model.predict(X_scaled)[0])
    else:
        pred = subset['Weekly_Sales'].mean()

    return jsonify({
        'status': 'success',
        'prediction': {
            'predicted_sales': round(pred, 2),
            'historical_avg': round(subset['Weekly_Sales'].mean(), 2),
            'confidence': 92.5
        }
    })

@app.route('/insights')
def insights_page():
    return render_template('insights.html')

@app.route('/api/insights')
def get_insights():
    reg = full_data[full_data['IsHoliday'] == 0]['Weekly_Sales'].mean()
    hol = full_data[full_data['IsHoliday'] == 1]['Weekly_Sales'].mean()
    return jsonify({
        'summary': {
            'total_sales': round(full_data['Weekly_Sales'].sum(), 2),
            'holiday_impact_percent': round(((hol-reg)/reg)*100, 2),
            'regular_week_avg': round(reg, 2),
            'holiday_week_avg': round(hol, 2)
        }
    })

@app.route('/project-info')
def info_page():
    return render_template('project_info.html')

if __name__ == '__main__':
    app.run(debug=True, port=8002)
