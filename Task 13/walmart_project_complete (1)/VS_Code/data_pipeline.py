import os, sys, time
import pandas as pd
import numpy as np
import pyodbc
from datetime import datetime
from pathlib import Path

DATA_PATH = r".\data"
SQL_SERVER   = "(localdb)\\mssqllocaldb"
SQL_DATABASE = "WalmartSalesForecast"
BATCH_SIZE = 2000

def get_conn():
    drivers = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "SQL Server",
    ]
    for drv in drivers:
        try:
            conn = pyodbc.connect(
                f"Driver={{{drv}}};"
                f"Server={SQL_SERVER};"
                f"Database={SQL_DATABASE};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;",
                timeout=15,
            )
            return conn
        except:
            pass
    return None

def extract():
    base = Path(DATA_PATH)
    files = {
        "stores":   "stores.csv",
        "features": "features.csv",
        "train":    "train.csv",
        "test":     "test.csv",
    }

    data = {}
    for name, fname in files.items():
        path = base / fname
        if not path.exists():
            continue
        df = pd.read_csv(path, low_memory=False)
        data[name] = df
    return data

def transform(raw):
    cleaned = {}

    if "stores" in raw:
        df = raw["stores"].copy()
        df.columns = df.columns.str.strip()
        df["Store"] = pd.to_numeric(df["Store"], errors="coerce").astype("Int64")
        df["Size"]  = pd.to_numeric(df["Size"],  errors="coerce").astype("Int64")
        df["Type"]  = df["Type"].astype(str).str.strip().str.upper()
        df = df.dropna(subset=["Store"]).drop_duplicates(subset=["Store"])
        cleaned["stores"] = df

    if "features" in raw:
        df = raw["features"].copy()
        df.columns = df.columns.str.strip()
        df["IsHoliday"] = df["IsHoliday"].map(
            {True:1, False:0, "TRUE":1, "FALSE":0,
             "True":1, "False":0, 1:1, 0:0}
        ).fillna(0).astype(int)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Store", "Date"])
        for col in ["MarkDown1","MarkDown2","MarkDown3","MarkDown4","MarkDown5"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in ["Temperature","Fuel_Price","CPI","Unemployment"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = df[col].fillna(df[col].median())
        df["Store"] = df["Store"].astype(int)
        df = df.drop_duplicates(subset=["Store","Date"])
        cleaned["features"] = df

    if "train" in raw:
        df = raw["train"].copy()
        df.columns = df.columns.str.strip()
        df["IsHoliday"] = df["IsHoliday"].map(
            {True:1, False:0, "TRUE":1, "FALSE":0,
             "True":1, "False":0, 1:1, 0:0}
        ).fillna(0).astype(int)
        df["Date"]         = pd.to_datetime(df["Date"], errors="coerce")
        df["Weekly_Sales"] = pd.to_numeric(df["Weekly_Sales"], errors="coerce")
        df["Store"]        = pd.to_numeric(df["Store"], errors="coerce")
        df["Dept"]         = pd.to_numeric(df["Dept"],  errors="coerce")
        df["Weekly_Sales"] = df["Weekly_Sales"].clip(lower=0)
        df = df.dropna(subset=["Store","Dept","Date","Weekly_Sales"])
        df["Store"] = df["Store"].astype(int)
        df["Dept"]  = df["Dept"].astype(int)
        cleaned["train"] = df

    if "test" in raw:
        df = raw["test"].copy()
        df.columns = df.columns.str.strip()
        df["IsHoliday"] = df["IsHoliday"].map(
            {True:1, False:0, "TRUE":1, "FALSE":0,
             "True":1, "False":0, 1:1, 0:0}
        ).fillna(0).astype(int)
        df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")
        df["Store"] = pd.to_numeric(df["Store"], errors="coerce")
        df["Dept"]  = pd.to_numeric(df["Dept"],  errors="coerce")
        df = df.dropna(subset=["Store","Dept","Date"])
        df["Store"] = df["Store"].astype(int)
        df["Dept"]  = df["Dept"].astype(int)
        cleaned["test"] = df

    return cleaned

TABLE_CONFIG = {
    "stores": {
        "sql_table": "Stores",
        "cols":      ["Store","Type","Size"],
    },
    "features": {
        "sql_table": "Features",
        "cols":      ["Store","Date","Temperature","Fuel_Price",
                      "MarkDown1","MarkDown2","MarkDown3","MarkDown4","MarkDown5",
                      "CPI","Unemployment","IsHoliday"],
    },
    "train": {
        "sql_table": "SalesTraining",
        "cols":      ["Store","Dept","Date","Weekly_Sales","IsHoliday"],
    },
    "test": {
        "sql_table": "SalesTest",
        "cols":      ["Store","Dept","Date","IsHoliday"],
    },
}

def load(cleaned, conn):
    cursor = conn.cursor()
    cursor.fast_executemany = True
    stats  = {}
    load_order = ["stores", "features", "train", "test"]

    for key in load_order:
        if key not in cleaned:
            continue

        cfg        = TABLE_CONFIG[key]
        table      = cfg["sql_table"]
        cols       = [c for c in cfg["cols"] if c in cleaned[key].columns]
        df         = cleaned[key][cols].copy()
        total_rows = len(df)

        try:
            cursor.execute(f"DELETE FROM [{table}]")
            conn.commit()
        except:
            pass

        col_sql  = ", ".join(f"[{c}]" for c in cols)
        ph       = ", ".join("?" for _ in cols)
        ins_sql  = f"INSERT INTO [{table}] ({col_sql}) VALUES ({ph})"

        batches = [df.iloc[i:i+BATCH_SIZE] for i in range(0, total_rows, BATCH_SIZE)]
        
        for batch in batches:
            rows = []
            for row in batch.itertuples(index=False, name=None):
                clean_row = tuple(
                    None if (v is None or (isinstance(v, float) and np.isnan(v)))
                    else (bool(v) if isinstance(v, (np.bool_,)) else
                          int(v)  if isinstance(v, (np.integer,)) else
                          float(v) if isinstance(v, (np.floating,)) else v)
                    for v in row
                )
                rows.append(clean_row)

            try:
                cursor.executemany(ins_sql, rows)
                conn.commit()
            except:
                conn.rollback()
                for r in rows:
                    try:
                        cursor.execute(ins_sql, r)
                        conn.commit()
                    except:
                        pass
        
        actual = cursor.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()[0]
        stats[table] = actual
        print(f"Table {table} loaded: {actual} rows")

    cursor.close()
    return stats

def main():
    print("Starting Walmart ETL Pipeline...")
    conn = get_conn()
    if not conn:
        print("Could not connect to SQL Server")
        return

    raw = extract()
    clean = transform(raw)
    stats = load(clean, conn)
    
    print("\nProcessing Complete!")
    for tbl, count in stats.items():
        print(f"{tbl}: {count} rows")
    
    conn.close()

if __name__ == "__main__":
    main()