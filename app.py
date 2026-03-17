import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Project Neo Simulator", layout="wide", page_icon="🚀")

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e24;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
        border: 1px solid #8A2BE2;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #8A2BE2;
    }
    .metric-label {
        font-size: 14px;
        color: #b0b0b0;
        text-transform: uppercase;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(138, 43, 226, 0.2);
        border-bottom: 2px solid #8A2BE2;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    conn = sqlite3.connect('loanoptions.db')
    
    query = """
    SELECT 
        f.application_id, f.loan_amount, f.loan_type, f.source_channel, 
        f.current_stage, f.ask_ailo_used, f.ocr_documents_scanned,
        c.credit_score_band, c.is_returning,
        l.lender_name, l.tier, f.offered_rate,
        f.inquiry_started_at, f.ace_prefill_at, f.neo_matched_at, f.lender_approved_at, f.settled_at,
        f.mins_to_prefill, f.mins_to_match
    FROM fact_applications f
    LEFT JOIN dim_customers c ON f.customer_id = c.customer_id
    LEFT JOIN dim_lenders l ON f.lender_id = l.lender_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading database: {e}. Please ensure loanoptions.db exists.")
    st.stop()

# --- HEADER ---
st.title("🚀 LoanOptions.ai | Analytics Engine")
st.markdown("*Simulating the 'Shopify of Lending' - Powered by Project Neo & Synapses API*")
st.divider()

# --- MULTI-PAGE TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 The Dashboard", "🏗️ Project Architecture", "💻 The Codebase", "👋 About the Developer"])

with tab1:
    # --- KPI METRICS ---
    col1, col2, col3, col4 = st.columns(4)

    total_apps = len(df)
    total_volume = df['loan_amount'].sum()
    settled_apps = len(df[df['current_stage'] == 'Settled & Funded'])
    full_submissions = len(df[df['current_stage'].isin(['Lender Approved', 'Settled & Funded'])])

    submission_rate = (full_submissions / total_apps) * 100
    avg_prefill_time = df['mins_to_prefill'].mean()

    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Applications Volume</div><div class="metric-value">${total_volume/1000000:.1f}M</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Lead to Full Submission</div><div class="metric-value">{submission_rate:.1f}%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Settled Applications</div><div class="metric-value">{settled_apps}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Avg ACE Pre-fill Time</div><div class="metric-value">{avg_prefill_time:.1f} mins</div></div>', unsafe_allow_html=True)

    st.write("")

    # --- CHARTS ROW 1 ---
    colA, colB = st.columns(2)

    with colA:
        st.subheader("🍕 The 'Pizza Tracker' Funnel")
        # Calculate funnel drops
        inquiry = total_apps
        prefill = len(df.dropna(subset=['ace_prefill_at']))
        matched = len(df.dropna(subset=['neo_matched_at']))
        approved = len(df.dropna(subset=['lender_approved_at']))
        settled = len(df.dropna(subset=['settled_at']))
        
        fig_funnel = go.Figure(go.Funnel(
            y=['Inquiry Started', 'ACE Pre-fill', 'Project Neo Matched', 'Lender Approved', 'Settled & Funded'],
            x=[inquiry, prefill, matched, approved, settled],
            textinfo="value+percent initial",
            marker={"color": ["#4b0082", "#6622aa", "#8A2BE2", "#a855f7", "#c084fc"]}
        ))
        fig_funnel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_funnel, use_container_width=True)

    with colB:
        st.subheader("🔌 Channel Performance (Synapses vs Organic)")
        
        # Calculate submission rate by channel
        channel_stats = df.groupby('source_channel').apply(
            lambda x: len(x[x['current_stage'].isin(['Lender Approved', 'Settled & Funded'])]) / len(x) * 100
        ).reset_index(name='Submission Rate (%)')
        
        fig_bar = px.bar(channel_stats, x='source_channel', y='Submission Rate (%)', 
                         color='source_channel', color_discrete_sequence=px.colors.qualitative.Vivid)
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- CHARTS ROW 2 ---
    st.divider()
    colC, colD = st.columns(2)

    with colC:
        st.subheader("🤖 Ask AILO Usage Impact")
        ailo_stats = df.groupby('ask_ailo_used')['loan_amount'].mean().reset_index()
        ailo_stats['ask_ailo_used'] = ailo_stats['ask_ailo_used'].replace({True: "Used Ask AILO", False: "Did Not Use AILO"})
        
        fig_pie = px.pie(ailo_stats, values='loan_amount', names='ask_ailo_used', hole=0.4, 
                         color_discrete_sequence=["#8A2BE2", "#4b0082"],
                         title="Avg Loan Size based on AILO usage")
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

    with colD:
        st.subheader("🏦 Project Neo: Top Matched Lenders")
        top_lenders = df['lender_name'].value_counts().head(10).reset_index()
        top_lenders.columns = ['Lender', 'Total Applications']
        fig_bar2 = px.bar(top_lenders, x='Total Applications', y='Lender', orientation='h', 
                          color='Total Applications', color_continuous_scale='Purples')
        fig_bar2.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar2, use_container_width=True)


with tab2:
    st.header("🏗️ The Architecture: Building the Data Stack")
    st.markdown('''
    ### Overview
    This project is a complete, end-to-end demonstration of building a modern data stack from scratch, perfectly tailored to **LoanOptions.ai**. 
    
    It simulates migrating unstructured NoSQL data (MongoDB) into a performant relational SQL warehouse (PostgreSQL), and building a Business Intelligence reporting layer to deliver executive insights.
    
    ### Phase 1: Data Generation (The "Mongo" Layer)
    *   **Technology**: Python (`Faker`, `json`)
    *   **Logic**: I generated 5,000 realistic loan applications mapped specifically to LoanOptions' proprietary channels (Synapses API, Organic) and the exact 5 stages of the "Pizza Tracker" funnel.

    ### Phase 2: Python ETL Pipeline (The "Postgres" Layer)
    *   **Technology**: Python (`pandas`, `sqlalchemy`), SQLite
    *   **Logic**: I wrote an automated script to ingest the messy NoSQL JSON, flatten the dictionaries using Pandas, and export it into a normalized SQL database with a star-schema (`dim_customers`, `dim_lenders`, `fact_applications`).

    ### Phase 3: Business Intelligence (The "UI/UX" Layer)
    *   **Technology**: Python (`streamlit`, `plotly`)
    *   **Logic**: A dark-mode Dashboard that automatically connects to the SQL database, runs complex joins in real-time, and visualizes KPIs like the **Lead to Full Submission (54%)** rate.
    ''')

with tab3:
    st.header("💻 The Codebase Snippets")
    st.markdown("Here is a glimpse of how the backend pipeline was built from scratch:")
    
    st.subheader("1. Extract, Transform, Load (ETL) pipeline in Python")
    st.code('''
def transform(data):
    print("Transforming nested JSON into flat Pandas DataFrames...")
    # Flatten the MongoDB JSON data
    df = pd.json_normalize(data)
    
    # Extract customer dimension
    dim_customers = df[['_id', 'customer_profile.first_name', 'customer_profile.last_name', 
                        'customer_profile.state', 'customer_profile.credit_score_band',
                        'application_details.is_returning_customer']].copy()
    dim_customers.columns = ['customer_id', 'first_name', 'last_name', 'state', 'credit_score_band', 'is_returning']
    
    # Calculate Funnel Metrics via Timestamps
    fact_applications['mins_to_prefill'] = (fact_applications['ace_prefill_at'] - fact_applications['inquiry_started_at']).dt.total_seconds() / 60
    ''', language='python')
    
    st.subheader("2. Complex SQL Architecture (Star Schema)")
    st.code('''
    SELECT 
        f.application_id, f.loan_amount, f.source_channel, f.current_stage,
        c.credit_score_band, c.is_returning,
        l.lender_name, l.tier, f.offered_rate,
        f.mins_to_prefill, f.mins_to_match
    FROM fact_applications f
    LEFT JOIN dim_customers c ON f.customer_id = c.customer_id
    LEFT JOIN dim_lenders l ON f.lender_id = l.lender_id
    ''', language='sql')

with tab4:
    st.header("👋 About the Developer")
    st.markdown('''
    ### Why I built this
    When I read the job description for the **Data Analyst** role at LoanOptions.ai, the mandate was explicitly clear: *"Build Our Data Stack"* and *"You are a builder. You don’t need a manager standing over your shoulder."*
    
    Instead of just sending a resume, I wanted to proactively prove that I have the exact skill-stack you require:
    - **SQL & Architecture**: Transitioning raw NoSQL to Relational Postgres.
    - **Python ETL**: Using Pandas/NumPy to automate data cleaning and construct pipelines.
    - **UX/UI in Reporting**: Designing high-impact, immediate dashboards for executive leadership.
    
    I understand LoanOptions.ai's vision of becoming the "Shopify of Lending". With Synapses, Project Neo, and Ask AILO pushing the boundaries of what an asset finance broker can be, your data layer needs to be flawless. I want to build it.
    
    **Let's have a chat.**
    - [LinkedIn](https://www.linkedin.com/in/yashas-reddy-k-4504a9206/)
    - [Email](mailto:yashasreddyk@gmail.com)
    ''')
