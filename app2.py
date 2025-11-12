# app.py

from flask import Flask, jsonify, request
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# -----------------------------
# Function to read Excel data
# -----------------------------
def read_excel_data():
    df = pd.read_excel('supermarkt_sales.xlsx')
    return df


# -----------------------------
# Function to read SQL data
# -----------------------------
def read_sql_data():
    engine = create_engine('sqlite:///sales.db')
    df = pd.read_sql('SELECT * FROM sales', con=engine)
    return df


# -----------------------------
# Endpoint for Excel data
# -----------------------------
@app.route('/api/xlsx', methods=['GET'])
def get_excel_data():
    df = read_excel_data()
    return jsonify(df.to_dict(orient='records'))


# -----------------------------
# Endpoint for SQL data
# -----------------------------
@app.route('/api/sql', methods=['GET'])
def get_sql_data():
    df = read_sql_data()
    return jsonify(df.to_dict(orient='records'))


# -----------------------------
# Endpoint for filtered sales data
# -----------------------------
@app.route('/api/sales', methods=['GET'])
def get_sales_data():
    source = request.args.get('source', 'excel')  # choose between excel or sql
    product_filter = request.args.get('product', None)

    if source == 'sql':
        df = read_sql_data()
    else:
        df = read_excel_data()

    # Apply product filter if provided
    if product_filter:
        df = df[df['Product'].str.contains(product_filter, case=False, na=False)]

    return jsonify(df.to_dict(orient='records'))


# -----------------------------
# Run the app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
