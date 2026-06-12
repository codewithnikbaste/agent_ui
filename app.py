"""
Enterprise AI-Powered Customer Complaint Classification and Routing Engine
A production-ready Streamlit dashboard for complaint management and analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from faker import Faker
import random
import hashlib
import json
from io import StringIO

# ==============================================================================
# PAGE CONFIGURATION & STYLING
# ==============================================================================

st.set_page_config(
    page_title="AI Complaint Classification Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
def inject_custom_css():
    """Inject custom CSS for enterprise look and feel"""
    custom_css = """
    <style>
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #2ca02c;
            --danger-color: #d62728;
            --warning-color: #ff7f0e;
            --success-color: #2ca02c;
            --dark-bg: #0f1419;
            --light-bg: #f8f9fa;
        }
        
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* KPI Card styling */
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .kpi-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }
        
        .kpi-label {
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .kpi-trend {
            font-size: 0.85rem;
            margin-top: 0.5rem;
            opacity: 0.8;
        }
        
        /* Chart container */
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 1rem 0;
        }
        
        /* Data table styling */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
        }
        
        /* Status badge styling */
        .status-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-open {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        
        .status-closed {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        
        .status-pending {
            background-color: #fff3e0;
            color: #e65100;
        }
        
        /* Priority styling */
        .priority-p1 {
            color: #d32f2f;
            font-weight: 700;
        }
        
        .priority-p2 {
            color: #f57c00;
            font-weight: 700;
        }
        
        .priority-p3 {
            color: #fbc02d;
            font-weight: 700;
        }
        
        .priority-p4 {
            color: #388e3c;
            font-weight: 700;
        }
        
        /* Navigation styling */
        .sidebar-nav {
            padding: 1rem 0;
        }
        
        /* Login container */
        .login-container {
            max-width: 400px;
            margin: 5rem auto;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            background: white;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .login-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
            margin: 0.5rem 0;
        }
        
        .login-subtitle {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Gauge styling */
        .gauge-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 300px;
        }
        
        /* Metric box */
        .metric-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 8px;
            color: white;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================

def init_session_state():
    """Initialize all session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "complaint_data" not in st.session_state:
        st.session_state.complaint_data = None
    if "selected_filters" not in st.session_state:
        st.session_state.selected_filters = {}
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "pagination_page" not in st.session_state:
        st.session_state.pagination_page = 0
    if "rows_per_page" not in st.session_state:
        st.session_state.rows_per_page = 25
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "new_tickets_count" not in st.session_state:
        st.session_state.new_tickets_count = 0

init_session_state()

# ==============================================================================
# DEMO DATA GENERATION
# ==============================================================================

@st.cache_data
def generate_complaint_data(num_records=1000, seed=42):
    """Generate realistic complaint data using Faker and numpy
    
    Reduced to 1000 records for faster Streamlit Cloud deployment.
    Increase num_records parameter for more data locally.
    """
    
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()
    
    categories = [
        "Technical Support", "Product Support", "Customer Service", "IT Support",
        "Billing & Payment", "Return & Exchange", "Service Outage", "Maintenance",
        "Sales", "Pre-Sales", "Human Resources", "General Inquiry"
    ]
    
    departments = ["Support", "Sales", "Billing", "Operations", "IT", "HR"]
    
    languages = ["English", "Spanish", "French", "German", "Portuguese"]
    
    statuses = ["Open", "Closed", "Pending", "On Hold"]
    
    priorities = ["P1", "P2", "P3", "P4"]
    
    sentiments = ["Positive", "Negative", "Neutral"]
    
    intents = ["Support Request", "Complaint", "Feedback", "Question", "Bug Report"]
    
    customer_types = ["Existing Customer", "Prospect", "Partner", "Enterprise"]
    
    products = ["CloudPlatform Pro", "Analytics Suite", "Enterprise CRM", "Support Portal", "Integration Hub"]
    
    teams_map = {
        "Support": ["L1 Support", "L2 Support", "L3 Support", "Escalation Team"],
        "Sales": ["Inside Sales", "Sales Engineering", "Enterprise Sales"],
        "Billing": ["Billing Team", "Finance", "Collections"],
        "Operations": ["Operations Team", "Process Team"],
        "IT": ["IT Support", "Infrastructure"],
        "HR": ["HR Team", "Recruitment"]
    }
    
    complaint_templates = [
        "Unable to login to the system",
        "Application keeps crashing",
        "Feature not working as expected",
        "Billing charge issue",
        "Need to return item",
        "Service is down",
        "Missing product features",
        "Performance issues",
        "Need technical assistance",
        "Question about pricing",
        "Cannot access my account",
        "Report of bug in system",
        "Integration not working",
        "Data loss incident",
        "Slow response times",
        "UI/UX issues",
        "Documentation unclear",
        "Export functionality broken",
        "API not responding",
        "Need password reset",
    ]
    
    records = []
    
    for i in range(num_records):
        # Generate timestamps
        created_date = datetime.now() - timedelta(days=random.randint(0, 90))
        resolution_hours = random.choice([2, 4, 8, 12, 16, 24, 48, 72, 120, 168])
        resolved_date = created_date + timedelta(hours=resolution_hours)
        
        category = random.choice(categories)
        department = random.choice(departments)
        team = random.choice(teams_map[department])
        
        # Determine priority based on weighted distribution
        priority = np.random.choice(["P1", "P2", "P3", "P4"], p=[0.05, 0.15, 0.35, 0.45])
        
        # SLA time based on priority
        sla_hours = {"P1": 4, "P2": 8, "P3": 24, "P4": 48}[priority]
        
        status = random.choice(statuses)
        
        # Sentiment often correlates with complaint content
        if status == "Closed":
            sentiment = np.random.choice(sentiments, p=[0.3, 0.4, 0.3])
        else:
            sentiment = np.random.choice(sentiments, p=[0.1, 0.7, 0.2])
        
        record = {
            "ticket_id": f"TKT-{2024000 + i}",
            "subject": random.choice(complaint_templates),
            "complaint_body": fake.text(max_nb_chars=300),
            "ai_summary": fake.text(max_nb_chars=150),
            "department": department,
            "category": category,
            "subcategory": f"{category} - Sub {random.randint(1, 5)}",
            "customer_type": random.choice(customer_types),
            "priority": priority,
            "sla_level": sla_hours,
            "status": status,
            "assigned_team": team,
            "language": random.choice(languages),
            "product_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
            "sentiment": sentiment,
            "intent": random.choice(intents),
            "confidence_score": round(random.uniform(0.5, 0.99), 2),
            "tag_1": f"Tag_{random.randint(1, 20)}",
            "tag_2": f"Tag_{random.randint(1, 20)}",
            "tag_3": f"Tag_{random.randint(1, 20)}",
            "creation_date": created_date,
            "resolution_date": resolved_date if status == "Closed" else None,
            "resolution_time_hours": resolution_hours if status == "Closed" else None,
            "customer_name": fake.name(),
            "customer_email": fake.email(),
            "customer_phone": fake.phone_number(),
        }
        
        records.append(record)
    
    df = pd.DataFrame(records)
    return df

# Get or create complaint data
if st.session_state.complaint_data is None:
    st.session_state.complaint_data = generate_complaint_data()

df = st.session_state.complaint_data

# ==============================================================================
# AUTHENTICATION
# ==============================================================================

def login_page():
    """Render premium minimal login screen"""
    
    # Inject premium minimal login CSS
    st.markdown("""
    <style>
        /* Hide Streamlit default elements */
        .stAppHeader { display: none; }
        #MainMenu { display: none; }
        footer { display: none; }
        
        /* Premium minimal design */
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        }
        
        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
        }
        
        .main {
            padding: 0 !important;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem;
        }
        
        .login-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 3.5rem 2.5rem;
            width: 100%;
            max-width: 380px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3), 
                        0 0 1px rgba(255, 255, 255, 0.5) inset;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .login-icon-top {
            font-size: 3.5rem;
            text-align: center;
            margin-bottom: 1.5rem;
            animation: pulse-icon 2s ease-in-out infinite;
        }
        
        @keyframes pulse-icon {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .login-title {
            font-size: 1.75rem;
            font-weight: 700;
            text-align: center;
            color: #0f172a;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.5px;
        }
        
        .login-subtitle {
            font-size: 0.85rem;
            text-align: center;
            color: #64748b;
            margin: 0 0 2rem 0;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 600;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.65rem;
        }
        
        .form-input {
            width: 100%;
            padding: 0.95rem 1.1rem;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #f8fafc;
            color: #0f172a;
            font-family: inherit;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #3b82f6;
            background: white;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        }
        
        .form-input::placeholder {
            color: #94a3b8;
        }
        
        .login-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-top: 1.5rem;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        }
        
        .login-btn:active {
            transform: translateY(0px);
        }
        
        .error-box {
            background: #fee2e2;
            border: 1px solid #fecaca;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            color: #991b1b;
            text-align: center;
        }
        
        .success-box {
            background: #dcfce7;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            color: #166534;
            text-align: center;
        }
        
        .footer-note {
            text-align: center;
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 1.5rem;
        }
        
        /* Stmetrics and other elements - hide */
        .stMetric { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize login error state
    if "login_error" not in st.session_state:
        st.session_state.login_error = False
    if "login_success" not in st.session_state:
        st.session_state.login_success = False
    
    # Login panel
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Icon
        st.markdown("""
        <div class='login-icon-top'>🎯</div>
        """, unsafe_allow_html=True)
        
        # Title and subtitle
        st.markdown("""
        <h1 class='login-title'>AI Complaint Engine</h1>
        <p class='login-subtitle'>Sign In to Dashboard</p>
        """, unsafe_allow_html=True)
        
        # Error message
        if st.session_state.login_error:
            st.markdown("""
            <div class='error-box'>
                ✗ Invalid username or password
            </div>
            """, unsafe_allow_html=True)
        
        # Success message
        if st.session_state.login_success:
            st.markdown("""
            <div class='success-box'>
                ✓ Welcome! Redirecting...
            </div>
            """, unsafe_allow_html=True)
            import time
            time.sleep(1.5)
            st.rerun()
        
        # Username input
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<label class='form-label'>Username</label>", unsafe_allow_html=True)
        username = st.text_input(
            "username",
            key="login_username",
            placeholder="admin",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Password input
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<label class='form-label'>Password</label>", unsafe_allow_html=True)
        password = st.text_input(
            "password",
            key="login_password",
            type="password",
            placeholder="••••••••",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Login button
        if st.button("Sign In", use_container_width=True, type="primary"):
            if username == "admin" and password == "Admin123@":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.login_error = False
                st.session_state.login_success = True
                st.rerun()
            else:
                st.session_state.login_error = True
                st.session_state.login_success = False
                st.rerun()
        
        # Footer note
        st.markdown("""
        <div class='footer-note'>
            Enterprise-Grade Complaint Management
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# REUSABLE COMPONENTS
# ==============================================================================

def render_kpi_card(label, value, trend=None, color="#667eea", icon="📊"):
    """Render a KPI card with trend indicator"""
    trend_html = ""
    if trend:
        trend_direction = "📈" if trend >= 0 else "📉"
        trend_html = f"<div style='font-size: 0.85rem; margin-top: 0.5rem;'>{trend_direction} {abs(trend):+.1f}%</div>"
    
    html = f"""
    <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                padding: 1.5rem; border-radius: 12px; color: white; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'>
        <div style='font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.05em;'>{icon} {label}</div>
        <div style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;'>{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def apply_filters(data, filters):
    """Apply multiple filters to dataframe"""
    df_filtered = data.copy()
    
    if "category" in filters and filters["category"]:
        df_filtered = df_filtered[df_filtered["category"].isin(filters["category"])]
    
    if "priority" in filters and filters["priority"]:
        df_filtered = df_filtered[df_filtered["priority"].isin(filters["priority"])]
    
    if "status" in filters and filters["status"]:
        df_filtered = df_filtered[df_filtered["status"].isin(filters["status"])]
    
    if "department" in filters and filters["department"]:
        df_filtered = df_filtered[df_filtered["department"].isin(filters["department"])]
    
    if "language" in filters and filters["language"]:
        df_filtered = df_filtered[df_filtered["language"].isin(filters["language"])]
    
    if "date_range" in filters and filters["date_range"]:
        start_date, end_date = filters["date_range"]
        df_filtered = df_filtered[(df_filtered["creation_date"] >= start_date) & 
                                  (df_filtered["creation_date"] <= end_date)]
    
    return df_filtered

def paginate_dataframe(data, page, rows_per_page):
    """Paginate dataframe"""
    total_rows = len(data)
    total_pages = (total_rows + rows_per_page - 1) // rows_per_page
    
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * rows_per_page
    end_idx = start_idx + rows_per_page
    
    return data.iloc[start_idx:end_idx], total_pages, total_rows

def export_to_csv(data):
    """Export dataframe to CSV"""
    csv = data.to_csv(index=False)
    return csv

def get_priority_color(priority):
    """Get color for priority level"""
    colors = {"P1": "#d32f2f", "P2": "#f57c00", "P3": "#fbc02d", "P4": "#388e3c"}
    return colors.get(priority, "#666")

def get_status_color(status):
    """Get color for status"""
    colors = {
        "Open": "#1565c0",
        "Closed": "#2e7d32",
        "Pending": "#e65100",
        "On Hold": "#6a1b9a"
    }
    return colors.get(status, "#666")

# ==============================================================================
# PAGE FUNCTIONS
# ==============================================================================

def page_dashboard():
    """Dashboard - Executive Overview"""
    st.title("📊 Executive Dashboard")
    
    # KPI Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card("Total Complaints", len(df), trend=2.5, 
                       color="#667eea", icon="📋")
    
    with col2:
        open_count = len(df[df["status"] == "Open"])
        render_kpi_card("Open Tickets", open_count, trend=-1.2,
                       color="#f57c00", icon="🔴")
    
    with col3:
        closed_count = len(df[df["status"] == "Closed"])
        render_kpi_card("Closed Tickets", closed_count, trend=5.3,
                       color="#2e7d32", icon="✅")
    
    with col4:
        pending_count = len(df[df["status"] == "Pending"])
        render_kpi_card("Pending Tickets", pending_count, trend=0.5,
                       color="#e65100", icon="⏳")
    
    st.markdown("---")
    
    # KPI Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_resolution = df[df["status"] == "Closed"]["resolution_time_hours"].mean()
        render_kpi_card("Avg Resolution (hrs)", f"{avg_resolution:.1f}", trend=-3.2,
                       color="#764ba2", icon="⏱️")
    
    with col2:
        sla_compliant = len(df[(df["status"] == "Closed") & 
                              (df["resolution_time_hours"] <= df["sla_level"])]) / len(df[df["status"] == "Closed"]) * 100
        render_kpi_card("SLA Compliance", f"{sla_compliant:.1f}%", trend=1.5,
                       color="#2ca02c", icon="✓")
    
    with col3:
        avg_confidence = df["confidence_score"].mean()
        render_kpi_card("Avg Confidence", f"{avg_confidence:.0%}", trend=2.1,
                       color="#1f77b4", icon="🎯")
    
    with col4:
        satisfaction = random.randint(75, 98)
        render_kpi_card("Satisfaction", f"{satisfaction}%", trend=3.2,
                       color="#d62728", icon="😊")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Complaints by Category")
        cat_counts = df["category"].value_counts().head(10)
        fig = px.bar(x=cat_counts.values, y=cat_counts.index, orientation='h',
                    labels={'x': 'Count', 'y': 'Category'},
                    color=cat_counts.values, color_continuous_scale='Blues')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Complaints by Priority")
        priority_counts = df["priority"].value_counts()
        colors = {"P1": "#d32f2f", "P2": "#f57c00", "P3": "#fbc02d", "P4": "#388e3c"}
        fig = go.Figure(data=[go.Pie(labels=priority_counts.index, values=priority_counts.values,
                                      marker=dict(colors=[colors[p] for p in priority_counts.index]))])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Status Distribution")
        status_counts = df["status"].value_counts()
        colors = {"Open": "#1565c0", "Closed": "#2e7d32", "Pending": "#e65100", "On Hold": "#6a1b9a"}
        fig = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values,
                                      marker=dict(colors=[colors.get(s, "#666") for s in status_counts.index]))])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Weekly Ticket Volume")
        df_sorted = df.sort_values("creation_date")
        df_sorted["week"] = df_sorted["creation_date"].dt.to_period("W")
        weekly_counts = df_sorted.groupby("week").size()
        fig = px.line(x=weekly_counts.index.astype(str), y=weekly_counts.values,
                     labels={'x': 'Week', 'y': 'Tickets'},
                     markers=True)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def page_complaint_explorer():
    """Complaint Explorer - Data Explorer"""
    st.title("🔍 Complaint Explorer")
    
    st.subheader("Search & Filter")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_query = st.text_input("Search by Subject or Body", value=st.session_state.search_query)
        st.session_state.search_query = search_query
    
    with col2:
        categories = st.multiselect("Category", df["category"].unique(), 
                                   default=st.session_state.selected_filters.get("category", []))
        st.session_state.selected_filters["category"] = categories
    
    with col3:
        priorities = st.multiselect("Priority", ["P1", "P2", "P3", "P4"],
                                   default=st.session_state.selected_filters.get("priority", []))
        st.session_state.selected_filters["priority"] = priorities
    
    with col4:
        statuses = st.multiselect("Status", df["status"].unique(),
                                 default=st.session_state.selected_filters.get("status", []))
        st.session_state.selected_filters["status"] = statuses
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        departments = st.multiselect("Department", df["department"].unique(),
                                    default=st.session_state.selected_filters.get("department", []))
        st.session_state.selected_filters["department"] = departments
    
    with col2:
        languages = st.multiselect("Language", df["language"].unique(),
                                  default=st.session_state.selected_filters.get("language", []))
        st.session_state.selected_filters["language"] = languages
    
    with col3:
        date_range = st.date_input("Date Range", 
                                   value=(df["creation_date"].min().date(), 
                                         df["creation_date"].max().date()),
                                   key="date_range_picker")
        if len(date_range) == 2:
            st.session_state.selected_filters["date_range"] = (
                pd.Timestamp(date_range[0]),
                pd.Timestamp(date_range[1])
            )
    
    # Apply filters
    df_filtered = apply_filters(df, st.session_state.selected_filters)
    
    # Search
    if search_query:
        df_filtered = df_filtered[
            (df_filtered["subject"].str.contains(search_query, case=False, na=False)) |
            (df_filtered["complaint_body"].str.contains(search_query, case=False, na=False))
        ]
    
    st.markdown("---")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(df_filtered))
    with col2:
        st.metric("Unique Categories", df_filtered["category"].nunique())
    with col3:
        st.metric("High Priority (P1/P2)", len(df_filtered[df_filtered["priority"].isin(["P1", "P2"])]))
    with col4:
        st.metric("SLA Compliance", f"{len(df_filtered[df_filtered['resolution_time_hours'] <= df_filtered['sla_level']]) / max(len(df_filtered[df_filtered['status'] == 'Closed']), 1):.1%}")
    
    st.markdown("---")
    
    # Pagination
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rows_per_page = st.selectbox("Rows per page", [10, 25, 50, 100],
                                    index=[10, 25, 50, 100].index(st.session_state.rows_per_page))
        st.session_state.rows_per_page = rows_per_page
    
    with col2:
        current_page = st.session_state.pagination_page
    
    with col3:
        pass
    
    with col4:
        if st.button("📥 Export to CSV"):
            csv = export_to_csv(df_filtered)
            st.download_button("Download CSV", csv, "complaints.csv", "text/csv")
    
    # Display data
    df_paginated, total_pages, total_rows = paginate_dataframe(df_filtered, current_page, rows_per_page)
    
    # Show table
    display_cols = ["ticket_id", "subject", "category", "priority", "status", "department", "sentiment", "confidence_score", "creation_date"]
    st.dataframe(df_paginated[display_cols], use_container_width=True, height=400)
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous") and current_page > 0:
            st.session_state.pagination_page -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align: center;'><b>Page {current_page + 1} of {total_pages}</b> ({total_rows} total records)</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️") and current_page < total_pages - 1:
            st.session_state.pagination_page += 1
            st.rerun()

