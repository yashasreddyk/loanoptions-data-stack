import pandas as pd
import sqlite3

db_path = 'loanoptions.db'
conn = sqlite3.connect(db_path)

# Extract and save dim_customers
df_customers = pd.read_sql_query("SELECT * FROM dim_customers", conn)
df_customers.to_csv('PowerBI_Export/dim_customers.csv', index=False)

# Extract and save dim_lenders
df_lenders = pd.read_sql_query("SELECT * FROM dim_lenders", conn)
df_lenders.to_csv('PowerBI_Export/dim_lenders.csv', index=False)

# Extract and save fact_applications
df_facts = pd.read_sql_query("SELECT * FROM fact_applications", conn)
df_facts.to_csv('PowerBI_Export/fact_applications.csv', index=False)

conn.close()
print("Data successfully exported to CSVs for PowerBI in the PowerBI_Export folder.")
