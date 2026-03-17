# Project Neo Simulator: LoanOptions.ai Data Stack Demonstration

## Overview
This project is a complete, end-to-end demonstration of building a modern data stack from scratch, specifically tailored to the business model and technological ecosystem of **LoanOptions.ai**. 

It simulates the exact challenge described in the Data Analyst job description: migrating unstructured NoSQL data (MongoDB) into a performant relational SQL warehouse (PostgreSQL), and then building a Business Intelligence reporting layer on top of it to deliver executive insights.

## The Architecture
The pipeline is broken down into three core technical phases:

### Phase 1: Data Mocking (The "Mongo" Layer)
*   **File**: `generate_mock_data.py`
*   **Technology**: Python (`Faker`, `json`)
*   **Concept**: I built a Python script to generate 5,000 realistic loan application records. To mimic LoanOptions' legacy MongoDB architecture, the data is output as heavily nested, unstructured JSON. 
*   **Business Logic**: The data specifically models LoanOptions' proprietary channels and tools:
    *   **Channels**: Organic, Synapses API (Embedded Finance), and Mortgage Brokers.
    *   **The "Pizza Tracker" Funnel**: Simulates realistic drop-off rates across the 5 stages of their application funnel (Inquiry Started -> ACE Pre-fill Complete -> Project Neo Matched -> Lender Approved -> Settled).

### Phase 2: ETL Processing (The "Postgres" Layer)
*   **File**: `etl_pipeline.py`
*   **Technology**: Python (`pandas`, `sqlalchemy`), SQLite
*   **Concept**: This represents the heavy lifting of the data engineering piece. The script ingests the messy JSON files and uses Pandas to flatten, clean, and map the semi-structured data.
*   **The Relational Schema**: I designed a star-schema optimized for fast analytical queries, pushing the data into a simulated relational database (SQLite acting as our Postgres warehouse).
    *   `dim_customers`: Customer demographics and credit bands.
    *   `dim_lenders`: Modeling the 90+ lenders split by Tier.
    *   `fact_applications`: The core fact table containing timestamps for every funnel stage, loan amounts, and channel origins.

### Phase 3: Business Intelligence (The "UI/UX" Layer)
*   **File**: `app.py` & PowerBI Integration
*   **Technology**: Python (`streamlit`, `plotly`), PowerBI
*   **Concept**: Instead of just running basic SQL queries, I built two presentation layers to prove an "eye for UX/UI in reporting":
    1.  **Streamlit Web App**: A fully interactive, dark-mode web dashboard constructed entirely in Python. It visually represents critical KPIs like the **"Lead to Full Submission" (targeting the ~54% metric)** and average ACE (Auto-Complete Engine) pre-fill times.
    2.  **PowerBI Export**: I authored an additional script (`export_to_csv.py`) to easily ingest the structured Postgres tables into PowerBI Desktop, allowing for rapid DAX modeling (calculating Submission Rates and Funnel Drop-offs) natively in Microsoft's ecosystem.

## Key Takeaways for LoanOptions.ai
This project proves several critical capabilities required for the Data Analyst role:
1.  **I am a Builder**: I don't wait for a clean dataset. I can synthesize the architecture, write the Python pipelines to migrate data from NoSQL to SQL, and model the warehouse myself.
2.  **I understand the Product**: The metrics aren't generic. I specifically modeled the performance of the **Synapses API**, the **ACE pre-fill funnel**, and the **Project Neo** matching logic to show how data impacts bottom-line revenue and conversion. 
3.  **Executive UX**: The reporting layer is designed exactly how a CEO or CTO wants to see it: clean, neon-branded, instantly actionable, and focused on finding bottlenecks in the "Pizza Tracker" funnel.