def page_ai_classification():
    """AI Classification - Analysis Workspace"""
    st.title("🤖 AI Classification Workspace")
    
    # Select complaint
    st.subheader("Select Complaint to Analyze")
    
    selected_id = st.selectbox(
        "Ticket ID",
        df["ticket_id"].values,
        format_func=lambda x: f"{x} - {df[df['ticket_id']==x]['subject'].values[0]}"
    )
    
    complaint = df[df["ticket_id"] == selected_id].iloc[0]
    
    st.markdown("---")
    
    # Original complaint
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Original Complaint")
        st.write(f"**Subject:** {complaint['subject']}")
        st.write(f"**Customer:** {complaint['customer_name']} ({complaint['customer_email']})")
        st.write(f"**Date:** {complaint['creation_date'].strftime('%Y-%m-%d %H:%M')}")
        st.write(f"**Language:** {complaint['language']}")
        st.markdown("---")
        st.write("**Complaint Body:**")
        st.write(complaint['complaint_body'])
    
    with col2:
        st.subheader("📊 AI Analysis Results")
        
        # Intent Detection Gauge
        intent_score = {"Support Request": 90, "Complaint": 85, "Feedback": 70, "Question": 60, "Bug Report": 95}
        intent_val = intent_score.get(complaint["intent"], 75)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=intent_val,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Intent Detection"},
            delta={"reference": 80},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 80], "color": "gray"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Results Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sentiment Analysis
        sentiment_scores = {"Positive": 70, "Negative": 90, "Neutral": 50}
        sentiment_val = sentiment_scores.get(complaint["sentiment"], 60)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sentiment_val,
            title={"text": "Sentiment Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": {"Positive": "green", "Negative": "red", "Neutral": "gray"}.get(complaint["sentiment"], "gray")},
                "steps": [
                    {"range": [0, 33], "color": "#ffcccc"},
                    {"range": [33, 66], "color": "#ffffcc"},
                    {"range": [66, 100], "color": "#ccffcc"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Priority Prediction
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value={"P1": 95, "P2": 75, "P3": 50, "P4": 25}[complaint["priority"]],
            title={"text": "Priority Prediction"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": get_priority_color(complaint["priority"])},
                "steps": [
                    {"range": [0, 25], "color": "#ccffcc"},
                    {"range": [25, 50], "color": "#ffffcc"},
                    {"range": [50, 75], "color": "#ffcccc"},
                    {"range": [75, 100], "color": "#ff9999"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Overall Confidence
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=int(complaint["confidence_score"] * 100),
            title={"text": "Overall Confidence"},
            delta={"reference": 80},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "purple"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 80], "color": "gray"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Predictions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center;'>
            <div style='font-size: 0.9rem; color: #666;'>Category Prediction</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #1565c0;'>{complaint['category']}</div>
            <div style='font-size: 0.85rem; color: #999;'>{complaint['confidence_score']:.1%} confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: #f3e5f5; padding: 1rem; border-radius: 8px; text-align: center;'>
            <div style='font-size: 0.9rem; color: #666;'>Department Routing</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #6a1b9a;'>{complaint['department']}</div>
            <div style='font-size: 0.85rem; color: #999;'>85% accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;'>
            <div style='font-size: 0.9rem; color: #666;'>Assigned Team</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #e65100;'>{complaint['assigned_team']}</div>
            <div style='font-size: 0.85rem; color: #999;'>SLA: {complaint['sla_level']}h</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: #e8f5e9; padding: 1rem; border-radius: 8px; text-align: center;'>
            <div style='font-size: 0.9rem; color: #666;'>SLA Risk</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #2e7d32;'>LOW</div>
            <div style='font-size: 0.85rem; color: #999;'>Safe</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Summary and tags
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("AI Summary")
        st.write(complaint["ai_summary"])
    
    with col2:
        st.subheader("Auto-Generated Tags")
        st.write(f"🏷️ {complaint['tag_1']} | {complaint['tag_2']} | {complaint['tag_3']}")
        st.write(f"**Intent:** {complaint['intent']}")
        st.write(f"**Sentiment:** {complaint['sentiment']}")

def page_routing_engine():
    """Routing Engine - Visual Workflow"""
    st.title("🔀 Routing Engine")
    
    st.subheader("Complaint Routing Workflow")
    
    # Visual workflow
    st.markdown("""
    <div style='display: flex; justify-content: space-around; align-items: center; margin: 2rem 0;'>
        <div style='text-align: center; flex: 1;'>
            <div style='background: #667eea; color: white; padding: 1.5rem; border-radius: 12px; margin: 0 0.5rem; font-weight: bold;'>
                👤 Customer Complaint
            </div>
            <div style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>Submission</div>
        </div>
        <div style='flex: 0; font-size: 1.5rem; color: #999;'>→</div>
        <div style='text-align: center; flex: 1;'>
            <div style='background: #764ba2; color: white; padding: 1.5rem; border-radius: 12px; margin: 0 0.5rem; font-weight: bold;'>
                🤖 AI Classification
            </div>
            <div style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>Analysis</div>
        </div>
        <div style='flex: 0; font-size: 1.5rem; color: #999;'>→</div>
        <div style='text-align: center; flex: 1;'>
            <div style='background: #f57c00; color: white; padding: 1.5rem; border-radius: 12px; margin: 0 0.5rem; font-weight: bold;'>
                ⚡ Priority Assignment
            </div>
            <div style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>Triage</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='display: flex; justify-content: space-around; align-items: center; margin: 2rem 0;'>
        <div style='text-align: center; flex: 1;'>
            <div style='background: #2ca02c; color: white; padding: 1.5rem; border-radius: 12px; margin: 0 0.5rem; font-weight: bold;'>
                🏢 Department Mapping
            </div>
            <div style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>Categorization</div>
        </div>
        <div style='flex: 0; font-size: 1.5rem; color: #999;'>→</div>
        <div style='text-align: center; flex: 1;'>
            <div style='background: #1f77b4; color: white; padding: 1.5rem; border-radius: 12px; margin: 0 0.5rem; font-weight: bold;'>
                👨‍💼 Agent Assignment
            </div>
            <div style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>Distribution</div>
        </div>
        <div style='flex: 0; font-size: 1.5rem; color: #999;'>→</div>
        <div style='text-align: center; flex: 1;'>
            <div style='background: #d62728; color: white; padding: 1.5rem; border-radius: 12px; margin: 0 0.5rem; font-weight: bold;'>
                📋 Resolution Queue
            </div>
            <div style='color: #999; font-size: 0.9rem; margin-top: 0.5rem;'>Resolution</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Routing Rules
    st.subheader("Routing Decision Rules")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Priority-Based Rules:**")
        st.write("""
        - **P1** → Escalate immediately to supervisor
        - **P2** → Route to L2/L3 support team
        - **P3** → Standard routing to available agent
        - **P4** → Queue for next available agent
        """)
    
    with col2:
        st.write("**Category-Based Department Mapping:**")
        st.write("""
        - **Technical/IT/Service Issues** → Support Department
        - **Billing/Payment** → Billing Department
        - **Product/Feature Issues** → Product Support
        - **Sales Questions** → Sales Department
        - **HR Related** → HR Department
        """)
    
    st.markdown("---")
    
    # Routing Performance
    st.subheader("Routing Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        correct_routes = len(df[df["assigned_team"] != ""])
        accuracy = (correct_routes / len(df)) * 100
        st.metric("Routing Accuracy", f"{accuracy:.1f}%", "+2.3%")
    
    with col2:
        avg_routing_time = random.randint(2, 8)
        st.metric("Avg Routing Time (sec)", avg_routing_time, "-1.2 sec")
    
    with col3:
        failed_routes = len(df[df["status"] == "On Hold"])
        st.metric("Escalations", failed_routes, "+12")
    
    with col4:
        misdirected = random.randint(15, 25)
        st.metric("Misdirected Tickets", f"{misdirected}", "-3")

def page_analytics():
    """Analytics - Comprehensive Analytics Dashboard"""
    st.title("📈 Analytics Dashboard")
    
    # Row 1: Category and Priority
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Complaints by Category (Top 10)")
        cat_data = df["category"].value_counts().head(10)
        fig = px.bar(x=cat_data.values, y=cat_data.index, orientation='h',
                    labels={'x': 'Count', 'y': 'Category'},
                    color=cat_data.values, color_continuous_scale='Viridis')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Monthly Ticket Volume")
        df_sorted = df.sort_values("creation_date")
        df_sorted["month"] = df_sorted["creation_date"].dt.to_period("M")
        monthly_counts = df_sorted.groupby("month").size()
        fig = px.bar(x=monthly_counts.index.astype(str), y=monthly_counts.values,
                    labels={'x': 'Month', 'y': 'Tickets'},
                    color=monthly_counts.values, color_continuous_scale='Blues')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Language and Team
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Complaints by Language")
        lang_data = df["language"].value_counts()
        fig = px.pie(labels=lang_data.index, values=lang_data.values,
                    title="Language Distribution")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tickets by Team (Top 10)")
        team_data = df["assigned_team"].value_counts().head(10)
        fig = px.bar(x=team_data.index, y=team_data.values,
                    labels={'x': 'Team', 'y': 'Tickets'},
                    color=team_data.values, color_continuous_scale='Plasma')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Resolution and SLA
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resolution Time by Priority")
        resolution_by_priority = df[df["status"] == "Closed"].groupby("priority")["resolution_time_hours"].apply(list).to_dict()
        fig = go.Figure()
        for priority in ["P1", "P2", "P3", "P4"]:
            if priority in resolution_by_priority:
                fig.add_trace(go.Box(y=resolution_by_priority[priority], name=priority,
                                    marker_color=get_priority_color(priority)))
        fig.update_layout(height=400, xaxis_title="Priority", yaxis_title="Resolution Time (hours)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("SLA Compliance by Priority")
        sla_data = []
        for priority in ["P1", "P2", "P3", "P4"]:
            priority_df = df[df["priority"] == priority]
            if len(priority_df) > 0:
                compliant = len(priority_df[priority_df["resolution_time_hours"] <= priority_df["sla_level"]]) / len(priority_df) * 100
            else:
                compliant = 0
            sla_data.append({"priority": priority, "compliance": compliant})
        sla_df = pd.DataFrame(sla_data)
        fig = px.bar(sla_df, x="priority", y="compliance",
                    labels={'priority': 'Priority', 'compliance': 'Compliance %'},
                    color="priority", color_discrete_map={"P1": "#d32f2f", "P2": "#f57c00", "P3": "#fbc02d", "P4": "#388e3c"})
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4: Sentiment and Confidence
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        sentiment_data = df["sentiment"].value_counts()
        colors = {"Positive": "#2e7d32", "Negative": "#d32f2f", "Neutral": "#f57c00"}
        fig = px.pie(labels=sentiment_data.index, values=sentiment_data.values,
                    color=sentiment_data.index, color_discrete_map=colors)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("AI Confidence Score Distribution")
        fig = px.histogram(df, x="confidence_score", nbins=30,
                          labels={'confidence_score': 'Confidence Score', 'count': 'Frequency'},
                          color_discrete_sequence=['#667eea'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def page_sla_monitor():
    """SLA Monitor - SLA Tracking Center"""
    st.title("⏰ SLA Monitoring Center")
    
    st.subheader("Tickets by Priority - SLA Status")
    
    for priority in ["P1", "P2", "P3", "P4"]:
        priority_df = df[df["priority"] == priority]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(f"Total {priority} Tickets", len(priority_df))
        
        with col2:
            if len(priority_df) > 0:
                breached = len(priority_df[priority_df["resolution_time_hours"] > priority_df["sla_level"]])
                st.metric(f"SLA Breaches", breached)
        
        with col3:
            if len(priority_df) > 0:
                compliance = len(priority_df[priority_df["resolution_time_hours"] <= priority_df["sla_level"]]) / len(priority_df) * 100
                st.metric(f"SLA Compliance", f"{compliance:.1f}%")
        
        with col4:
            st.metric(f"SLA Time", f"{priority_df['sla_level'].iloc[0]}h")
        
        # Display tickets table
        if len(priority_df) > 0:
            display_cols = ["ticket_id", "subject", "status", "assigned_team", "resolution_time_hours", "sla_level", "creation_date"]
            st.dataframe(priority_df[display_cols], use_container_width=True, height=200)
        
        st.markdown("---")

def page_agent_performance():
    """Agent Performance - Team Performance Dashboard"""
    st.title("👨‍💼 Agent Performance Dashboard")
    
    st.subheader("Agent Leaderboard")
    
    # Create agent performance data
    agents = df["assigned_team"].unique()[:15]  # Top 15 teams
    
    agent_stats = []
    for agent in agents:
        agent_df = df[df["assigned_team"] == agent]
        resolved = len(agent_df[agent_df["status"] == "Closed"])
        total = len(agent_df)
        resolution_rate = (resolved / total * 100) if total > 0 else 0
        avg_resolution_time = agent_df[agent_df["status"] == "Closed"]["resolution_time_hours"].mean() if resolved > 0 else 0
        escalation_rate = len(agent_df[agent_df["status"] == "On Hold"]) / total * 100 if total > 0 else 0
        satisfaction = random.randint(3, 5)
        
        agent_stats.append({
            "Agent/Team": agent,
            "Tickets": total,
            "Resolved": resolved,
            "Resolution Rate": f"{resolution_rate:.1f}%",
            "Avg Time (hrs)": f"{avg_resolution_time:.1f}",
            "Escalations": len(agent_df[agent_df["status"] == "On Hold"]),
            "Satisfaction": f"⭐ {satisfaction}/5"
        })
    
    agent_df_display = pd.DataFrame(agent_stats)
    st.dataframe(agent_df_display, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resolution Rate by Team")
        team_resolution = []
        for agent in agents[:10]:
            agent_data = df[df["assigned_team"] == agent]
            resolved = len(agent_data[agent_data["status"] == "Closed"])
            total = len(agent_data)
            rate = (resolved / total * 100) if total > 0 else 0
            team_resolution.append({"team": agent, "rate": rate})
        
        team_res_df = pd.DataFrame(team_resolution)
        fig = px.bar(team_res_df, x="team", y="rate",
                    labels={'team': 'Team', 'rate': 'Resolution Rate %'},
                    color="rate", color_continuous_scale='Greens')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Ticket Load Distribution")
        team_load = []
        for agent in agents[:10]:
            count = len(df[df["assigned_team"] == agent])
            team_load.append({"team": agent, "tickets": count})
        
        team_load_df = pd.DataFrame(team_load)
        fig = px.bar(team_load_df, x="team", y="tickets",
                    labels={'team': 'Team', 'tickets': 'Ticket Count'},
                    color="tickets", color_continuous_scale='Blues')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def page_ai_insights():
    """AI Insights - Insights and Predictive Panel"""
    st.title("💡 AI Insights & Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Complaint Drivers")
        subjects = df["subject"].value_counts().head(10)
        fig = px.bar(x=subjects.values, y=subjects.index, orientation='h',
                    labels={'x': 'Frequency', 'y': 'Subject'},
                    color=subjects.values, color_continuous_scale='Reds')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Emerging Issues (Week-over-Week Growth)")
        categories = df["category"].value_counts().head(8)
        growth_data = []
        for cat in categories.index:
            growth_data.append({"category": cat, "growth": random.randint(-5, 15)})
        growth_df = pd.DataFrame(growth_data)
        fig = px.bar(growth_df, x="category", y="growth",
                    labels={'category': 'Category', 'growth': 'WoW Growth %'},
                    color="growth", color_continuous_scale='RdYlGn_r')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("High-Risk Categories")
        risk_data = []
        for cat in df["category"].unique()[:10]:
            cat_df = df[df["category"] == cat]
            avg_satisfaction = random.randint(2, 5)
            escalation_rate = len(cat_df[cat_df["status"] == "On Hold"]) / len(cat_df) * 100 if len(cat_df) > 0 else 0
            risk_data.append({"category": cat, "risk_score": escalation_rate})
        
        risk_df = pd.DataFrame(risk_data).sort_values("risk_score", ascending=True).tail(8)
        fig = px.bar(risk_df, x="risk_score", y="category", orientation='h',
                     labels={'risk_score': 'Risk Score', 'category': 'Category'},
                     color="risk_score", color_continuous_scale='Reds')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Predicted SLA Breaches (Next 24h)")
        upcoming_breaches = []
        sample_df = df[df["status"] == "Open"].head(20)
        for idx, row in sample_df.iterrows():
            sla_time = row["sla_level"]
            breach_risk = random.choice([True, False]) if random.random() > 0.7 else False
            if breach_risk:
                upcoming_breaches.append({"ticket": row["ticket_id"], "risk": "HIGH"})
        
        if upcoming_breaches:
            breach_df = pd.DataFrame(upcoming_breaches)
            st.write(f"⚠️ {len(breach_df)} tickets at risk of SLA breach")
            st.dataframe(breach_df, use_container_width=True)
        else:
            st.info("✅ No predicted SLA breaches in next 24 hours")

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def page_ticket_creation():
    """Ticket Creation - Customer Complaint Submission"""
    st.title("📝 Create New Complaint Ticket")
    
    # Initialize form state
    if "form_success" not in st.session_state:
        st.session_state.form_success = False
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    st.markdown("""
    <div style='background: #f0f7ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #1f77b4; margin-bottom: 1.5rem;'>
        <p style='margin: 0; color: #333;'><strong>📋 Instructions:</strong> Please provide detailed information about your complaint. Our AI will automatically classify and route your ticket to the appropriate team.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("👤 Customer Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input(
            "Customer Name *",
            placeholder="Enter your full name",
            value=st.session_state.form_data.get("customer_name", "")
        )
        customer_email = st.text_input(
            "Customer Email *",
            placeholder="Enter your email address",
            value=st.session_state.form_data.get("customer_email", "")
        )
    
    with col2:
        customer_type = st.selectbox(
            "Customer Type *",
            ["Existing Customer", "Prospect", "Partner", "Enterprise"],
            index=0
        )
        customer_phone = st.text_input(
            "Phone (Optional)",
            placeholder="Enter your phone number",
            value=st.session_state.form_data.get("customer_phone", "")
        )
    
    st.markdown("---")
    
    # Default values for auto-filled fields
    language = "English"
    product_version = "v2.0"
    channel = "Web"
    
    st.subheader("📝 Complaint Description")
    
    complaint_text = st.text_area(
        "Complaint Description *",
        placeholder="Please describe your issue in detail (minimum 20 characters)\n\nExample: 'I am unable to access the dashboard after updating to the latest version...'",
        height=150,
        value=st.session_state.form_data.get("complaint_text", "")
    )
    
    # Character counter
    char_count = len(complaint_text)
    min_chars = 20
    
    if char_count < min_chars:
        st.warning(f"⚠️ Please enter at least {min_chars} characters. Current: {char_count}/{min_chars}")
    else:
        st.success(f"✅ Character count: {char_count} (minimum {min_chars} met)")
    
    st.markdown("---")
    
    # Form validation and submission
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        submit_button = st.button("🤖 Analyze & Submit", use_container_width=True, type="primary")
    
    with col2:
        clear_button = st.button("🔄 Clear Form", use_container_width=True)
    
    with col3:
        pass
    
    if clear_button:
        st.session_state.form_data = {}
        st.session_state.form_success = False
        st.rerun()
    
    # Validation and submission
    if submit_button:
        # Validation checks
        errors = []
        
        if not customer_name or not customer_name.strip():
            errors.append("❌ Customer Name is required")
        
        if not customer_email or not customer_email.strip():
            errors.append("❌ Customer Email is required")
        elif not validate_email(customer_email):
            errors.append("❌ Please enter a valid email address")
        
        if char_count < min_chars:
            errors.append(f"❌ Complaint description must be at least {min_chars} characters (current: {char_count})")
        
        if not complaint_text or not complaint_text.strip():
            errors.append("❌ Complaint description is required")
        
        # Show validation errors
        if errors:
            for error in errors:
                st.error(error)
            st.stop()
        
        # Store form data for potential re-use
        st.session_state.form_data = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "complaint_text": complaint_text,
        }
        
        # Show loading spinner and analyze
        with st.spinner("🔍 Analyzing complaint with AI (this may take a moment)..."):
            import time
            time.sleep(1.5)  # Simulate AI analysis time
            
            # Simulate AI analysis
            categories = [
                "Technical Support", "Product Support", "Customer Service", "IT Support",
                "Billing & Payment", "Return & Exchange", "Service Outage", "Maintenance",
                "Sales", "Pre-Sales", "Human Resources", "General Inquiry"
            ]
            
            departments = ["Support", "Sales", "Billing", "Operations", "IT", "HR"]
            
            pred_category = random.choice(categories)
            pred_department = random.choice(departments)
            pred_priority = np.random.choice(["P1", "P2", "P3", "P4"], p=[0.05, 0.15, 0.35, 0.45])
            
            teams_map = {
                "Support": ["L1 Support", "L2 Support", "L3 Support"],
                "Sales": ["Inside Sales", "Sales Engineering"],
                "Billing": ["Billing Team", "Finance"],
                "Operations": ["Operations Team"],
                "IT": ["IT Support", "Infrastructure"],
                "HR": ["HR Team"]
            }
            
            pred_team = random.choice(teams_map.get(pred_department, ["Support Team"]))
            pred_sentiment = random.choice(["Positive", "Negative", "Neutral"])
            pred_intent = random.choice(["Support Request", "Complaint", "Feedback"])
            pred_confidence = round(random.uniform(0.75, 0.99), 2)
            
            sla_times = {"P1": 4, "P2": 8, "P3": 24, "P4": 48}
            pred_sla = sla_times[pred_priority]
        
        st.success("✅ Analysis complete!")
        
        st.markdown("---")
        
        st.subheader("📊 AI Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 Auto-Detected Information:**
            """)
            st.write(f"**Category:** `{pred_category}`")
            st.write(f"**Subcategory:** `{pred_category} - Issue`")
            st.write(f"**Department:** `{pred_department}`")
            st.write(f"**Assigned Team:** `{pred_team}`")
        
        with col2:
            st.markdown("""
            **📈 Analysis Metrics:**
            """)
            st.write(f"**Priority Level:** `{pred_priority}`")
            st.write(f"**Sentiment Analysis:** `{pred_sentiment}`")
            st.write(f"**Intent Classification:** `{pred_intent}`")
            st.write(f"**Confidence Score:** `{pred_confidence:.1%}`")
        
        st.markdown("---")
        
        st.subheader("📋 Ticket Submission Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 8px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.05em;'>SLA Time</div>
                <div style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{pred_sla}h</div>
                <div style='font-size: 0.85rem; opacity: 0.8;'>Response Target</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f57c00 0%, #ff5722 100%); padding: 1.5rem; border-radius: 8px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.05em;'>Status</div>
                <div style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>OPEN</div>
                <div style='font-size: 0.85rem; opacity: 0.8;'>New Ticket</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Create new ticket
        new_ticket_id = f"TKT-{2024000 + len(df) + st.session_state.new_tickets_count + 1}"
        st.session_state.new_tickets_count += 1
        
        new_record = {
            "ticket_id": new_ticket_id,
            "subject": complaint_text[:80],
            "complaint_body": complaint_text,
            "ai_summary": complaint_text[:150],
            "department": pred_department,
            "category": pred_category,
            "subcategory": f"{pred_category} - Issue",
            "customer_type": customer_type,
            "priority": pred_priority,
            "sla_level": pred_sla,
            "status": "Open",
            "assigned_team": pred_team,
            "language": language,
            "product_version": product_version,
            "sentiment": pred_sentiment,
            "intent": pred_intent,
            "confidence_score": pred_confidence,
            "tag_1": "auto-created",
            "tag_2": pred_category.replace(" ", "-").lower(),
            "tag_3": pred_priority,
            "creation_date": datetime.now(),
            "resolution_date": None,
            "resolution_time_hours": None,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone or "N/A",
        }
        
        # Add to dataframe
        st.session_state.complaint_data = pd.concat(
            [st.session_state.complaint_data, pd.DataFrame([new_record])],
            ignore_index=True
        )
        
        # Success message with ticket details
        sla_expiration = (datetime.now() + timedelta(hours=pred_sla)).strftime('%Y-%m-%d %H:%M')
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%); color: white; padding: 2rem; border-radius: 12px; margin-top: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.15);'>
            <h2 style='color: white; margin-top: 0;'>✅ Ticket Created Successfully!</h2>
            <table style='width: 100%; color: white; margin: 1rem 0;'>
                <tr>
                    <td style='padding: 0.5rem;'><strong>Ticket ID:</strong></td>
                    <td style='padding: 0.5rem; font-family: monospace; font-weight: bold; background: rgba(0,0,0,0.2); border-radius: 4px;'>{new_ticket_id}</td>
                </tr>
                <tr>
                    <td style='padding: 0.5rem;'><strong>Routed To:</strong></td>
                    <td style='padding: 0.5rem;'>{pred_team} ({pred_department})</td>
                </tr>
                <tr>
                    <td style='padding: 0.5rem;'><strong>Priority:</strong></td>
                    <td style='padding: 0.5rem;'>{pred_priority} - SLA: {pred_sla} hours</td>
                </tr>
                <tr>
                    <td style='padding: 0.5rem;'><strong>SLA Expiration:</strong></td>
                    <td style='padding: 0.5rem;'>{sla_expiration}</td>
                </tr>
                <tr>
                    <td style='padding: 0.5rem;'><strong>Confirmation Email:</strong></td>
                    <td style='padding: 0.5rem;'>{customer_email}</td>
                </tr>
            </table>
            <p style='margin: 1rem 0 0 0; opacity: 0.9;'>📧 You will receive updates and status notifications at {customer_email}. Track your ticket using the <strong>Complaint Explorer</strong> page.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Next steps
        st.subheader("🚀 Next Steps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **What happens next?**
            
            1. Your ticket has been automatically analyzed by our AI system
            2. It has been routed to the appropriate team based on the category
            3. Your assigned team will review and begin working on your issue
            4. You'll receive email notifications at each milestone
            5. You can track progress in the **Complaint Explorer** page
            """)
        
        with col2:
            st.markdown("""
            **Useful Resources**
            
            - 🔍 **Complaint Explorer**: Track all tickets and their status
            - 📊 **Dashboard**: View overall system metrics
            - ⏰ **SLA Monitor**: Check SLA compliance and deadlines
            - 💡 **AI Insights**: See trending issues and predictions
            - ⚙️ **Settings**: Manage your preferences
            """)
        
        # Clear form after successful submission
        st.session_state.form_data = {}
        st.session_state.form_success = True

def page_settings():
    """Settings - User Preferences"""
    st.title("⚙️ Settings")
    
    st.subheader("Display Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.radio("Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "light" else 1)
        st.session_state.theme = theme.lower()
        
        rows_per_page = st.selectbox("Rows per page in tables",
                                    [10, 25, 50, 100],
                                    index=[10, 25, 50, 100].index(st.session_state.rows_per_page))
        st.session_state.rows_per_page = rows_per_page
    
    with col2:
        st.write("**Animation Settings**")
        animations = st.checkbox("Enable chart animations", value=True)
        
        st.write("**Notification Settings**")
        sla_alerts = st.checkbox("SLA breach alerts", value=True)
        high_priority_alerts = st.checkbox("High priority alerts (P1/P2)", value=True)
    
    st.markdown("---")
    
    st.subheader("About")
    st.write("""
    **AI-Powered Customer Complaint Classification & Routing Engine**
    
    📊 Version: 1.0.0
    🛠️ Built with: Streamlit, Pandas, Plotly
    📅 Last Updated: 2024-06-12
    
    **Demo Data:**
    - Total Records: 5,000+
    - Time Period: Last 90 days
    - Languages: 5+ (English, Spanish, French, German, Portuguese)
    - Categories: 12 complaint types
    - Teams: 20+ routing teams
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset Demo Data", use_container_width=True):
            st.session_state.complaint_data = None
            st.success("✅ Demo data reset. Page will refresh...")
            st.rerun()
    
    with col2:
        if st.button("📋 View System Info", use_container_width=True):
            st.write(f"""
            **Current Session:**
            - User: {st.session_state.username}
            - Total Records: {len(df)}
            - New Tickets Created: {st.session_state.new_tickets_count}
            - Timestamp: {datetime.now()}
            """)

# ==============================================================================
# MAIN APP ROUTER
# ==============================================================================

def main():
    """Main application router"""
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <div style='font-size: 2rem;'>🎯</div>
            <h2 style='color: #1f77b4; margin: 0;'>AI Complaint Engine</h2>
            <p style='color: #999; font-size: 0.85rem; margin: 0;'>Enterprise Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.write(f"👤 **Logged in as:** `{st.session_state.username}`")
        
        st.markdown("---")
        
        pages = [
            ("📊", "Dashboard"),
            ("🔍", "Complaint Explorer"),
            ("🤖", "AI Classification"),
            ("🔀", "Routing Engine"),
            ("📈", "Analytics"),
            ("⏰", "SLA Monitor"),
            ("👨‍💼", "Agent Performance"),
            ("💡", "AI Insights"),
            ("📝", "Ticket Creation"),
            ("⚙️", "Settings"),
        ]
        
        st.write("**Navigation**")
        for icon, page_name in pages:
            if st.button(f"{icon} {page_name}", use_container_width=True,
                        key=f"nav_{page_name}"):
                st.session_state.page = page_name
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
    
    # Route to page
    if st.session_state.page == "Dashboard":
        page_dashboard()
    elif st.session_state.page == "Complaint Explorer":
        page_complaint_explorer()
    elif st.session_state.page == "AI Classification":
        page_ai_classification()
    elif st.session_state.page == "Routing Engine":
        page_routing_engine()
    elif st.session_state.page == "Analytics":
        page_analytics()
    elif st.session_state.page == "SLA Monitor":
        page_sla_monitor()
    elif st.session_state.page == "Agent Performance":
        page_agent_performance()
    elif st.session_state.page == "AI Insights":
        page_ai_insights()
    elif st.session_state.page == "Ticket Creation":
        page_ticket_creation()
    elif st.session_state.page == "Settings":
        page_settings()
    else:
        page_dashboard()

if __name__ == "__main__":
    main()
