# WALMART SALES FORECASTING PROJECT
## Setup and Execution Guide

### Project Structure

```
walmart_project_files/
│
├── walmart_database_SSMS.sql      
│
└── VS_Code/
    ├── data_pipeline.py           
    ├── train_models.py
    └── flask_app/
        └── app.py
```

### Step 1: Database Setup

1. Open SQL Server Management Studio (SSMS).
2. Connect to your local server.
3. Open and execute `walmart_database_SSMS.sql`.
4. This will create the `WalmartSalesForecast` database and all necessary tables, views, and procedures.

### Step 2: Python Environment Setup

Install the required packages:

```bash
pip install flask pandas numpy scikit-learn joblib xgboost pyodbc
```

### Step 3: Run ETL Pipeline

1. Open `data_pipeline.py`.
2. Update the `SQL_SERVER` variable if necessary.
3. Run the script:
   ```bash
   python data_pipeline.py
   ```

### Step 4: Train Machine Learning Model

Run the training script to generate the model files:
```bash
python train_models.py
```

### Step 5: Run Web Application

```bash
cd flask_app
python app.py
```
Open your browser at: **http://localhost:5000**

### Database Schema

- **Stores**: Store ID, Type, Size
- **Features**: Environmental factors like Temperature, Fuel Price, CPI.
- **SalesTraining**: Historical weekly sales data.
- **ModelPredictions**: Log of all predictions made by the system.
- **PipelineLog**: History of ETL pipeline executions.

### Project Features

- Complete ETL Pipeline from CSV to SQL Server.
- Advanced Feature Engineering (Lag features, rolling averages).
- Machine Learning models (XGBoost) for sales prediction.
- Interactive Flask Web Dashboard for visualization.
