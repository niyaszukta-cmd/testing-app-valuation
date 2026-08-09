import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import time
from functools import wraps
from io import BytesIO
import statistics
from urllib.parse import quote
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================.
st.set_page_config(
    page_title="NYZTrade Stock Valuation + Screener Professional dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MOBILE-OPTIMIZED CSS STYLING
# ============================================================================.
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0 1rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header h3 {
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    .main-header p {
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.8;
    }
    
    .auth-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem 1rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
        padding: 0 0.5rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 0.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stat-card h3 {
        font-size: 1.5rem;
        margin: 0 0 0.25rem 0;
        font-weight: 600;
    }
    
    .stat-card p {
        font-size: 0.8rem;
        margin: 0;
        opacity: 0.9;
    }
    
    .highlight-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1));
        border: 2px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-message {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.15));
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #059669;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid rgba(124, 58, 237, 0.3);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.15);
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #a78bfa;
        margin: 0.3rem 0;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #c4b5fd;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.3;
    }
    
    .company-header {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 15px;
        padding: 1.5rem 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(167, 139, 250, 0.3);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.15);
    }
    
    .company-title {
        font-size: 1.8rem;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
        font-weight: 700;
        line-height: 1.3;
    }
    
    .company-info {
        color: #a78bfa;
        font-size: 0.9rem;
        margin: 0.15rem 0;
        line-height: 1.4;
    }
    
    .fair-value-card {
        background: linear-gradient(135deg, #059669, #10b981);
        border-radius: 15px;
        padding: 1.5rem 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        margin: 1rem 0;
    }
    
    .fair-value-title {
        font-size: 1rem;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    
    .fair-value-amount {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 1rem 0;
        line-height: 1.2;
    }
    
    .fair-value-details {
        font-size: 0.9rem;
        opacity: 0.8;
        line-height: 1.4;
    }
    
    .section-header {
        font-size: 1.3rem;
        color: #a78bfa;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(167, 139, 250, 0.3);
        font-weight: 600;
    }
    
    .recommendation-card {
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }
    
    .rec-strong-buy {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
    }
    
    .rec-buy {
        background: linear-gradient(135deg, #0891b2, #06b6d4);
        color: white;
    }
    
    .rec-hold {
        background: linear-gradient(135deg, #ca8a04, #eab308);
        color: white;
    }
    
    .rec-avoid {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
    }
    
    .valuation-box {
        background: rgba(30, 27, 75, 0.6);
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    
    .valuation-method {
        color: #a78bfa;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .valuation-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.4rem 0;
        padding: 0.4rem;
        border-radius: 6px;
        background: rgba(167, 139, 250, 0.05);
        font-size: 0.9rem;
    }
    
    .valuation-label {
        color: #c4b5fd;
        font-weight: 500;
    }
    
    .valuation-value {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    .welcome-section {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(167, 139, 250, 0.1));
        border-radius: 15px;
        padding: 2rem 1rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    .welcome-title {
        font-size: 2rem;
        color: #a78bfa;
        margin-bottom: 1rem;
        font-weight: 700;
        line-height: 1.3;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #c4b5fd;
        margin-bottom: 1.5rem;
        line-height: 1.4;
    }
    
    .feature-list {
        text-align: left;
        max-width: 600px;
        margin: 0 auto;
        color: #e2e8f0;
    }
    
    .feature-list li {
        margin: 0.4rem 0;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* 52-week range styling */
    .range-container {
        background: rgba(30, 27, 75, 0.6);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }
    
    .range-labels {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: #a78bfa;
    }
    
    .range-bar {
        width: 100%;
        height: 18px;
        background: linear-gradient(90deg, #dc2626 0%, #eab308 50%, #059669 100%);
        border-radius: 9px;
        position: relative;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .range-indicator {
        position: absolute;
        top: -3px;
        width: 4px;
        height: 24px;
        background: #e2e8f0;
        border-radius: 2px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    .range-info {
        text-align: center;
        margin-top: 1rem;
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Footer styling */
    .footer {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        color: #c4b5fd;
        text-align: center;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        margin-top: 2rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    
    .disclaimer {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 1rem;
        font-style: italic;
        line-height: 1.4;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem 0.5rem;
            margin: 0.25rem 0 0.75rem 0;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header h3 {
            font-size: 1rem;
        }
        
        .main-header p {
            font-size: 0.8rem;
        }
        
        .stats-container {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            padding: 0 0.25rem;
        }
        
        .stat-card {
            padding: 0.75rem 0.5rem;
        }
        
        .stat-card h3 {
            font-size: 1.2rem;
        }
        
        .company-title {
            font-size: 1.4rem;
        }
        
        .fair-value-amount {
            font-size: 1.8rem;
        }
        
        .welcome-title {
            font-size: 1.6rem;
        }
        
        .metric-card {
            padding: 0.75rem;
            min-height: 85px;
        }
        
        .metric-value {
            font-size: 1.2rem;
        }
        
        .metric-label {
            font-size: 0.7rem;
        }
        
        .valuation-row {
            font-size: 0.8rem;
            padding: 0.3rem;
        }
        
        .section-header {
            font-size: 1.1rem;
        }
    }
    
    @media (max-width: 480px) {
        .stats-container {
            grid-template-columns: 1fr;
        }
        
        .main-header h1 {
            font-size: 1.3rem;
        }
        
        .company-title {
            font-size: 1.2rem;
        }
        
        .fair-value-amount {
            font-size: 1.6rem;
        }
        
        .metric-value {
            font-size: 1rem;
        }
    }
    
    /* Ensure proper contrast and visibility */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stButton > button {
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    /* Fix potential black screen issues */
    .stApp > div {
        background: transparent !important;
    }
    
    .main > div {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PASSWORD AUTHENTICATION
# ============================================================================
def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "nytddemo", "premium": "zuktasempire", "niyas": "buffett123"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("""
        <div class="auth-container">
            <h1>🎯 NYZTrade Comprehensive Platform</h1>
            <h3>Professional Stock Analysis & Screening</h3>
            <p>Advanced Valuation • Industry Screening • Portfolio Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("👤 Username", key="username", placeholder="Enter username")
            st.text_input("🔒 Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True, type="primary")
            
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect credentials. Please try again.")
        return False
    return True

if not check_password():
    st.stop()

# ============================================================================
# COMPREHENSIVE INDIAN STOCKS DATABASE
# ============================================================================
"""
Indian Stocks Database
Generated from stocks_universe_categorized_enhanced.csv
Total Categories: 117
Total Stocks: 8984
"""

"""
Indian Stocks Database
Generated from stocks_universe_categorized_enhanced.csv
Total Categories: 117
Total Stocks: 8984
"""

INDIAN_STOCKS = {
    "Advertising Agencies": {
        "AMMLTD.BO": "Appu Marketing & Manufacturing",
        "GOVMC.BO": "GOOD VALUE MARKETING CO.LTD.",
        "NEERAJ.BO": "NEERAJ PAPER MARKETING LIMITED",
        "PRESSMN.BO": "PRESSMAN ADVERTISING LIMITED",
        "PRESSMN.NS": "Pressman Advertising Limited",
        "SPECMKT.BO": "SPECULAR MARKETING & FINANCING",
        "SURYAMARK.BO": "SURYA MARKETING LTD"
    },

    "Aerospace/Defense - Major Diversified": {
        "ABGSHIP.NS": "ABG Shipyard Limited",
        "BEL.NS": "Bharat Electronics Limited",
        "BHARATIDIL.NS": "Bharati Defence And Infrastructure Limited",
        "RDEL.NS": "Reliance Defence and Engineering Limited",
        "COCHINSHIP.BO": "COCHIN SHIPYARD LTD."
    },

    "Agricultural Chemicals": {
        "AGRITECH.NS": "Agri-Tech (India) Ltd",
        "AGRODUTCH-BE.NS": "AGRO DUTCH INDUSTRIES LTD",
        "AGRODUTCH.BO": "AGRO DUTCH INDUSTRIES LTD.",
        "ARIES.NS": "ARIES AGRO LIMITED",
        "ARIES.BO": "Aries Agro Limited",
        "ARIES.NS": "Aries Agro Limited",
        "ASHAI.BO": "Ashiana Agro Industries Ltd.",
        "ASIANFR.BO": "ASIAN FERTILIZERS LTD.",
        "BAMBINO.BO": "Bambino Agro Industries Ltd.",
        "BAYERCROP.NS": "Bayer CropScience Limited",
        "BELAGRO.BO": "Bell Agromachina Ltd.",
        "BHARATRAS.NS": "Bharat Rasayan Limited",
        "BHASKAGR.BO": "BHASKAR AGROCHEMICALS LTD.",
        "CHAMBLFERT.NS": "Chambal Fertilisers and Chemicals Limited",
        "COROMANDEL.NS": "Coromandel International Limited",
        "CRYPTAG.BO": "CRYPTOGEN AGRO INDUSTRIES LTD.",
        "DEEPAKFERT.NS": "DEEPAK FERTILIZERS AND PETROCHE",
        "DEEPAKFERT.NS": "Deepak Fertilisers And Petrochemicals Corporation Limited",
        "DHANUKA.NS": "Dhanuka Agritech Limited",
        "DHARNAG.BO": "DHARNENDRA AGRO FOOD INDUSTRIE",
        "EXCELCROP.NS": "Excel Crop Care Limited",
        "FACT.NS": "The Fertilisers And Chemicals Travancore Limited",
        "GNFC.NS": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
        "GOKULAGRO.BO": "Gokul Agro Resources Ltd",
        "GREENFIRE.NS": "Proseed India Limited",
        "GSFC.NS": "Gujarat State Fertilizers & Chemicals Limited",
        "HATSUN.NS": "HATSUN AGRO PRODUC INR1",
        "HATSUN.BO": "Hatsun Agro Product Limited",
        "HERUKAG.BO": "HERUK AGRO FOODS LTD.",
        "IFBAGRO.BO": "IFB AGRO INDUSTRIES LTD.",
        "INSECTICID.NS": "Insecticides (India) Limited",
        "JAYAGROGN.NS": "JAYANT AGRO ORGANICS LIMITED",
        "JAYAGROGN.BO": "JAYANT AGRO-ORGANICS LTD.",
        "JVLAGRO.BO": "JVL Agro Industries Ltd",
        "KGNAGRO.BO": "KGN AGRO INTERNATIONALS LTD.",
        "MADRASFERT.NS": "MADRAS FERTILIZERS INR10(DEMAT)",
        "MADRASFERT.BO": "Madras Fertilizer Limited",
        "MADRASFERT.NS": "Madras Fertilizers Limited",
        "MANGCHEFER.NS": "Mangalore Chemicals & Fertilizers Limited",
        "MAYAGRP.BO": "MAYA AGRO PRODUCTS LTD.",
        "MEGH.NS": "Meghmani Organics Limited",
        "MONESHIA.BO": "MONESHI AGRO INDUSTRIES LTD.",
        "MONSANTO.NS": "Monsanto India Limited",
        "MPAGI.BO": "M. P. Agro Industries Ltd",
        "NAPL.BO": "Naturite Agro Products Limited",
        "NATHBIOGEN.NS": "Nath Bio-Genes (India) Limited",
        "NEAGI.BO": "Neelamalai Agro Industries Ltd.",
        "NEPCAGRO.BO": "NEPC AGRO FOODS LTD.",
        "NFL.BO": "National Fertilizers Ltd.",
        "NFL.NS": "National Fertilizers Limited",
        "NIJJER.BO": "NIJJER AGRO FOODS LTD.",
        "OCEAGRO.BO": "Ocean Agro (India) Limited",
        "OSWALAGRO.BO": "OSWAL AGRO MILLS LTD.",
        "PARKERAC.BO": "Parker Agrochem Exports Ltd.",
        "PICCADIL.BO": "Piccadily Agro Industries Limited",
        "PIIND.NS": "PI Industries Limited",
        "PIONAGR.BO": "Pioneer Agro Extracts Ltd",
        "PRIMAGR.BO": "Prima Agro Limited",
        "RAASHIF.BO": "RAASHI FERTILIZERS LTD.",
        "RAFL.BO": "Raghuvansh Agrofarms Limited",
        "RAJAGRO.BO": "Raj Agro Mills Ltd.",
        "RALLIS.NS": "Rallis India Limited",
        "RATNAMAGRO.BO": "RATNAMANI AGRO INDUSTRIES LTD",
        "RCF.NS": "Rashtriya Chemicals And Fertilizers Limited",
        "REIAGROLTD-BE.NS": "REI AGRO LTD INR1",
        "REIAGROLTD.NS": "REI AGRO LTD INR1",
        "REIAGROLTD.BO": "REI AGRO LTD.",
        "REIAGROLTD6.BO": "REIAGROLTD6.BO",
        "RKB.BO": "RKB AGRO INDUSTRIES LIMITED",
        "SANJAG.BO": "SANJIVANI AGRO INDUSTRIES LTD.",
        "SATGAGR.BO": "SATGURU AGRO INDUSTRIES LTD.",
        "SEASTAG.BO": "SOUTH EAST AGRO INDUSTRIES LTD",
        "SH-ANJY.BO": "SHRI ANJANEY AGRO FOODS LTD.",
        "SHARDACROP.NS": "Sharda Cropchem Limited",
        "SHIVAAGRO.BO": "SHIVA GLOBAL AGRO INDUSTRIES L",
        "SPIC.NS": "Southern Petrochemical Industries Corporation Limited",
        "SPTRSHI.BO": "Saptarishi Agro Industries Limited",
        "SUNILAGR.BO": "Sunil Agro Foods Ltd",
        "SYPAGFD.BO": "SYP AGRO FOODS LTD.",
        "TEEAI.BO": "Teesta Agro Industries Ltd.",
        "UMREAGR.BO": "CIAN AGRO IND & INFRA LTD",
        "UNQAGRO.BO": "UNIQUE AGRO PROCESSORS (INDIA)",
        "UPL.NS": "UPL Limited",
        "USHERAGRO.BO": "USHER AGRO LTD.",
        "VITANAGRO.BO": "VITAN AGRO INDUSTRIES LTD",
        "VRUNAGR.BO": "VARUNA AGROPROTEINS LTD.",
        "ZUARI.BO": "ZUARI AGRO CHEMICALS LTD.",
        "ZUARI.NS": "Zuari Agro Chemicals Limited",
        "ZUARIGLOB.NS": "Zuari Global Limited"
    },

    "Air Delivery & Freight Services": {
        "ALLCARGO.NS": "Allcargo Logistics Limited",
        "ARSHIYA.NS": "Arshiya Limited",
        "BLUEDART.NS": "Blue Dart Express Limited",
        "CONCOR.NS": "Container Corporation of India Limited",
        "GATI.NS": "Gati Limited",
        "GDL.NS": "Gateway Distriparks Limited",
        "NAVKARCORP.NS": "Navkar Corporation Limited",
        "PATINTLOG.NS": "Patel Integrated Logistics Limited",
        "SICAL.NS": "Sical Logistics Limited",
        "SNOWMAN.NS": "Snowman Logistics Limited",
        "TCI.NS": "Transport Corporation of India Limited"
    },

    # ========================================================================
    # >>> ADD THE REST OF YOUR CATEGORY LISTS BELOW, IN THE SAME FORMAT <<<
    #
    #     "Category Name": {
    #         "TICKER.NS": "Company Name",
    #         "TICKER2.NS": "Company Name 2"      <- last entry: no comma
    #     },
    # ========================================================================

}

# ============================================================================
# COMPREHENSIVE INDUSTRY-SPECIFIC BENCHMARKS SYSTEM
# ============================================================================

# Industry-specific benchmarks based on Indian market analysis
INDUSTRY_BENCHMARKS = {
    # Financial Services - Industry Specific
    "Credit Services": {'pe': 16.0, 'pb': 2.8, 'roe': 18.0, 'ev_ebitda': 10.0, 'debt_equity': 4.5},
    "Financial Services": {'pe': 15.0, 'pb': 2.2, 'roe': 16.0, 'ev_ebitda': 9.0, 'debt_equity': 3.8},
    "Insurance - Life": {'pe': 20.0, 'pb': 2.0, 'roe': 14.0, 'ev_ebitda': 12.0, 'debt_equity': 0.2},
    "Insurance - Property & Casualty": {'pe': 18.0, 'pb': 1.8, 'roe': 15.0, 'ev_ebitda': 11.0, 'debt_equity': 0.3},
    "Money Center Banks": {'pe': 12.0, 'pb': 1.2, 'roe': 15.0, 'ev_ebitda': 8.0, 'debt_equity': 0.1},
    
    # Technology - Industry Specific
    "Information Technology Services": {'pe': 24.0, 'pb': 4.2, 'roe': 22.0, 'ev_ebitda': 16.0, 'debt_equity': 0.1},
    "Wireless Communications": {'pe': 18.0, 'pb': 2.8, 'roe': 16.0, 'ev_ebitda': 12.0, 'debt_equity': 1.2},
    
    # Healthcare & Pharma - Industry Specific
    "Drug Manufacturers - Major": {'pe': 26.0, 'pb': 3.2, 'roe': 18.0, 'ev_ebitda': 15.0, 'debt_equity': 0.3},
    "Drug Manufacturers - Other": {'pe': 28.0, 'pb': 3.5, 'roe': 16.0, 'ev_ebitda': 16.0, 'debt_equity': 0.2},
    "Medical Services": {'pe': 32.0, 'pb': 3.8, 'roe': 17.0, 'ev_ebitda': 18.0, 'debt_equity': 0.8},
    
    # Auto & Manufacturing - Industry Specific  
    "Auto Manufacturers - Major": {'pe': 18.0, 'pb': 2.2, 'roe': 14.0, 'ev_ebitda': 10.0, 'debt_equity': 0.8},
    "Auto Parts": {'pe': 22.0, 'pb': 2.8, 'roe': 16.0, 'ev_ebitda': 12.0, 'debt_equity': 0.6},
    "Diversified Electronics": {'pe': 24.0, 'pb': 3.0, 'roe': 17.0, 'ev_ebitda': 13.0, 'debt_equity': 0.4},
    "Diversified Machinery": {'pe': 20.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 11.0, 'debt_equity': 0.7},
    
    # Materials & Chemicals - Industry Specific
    "Steel & Iron": {'pe': 12.0, 'pb': 1.0, 'roe': 12.0, 'ev_ebitda': 6.0, 'debt_equity': 1.5},
    "Cement & Aggregates": {'pe': 16.0, 'pb': 1.8, 'roe': 13.0, 'ev_ebitda': 8.0, 'debt_equity': 1.0},
    "Chemicals - Major Diversified": {'pe': 22.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 12.0, 'debt_equity': 0.5},
    "Agricultural Chemicals": {'pe': 20.0, 'pb': 2.2, 'roe': 16.0, 'ev_ebitda': 11.0, 'debt_equity': 0.6},
    
    # Energy & Utilities - Industry Specific
    "Oil & Gas Operations": {'pe': 8.0, 'pb': 0.8, 'roe': 12.0, 'ev_ebitda': 5.0, 'debt_equity': 0.6},
    "Oil & Gas Refining & Marketing": {'pe': 10.0, 'pb': 1.0, 'roe': 10.0, 'ev_ebitda': 6.0, 'debt_equity': 0.8},
    "Electric Utilities": {'pe': 14.0, 'pb': 1.2, 'roe': 11.0, 'ev_ebitda': 8.0, 'debt_equity': 1.8},
    "Gas Utilities": {'pe': 16.0, 'pb': 1.5, 'roe': 12.0, 'ev_ebitda': 9.0, 'debt_equity': 1.5},
    "Renewable Energy": {'pe': 25.0, 'pb': 2.0, 'roe': 10.0, 'ev_ebitda': 12.0, 'debt_equity': 2.2},
    
    # Consumer - Industry Specific
    "Food - Major Diversified": {'pe': 35.0, 'pb': 4.5, 'roe': 18.0, 'ev_ebitda': 18.0, 'debt_equity': 0.3},
    "Jewelry Stores": {'pe': 25.0, 'pb': 2.8, 'roe': 16.0, 'ev_ebitda': 15.0, 'debt_equity': 0.4},
    "Retail - Apparel & Accessories": {'pe': 28.0, 'pb': 3.2, 'roe': 17.0, 'ev_ebitda': 16.0, 'debt_equity': 0.6},
    
    # Others
    "Real Estate Development": {'pe': 15.0, 'pb': 1.2, 'roe': 8.0, 'ev_ebitda': 12.0, 'debt_equity': 2.5},
    "Textile Industrial": {'pe': 18.0, 'pb': 1.5, 'roe': 12.0, 'ev_ebitda': 10.0, 'debt_equity': 0.9},
}

# Cap-size specific multipliers for benchmarks
CAP_SIZE_MULTIPLIERS = {
    'Large': {'pe': 1.0, 'pb': 1.0, 'ev_ebitda': 1.0},      # Base benchmarks
    'Mid': {'pe': 1.15, 'pb': 1.1, 'ev_ebitda': 1.1},       # 10-15% premium for growth
    'Small': {'pe': 1.25, 'pb': 1.2, 'ev_ebitda': 1.15}     # 15-25% premium for higher growth
}

# Sector mapping for fallback when industry not found
INDUSTRY_TO_SECTOR = {
    # Financial Services
    "Credit Services": "Financial Services", 
    "Financial Services": "Financial Services",
    "Insurance - Life": "Financial Services",
    "Insurance - Property & Casualty": "Financial Services",
    "Money Center Banks": "Financial Services",
    
    # Technology
    "Information Technology Services": "Technology",
    "Wireless Communications": "Technology",
    
    # Healthcare & Pharma
    "Drug Manufacturers - Major": "Healthcare & Pharma",
    "Drug Manufacturers - Other": "Healthcare & Pharma",
    "Medical Services": "Healthcare & Pharma",
    
    # Industrial & Manufacturing
    "Diversified Electronics": "Industrial & Manufacturing",
    "Diversified Machinery": "Industrial & Manufacturing",
    "Steel & Iron": "Industrial & Manufacturing",
    "Auto Manufacturers - Major": "Industrial & Manufacturing",
    "Auto Parts": "Industrial & Manufacturing",
    
    # Energy & Utilities
    "Electric Utilities": "Energy & Utilities",
    "Gas Utilities": "Energy & Utilities",
    "Oil & Gas Operations": "Energy & Utilities",
    "Oil & Gas Refining & Marketing": "Energy & Utilities",
    "Renewable Energy": "Energy & Utilities",
    
    # Consumer & Retail
    "Food - Major Diversified": "Consumer & Retail",
    "Jewelry Stores": "Consumer & Retail",
    "Retail - Apparel & Accessories": "Consumer & Retail",
    
    # Materials & Chemicals
    "Agricultural Chemicals": "Materials & Chemicals",
    "Cement & Aggregates": "Materials & Chemicals",
    "Chemicals - Major Diversified": "Materials & Chemicals",
    
    # Real Estate & Construction
    "Real Estate Development": "Real Estate & Construction",
    
    # Textiles
    "Textile Industrial": "Textiles"
}

# Fallback sector benchmarks
SECTOR_BENCHMARKS = {
    'Financial Services': {'pe': 15.0, 'pb': 2.0, 'roe': 16.0, 'ev_ebitda': 10.0},
    'Technology': {'pe': 24.0, 'pb': 4.0, 'roe': 22.0, 'ev_ebitda': 16.0},
    'Healthcare & Pharma': {'pe': 28.0, 'pb': 3.4, 'roe': 17.0, 'ev_ebitda': 16.0},
    'Industrial & Manufacturing': {'pe': 20.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 11.0},
    'Energy & Utilities': {'pe': 12.0, 'pb': 1.2, 'roe': 11.0, 'ev_ebitda': 7.0},
    'Consumer & Retail': {'pe': 30.0, 'pb': 3.5, 'roe': 17.0, 'ev_ebitda': 16.0},
    'Materials & Chemicals': {'pe': 18.0, 'pb': 2.0, 'roe': 14.0, 'ev_ebitda': 10.0},
    'Real Estate & Construction': {'pe': 15.0, 'pb': 1.2, 'roe': 8.0, 'ev_ebitda': 12.0},
    'Textiles': {'pe': 18.0, 'pb': 1.5, 'roe': 12.0, 'ev_ebitda': 10.0},
    'Other': {'pe': 20.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 12.0}
}

# ============================================================================
# TECHNICAL ANALYSIS FUNCTIONS
# ============================================================================
@st.cache_data(ttl=3600)
def fetch_price_history(ticker, period="3mo"):
    """Fetch historical price data for technical analysis"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        return hist
    except:
        return None

def calculate_supertrend(high, low, close, period=10, multiplier=3):
    """Calculate SuperTrend indicator"""
    try:
        # Calculate ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Calculate basic upper and lower bands
        hl_avg = (high + low) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        # Initialize SuperTrend
        supertrend = pd.Series(index=close.index, dtype=float)
        direction = pd.Series(index=close.index, dtype=int)
        
        # Calculate SuperTrend
        for i in range(1, len(close)):
            if pd.isna(upper_band.iloc[i]) or pd.isna(lower_band.iloc[i]):
                continue
                
            # Current upper and lower bands
            curr_upper = upper_band.iloc[i]
            curr_lower = lower_band.iloc[i]
            prev_close = close.iloc[i-1]
            curr_close = close.iloc[i]
            
            # Adjust bands
            if curr_upper < upper_band.iloc[i-1] or prev_close > upper_band.iloc[i-1]:
                upper_band.iloc[i] = curr_upper
            else:
                upper_band.iloc[i] = upper_band.iloc[i-1]
                
            if curr_lower > lower_band.iloc[i-1] or prev_close < lower_band.iloc[i-1]:
                lower_band.iloc[i] = curr_lower
            else:
                lower_band.iloc[i] = lower_band.iloc[i-1]
            
            # Determine trend direction
            if i == 1:
                direction.iloc[i] = 1 if curr_close <= lower_band.iloc[i] else -1
                supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
            else:
                prev_supertrend = supertrend.iloc[i-1]
                prev_direction = direction.iloc[i-1]
                
                if prev_direction == 1 and curr_close >= lower_band.iloc[i]:
                    direction.iloc[i] = -1
                    supertrend.iloc[i] = upper_band.iloc[i]
                elif prev_direction == -1 and curr_close <= upper_band.iloc[i]:
                    direction.iloc[i] = 1
                    supertrend.iloc[i] = lower_band.iloc[i]
                else:
                    direction.iloc[i] = prev_direction
                    supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
        
        # Return signal: 1 for bullish (price > supertrend), -1 for bearish
        signal = (close > supertrend).astype(int) * 2 - 1
        
        return {
            'supertrend': supertrend,
            'direction': direction,
            'signal': signal.iloc[-1] if len(signal) > 0 else 0,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
    except Exception as e:
        return None

def is_near_52w_high(price, high_52w, threshold=0.95):
    """Check if current price is near 52-week high"""
    if not price or not high_52w or high_52w <= 0:
        return False
    return (price / high_52w) >= threshold

def get_technical_signals(ticker):
    """Get comprehensive technical signals for a stock"""
    hist = fetch_price_history(ticker, period="6mo")
    if hist is None or len(hist) < 50:
        return None
    
    try:
        # Calculate SuperTrend
        supertrend_data = calculate_supertrend(
            hist['High'], 
            hist['Low'], 
            hist['Close']
        )
        
        if not supertrend_data:
            return None
        
        # Get current price and 52-week high
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].rolling(window=252).max().iloc[-1]
        
        # Additional technical indicators
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        # Volume trend
        avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
        recent_volume = hist['Volume'].iloc[-5:].mean()
        
        return {
            'supertrend_signal': supertrend_data['signal'],
            'supertrend_value': supertrend_data['supertrend'].iloc[-1] if not pd.isna(supertrend_data['supertrend'].iloc[-1]) else None,
            'near_52w_high': is_near_52w_high(current_price, high_52w),
            'price_vs_52w_high': (current_price / high_52w) if high_52w > 0 else 0,
            'above_sma20': current_price > sma_20 if not pd.isna(sma_20) else False,
            'above_sma50': current_price > sma_50 if not pd.isna(sma_50) else False,
            'volume_surge': recent_volume > avg_volume * 1.2 if avg_volume > 0 else False,
            'current_price': current_price
        }
    except Exception as e:
        return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_all_tickers():
    """Get list of all ticker symbols"""
    tickers = []
    for category_stocks in INDIAN_STOCKS.values():
        tickers.extend(category_stocks.keys())
    return tickers

def get_stocks_by_category(category):
    """Get stocks in a specific category"""
    return INDIAN_STOCKS.get(category, {})

def get_all_categories():
    """Get list of all categories"""
    return list(INDIAN_STOCKS.keys())

def search_stock(query):
    """Search for stocks by ticker or name"""
    results = {}
    query_upper = query.upper()
    
    for category, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query_upper in ticker.upper() or query_upper in name.upper():
                if category not in results:
                    results[category] = {}
                results[category][ticker] = name
    
    return results

def get_stock_info(ticker):
    """Get stock information by ticker"""
    for category, stocks in INDIAN_STOCKS.items():
        if ticker in stocks:
            return {
                "ticker": ticker,
                "name": stocks[ticker],
                "category": category
            }
    return None

def get_sector_for_industry(industry):
    """Get broad sector for a given industry"""
    return INDUSTRY_TO_SECTOR.get(industry, "Other")

# Statistics
TOTAL_STOCKS = sum(len(stocks) for stocks in INDIAN_STOCKS.values())
TOTAL_CATEGORIES = len(INDIAN_STOCKS)

# ============================================================================
# STOCK DATA FETCHING AND CACHING
# ============================================================================
def retry_with_backoff(retries=3, backoff_in_seconds=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator

@st.cache_data(ttl=3600)
@retry_with_backoff(retries=3, backoff_in_seconds=2)
def fetch_stock_data(ticker):
    """Fetch stock data with caching and retry mechanism"""
    try:
        time.sleep(0.5)  # Rate limiting
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        return info, None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate" in error_msg.lower():
            return None, "Rate limit reached"
        return None, str(e)[:100]

def get_stock_fundamentals(ticker):
    """Get key fundamental metrics for a stock with enhanced sector analysis"""
    info, error = fetch_stock_data(ticker)
    
    if error or not info:
        return None
    
    try:
        # Extract key metrics
        market_cap = info.get('marketCap', 0)
        fundamentals = {
            'ticker': ticker,
            'name': info.get('longName', info.get('shortName', 'Unknown')),
            'price': info.get('currentPrice', info.get('regularMarketPrice')),
            'market_cap': market_cap,
            'trailing_pe': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'roe': info.get('returnOnEquity'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'profit_margin': info.get('profitMargins'),
            'debt_to_equity': info.get('debtToEquity'),
            '52w_high': info.get('fiftyTwoWeekHigh'),
            '52w_low': info.get('fiftyTwoWeekLow'),
            'volume': info.get('volume') or info.get('regularMarketVolume'),
            'avg_volume': info.get('averageVolume') or info.get('averageDailyVolume10Day'),
            'trailing_eps': info.get('trailingEps'),
            'forward_pe': info.get('forwardPE'),
            'enterprise_value': info.get('enterpriseValue'),
            'ebitda': info.get('ebitda'),
            'book_value': info.get('bookValue'),
            'revenue': info.get('totalRevenue'),
            'sector': info.get('sector', 'Other'),
            'industry': info.get('industry', 'Other'),
            # Growth / profitability fields (available for future use and for
            # the Individual Analysis screen; the breakout screener does not filter on them)
            'earnings_growth': info.get('earningsGrowth') or info.get('earningsQuarterlyGrowth'),
            'revenue_growth': info.get('revenueGrowth'),
            'operating_margin': info.get('operatingMargins'),
            'return_on_assets': info.get('returnOnAssets'),
            'current_ratio': info.get('currentRatio'),
            'free_cashflow': info.get('freeCashflow')
        }
        
        # Calculate additional metrics
        if fundamentals['price'] and fundamentals['52w_high']:
            fundamentals['pct_from_high'] = ((fundamentals['price'] - fundamentals['52w_high']) / fundamentals['52w_high']) * 100
        
        if fundamentals['price'] and fundamentals['52w_low']:
            fundamentals['pct_from_low'] = ((fundamentals['price'] - fundamentals['52w_low']) / fundamentals['52w_low']) * 100
        
        # Determine market cap category for Indian market (in INR)
        if market_cap:
            if market_cap >= 200000000000:  # ≥₹20,000 Cr
                fundamentals['cap_type'] = 'Large'
            elif market_cap >= 50000000000:  # ₹5,000-20,000 Cr
                fundamentals['cap_type'] = 'Mid'
            else:  # <₹5,000 Cr
                fundamentals['cap_type'] = 'Small'
        else:
            fundamentals['cap_type'] = 'Unknown'
        
        return fundamentals
    
    except Exception as e:
        return None

def get_industry_benchmarks(industry, cap_type='Large'):
    """Get industry-specific benchmarks with cap-size adjustments"""
    # Get industry-specific benchmarks first
    if industry in INDUSTRY_BENCHMARKS:
        base_benchmarks = INDUSTRY_BENCHMARKS[industry].copy()
    else:
        # Fallback to sector benchmarks
        sector = get_sector_for_industry(industry)
        base_benchmarks = SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other']).copy()
    
    # Apply cap-size multipliers
    if cap_type in CAP_SIZE_MULTIPLIERS:
        multipliers = CAP_SIZE_MULTIPLIERS[cap_type]
        base_benchmarks['pe'] *= multipliers['pe']
        base_benchmarks['pb'] *= multipliers['pb'] 
        base_benchmarks['ev_ebitda'] *= multipliers['ev_ebitda']
    
    return base_benchmarks

def calculate_fair_value(fundamentals, industry, cap_type='Large'):
    """Calculate fair value using enhanced industry-specific benchmarks"""
    if not fundamentals or not fundamentals.get('price'):
        return None
    
    try:
        # Get industry-specific benchmarks with cap-size adjustments
        benchmarks = get_industry_benchmarks(industry, cap_type)
        fair_values = []
        
        # PE-based fair value
        if fundamentals.get('trailing_pe') and fundamentals.get('trailing_eps'):
            if 0 < fundamentals['trailing_pe'] < 100:  # Sanity check
                # Use blended approach: 70% industry benchmark, 30% historical
                target_pe = (0.7 * benchmarks['pe']) + (0.3 * fundamentals['trailing_pe'])
                pe_fair_value = fundamentals['trailing_eps'] * target_pe
                if pe_fair_value > 0:
                    fair_values.append(pe_fair_value)
        
        # PB-based fair value (for asset-heavy industries)
        if fundamentals.get('book_value') and benchmarks.get('pb'):
            if fundamentals['book_value'] > 0:
                pb_fair_value = fundamentals['book_value'] * benchmarks['pb']
                if pb_fair_value > 0:
                    fair_values.append(pb_fair_value)
        
        # For high-growth industries, give more weight to forward-looking metrics
        if industry in ['Information Technology Services', 'Drug Manufacturers - Major', 'Renewable Energy']:
            if fundamentals.get('forward_pe') and fundamentals.get('trailing_eps'):
                if 0 < fundamentals['forward_pe'] < 50:
                    forward_fair_value = fundamentals['trailing_eps'] * fundamentals['forward_pe'] * 1.1
                    if forward_fair_value > 0:
                        fair_values.append(forward_fair_value)
        
        # Return weighted average if we have multiple estimates
        if len(fair_values) >= 2:
            # Weight PE more heavily for most industries
            if len(fair_values) == 2:
                return (fair_values[0] * 0.7 + fair_values[1] * 0.3)
            else:
                return np.mean(fair_values)
        elif fair_values:
            return fair_values[0]
        else:
            return None
            
    except:
        return None

def calculate_valuations(info, industry=None):
    """Advanced valuation calculations using industry-specific benchmarks"""
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        book_value = info.get('bookValue', 0)
        revenue = info.get('totalRevenue', 0)
        
        # Determine market cap category
        if market_cap >= 200000000000:  # ≥₹20,000 Cr
            cap_type = 'Large'
        elif market_cap >= 50000000000:  # ₹5,000-20,000 Cr
            cap_type = 'Mid'
        else:  # <₹5,000 Cr
            cap_type = 'Small'
        
        # Get industry-specific benchmarks
        if industry:
            benchmarks = get_industry_benchmarks(industry, cap_type)
        else:
            # Fallback to yfinance sector mapping
            sector = info.get('sector', 'Other')
            sector_mapping = {
                'Technology': 'Information Technology Services',
                'Financial Services': 'Money Center Banks', 
                'Healthcare': 'Drug Manufacturers - Major',
                'Industrials': 'Diversified Machinery',
                'Energy': 'Oil & Gas Operations',
                'Consumer Cyclical': 'Auto Manufacturers - Major',
                'Consumer Defensive': 'Food - Major Diversified',
                'Basic Materials': 'Steel & Iron',
                'Communication Services': 'Wireless Communications',
                'Real Estate': 'Real Estate Development',
                'Utilities': 'Electric Utilities'
            }
            mapped_industry = sector_mapping.get(sector, 'Other')
            benchmarks = get_industry_benchmarks(mapped_industry, cap_type)
        
        industry_pe = benchmarks['pe']
        industry_ev_ebitda = benchmarks['ev_ebitda']
        
        # Enhanced PE-based valuation
        historical_pe = trailing_pe if trailing_pe and 0 < trailing_pe < 100 else industry_pe
        # Blend industry benchmark with historical PE (weighted by cap size)
        pe_weight = 0.8 if cap_type == 'Large' else 0.7 if cap_type == 'Mid' else 0.6
        blended_pe = (industry_pe * pe_weight) + (historical_pe * (1 - pe_weight))
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # Enhanced EV/EBITDA-based valuation
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        
        if current_ev_ebitda and 0 < current_ev_ebitda < 50:
            # Blend current and industry EV/EBITDA
            ev_weight = 0.7 if cap_type == 'Large' else 0.6 if cap_type == 'Mid' else 0.5
            target_ev_ebitda = (industry_ev_ebitda * ev_weight) + (current_ev_ebitda * (1 - ev_weight))
        else:
            target_ev_ebitda = industry_ev_ebitda
        
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        
        # Additional ratios
        pb_ratio = price / book_value if book_value and book_value > 0 else None
        ps_ratio = market_cap / revenue if revenue and revenue > 0 else None
        
        return {
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,
            'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,
            'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,
            'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev,
            'pb_ratio': pb_ratio, 'ps_ratio': ps_ratio,
            'book_value': book_value, 'revenue': revenue,
            'net_debt': (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'roe': info.get('returnOnEquity', 0),
            'profit_margin': info.get('profitMargins', 0),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
            'cap_type': cap_type,
            'benchmarks_used': benchmarks
        }
    except:
        return None

# ============================================================================
# SCREENING LOGIC
# ============================================================================
def run_industry_screener(industry, strategy_type="undervalued", max_results=50):
    """Run comprehensive screening for a specific industry using enhanced benchmarks"""
    
    stocks = get_stocks_by_category(industry)
    if not stocks:
        return pd.DataFrame()
    
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_stocks = len(stocks)
    
    for i, (ticker, name) in enumerate(stocks.items()):
        # Update progress
        progress = (i + 1) / total_stocks
        progress_bar.progress(progress)
        status_text.text(f"Processing {ticker} ({i + 1}/{total_stocks})")
        
        # Get fundamentals
        fundamentals = get_stock_fundamentals(ticker)
        if not fundamentals or not fundamentals['price']:
            continue
        
        # Calculate fair value using industry-specific benchmarks
        fair_value = calculate_fair_value(fundamentals, industry, fundamentals.get('cap_type', 'Large'))
        if not fair_value or fair_value <= 0:
            continue
        
        # Calculate upside
        upside = ((fair_value - fundamentals['price']) / fundamentals['price']) * 100
        
        # Remove outliers: Skip stocks with upside > 500% (likely data errors)
        if upside > 350:
            continue
        
        # Get industry benchmarks for additional filtering
        benchmarks = get_industry_benchmarks(industry, fundamentals.get('cap_type', 'Large'))
        
        # Apply strategy filters with enhanced criteria
        passes_filter = False
        
        if strategy_type == "undervalued":
            # Basic undervalued filter
            if upside >= 15:  # At least 15% upside
                passes_filter = True
        
        elif strategy_type == "undervalued_near_high":
            # Undervalued stocks trading near 52-week highs (strong momentum + value)
            if upside >= 15:  # Must be undervalued
                pct_from_high = fundamentals.get('pct_from_high', -100)
                # Near 52-week high: within 5% of high
                if pct_from_high >= -5:
                    passes_filter = True
        
        elif strategy_type == "undervalued_supertrend":
            # Undervalued + Real SuperTrend bullish signal
            if upside >= 15:  # Must be undervalued
                # Get technical signals
                with st.spinner(f"Analyzing technical signals for {ticker}..."):
                    technical = get_technical_signals(ticker)
                
                if technical:
                    # SuperTrend bullish (1) and additional confirmations
                    if (technical['supertrend_signal'] == 1 and
                        technical['above_sma20'] and 
                        technical.get('price_vs_52w_high', 0) > 0.7):  # Not in deep correction
                        passes_filter = True
        
        elif strategy_type == "undervalued_rsi_macd":
            # Undervalued + momentum indicators (proxy using price action)
            if (upside >= 15 and
                fundamentals.get('pct_from_high', -100) >= -30 and
                fundamentals.get('volume', 0) > 0):  # Has volume
                passes_filter = True
        
        elif strategy_type == "momentum":
            # Momentum: stocks near 52W high with reasonable valuation
            if (fundamentals.get('pct_from_high', -100) >= -10 and
                fundamentals.get('trailing_pe', 999) <= benchmarks['pe'] * 1.5):
                passes_filter = True
        
        elif strategy_type == "quality":
            # Quality: good fundamentals with reasonable valuation
            roe_threshold = benchmarks.get('roe', 15) / 100
            if (fundamentals.get('roe', 0) > roe_threshold and
                fundamentals.get('trailing_pe', 999) <= benchmarks['pe'] * 1.2 and
                upside >= 5 and
                fundamentals.get('debt_to_equity', 999) <= benchmarks.get('debt_equity', 1.0)):
                passes_filter = True
        
        if not passes_filter:
            continue
        
        # Add to results
        result = {
            'Ticker': ticker,
            'Name': name,
            'Industry': industry,
            'Price': fundamentals['price'],
            'Fair Value': fair_value,
            'Upside %': upside,
            'PE Ratio': fundamentals['trailing_pe'],
            'PB Ratio': fundamentals['pb_ratio'],
            'ROE %': fundamentals['roe'] * 100 if fundamentals['roe'] else None,
            'Market Cap': fundamentals['market_cap'],
            'Cap Type': fundamentals['cap_type'],
            'From 52W High %': fundamentals['pct_from_high'],
            'From 52W Low %': fundamentals['pct_from_low'],
            'Beta': fundamentals['beta'],
            'Dividend Yield %': fundamentals['dividend_yield'] * 100 if fundamentals['dividend_yield'] else None,
            'Volume': fundamentals.get('volume'),
            'Avg Volume': fundamentals.get('avg_volume'),
            'Rel Vol': (fundamentals.get('volume') / fundamentals.get('avg_volume'))
                       if (fundamentals.get('volume') and fundamentals.get('avg_volume')) else None,
            'Industry PE Benchmark': benchmarks['pe'],
            'Industry EV/EBITDA Benchmark': benchmarks['ev_ebitda'],
            'Valuation': build_valuation_link(ticker)
        }
        results.append(result)
        
        if len(results) >= max_results:
            break
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def search_stocks_by_name(query, max_results=50):
    """Search stocks by company name across all industries"""
    results = []
    query_lower = query.lower()
    
    for industry, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query_lower in name.lower() or query_lower in ticker.lower():
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'industry': industry
                })
                if len(results) >= max_results:
                    break
        if len(results) >= max_results:
            break
    
    return results

# ============================================================================
# LOWER TIMEFRAME BREAKOUT SCREENER ENGINE (1 HOUR / 15 MINUTE)
# ----------------------------------------------------------------------------
# DESIGN NOTES
#
# The scoring model deliberately uses only FIVE factors. Earlier drafts used
# eleven, but most of them measured the same underlying thing: an N-bar range
# break, an opening-range break and a previous-day-high break are all "price is
# above a recent high" and fire together, so the composite score clustered in a
# narrow band and stopped discriminating between good and mediocre setups.
#
# Each factor is now GRADED (0.0 - 1.0) rather than binary. A break that clears
# its level by 0.6 ATR on 3x volume out of a 40-bar base should not score the
# same as one that clears by 0.02 ATR on 1.5x volume out of a 6-bar base.
#
# Structural conditions - trend alignment, volume, liquidity - are HARD GATES
# rather than score contributors. A breakout against the daily trend is not
# "a slightly lower score", it is a different (and worse) trade.
#
# The screener is PURELY TECHNICAL. Fair Value and Upside are fetched for
# display so you can see what you are buying, but no fundamental figure is
# ever allowed to remove a valid technical setup from the results.
# ============================================================================

# Timeframe configuration
SCREENER_TIMEFRAMES = {
    "15 Minute": {
        "interval": "15m",
        "period": "30d",
        "label": "15m",
        "session_vwap": True,
        "note": "Intraday. Yahoo caps 15m history at 60 days."
    },
    "1 Hour": {
        "interval": "1h",
        "period": "90d",
        "label": "1H",
        "session_vwap": True,
        "note": "Intraday. Roughly 7 candles per session."
    },
    "1 Day": {
        "interval": "1d",
        "period": "2y",
        "label": "1D",
        "session_vwap": False,
        "note": "Positional. VWAP becomes a rolling 20-day VWAP, since a daily "
                "candle has no intraday session to anchor to."
    },
}


def _ns(symbols):
    """Helper to append NSE suffix to a list of raw symbols"""
    return [s if s.endswith((".NS", ".BO")) else f"{s}.NS" for s in symbols]


# Preset liquid universes for fast intraday scanning (yfinance rate-limit friendly)
BREAKOUT_PRESET_UNIVERSES = {
    "NIFTY 50 (Most Liquid)": _ns([
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN",
        "BHARTIARTL", "KOTAKBANK", "LT", "BAJFINANCE", "AXISBANK", "ASIANPAINT", "MARUTI",
        "HCLTECH", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", "WIPRO", "ONGC", "NTPC",
        "POWERGRID", "M&M", "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "ADANIENT", "ADANIPORTS",
        "COALINDIA", "GRASIM", "HINDALCO", "DRREDDY", "CIPLA", "APOLLOHOSP", "BAJAJFINSV",
        "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "BRITANNIA", "TATACONSUM", "INDUSINDBK",
        "SBILIFE", "HDFCLIFE", "TECHM", "LTIM", "SHRIRAMFIN", "BPCL", "TRENT"
    ]),
    "NIFTY NEXT 50 / Midcap Liquid": _ns([
        "DMART", "PIDILITIND", "GODREJCP", "DABUR", "HAVELLS", "SIEMENS", "ABB", "BOSCHLTD",
        "AMBUJACEM", "ACC", "VEDL", "DLF", "ICICIPRULI", "ICICIGI", "CHOLAFIN", "TVSMOTOR",
        "IOC", "GAIL", "PFC", "RECLTD", "HAL", "BEL", "IRCTC", "INDIGO", "NAUKRI",
        "MOTHERSON", "MARICO", "COLPAL", "BERGEPAINT", "TORNTPHARM", "LUPIN", "AUROPHARMA",
        "ZYDUSLIFE", "ALKEM", "MPHASIS", "PERSISTENT", "COFORGE", "POLYCAB", "ASTRAL",
        "SRF", "PIIND", "UPL", "TATAPOWER", "JINDALSTEL", "SAIL", "NMDC", "CANBK", "PNB",
        "BANKBARODA", "IDFCFIRSTB", "AUBANK", "FEDERALBNK", "MUTHOOTFIN", "LICHSGFIN"
    ]),
    "High Beta / F&O Movers": _ns([
        "ADANIENT", "ADANIPORTS", "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL",
        "SAIL", "NMDC", "JINDALSTEL", "IDFCFIRSTB", "YESBANK", "PNB", "CANBK", "BANKBARODA",
        "RBLBANK", "BANDHANBNK", "IEX", "BSE", "ANGELONE", "PAYTM", "POLICYBZR", "NYKAA",
        "IRFC", "RVNL", "IRCON", "NBCC", "HUDCO", "SJVN", "NHPC", "PFC", "RECLTD",
        "TATAPOWER", "SUZLON", "IDEA", "ZEEL", "DELHIVERY", "MAZDOCK", "COCHINSHIP", "BDL"
    ]),
    "Banking & Financials": _ns([
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "BANKBARODA",
        "PNB", "CANBK", "FEDERALBNK", "IDFCFIRSTB", "AUBANK", "BAJFINANCE", "BAJAJFINSV",
        "CHOLAFIN", "SHRIRAMFIN", "MUTHOOTFIN", "LICHSGFIN", "PFC", "RECLTD", "SBILIFE",
        "HDFCLIFE", "ICICIPRULI", "ICICIGI", "IIFL", "MANAPPURAM", "PEL", "M&MFIN"
    ]),
    "IT & Tech": _ns([
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "MPHASIS", "PERSISTENT",
        "COFORGE", "LTTS", "OFSS", "KPITTECH", "TATAELXSI", "CYIENT", "SONATSOFTW",
        "BIRLASOFT", "ZENSARTECH", "NEWGEN", "HAPPSTMNDS", "INTELLECT"
    ]),
}


# ---------------------------------------------------------------------------
# Indicator helpers
# ---------------------------------------------------------------------------
def calculate_rsi(series, period=14):
    """Wilder's RSI"""
    try:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))
    except Exception:
        return pd.Series(index=series.index, dtype=float)


def calculate_atr_series(high, low, close, period=14):
    """Average True Range series"""
    try:
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.ewm(alpha=1 / period, adjust=False).mean()
    except Exception:
        return pd.Series(index=close.index, dtype=float)


def calculate_session_vwap(df):
    """Session-anchored VWAP (resets every trading day) - the true intraday VWAP"""
    try:
        typical = (df['High'] + df['Low'] + df['Close']) / 3.0
        volume = df['Volume'].fillna(0)
        session_key = pd.Series(pd.to_datetime(df.index).date, index=df.index)
        cum_pv = (typical * volume).groupby(session_key).cumsum()
        cum_vol = volume.groupby(session_key).cumsum()
        vwap = cum_pv / cum_vol.replace(0, np.nan)
        return vwap.ffill()
    except Exception:
        return pd.Series(index=df.index, dtype=float)


def _pct_rank(series, value):
    """Fraction of observations below `value` (0..1). Avoids a scipy dependency."""
    try:
        arr = pd.Series(series).dropna().values
        if len(arr) < 10:
            return 0.5
        return float((arr < value).mean())
    except Exception:
        return 0.5


def format_volume(v):
    """Format volume in Indian convention (K / L / Cr)"""
    try:
        if v is None or pd.isna(v) or v <= 0:
            return "N/A"
        v = float(v)
        if v >= 1e7:
            return f"{v/1e7:.2f} Cr"
        if v >= 1e5:
            return f"{v/1e5:.2f} L"
        if v >= 1e3:
            return f"{v/1e3:.1f} K"
        return f"{v:,.0f}"
    except Exception:
        return "N/A"


# ---------------------------------------------------------------------------
# Batch data fetching
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def fetch_intraday_batch(tickers_tuple, interval, period):
    """Batch download intraday OHLCV for many tickers at once. Cached 5 minutes."""
    return _batch_download(tickers_tuple, interval, period)


def _batch_download(tickers_tuple, interval, period):
    """Shared batch downloader returning {ticker: DataFrame}"""
    tickers = list(tickers_tuple)
    out = {}
    if not tickers:
        return out
    try:
        data = yf.download(
            tickers=" ".join(tickers),
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=False,
            prepost=False
        )
    except Exception:
        return out

    if data is None or len(data) == 0:
        return out

    try:
        if isinstance(data.columns, pd.MultiIndex):
            for t in tickers:
                try:
                    sub = data[t].dropna(how="all")
                    if not sub.empty and len(sub) > 5:
                        out[t] = sub
                except Exception:
                    continue
        else:
            if len(tickers) == 1:
                sub = data.dropna(how="all")
                if not sub.empty:
                    out[tickers[0]] = sub
    except Exception:
        pass
    return out


# ---------------------------------------------------------------------------
# GAMMA BLAST ENGINE
# ---------------------------------------------------------------------------
# A direct port of the "Nyztrade Gamma Flow" Pine v5 indicator. Every number
# produced here reproduces the TradingView formula exactly:
#
#     volume_ratio         = volume / SMA(volume, vol_ma_len)
#     price_momentum       = (close - close[mom_len]) / close[mom_len] * 100
#     volatility_expansion = ATR(14) / SMA(ATR(14), 20)
#
#     gamma_score = (volume_ratio - 1) * 25
#                 + abs(price_momentum) * 2
#                 + (volatility_expansion - 1) * 50
#
#     blast (bull) = volume_ratio > vol_mult
#                    AND rsi > rsi_bull
#                    AND price_momentum > sensitivity
#                    AND volatility_expansion > 1.2
#
#     spike        = blast AND gamma_score > score_floor
# ---------------------------------------------------------------------------

def compute_blast_features(df, cfg, rsi_len=14, vol_ma_len=20, mom_len=10,
                           sensitivity=1.5, vol_mult=2.0, rsi_bull=70.0,
                           rsi_bear=30.0, score_floor=50.0, bullish=True):
    """
    Compute every Gamma Blast input for one symbol on one timeframe.

    Returns None when there is not enough history to form the 20-bar ATR
    average that volatility_expansion depends on.
    """
    try:
        if df is None or len(df) < 45:
            return None

        d = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        d = d.dropna(subset=['Close', 'High', 'Low'])
        if len(d) < 45:
            return None

        close, high, low = d['Close'], d['High'], d['Low']
        volume = d['Volume'].fillna(0)

        # ---- Pine inputs ----
        rsi = calculate_rsi(close, rsi_len)
        vol_ma = volume.rolling(vol_ma_len).mean()
        vol_ratio_s = volume / vol_ma.replace(0, np.nan)
        mom_s = (close - close.shift(mom_len)) / close.shift(mom_len).replace(0, np.nan) * 100

        atr = calculate_atr_series(high, low, close, 14)
        atr_ma = atr.rolling(20).mean()
        vol_exp_s = atr / atr_ma.replace(0, np.nan)

        gamma_s = ((vol_ratio_s - 1) * 25
                   + mom_s.abs() * 2
                   + (vol_exp_s - 1) * 50)

        # ---- Blast condition, evaluated across the whole series ----
        if bullish:
            cond_s = ((vol_ratio_s > vol_mult) & (rsi > rsi_bull)
                      & (mom_s > sensitivity) & (vol_exp_s > 1.2))
        else:
            cond_s = ((vol_ratio_s > vol_mult) & (rsi < rsi_bear)
                      & (mom_s < -sensitivity) & (vol_exp_s > 1.2))
        cond_s = cond_s.fillna(False)
        spike_s = cond_s & (gamma_s > score_floor)

        # ---- VWAP: session-anchored intraday, rolling on the daily chart ----
        if cfg.get('session_vwap', True):
            vwap_s = calculate_session_vwap(d)
        else:
            typical = (high + low + close) / 3.0
            pv = (typical * volume).rolling(20).sum()
            vv = volume.rolling(20).sum().replace(0, np.nan)
            vwap_s = pv / vv

        i = -1
        last_close = float(close.iloc[i])
        last_vol = float(volume.iloc[i]) if not pd.isna(volume.iloc[i]) else 0.0
        avg_vol = float(vol_ma.iloc[i]) if not pd.isna(vol_ma.iloc[i]) else 0.0
        last_atr = float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else 0.0
        last_vwap = float(vwap_s.iloc[i]) if not pd.isna(vwap_s.iloc[i]) else None

        vol_ratio = float(vol_ratio_s.iloc[i]) if not pd.isna(vol_ratio_s.iloc[i]) else 0.0
        momentum = float(mom_s.iloc[i]) if not pd.isna(mom_s.iloc[i]) else 0.0
        vol_expansion = float(vol_exp_s.iloc[i]) if not pd.isna(vol_exp_s.iloc[i]) else 1.0
        gamma_score = float(gamma_s.iloc[i]) if not pd.isna(gamma_s.iloc[i]) else 0.0

        blast_now = bool(cond_s.iloc[i])
        blast_prev = bool(cond_s.iloc[i - 1]) if len(cond_s) > 1 else False
        spike_now = bool(spike_s.iloc[i])

        # How many consecutive bars has the blast been firing?
        streak = 0
        for k in range(1, min(len(cond_s), 40) + 1):
            if bool(cond_s.iloc[-k]):
                streak += 1
            else:
                break

        # How often does this stock blast? A name that fires constantly is
        # noisy, not exceptional — this is the context the raw score lacks.
        blast_freq = int(cond_s.iloc[-100:].sum()) if len(cond_s) >= 100 else int(cond_s.sum())

        # Percentile of the current score against this stock's own history
        gamma_rank = 0.5
        try:
            g_hist = gamma_s.dropna().iloc[-150:]
            if len(g_hist) >= 30:
                gamma_rank = _pct_rank(g_hist, gamma_score)
        except Exception:
            pass

        # ---- Session / prior-bar context ----
        if cfg.get('session_vwap', True):
            session_key = pd.Series(pd.to_datetime(d.index).date, index=d.index)
            sessions = list(dict.fromkeys(session_key.tolist()))
            cur = d[session_key == sessions[-1]]
            session_volume = float(cur['Volume'].fillna(0).sum()) if not cur.empty else last_vol
            ref_close = None
            if len(sessions) >= 2:
                prev = d[session_key == sessions[-2]]
                if not prev.empty:
                    ref_close = float(prev['Close'].iloc[-1])
        else:
            session_volume = last_vol
            ref_close = float(close.iloc[i - 1])

        return {
            'price': last_close,
            'last_volume': last_vol,
            'avg_volume': avg_vol,
            'session_volume': session_volume,
            'vol_ratio': vol_ratio,
            'rsi': float(rsi.iloc[i]) if not pd.isna(rsi.iloc[i]) else 50.0,
            'momentum': momentum,
            'vol_expansion': vol_expansion,
            'gamma_score': gamma_score,
            'gamma_rank': gamma_rank,
            'blast': blast_now,
            'blast_prev': blast_prev,
            'spike': spike_now,
            'streak': streak,
            'blast_freq': blast_freq,
            'atr': last_atr,
            'atr_pct': (last_atr / last_close * 100) if last_close else 0.0,
            'vwap': last_vwap,
            'day_change_pct': ((last_close - ref_close) / ref_close * 100) if ref_close else 0.0,
            'last_bar_time': d.index[i],
        }
    except Exception:
        return None


def evaluate_blast(feat, spike_only=False, min_score=50.0):
    """
    Accept or reject a candidate on the blast condition alone.

    Returns None when the blast is not firing, so nothing reaches the results
    table unless the full Pine condition is satisfied.
    """
    if not feat or not feat.get('blast'):
        return None
    if spike_only and not feat.get('spike'):
        return None
    if feat.get('gamma_score', 0.0) < min_score:
        return None

    # The three additive terms of the Pine score, exposed so you can see which
    # one is carrying the signal. Volume-only blasts behave differently from
    # volatility-expansion blasts.
    vol_component = (feat['vol_ratio'] - 1) * 25
    mom_component = abs(feat['momentum']) * 2
    exp_component = (feat['vol_expansion'] - 1) * 50

    if feat['spike']:
        signal = "💥 Spike"
    else:
        signal = "⚡ Blast"

    stage = "🆕 New" if not feat.get('blast_prev') else f"🔁 Bar {feat['streak']}"

    return {
        'score': round(feat['gamma_score'], 1),
        'signal': signal,
        'stage': stage,
        'vol_component': vol_component,
        'mom_component': mom_component,
        'exp_component': exp_component,
    }


# ---------------------------------------------------------------------------
# Valuation enrichment (fair value + upside %)
# ---------------------------------------------------------------------------
def get_valuation_tag(upside):
    """Human readable valuation status from the upside percentage"""
    if upside is None or pd.isna(upside):
        return "❔ No Data"
    if upside > 25:
        return "🚀 Deep Value"
    if upside > 15:
        return "✅ Undervalued"
    if upside > 0:
        return "📥 Fairly Valued"
    if upside > -10:
        return "⏸️ Slightly Rich"
    return "⚠️ Overvalued"


def enrich_with_valuation(rows, show_progress=True):
    """
    Attach fair value and upside to breakout candidates.

    DISPLAY ONLY. Nothing here can remove a stock from the results - the
    screener is purely technical, and these columns exist so you can see what
    you are buying, not to veto a valid setup. Runs after the technical and
    trend gates, so the per-ticker calls only touch survivors, and
    fetch_stock_data() is cached for an hour.
    """
    if not rows:
        return rows

    total = len(rows)
    progress_bar = st.progress(0) if show_progress else None
    status_text = st.empty() if show_progress else None

    for n, row in enumerate(rows):
        ticker = row['Ticker']
        if show_progress:
            try:
                progress_bar.progress(min((n + 1) / total, 1.0))
                status_text.text(f"💰 Fetching fair value... {n + 1}/{total} — {ticker}")
            except Exception:
                pass

        fair_value = upside = pe_ratio = market_cap = cap_type = None

        try:
            fundamentals = get_stock_fundamentals(ticker)
            if fundamentals and fundamentals.get('price'):
                stock_info = get_stock_info(ticker)
                industry = stock_info['category'] if stock_info else fundamentals.get('industry', 'Other')
                cap_type = fundamentals.get('cap_type', 'Large')
                pe_ratio = fundamentals.get('trailing_pe')
                market_cap = fundamentals.get('market_cap')

                fv = calculate_fair_value(fundamentals, industry, cap_type)
                if fv and fv > 0:
                    ref = fundamentals['price']
                    up = ((fv - ref) / ref) * 100
                    if -95 <= up <= 350:
                        fair_value, upside = fv, up
        except Exception:
            pass

        row['Fair Value'] = fair_value
        row['Upside %'] = upside
        row['Value Tag'] = get_valuation_tag(upside)
        row['PE Ratio'] = pe_ratio
        row['Market Cap'] = market_cap
        row['Cap Type'] = cap_type

    if show_progress:
        try:
            progress_bar.empty()
            status_text.empty()
        except Exception:
            pass

    return rows


# ---------------------------------------------------------------------------
# MAIN SCREENER PIPELINE
# ---------------------------------------------------------------------------
def run_blast_screener(universe, timeframe_label, direction="Bullish Blast",
                       rsi_len=14, vol_ma_len=20, mom_len=10, sensitivity=1.5,
                       vol_mult=2.0, rsi_bull=70.0, rsi_bear=30.0,
                       score_floor=50.0, min_score=50.0, spike_only=False,
                       min_price=10.0, min_avg_volume=25000, max_results=40,
                       chunk_size=25, final_rank="Gamma Score",
                       include_valuation=True):
    """
    Single-criterion screener: the Gamma Blast condition, nothing else.

    There is no breakout-structure model, no multi-timeframe trend gate and no
    exhaustion veto. A stock appears if and only if the Pine blast condition is
    firing on the selected timeframe. Fair value and upside are attached
    afterwards for context and never remove a row.
    """
    cfg = SCREENER_TIMEFRAMES.get(timeframe_label, SCREENER_TIMEFRAMES["15 Minute"])
    bullish = direction.startswith("Bullish")
    tickers = list(universe.keys())
    total = len(tickers)
    funnel = {'scanned': 0, 'with_data': 0, 'blast': 0, 'spike': 0, 'final': 0}

    if total == 0:
        return pd.DataFrame(), funnel

    rows = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    processed = 0

    for start in range(0, total, chunk_size):
        chunk = tickers[start:start + chunk_size]
        status_text.text(f"⚡ Scanning {cfg['label']} candles... "
                         f"{processed}/{total} | blasts: {len(rows)}")
        data_map = fetch_intraday_batch(tuple(chunk), cfg['interval'], cfg['period'])

        for ticker in chunk:
            processed += 1
            funnel['scanned'] += 1
            try:
                progress_bar.progress(min(processed / total, 1.0))
            except Exception:
                pass

            df = data_map.get(ticker)
            if df is None or df.empty:
                continue
            funnel['with_data'] += 1

            feat = compute_blast_features(
                df, cfg, rsi_len=rsi_len, vol_ma_len=vol_ma_len, mom_len=mom_len,
                sensitivity=sensitivity, vol_mult=vol_mult, rsi_bull=rsi_bull,
                rsi_bear=rsi_bear, score_floor=score_floor, bullish=bullish
            )
            if not feat:
                continue
            if feat['price'] < min_price or (feat['avg_volume'] or 0) < min_avg_volume:
                continue

            if feat.get('blast'):
                funnel['blast'] += 1
            if feat.get('spike'):
                funnel['spike'] += 1

            verdict = evaluate_blast(feat, spike_only=spike_only, min_score=min_score)
            if not verdict:
                continue

            vwap_dist = ((feat['price'] - feat['vwap']) / feat['vwap'] * 100) if feat.get('vwap') else None

            rows.append({
                'Ticker': ticker,
                'Name': universe.get(ticker, ticker),
                'Timeframe': cfg['label'],
                'LTP': feat['price'],
                'Fair Value': None,
                'Upside %': None,
                'Value Tag': None,
                'Chg %': feat['day_change_pct'],
                'Signal': verdict['signal'],
                'Stage': verdict['stage'],
                'Gamma Score': verdict['score'],
                'Blast Rank': feat['gamma_rank'] * 100,
                'Vol Ratio': feat['vol_ratio'],
                'Momentum %': feat['momentum'],
                'Vol Expansion': feat['vol_expansion'],
                'RSI': feat['rsi'],
                'Volume': feat['last_volume'],
                'Avg Volume': feat['avg_volume'],
                'Session Volume': feat['session_volume'],
                'VWAP': feat['vwap'],
                'VWAP Dist %': vwap_dist,
                'ATR %': feat['atr_pct'],
                'Streak': feat['streak'],
                'Blasts/100': feat['blast_freq'],
                'Vol Term': verdict['vol_component'],
                'Mom Term': verdict['mom_component'],
                'Exp Term': verdict['exp_component'],
                'Last Candle': feat['last_bar_time'].strftime('%d-%b %H:%M')
                               if hasattr(feat['last_bar_time'], 'strftime') else str(feat['last_bar_time']),
                'Valuation': build_valuation_link(ticker),
            })

    try:
        progress_bar.empty()
        status_text.empty()
    except Exception:
        pass

    if not rows:
        return pd.DataFrame(), funnel

    # Rank first, then value only the survivors
    rows.sort(key=lambda r: r['Gamma Score'], reverse=True)
    rows = rows[:max_results]

    if include_valuation:
        rows = enrich_with_valuation(rows)

    df_out = pd.DataFrame(rows)

    if final_rank == "Upside %" and 'Upside %' in df_out.columns:
        df_out = df_out.sort_values('Upside %', ascending=False, na_position='last')
    elif final_rank == "Blast Rank" and 'Blast Rank' in df_out.columns:
        df_out = df_out.sort_values('Blast Rank', ascending=False, na_position='last')
    else:
        df_out = df_out.sort_values('Gamma Score', ascending=False)

    df_out = df_out.reset_index(drop=True)
    funnel['final'] = len(df_out)
    return df_out, funnel


# ---------------------------------------------------------------------------
# Deep-link helpers: jump from screener result row -> valuation screen
# ---------------------------------------------------------------------------
def build_valuation_link(ticker):
    """Build a deep link that opens the Individual Analysis (valuation) screen"""
    try:
        base = st.session_state.get("app_base_url", "").strip().rstrip("/")
    except Exception:
        base = ""
    query = f"?mode=valuation&ticker={quote(str(ticker))}"
    return f"{base}{query}" if base else query


def _get_query_param(name):
    """Read a URL query parameter across Streamlit versions"""
    val = None
    try:
        val = st.query_params.get(name)
    except Exception:
        try:
            val = st.experimental_get_query_params().get(name)
        except Exception:
            val = None
    if isinstance(val, list):
        val = val[0] if val else None
    return val


def render_valuation_jump(results_df, key_prefix):
    """Fallback in-app navigation to the valuation screen for any screened ticker"""
    if results_df is None or results_df.empty or 'Ticker' not in results_df.columns:
        return
    st.markdown("##### 🔗 Open Valuation Screen")
    c1, c2 = st.columns([3, 1])
    with c1:
        options = [f"{r['Ticker']} — {r.get('Name', '')}" for _, r in results_df.iterrows()]
        picked = st.selectbox(
            "Select a screened stock to run full valuation",
            options,
            key=f"{key_prefix}_val_pick",
            label_visibility="collapsed"
        )
    with c2:
        if st.button("📊 Open Valuation", key=f"{key_prefix}_val_btn",
                     use_container_width=True, type="primary"):
            chosen = picked.split(" — ")[0].strip()
            st.session_state["_pending_mode"] = "📈 Individual Analysis"
            st.session_state["input_method_radio"] = "✏️ Direct Ticker"
            st.session_state["deeplink_ticker"] = chosen
            st.session_state["auto_analyze"] = True
            st.rerun()


def valuation_column_config(extra=None):
    """Column config that renders the Valuation column as a clickable link"""
    cfg = {}
    try:
        cfg["Valuation"] = st.column_config.LinkColumn(
            "Valuation",
            display_text="📊 Analyze",
            help="Open this stock in the Individual Analysis / valuation screen"
        )
    except Exception:
        cfg = {}
    if extra and cfg:
        cfg.update(extra)
    return cfg


# ============================================================================
# CHART GENERATION FUNCTIONS
# ============================================================================
def create_gauge_chart(upside_pe, upside_ev):
    """Create professional dual gauge chart for valuations"""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        horizontal_spacing=0.15
    )
    
    # PE Multiple Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_pe if upside_pe else 0,
        number={'suffix': "%", 'font': {'size': 28, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "PE Multiple", 'font': {'size': 14, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#7c3aed", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    # EV/EBITDA Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 28, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "EV/EBITDA", 'font': {'size': 14, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#ec4899", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': '#e2e8f0'}
    )
    return fig

def create_valuation_comparison_chart(vals):
    """Create professional bar chart comparing current vs fair values"""
    categories = []
    current_vals = []
    fair_vals = []
    
    if vals['fair_value_pe']:
        categories.append('PE Multiple')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_pe'])
    
    if vals['fair_value_ev']:
        categories.append('EV/EBITDA')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_ev'])
    
    if not categories:
        return None
    
    fig = go.Figure()
    
    # Current Price bars
    fig.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current_vals,
        marker=dict(
            color='#6366f1',
            line=dict(color='#818cf8', width=2),
        ),
        text=[f'₹{v:,.2f}' for v in current_vals],
        textposition='outside',
        textfont=dict(size=12, color='#e2e8f0', family='Inter')
    ))
    
    # Fair Value bars
    colors = ['#34d399' if fv > cv else '#f87171' for fv, cv in zip(fair_vals, current_vals)]
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair_vals,
        marker=dict(
            color=colors,
            line=dict(color=['#6ee7b7' if c == '#34d399' else '#fca5a5' for c in colors], width=2),
        ),
        text=[f'₹{v:,.2f}' for v in fair_vals],
        textposition='outside',
        textfont=dict(size=12, color='#e2e8f0', family='Inter')
    ))
    
    fig.update_layout(
        barmode='group',
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=11, color='#e2e8f0'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#e2e8f0')
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#4c1d95',
            tickfont=dict(size=11, color='#e2e8f0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(167, 139, 250, 0.2)',
            showline=False,
            tickprefix='₹',
            tickfont=dict(size=10, color='#a78bfa')
        ),
        margin=dict(l=40, r=30, t=40, b=30)
    )
    
    return fig

def create_52week_range_display(vals):
    """Create 52-week price range display using HTML/CSS"""
    low = vals.get('52w_low', 0)
    high = vals.get('52w_high', 0)
    current = vals.get('price', 0)
    
    if not all([low, high, current]) or high <= low:
        return None
    
    # Calculate position percentage
    position = ((current - low) / (high - low)) * 100
    position = max(0, min(100, position))  # Clamp between 0-100
    
    html = f'''
    <div class="range-container">
        <div class="range-labels">
            <span>52W Low: ₹{low:,.2f}</span>
            <span>52W High: ₹{high:,.2f}</span>
        </div>
        <div class="range-bar">
            <div class="range-indicator" style="left: {position}%;"></div>
        </div>
        <div class="range-info">
            Current Price: ₹{current:,.2f} ({position:.1f}% of range)
        </div>
    </div>
    '''
    return html

# ============================================================================
# PDF REPORT GENERATION
# ============================================================================
def create_pdf_report(company, ticker, sector, vals):
    """Generate professional PDF report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'], 
        fontSize=24, 
        textColor=colors.HexColor('#7c3aed'), 
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    story = []
    story.append(Paragraph("NYZTrade Comprehensive Analysis", title_style))
    story.append(Paragraph("Professional Stock Valuation Report", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Company Info
    story.append(Paragraph(f"{company}", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Calculate averages
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Fair Value Summary
    fair_data = [
        ['Metric', 'Value'],
        ['Fair Value', f"₹ {avg_fair:,.2f}"],
        ['Current Price', f"₹ {vals['price']:,.2f}"],
        ['Potential Upside', f"{avg_up:+.2f}%"]
    ]
    fair_table = Table(fair_data, colWidths=[3*inch, 2.5*inch])
    fair_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(fair_table)
    story.append(Spacer(1, 25))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        spaceBefore=20
    )
    story.append(Paragraph(
        "DISCLAIMER: This report is for educational purposes only and does not constitute financial advice. "
        "Always consult a qualified financial advisor before making investment decisions.",
        disclaimer_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    # ------------------------------------------------------------------
    # NAVIGATION / DEEP-LINK HANDLING (screener result -> valuation screen)
    # ------------------------------------------------------------------
    MODE_OPTIONS = [
        "🎯 Industry Screener",
        "⚡ Gamma Blast Screener",
        "📈 Individual Analysis",
        "📊 Industry Explorer"
    ]

    # Apply any pending navigation requested on the previous run
    if st.session_state.get("_pending_mode"):
        st.session_state["mode_select"] = st.session_state.pop("_pending_mode")

    # Handle ?mode=valuation&ticker=XXX deep links coming from the result tables
    _qp_ticker = _get_query_param("ticker")
    if _qp_ticker and st.session_state.get("_last_qp_ticker") != _qp_ticker:
        st.session_state["_last_qp_ticker"] = _qp_ticker
        st.session_state["deeplink_ticker"] = str(_qp_ticker).upper()
        st.session_state["input_method_radio"] = "✏️ Direct Ticker"
        st.session_state["auto_analyze"] = True
        st.session_state["mode_select"] = "📈 Individual Analysis"

    if "mode_select" not in st.session_state:
        st.session_state["mode_select"] = MODE_OPTIONS[0]

    # Header
    st.markdown(f'''
    <div class="main-header">
        <h1>🎯 NYZTrade Comprehensive Platform</h1>
        <h3>Professional Stock Analysis & Industry Screening</h3>
        <p>Advanced Valuation • {TOTAL_CATEGORIES} Industries • {TOTAL_STOCKS:,} Stock Universe</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Stats row
    st.markdown(f'''
    <div class="stats-container">
        <div class="stat-card">
            <h3>{TOTAL_CATEGORIES}</h3>
            <p>Industries</p>
        </div>
        <div class="stat-card">
            <h3>{TOTAL_STOCKS:,}</h3>
            <p>Stocks</p>
        </div>
        <div class="stat-card">
            <h3>6</h3>
            <p>Strategies</p>
        </div>
        <div class="stat-card">
            <h3>Live</h3>
            <p>Data</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔐 Account")
        st.markdown(f"**User:** {st.session_state.get('authenticated_user', 'Guest').title()}")
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔧 Analysis Mode")
        
        # Mode selection
        mode = st.selectbox(
            "Choose Mode",
            MODE_OPTIONS,
            key="mode_select"
        )

        with st.expander("🔗 Link Settings"):
            st.text_input(
                "App Base URL (optional)",
                key="app_base_url",
                placeholder="https://your-app.streamlit.app",
                help="Set this if the 'Valuation' links in the result tables should open "
                     "as full URLs (e.g. in a new tab). Leave blank to use relative links."
            )
    
    # Mode-specific content
    if mode == "🎯 Industry Screener":
        
        st.markdown("### 🎯 Industry-Based Stock Screener")
        
        # Industry selection with stock counts
        industries = sorted(get_all_categories())
        industry_options = []
        for industry in industries:
            stock_count = len(get_stocks_by_category(industry))
            industry_options.append(f"{industry} ({stock_count} stocks)")
        
        selected_industry_with_count = st.sidebar.selectbox("Select Industry", industry_options)
        selected_industry = selected_industry_with_count.split(" (")[0]  # Extract industry name
        
        # Strategy selection  
        strategy_options = [
            ("undervalued", "🎯 Undervalued Stocks (15%+ upside)"),
            ("undervalued_near_high", "🚀 Undervalued Near 52W High"),
            ("undervalued_supertrend", "📈 Undervalued + SuperTrend Bullish")
           
        ]
        
        strategy_choice = st.sidebar.selectbox(
            "Screening Strategy",
            strategy_options,
            format_func=lambda x: x[1]
        )
        
        strategy_type = strategy_choice[0]
        strategy_name = strategy_choice[1]
        
        # Parameters
        max_results = st.sidebar.slider("Max Results", 10, 100, 30)
        
        # Run screener
        if st.sidebar.button("🚀 Run Screener", type="primary"):
            
            # Show industry info
            industry_stocks = get_stocks_by_category(selected_industry)
            sector = get_sector_for_industry(selected_industry)
            
            st.markdown(f'''
            <div class="highlight-box">
                <h3>📊 {strategy_name}</h3>
                <p><strong>Industry:</strong> {selected_industry}</p>
                <p><strong>Sector:</strong> {sector}</p>
                <p><strong>Universe:</strong> {len(industry_stocks):,} stocks</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Run screener
            with st.spinner(f"🔍 Screening {len(industry_stocks):,} stocks..."):
                results_df = run_industry_screener(selected_industry, strategy_type, max_results)
            
            # Persist results so they survive reruns (needed for the valuation deep-link)
            st.session_state['screener_results'] = results_df
            st.session_state['screener_meta'] = {
                'industry': selected_industry,
                'strategy_type': strategy_type,
                'strategy_name': strategy_name
            }
        
        # ------------------------------------------------------------------
        # Render persisted screener results
        # ------------------------------------------------------------------
        results_df = st.session_state.get('screener_results')
        meta = st.session_state.get('screener_meta', {})
        
        if results_df is not None:
            _industry = meta.get('industry', selected_industry)
            _strategy_type = meta.get('strategy_type', strategy_type)
            _strategy_name = meta.get('strategy_name', strategy_name)
            
            if results_df.empty:
                st.warning(f"❌ No stocks found matching {_strategy_name} criteria in {_industry}")
            else:
                # Display results
                st.markdown(f'''
                <div class="success-message">
                    ✅ Found <strong>{len(results_df)}</strong> opportunities in {_industry}<br>
                    🎯 Strategy: {_strategy_name}
                </div>
                ''', unsafe_allow_html=True)
                
                # Sort results by upside
                results_df = results_df.sort_values('Upside %', ascending=False)
                
                # Format display
                display_df = results_df.copy()
                
                # Format currency columns
                for col in ['Price', 'Fair Value']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                # Format percentage columns
                for col in ['Upside %', 'ROE %', 'From 52W High %', 'From 52W Low %', 'Dividend Yield %']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else 'N/A')
                
                # Format ratio columns
                for col in ['PE Ratio', 'PB Ratio', 'Beta']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
                
                # Format volume columns (latest traded volume + relative volume)
                for col in ['Volume', 'Avg Volume']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(format_volume)
                if 'Rel Vol' in display_df.columns:
                    display_df['Rel Vol'] = display_df['Rel Vol'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A'
                    )
                
                # Format market cap
                if 'Market Cap' in display_df.columns:
                    display_df['Market Cap'] = display_df['Market Cap'].apply(
                        lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A'
                    )
                
                # Select key columns for display (now includes latest Volume + Valuation link)
                display_columns = ['Ticker', 'Name', 'Price', 'Fair Value', 'Upside %', 'PE Ratio',
                                   'Volume', 'Avg Volume', 'Rel Vol', 'From 52W High %', 'Cap Type', 'Valuation']
                display_columns = [c for c in display_columns if c in display_df.columns]
                
                # Display table
                st.dataframe(
                    display_df[display_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=min(500, len(display_df) * 35 + 100),
                    column_config=valuation_column_config()
                )
                
                # In-app jump to the valuation screen for any screened stock
                render_valuation_jump(results_df, "industry_screener")
                
                # Download CSV
                csv = results_df.to_csv(index=False)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"NYZTrade_{_industry.replace(' ', '_')}_{_strategy_type}_{timestamp}.csv"
                
                st.download_button(
                    f"📥 Download Results ({len(results_df)} stocks)",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
    
    elif mode == "⚡ Gamma Blast Screener":
        
        st.markdown("### ⚡ Gamma Blast Screener")
        st.caption("A direct port of the Nyztrade Gamma Flow indicator. One criterion only: "
                   "the blast condition. No breakout structure model, no trend confirmation.")
        
        # ---------------- Sidebar controls ----------------
        st.sidebar.markdown("### ⏱️ Timeframe & Direction")
        
        timeframe_label = st.sidebar.selectbox(
            "Timeframe",
            list(SCREENER_TIMEFRAMES.keys()),
            index=0
        )
        _cfg = SCREENER_TIMEFRAMES[timeframe_label]
        st.sidebar.caption(_cfg['note'])
        
        direction = st.sidebar.radio("Direction", ["Bullish Blast", "Bearish Blast"])
        
        st.sidebar.markdown("### 🌐 Universe")
        universe_mode = st.sidebar.selectbox(
            "Source", ["Preset Watchlist", "By Industry", "Custom Tickers"]
        )
        
        universe = {}
        universe_label = ""
        
        if universe_mode == "Preset Watchlist":
            preset = st.sidebar.selectbox("Watchlist", list(BREAKOUT_PRESET_UNIVERSES.keys()))
            universe = {t: t.replace('.NS', '').replace('.BO', '') for t in BREAKOUT_PRESET_UNIVERSES[preset]}
            universe_label = preset
        
        elif universe_mode == "By Industry":
            bo_industries = sorted(get_all_categories())
            bo_options = [f"{ind} ({len(get_stocks_by_category(ind))} stocks)" for ind in bo_industries]
            bo_selected = st.sidebar.selectbox("Industry", bo_options)
            bo_industry = bo_selected.split(" (")[0]
            universe = dict(get_stocks_by_category(bo_industry))
            universe_label = bo_industry
            scan_cap = st.sidebar.slider("Max stocks to scan", 20, 400, 120, step=20)
            if len(universe) > scan_cap:
                universe = dict(list(universe.items())[:scan_cap])
        
        else:
            custom_input = st.sidebar.text_area(
                "Tickers (comma or newline separated)",
                placeholder="RELIANCE.NS, TCS.NS, HDFCBANK.NS",
                height=120
            )
            raw = [x.strip().upper() for x in custom_input.replace("\n", ",").split(",") if x.strip()]
            raw = [x if x.endswith(('.NS', '.BO')) else f"{x}.NS" for x in raw]
            universe = {t: t.replace('.NS', '').replace('.BO', '') for t in raw}
            universe_label = "Custom List"
        
        # ---------------- Pine indicator inputs ----------------
        st.sidebar.markdown("### 💥 Blast Parameters")
        st.sidebar.caption("These map 1:1 to the inputs in your Pine indicator.")
        
        vol_mult = st.sidebar.slider(
            "Volume Threshold Multiplier", 1.0, 5.0, 2.0, 0.1,
            help="volume_threshold — volume must exceed this multiple of its moving average."
        )
        sensitivity = st.sidebar.slider(
            "Gamma Blast Sensitivity", 0.5, 3.0, 1.5, 0.1,
            help="sensitivity — minimum rate of change, in percent, in the trade direction."
        )
        mom_len = st.sidebar.slider(
            "Momentum Length", 2, 50, 10,
            help="momentum_length — lookback for the rate of change calculation."
        )
        vol_ma_len = st.sidebar.slider(
            "Volume MA Length", 5, 60, 20,
            help="volume_ma_length — baseline for the volume ratio."
        )
        rsi_len = st.sidebar.slider(
            "RSI Length", 2, 50, 14,
            help="length — RSI period."
        )
        
        with st.sidebar.expander("RSI thresholds"):
            rsi_bull = st.slider("Bullish RSI above", 50.0, 90.0, 70.0, 1.0)
            rsi_bear = st.slider("Bearish RSI below", 10.0, 50.0, 30.0, 1.0)
        
        st.sidebar.markdown("### 🎚️ Result Filters")
        spike_only = st.sidebar.checkbox(
            "Spikes only (gamma > floor)", value=False,
            help="The Pine 'spike' marker: a blast that also clears the score floor. "
                 "Fewer, stronger signals."
        )
        score_floor = st.sidebar.slider("Spike Score Floor", 0, 200, 50, 5)
        min_score = st.sidebar.slider("Min Gamma Score", 0, 200, 0, 5,
                                      help="Applies to every result, not just spikes.")
        min_price = st.sidebar.number_input("Min Price (₹)", min_value=1.0, value=20.0, step=5.0)
        min_avg_volume = st.sidebar.number_input("Min Avg Bar Volume", min_value=0,
                                                 value=25000, step=5000)
        max_results = st.sidebar.slider("Max Results", 10, 100, 40, key="bo_max_results")
        
        st.sidebar.markdown("### 💰 Valuation (display only)")
        include_valuation = st.sidebar.checkbox(
            "Show Fair Value & Upside %", value=True,
            help="Informational columns only — they never filter a stock out."
        )
        
        final_rank = st.sidebar.selectbox(
            "Rank results by", ["Gamma Score", "Blast Rank", "Upside %"]
        )
        
        with st.expander("📐 What the Gamma Score measures"):
            st.markdown("""
The score is the sum of three terms, exactly as in the Pine indicator:

| Term | Formula | Reads as |
|---|---|---|
| **Volume** | `(volume_ratio − 1) × 25` | How far above its own average the volume is |
| **Momentum** | `abs(price_momentum) × 2` | Rate of change over the momentum lookback |
| **Expansion** | `(volatility_expansion − 1) × 50` | ATR against its own 20-bar average |

A stock reaches this table only when **all four** blast conditions hold at once:
volume above the multiplier, RSI beyond its threshold, rate of change beyond
sensitivity in the trade direction, and ATR expansion above 1.2.

Two caveats worth holding onto. The momentum term uses an absolute value, so the
score itself is direction-blind — direction comes from the condition, not the
number. And **Blast Rank** matters more than the raw score: a reading of 70 is
routine on a habitually volatile counter and extraordinary on a quiet one. The
**Blasts/100** column tells you how often the name fires at all; a stock showing
30 blasts per 100 bars is not signalling anything.
            """)
        
        if st.sidebar.button("⚡ Run Blast Scan", type="primary"):
            if not universe:
                st.warning("❌ No tickers in the selected universe.")
            else:
                st.markdown(f'''
                <div class="highlight-box">
                    <h3>⚡ {direction} — {timeframe_label}</h3>
                    <p><strong>Universe:</strong> {universe_label} ({len(universe):,} stocks)</p>
                    <p><strong>Volume ×:</strong> {vol_mult:.1f} &nbsp;•&nbsp;
                       <strong>Sensitivity:</strong> {sensitivity:.1f}% &nbsp;•&nbsp;
                       <strong>Momentum:</strong> {mom_len} bars</p>
                </div>
                ''', unsafe_allow_html=True)
                
                with st.spinner(f"⚡ Scanning {len(universe):,} stocks..."):
                    bo_df, bo_funnel = run_blast_screener(
                        universe=universe,
                        timeframe_label=timeframe_label,
                        direction=direction,
                        rsi_len=rsi_len,
                        vol_ma_len=vol_ma_len,
                        mom_len=mom_len,
                        sensitivity=sensitivity,
                        vol_mult=vol_mult,
                        rsi_bull=rsi_bull,
                        rsi_bear=rsi_bear,
                        score_floor=score_floor,
                        min_score=min_score,
                        spike_only=spike_only,
                        min_price=min_price,
                        min_avg_volume=min_avg_volume,
                        max_results=max_results,
                        final_rank=final_rank,
                        include_valuation=include_valuation
                    )
                
                st.session_state['breakout_results'] = bo_df
                st.session_state['breakout_funnel'] = bo_funnel
                st.session_state['breakout_meta'] = {
                    'timeframe': timeframe_label,
                    'direction': direction,
                    'universe_label': universe_label
                }
        
        # ---------------- Render results ----------------
        bo_df = st.session_state.get('breakout_results')
        bo_meta = st.session_state.get('breakout_meta', {})
        bo_funnel = st.session_state.get('breakout_funnel', {})
        
        if bo_df is not None:
            if bo_funnel:
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("Scanned", bo_funnel.get('scanned', 0))
                f2.metric("Had Data", bo_funnel.get('with_data', 0))
                f3.metric("Blast Firing", bo_funnel.get('blast', 0))
                f4.metric("Spikes", bo_funnel.get('spike', 0))
            
            if bo_df.empty:
                st.warning(
                    "❌ No blasts firing right now. This is normal — the blast condition "
                    "requires four things to be true simultaneously and can go long stretches "
                    "without triggering, especially outside market hours. Try a wider universe, "
                    "a lower volume multiplier, or a lower sensitivity."
                )
            else:
                st.markdown(f'''
                <div class="success-message">
                    ✅ <strong>{len(bo_df)}</strong> {bo_meta.get('direction', direction).lower()}
                    signals on the <strong>{bo_meta.get('timeframe', timeframe_label)}</strong> chart<br>
                    🌐 Universe: {bo_meta.get('universe_label', universe_label)}
                </div>
                ''', unsafe_allow_html=True)
                
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Signals", len(bo_df))
                s2.metric("Avg Gamma", f"{bo_df['Gamma Score'].mean():.1f}")
                s3.metric("Max Gamma", f"{bo_df['Gamma Score'].max():.1f}")
                s4.metric("Spikes", int((bo_df['Signal'] == "💥 Spike").sum()))
                
                bo_display = bo_df.copy()
                
                for col in ['LTP', 'Fair Value', 'VWAP']:
                    if col in bo_display.columns:
                        bo_display[col] = bo_display[col].apply(
                            lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                for col in ['Chg %', 'VWAP Dist %', 'Upside %', 'Momentum %']:
                    if col in bo_display.columns:
                        bo_display[col] = bo_display[col].apply(
                            lambda x: f"{x:+.2f}%" if pd.notna(x) else 'N/A')
                
                for col in ['Gamma Score', 'Vol Term', 'Mom Term', 'Exp Term']:
                    if col in bo_display.columns:
                        bo_display[col] = bo_display[col].apply(
                            lambda x: f"{x:.1f}" if pd.notna(x) else 'N/A')
                
                if 'Blast Rank' in bo_display.columns:
                    bo_display['Blast Rank'] = bo_display['Blast Rank'].apply(
                        lambda x: f"{x:.0f}%ile" if pd.notna(x) else 'N/A')
                for col in ['Vol Ratio', 'Vol Expansion']:
                    if col in bo_display.columns:
                        bo_display[col] = bo_display[col].apply(
                            lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                if 'RSI' in bo_display.columns:
                    bo_display['RSI'] = bo_display['RSI'].apply(
                        lambda x: f"{x:.1f}" if pd.notna(x) else 'N/A')
                if 'ATR %' in bo_display.columns:
                    bo_display['ATR %'] = bo_display['ATR %'].apply(
                        lambda x: f"{x:.2f}%" if pd.notna(x) else 'N/A')
                if 'PE Ratio' in bo_display.columns:
                    bo_display['PE Ratio'] = bo_display['PE Ratio'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                
                for col in ['Volume', 'Avg Volume', 'Session Volume']:
                    if col in bo_display.columns:
                        bo_display[col] = bo_display[col].apply(format_volume)
                
                bo_columns = ['Ticker', 'Name', 'Timeframe', 'LTP', 'Fair Value', 'Upside %',
                              'Value Tag', 'Signal', 'Stage', 'Gamma Score', 'Blast Rank',
                              'Chg %', 'Vol Ratio', 'Volume', 'Avg Volume', 'Session Volume',
                              'Momentum %', 'Vol Expansion', 'RSI', 'ATR %',
                              'VWAP', 'VWAP Dist %', 'Streak', 'Blasts/100',
                              'PE Ratio', 'Cap Type', 'Last Candle', 'Valuation']
                bo_columns = [c for c in bo_columns if c in bo_display.columns]
                
                st.dataframe(
                    bo_display[bo_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=min(600, len(bo_display) * 35 + 100),
                    column_config=valuation_column_config()
                )
                
                render_valuation_jump(bo_df, "breakout_screener")
                
                with st.expander("🔬 Score decomposition"):
                    st.caption("Which of the three terms is carrying the score. A blast built "
                               "almost entirely on the volume term is a different event from one "
                               "built on volatility expansion.")
                    d_cols = ['Ticker', 'Gamma Score', 'Vol Term', 'Mom Term', 'Exp Term',
                              'Blast Rank', 'Streak', 'Blasts/100']
                    d_cols = [c for c in d_cols if c in bo_df.columns]
                    st.dataframe(bo_df[d_cols], use_container_width=True, hide_index=True)
                
                if 'Fair Value' in bo_df.columns and bo_df['Fair Value'].notna().any():
                    with st.expander("💰 Valuation detail"):
                        st.caption("Context only — none of these figures filtered any stock out.")
                        q_cols = ['Ticker', 'LTP', 'Fair Value', 'Upside %', 'Value Tag',
                                  'PE Ratio', 'Cap Type']
                        q_cols = [c for c in q_cols if c in bo_df.columns]
                        st.dataframe(bo_df[q_cols], use_container_width=True, hide_index=True)
                
                bo_csv = bo_df.to_csv(index=False)
                bo_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                bo_tf = bo_meta.get('timeframe', timeframe_label).replace(' ', '')
                st.download_button(
                    f"📥 Download Blast Results ({len(bo_df)} stocks)",
                    data=bo_csv,
                    file_name=f"NYZTrade_GammaBlast_{bo_tf}_{bo_ts}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    elif mode == "📈 Individual Analysis":
        
        st.markdown("### 📈 Individual Stock Analysis")
        
        # Stock selection methods
        st.sidebar.subheader("Stock Selection")
        
        if "input_method_radio" not in st.session_state:
            st.session_state["input_method_radio"] = "🔍 Search by Name"
        
        input_method = st.sidebar.radio(
            "Input Method",
            ["🔍 Search by Name", "✏️ Direct Ticker", "📋 Browse by Industry"],
            key="input_method_radio"
        )
        
        selected_ticker = None
        
        if input_method == "🔍 Search by Name":
            search_query = st.sidebar.text_input("Search Company", placeholder="e.g., Reliance, TCS, HDFC")
            
            if search_query and len(search_query) >= 2:
                search_results = search_stocks_by_name(search_query, 15)
                if search_results:
                    options = [f"{r['ticker']} - {r['name']}" for r in search_results]
                    selected = st.sidebar.selectbox("Select Stock", [""] + options)
                    if selected:
                        selected_ticker = selected.split(" - ")[0]
                else:
                    st.sidebar.info("No stocks found")
        
        elif input_method == "✏️ Direct Ticker":
            selected_ticker = st.sidebar.text_input(
                "Enter Ticker",
                value=st.session_state.get("deeplink_ticker", ""),
                placeholder="e.g., RELIANCE.NS"
            ).upper()
        
        elif input_method == "📋 Browse by Industry":
            browse_industries = sorted(get_all_categories())
            browse_industry_options = [""] + [f"{industry} ({len(get_stocks_by_category(industry))} stocks)" for industry in browse_industries]
            selected_browse_industry_with_count = st.sidebar.selectbox("Select Industry", browse_industry_options)
            
            if selected_browse_industry_with_count:
                browse_industry = selected_browse_industry_with_count.split(" (")[0]  # Extract industry name
                industry_stocks = get_stocks_by_category(browse_industry)
                stock_options = [f"{ticker} - {name}" for ticker, name in industry_stocks.items()]
                selected_stock = st.sidebar.selectbox("Select Stock", [""] + sorted(stock_options))
                if selected_stock:
                    selected_ticker = selected_stock.split(" - ")[0]
        
        # Analyze button (auto-triggers when arriving from a screener valuation link)
        analyze_clicked = st.sidebar.button("🚀 Analyze", type="primary")
        auto_analyze = st.session_state.pop("auto_analyze", False)
        
        if selected_ticker and (analyze_clicked or auto_analyze):
            
            # Get stock info for industry context
            stock_info = get_stock_info(selected_ticker)
            
            with st.spinner(f"Analyzing {selected_ticker}..."):
                info, error = fetch_stock_data(selected_ticker)
            
            if error or not info:
                st.error(f"❌ Error: {error if error else 'Failed to fetch stock data'}")
                st.stop()
            
            vals = calculate_valuations(info, stock_info['category'] if stock_info else None)
            if not vals:
                st.error("❌ Unable to calculate valuations for this stock")
                st.stop()
            
            # Data Quality Validation
            data_quality_issues = []
            if not vals.get('trailing_pe') or vals['trailing_pe'] <= 0:
                data_quality_issues.append("PE Ratio unavailable or negative")
            if not vals.get('trailing_eps') or vals['trailing_eps'] <= 0:
                data_quality_issues.append("EPS unavailable or negative")
            if not vals.get('fair_value_pe') and not vals.get('fair_value_ev'):
                data_quality_issues.append("No fair value calculation possible")
            
            # Show data quality alert if issues found
            if data_quality_issues:
                st.warning(f"""
                ⚠️ **Data Quality Alert**: Unaudited data suspected and thus limited valuation possible
                
                **Issues detected:**
                - {chr(10).join(['• ' + issue for issue in data_quality_issues])}
                
                **Recommendation**: Verify financial data from official sources before making investment decisions.
                """)
            
            # Extract company info
            company = info.get('longName', selected_ticker)
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            
            # Company Header
            st.markdown(f'''
            <div class="company-header">
                <div class="company-title">{company}</div>
                <div class="company-info">
                    🏷️ {selected_ticker} • 🏢 {sector} • 🏭 {industry}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Calculate average values
            ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
            avg_up = np.mean(ups) if ups else 0
            fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
            avg_fair = np.mean(fairs) if fairs else vals['price']
            
            # Main metrics row
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Fair Value Card
                st.markdown(f'''
                <div class="fair-value-card">
                    <div class="fair-value-title">📊 Calculated Fair Value</div>
                    <div class="fair-value-amount">₹{avg_fair:,.2f}</div>
                    <div class="fair-value-details">
                        Current Price: ₹{vals["price"]:,.2f}<br>
                        {"📈" if avg_up > 0 else "📉"} {avg_up:+.2f}% Potential
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                # Recommendation
                if avg_up > 25:
                    rec_class, rec_text, rec_icon = "rec-strong-buy", "Significantly Undervalued", "🚀"
                elif avg_up > 15:
                    rec_class, rec_text, rec_icon = "rec-buy", "Undervalued", "✅"
                elif avg_up > 0:
                    rec_class, rec_text, rec_icon = "rec-buy", "Fairly Valued", "📥"
                elif avg_up > -10:
                    rec_class, rec_text, rec_icon = "rec-hold", "Slightly Overvalued", "⏸️"
                else:
                    rec_class, rec_text, rec_icon = "rec-avoid", "Overvalued", "⚠️"
                
                st.markdown(f'''
                <div class="recommendation-card {rec_class}">
                    <h3>{rec_icon} {rec_text}</h3>
                    <p>Expected Return: {avg_up:+.2f}%</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # PDF Download
                if not data_quality_issues:  # Only offer PDF if data quality is good
                    pdf = create_pdf_report(company, selected_ticker, sector, vals)
                    st.download_button(
                        "📥 Download PDF Report",
                        data=pdf,
                        file_name=f"NYZTrade_{selected_ticker}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            # Key Metrics Cards
            st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
            
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            
            metrics_data = [
                (m1, "💰", f"₹{vals['price']:,.2f}", "Current Price"),
                (m2, "📈", f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A", "PE Ratio"),
                (m3, "💵", f"₹{vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A", "EPS (TTM)"),
                (m4, "🏦", f"₹{vals['market_cap']/10000000:,.0f}Cr" if vals['market_cap'] else "N/A", "Market Cap"),
                (m5, "📊", f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else "N/A", "EV/EBITDA"),
                (m6, "📚", f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else "N/A", "P/B Ratio")
            ]
            
            for col, icon, value, label in metrics_data:
                with col:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div style="font-size: 1.5rem;">{icon}</div>
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Charts Section
            st.markdown("---")
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown('<div class="section-header">🎯 Valuation Gauges</div>', unsafe_allow_html=True)
                if vals['upside_pe'] is not None or vals['upside_ev'] is not None:
                    fig_gauge = create_gauge_chart(
                        vals['upside_pe'] if vals['upside_pe'] else 0,
                        vals['upside_ev'] if vals['upside_ev'] else 0
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                else:
                    st.info("Insufficient data for gauge charts")
            
            with chart_col2:
                st.markdown('<div class="section-header">📊 Price vs Fair Value</div>', unsafe_allow_html=True)
                fig_bar = create_valuation_comparison_chart(vals)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Insufficient data for comparison chart")
            
            # Additional Chart
            st.markdown('<div class="section-header">📍 52-Week Range</div>', unsafe_allow_html=True)
            range_html = create_52week_range_display(vals)
            if range_html:
                st.markdown(range_html, unsafe_allow_html=True)
            else:
                st.info("52-week data not available")
            
            # Detailed Valuation Methods
            st.markdown("---")
            st.markdown('<div class="section-header">📋 Valuation Breakdown</div>', unsafe_allow_html=True)
            
            val_col1, val_col2 = st.columns(2)
            
            with val_col1:
                if vals['fair_value_pe'] and vals['trailing_pe']:
                    st.markdown(f'''
                    <div class="valuation-box">
                        <div class="valuation-method">📈 PE Multiple Method</div>
                        <div class="valuation-row">
                            <span class="valuation-label">Current PE</span>
                            <span class="valuation-value">{vals['trailing_pe']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Industry PE</span>
                            <span class="valuation-value">{vals['industry_pe']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">EPS (TTM)</span>
                            <span class="valuation-value">₹{vals['trailing_eps']:.2f}</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Fair Value (PE)</span>
                            <span class="valuation-value">₹{vals['fair_value_pe']:,.2f}</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Upside (PE)</span>
                            <span class="valuation-value">{vals['upside_pe']:+.2f}%</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("PE valuation not available due to data quality issues")
            
            with val_col2:
                if vals['fair_value_ev'] and vals['current_ev_ebitda']:
                    st.markdown(f'''
                    <div class="valuation-box">
                        <div class="valuation-method">💼 EV/EBITDA Method</div>
                        <div class="valuation-row">
                            <span class="valuation-label">Current EV/EBITDA</span>
                            <span class="valuation-value">{vals['current_ev_ebitda']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Industry EV/EBITDA</span>
                            <span class="valuation-value">{vals['industry_ev_ebitda']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">EBITDA</span>
                            <span class="valuation-value">₹{vals['ebitda']/10000000:,.0f} Cr</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Fair Value (EV)</span>
                            <span class="valuation-value">₹{vals['fair_value_ev']:,.2f}</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Upside (EV)</span>
                            <span class="valuation-value">{vals['upside_ev']:+.2f}%</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("EV/EBITDA valuation not available due to data quality issues")
    
    elif mode == "📊 Industry Explorer":
        
        st.markdown("### 📊 Industry Explorer")
        
        # Show industry statistics
        industry_counts = {industry: len(stocks) for industry, stocks in INDIAN_STOCKS.items()}
        top_industries = dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:12])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Top Industries by Stock Count")
            
            # Create bar chart
            industries_df = pd.DataFrame(list(top_industries.items()), columns=['Industry', 'Stock Count'])
            fig = px.bar(
                industries_df, 
                x='Stock Count', 
                y='Industry',
                orientation='h',
                height=400,
                color='Stock Count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Database Statistics")
            
            st.metric("Total Industries", f"{TOTAL_CATEGORIES}")
            st.metric("Total Stocks", f"{TOTAL_STOCKS:,}")
            st.metric("Avg per Industry", f"{TOTAL_STOCKS // TOTAL_CATEGORIES}")
            
            # Sector distribution
            st.markdown("#### Sector Breakdown")
            sectors_count = {}
            for industry in get_all_categories():
                sector = get_sector_for_industry(industry)
                sectors_count[sector] = sectors_count.get(sector, 0) + 1
            
            for sector, count in sorted(sectors_count.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{sector}: {count}")
        
        # Specific industry exploration
        st.markdown("---")
        st.markdown("#### 🔍 Explore Industry Details")
        
        # Create industry options with stock counts
        explore_industries = sorted(get_all_categories())
        explore_industry_options = [""] + [f"{industry} ({len(get_stocks_by_category(industry))} stocks)" for industry in explore_industries]
        selected_explore_industry_with_count = st.selectbox("Select Industry", explore_industry_options)
        
        if selected_explore_industry_with_count:
            explore_industry = selected_explore_industry_with_count.split(" (")[0]  # Extract industry name
            industry_stocks = get_stocks_by_category(explore_industry)
            sector = get_sector_for_industry(explore_industry)
            
            st.info(f"**{explore_industry}** • Sector: {sector} • {len(industry_stocks)} stocks")
            
            # Show stocks in expandable section
            if st.expander(f"View all {len(industry_stocks)} stocks"):
                stocks_df = pd.DataFrame(list(industry_stocks.items()), columns=['Ticker', 'Company'])
                st.dataframe(stocks_df, use_container_width=True, hide_index=True)
    
    else:
        # Welcome screen
        st.markdown('''
        <div class="welcome-section">
            <div class="welcome-title">👋 Welcome to NYZTrade Platform</div>
            <div class="welcome-subtitle">Your comprehensive solution for stock analysis and industry screening</div>
            
            <div class="feature-list">
                <h4>🎯 Platform Features:</h4>
                <ul>
                    <li>🔍 <strong>Industry Screener:</strong> Advanced filtering with 6 proven strategies</li>
                    <li>📈 <strong>Individual Analysis:</strong> Multi-factor valuation with data quality alerts</li>
                    <li>📊 <strong>Professional Charts:</strong> Interactive visualizations and technical analysis</li>
                    <li>📥 <strong>PDF Reports:</strong> Downloadable professional analysis reports</li>
                    <li>🎯 <strong>Buy/Sell Recommendations:</strong> AI-powered investment guidance</li>
                    <li>📱 <strong>Mobile Optimized:</strong> Perfect for analysis on any device</li>
                </ul>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Footer
    st.markdown('''
    <div class="footer">
        <h3>NYZTrade Comprehensive Platform</h3>
        <p>Professional Stock Analysis & Industry Screening Solution</p>
        <div class="disclaimer">
            ⚠️ Disclaimer: This platform is for educational and research purposes only. 
            Always consult a qualified financial advisor before making investment decisions.
            Past performance does not guarantee future results.
        </div>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
