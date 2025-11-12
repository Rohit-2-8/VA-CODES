# create_db.py

import sqlite3
import pandas as pd
import os

def create_and_populate_db():
    # Check if database already exists
    if os.path.exists('sales.db'):
        print("Database already exists. Skipping creation.")
        return

    # Connect to SQLite database (creates it if not existing)
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()

    # Create sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Product TEXT,
        Revenue REAL
    )
    ''')

    # Read Excel data
    df = pd.read_excel('supermarkt_sales.xlsx')

    # Insert data into the sales table
    for index, row in df.iterrows():
        cursor.execute('''
        INSERT INTO sales (Date, Product, Revenue)
        VALUES (?, ?, ?)
        ''', (row['Date'], row['Product'], row['Revenue']))

    # Commit and close
    conn.commit()
    conn.close()
    print("✅ Database created and populated successfully.")


if __name__ == "__main__":
    create_and_populate_db()
