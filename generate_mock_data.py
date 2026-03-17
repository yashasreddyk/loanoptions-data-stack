import json
import random
from faker import Faker
import datetime

fake = Faker('en_AU')

# Configuration
NUM_RECORDS = 5000
OUTPUT_FILE = 'raw_applications.json'

# LoanOptions.ai specific dimensions
CHANNELS = [
    ('Organic', 0.4),
    ('Synapses API', 0.3),
    ('Mortgage Broker', 0.15),
    ('TikTok/Meta Ads', 0.15)
]

LOAN_TYPES = ['Car / Asset Finance', 'Personal Loan', 'Business / Equipment', 'Home Loan']

PIZZA_TRACKER_STAGES = [
    'Inquiry Started',
    'ACE Pre-fill Complete',
    'Project Neo Matched',
    'Lender Approved',
    'Settled & Funded'
]

# Simulate realistic dropoffs to reach ~54% full submission (which we'll define as 'Lender Approved' or further)
# Inquiry Started (100%) -> ACE Pre-fill (80%) -> Project Neo Matched (65%) -> Lender Approved (54%) -> Settled (45%)

def generate_record(app_id):
    # Determine channel based on weights
    channels, weights = zip(*CHANNELS)
    channel = random.choices(channels, weights=weights)[0]
    
    # Determine dropoff funnel stage
    rand_val = random.random()
    if rand_val < 0.20:
        stage_idx = 0 # 20% drop off at inquiry
    elif rand_val < 0.46:
        stage_idx = 2 # 11% drop off after matching
    elif rand_val < 0.55:
        stage_idx = 3 # 9% drop off after approval (don't settle)
    else:
        stage_idx = 4 # 45% settle
        
    current_stage = PIZZA_TRACKER_STAGES[stage_idx]
    
    # Generate timestamps for each stage reached
    base_date = fake.date_time_between(start_date='-1y', end_date='now')
    timestamps = {}
    timestamps['inquiry_started_at'] = base_date.isoformat()
    
    if stage_idx >= 1:
        # ACE is fast (<5 mins)
        base_date += datetime.timedelta(minutes=random.randint(1, 10))
        timestamps['ace_prefill_at'] = base_date.isoformat()
    
    if stage_idx >= 2:
        # Neo matching is fast
        base_date += datetime.timedelta(minutes=random.randint(1, 15))
        timestamps['neo_matched_at'] = base_date.isoformat()
        
    if stage_idx >= 3:
        # Lender approval takes days
        base_date += datetime.timedelta(days=random.randint(1, 14))
        timestamps['lender_approved_at'] = base_date.isoformat()
        
    if stage_idx >= 4:
        # Settlement takes a little longer
        base_date += datetime.timedelta(days=random.randint(1, 7))
        timestamps['settled_at'] = base_date.isoformat()

    # Nested JSON structure to simulate MongoDB document
    record = {
        "_id": f"app_{app_id}",
        "customer_profile": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "state": fake.state_abbr(),
            "credit_score_band": random.choices(
                ['Excellent', 'Good', 'Fair', 'Poor'], 
                weights=[0.3, 0.4, 0.2, 0.1]
            )[0]
        },
        "application_details": {
            "loan_amount": round(random.uniform(5000, 150000), 2),
            "loan_type": random.choice(LOAN_TYPES),
            "source_channel": channel,
            "is_returning_customer": random.choices([True, False], weights=[0.15, 0.85])[0]
        },
        "funnel_metrics": {
            "current_stage": current_stage,
            "timestamps": timestamps,
            "ask_ailo_used": random.choices([True, False], weights=[0.4, 0.6])[0],
            "ocr_documents_scanned": random.randint(1, 4) if stage_idx >= 1 else 0
        }
    }
    
    # If they matched/approved, add lender details
    if stage_idx >= 2:
        record['lender_details'] = {
            "lender_name": f"Lender {random.randint(1, 90)}",
            "tier": random.choices(['Tier 1', 'Tier 2', 'Tier 3'], weights=[0.5, 0.3, 0.2])[0],
            "offered_rate": round(random.uniform(4.5, 12.5), 2)
        }
        
    return record

def main():
    print(f"Generating {NUM_RECORDS} mock application records...")
    data = [generate_record(i) for i in range(1, NUM_RECORDS + 1)]
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully generated mock data into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
