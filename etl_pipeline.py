import json
import pandas as pd
from sqlalchemy import create_engine

INPUT_FILE = 'raw_applications.json'
DB_FILE = 'sqlite:///loanoptions.db'

def extract():
    print("Extracting data from simulated NoSQL (MongoDB) JSON...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
    return data

def transform(data):
    print("Transforming nested JSON into flat Pandas DataFrames...")
    
    # Flatten the data
    df = pd.json_normalize(data)
    
    # Extract customer dimension
    dim_customers = df[['_id', 'customer_profile.first_name', 'customer_profile.last_name', 
                        'customer_profile.state', 'customer_profile.credit_score_band',
                        'application_details.is_returning_customer']].copy()
    dim_customers.columns = ['customer_id', 'first_name', 'last_name', 'state', 'credit_score_band', 'is_returning']
    
    # Extract lender dimension
    lender_cols = ['lender_details.lender_name', 'lender_details.tier']
    # Some records don't reach the lender stage, so they'll have NaNs. 
    # Grab unique combinations for dimension
    if set(lender_cols).issubset(df.columns):
        dim_lenders = df[lender_cols].dropna().drop_duplicates().copy()
        dim_lenders.columns = ['lender_name', 'tier']
        # add an id column
        dim_lenders['lender_id'] = range(1, len(dim_lenders) + 1)
        
        # Merge lender_id back to main DF
        df = df.merge(dim_lenders, left_on=['lender_details.lender_name', 'lender_details.tier'], 
                      right_on=['lender_name', 'tier'], how='left')
    else:
        dim_lenders = pd.DataFrame(columns=['lender_id', 'lender_name', 'tier'])
        df['lender_id'] = None
    
    # Extract application facts
    fact_applications = df[['_id', 'customer_id' if 'customer_id' in df.columns else '_id', 
                            'application_details.loan_amount', 'application_details.loan_type',
                            'application_details.source_channel', 'funnel_metrics.current_stage',
                            'funnel_metrics.ask_ailo_used', 'funnel_metrics.ocr_documents_scanned',
                            'lender_id', 'lender_details.offered_rate',
                            'funnel_metrics.timestamps.inquiry_started_at',
                            'funnel_metrics.timestamps.ace_prefill_at',
                            'funnel_metrics.timestamps.neo_matched_at',
                            'funnel_metrics.timestamps.lender_approved_at',
                            'funnel_metrics.timestamps.settled_at']].copy()
    
    fact_applications.columns = [
        'application_id', 'customer_id', 'loan_amount', 'loan_type', 'source_channel', 
        'current_stage', 'ask_ailo_used', 'ocr_documents_scanned', 'lender_id', 'offered_rate',
        'inquiry_started_at', 'ace_prefill_at', 'neo_matched_at', 'lender_approved_at', 'settled_at'
    ]
    
    # Convert timestamps
    time_cols = ['inquiry_started_at', 'ace_prefill_at', 'neo_matched_at', 'lender_approved_at', 'settled_at']
    for col in time_cols:
        fact_applications[col] = pd.to_datetime(fact_applications[col])
        
    # Calculate time differences (in minutes for early funnel, days for later)
    fact_applications['mins_to_prefill'] = (fact_applications['ace_prefill_at'] - fact_applications['inquiry_started_at']).dt.total_seconds() / 60
    fact_applications['mins_to_match'] = (fact_applications['neo_matched_at'] - fact_applications['ace_prefill_at']).dt.total_seconds() / 60
    
    return dim_customers, dim_lenders, fact_applications

def load(dim_customers, dim_lenders, fact_applications):
    print("Loading data into simulated SQL (PostgreSQL) relational schema...")
    engine = create_engine(DB_FILE)
    
    # Write to SQLite
    dim_customers.to_sql('dim_customers', engine, if_exists='replace', index=False)
    dim_lenders.to_sql('dim_lenders', engine, if_exists='replace', index=False)
    fact_applications.to_sql('fact_applications', engine, if_exists='replace', index=False)
    
    print("ETL complete. Database is ready.")

def main():
    data = extract()
    cust, lend, fact = transform(data)
    load(cust, lend, fact)

if __name__ == "__main__":
    main()
