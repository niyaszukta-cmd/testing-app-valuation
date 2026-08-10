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
    
    # ---- Peer-average P/E override -----------------------------------------
    # When enabled, the industry P/E becomes the mean trailing P/E of the
    # stocks actually in this industry, with missing P/Es excluded rather than
    # counted as zero. Applied AFTER the cap multipliers and deliberately not
    # scaled by them: a measured peer average already embodies the size mix of
    # the industry, so multiplying again would double-count it.
    try:
        if st.session_state.get('use_peer_pe'):
            peer = compute_peer_industry_pe(
                industry,
                max_sample=int(st.session_state.get('peer_pe_sample', 60)),
                pe_cap=float(st.session_state.get('peer_pe_cap', 200.0))
            )
            min_n = int(st.session_state.get('peer_pe_min_n', 3))
            if peer and peer.get('n', 0) >= min_n and peer.get('mean'):
                base_benchmarks['pe'] = peer['mean']
                base_benchmarks['pe_source'] = 'peer'
                base_benchmarks['peer_n'] = peer['n']
    except Exception:
        pass
    
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
# EARNINGS + VALUE SCREENER
# ----------------------------------------------------------------------------
# DESIGN NOTES
#
# Exactly three criteria, and no technical/momentum model at all:
#
#   1. Price is near its 52-week high
#   2. Price is below the fair value estimate
#   3. Earnings fall inside a chosen calendar window
#
# The stages run cheapest-first. Stage 1 works from batched daily bars and
# typically removes most of a universe for the cost of a few requests. Only
# the survivors reach the per-ticker calls in stages 2 and 3, both of which
# are cached (fair value 1h, earnings dates 1h).
#
# The two earnings windows are OPPOSITE trades and the UI says so. "Reported
# in the last N days" is post-earnings drift: the event is behind you and the
# surprise is known. "Due in the next N days" means holding through a binary
# event, where a gap passes straight through a stop.
# ============================================================================

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
# EARNINGS CALENDAR + VALUE + 52-WEEK HIGH ENGINE
# ---------------------------------------------------------------------------
# Three criteria only:
#
#   1. Price is approaching its 52-week high
#   2. Price is below fair value (undervalued)
#   3. Earnings fall inside a chosen window - either due in the next N days,
#      or already reported in the last N days
#
# No breakout structure, no momentum indicators, no timeframe scanning.
# ---------------------------------------------------------------------------

EARNINGS_MODES = {
    "Reported in last N days (post-earnings drift)": "reported",
    "Due in next N days (pre-earnings run-up)": "upcoming",
    "Either side of earnings": "either",
    "No earnings filter": "off",
}


@st.cache_data(ttl=900, show_spinner=False)
def fetch_daily_history_batch(tickers_tuple, period="1y"):
    """Daily OHLCV for the 52-week high calculation. Cached 15 minutes."""
    return _batch_download(tickers_tuple, "1d", period)


# ---------------------------------------------------------------------------
# PEER-AVERAGE INDUSTRY P/E
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def compute_peer_industry_pe(industry, max_sample=60, pe_cap=200.0):
    """
    Mean trailing P/E of the stocks actually in this industry.

    Stocks with no P/E are excluded, not treated as zero. A missing P/E on
    Yahoo almost always means negative or nil earnings, and averaging those
    in as zeros would drag every fair value down.

    Also excluded: non-positive P/E (loss-making, where the ratio carries no
    valuation meaning) and anything above `pe_cap`, since one 900x outlier
    moves the mean of a 20-stock industry by 45 points on its own.
    """
    result = {'mean': None, 'median': None, 'n': 0, 'excluded_missing': 0,
              'excluded_negative': 0, 'excluded_outlier': 0, 'values': [],
              'sample_size': 0}
    try:
        stocks = get_stocks_by_category(industry)
        if not stocks:
            return result

        tickers = list(stocks.keys())[:max_sample]
        result['sample_size'] = len(tickers)
        values = []

        for ticker in tickers:
            try:
                f = get_stock_fundamentals(ticker)
            except Exception:
                f = None
            if not f:
                result['excluded_missing'] += 1
                continue
            pe = f.get('trailing_pe')
            if pe is None or (isinstance(pe, float) and pd.isna(pe)):
                result['excluded_missing'] += 1
                continue
            pe = float(pe)
            if pe <= 0:
                result['excluded_negative'] += 1
                continue
            if pe > pe_cap:
                result['excluded_outlier'] += 1
                continue
            values.append(pe)

        if values:
            result['values'] = sorted(values)
            result['n'] = len(values)
            result['mean'] = float(np.mean(values))
            result['median'] = float(np.median(values))
    except Exception:
        pass
    return result


# ---------------------------------------------------------------------------
# EARNINGS DATES - MULTI-SOURCE FALLBACK CHAIN
# ---------------------------------------------------------------------------
# Yahoo has no earnings dates for large parts of the NSE mid and small cap
# universe. Each source below is tried in turn and the winner is recorded in
# the 'source' field so you can see how a date was obtained.
# ---------------------------------------------------------------------------

# SEBI LODR Regulation 33: quarterly results must be filed within 45 days of
# the quarter end (60 days for the final quarter of the financial year).
SEBI_FILING_LAG_DAYS = 45
SEBI_Q4_FILING_LAG_DAYS = 60


def _earnings_from_info(ticker):
    """Source 3: the earnings timestamps buried in the already-cached info dict."""
    try:
        info, err = fetch_stock_data(ticker)
        if err or not info:
            return None, None
        nxt = last = None
        for key in ('earningsTimestamp', 'earningsTimestampStart', 'earningsTimestampEnd'):
            ts = info.get(key)
            if not ts:
                continue
            try:
                d = pd.Timestamp(int(ts), unit='s')
            except Exception:
                continue
            now = pd.Timestamp.now()
            if d > now:
                nxt = d if nxt is None or d < nxt else nxt
            else:
                last = d if last is None or d > last else last
        return nxt, last
    except Exception:
        return None, None


def _earnings_from_quarter_end(ticker):
    """
    Source 4: infer the announcement from the most recent reported quarter.

    Yahoo exposes the quarter END date even when it has no announcement date.
    Adding the statutory filing lag gives an approximation - clearly flagged as
    estimated, never presented as a confirmed date.
    """
    try:
        info, err = fetch_stock_data(ticker)
        q_end = None
        if not err and info:
            ts = info.get('mostRecentQuarter')
            if ts:
                try:
                    q_end = pd.Timestamp(int(ts), unit='s')
                except Exception:
                    q_end = None

        if q_end is None:
            tk = yf.Ticker(ticker)
            for attr in ('quarterly_income_stmt', 'quarterly_financials'):
                try:
                    qdf = getattr(tk, attr)
                    if qdf is not None and not qdf.empty:
                        cols = [pd.Timestamp(c) for c in qdf.columns]
                        q_end = max(cols)
                        break
                except Exception:
                    continue

        if q_end is None:
            return None, None, None

        # Q4 (financial year ending March in India) gets the longer window
        lag = SEBI_Q4_FILING_LAG_DAYS if q_end.month == 3 else SEBI_FILING_LAG_DAYS
        deadline = q_end + pd.Timedelta(days=lag)
        now = pd.Timestamp.now()

        # The filing deadline for the most recent quarter end may not have
        # arrived yet. In that case it is the NEXT expected announcement, and
        # the last one belongs to the quarter before it - otherwise a stock
        # reports a "last earnings" date that has not happened.
        if deadline > now:
            est_next = deadline
            prev_q_end = q_end - pd.Timedelta(days=91)
            prev_lag = SEBI_Q4_FILING_LAG_DAYS if prev_q_end.month == 3 else SEBI_FILING_LAG_DAYS
            est_last = prev_q_end + pd.Timedelta(days=prev_lag)
            if est_last > now:
                est_last = None
        else:
            est_last = deadline
            next_q_end = q_end + pd.Timedelta(days=91)
            next_lag = SEBI_Q4_FILING_LAG_DAYS if next_q_end.month == 3 else SEBI_FILING_LAG_DAYS
            est_next = next_q_end + pd.Timedelta(days=next_lag)

        return est_next, est_last, q_end
    except Exception:
        return None, None, None


@st.cache_data(ttl=21600, show_spinner=False)
def _earnings_from_nse(symbol):
    """
    Source 5: NSE India board-meeting calendar. OFF by default.

    NSE requires a cookie handshake and blocks most datacentre IP ranges, so
    this frequently fails from Streamlit Cloud and other hosted environments.
    It is opt-in for that reason, and every failure is silent.
    """
    try:
        import requests
    except Exception:
        return None, None

    base = "https://www.nseindia.com"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{base}/get-quotes/equity?symbol={symbol}",
    }
    try:
        sess = requests.Session()
        sess.headers.update(headers)
        sess.get(base, timeout=6)                      # cookie handshake
        sess.get(f"{base}/get-quotes/equity?symbol={symbol}", timeout=6)

        for url in (f"{base}/api/top-corp-info?symbol={symbol}&market=equities",
                    f"{base}/api/quote-equity?symbol={symbol}&section=corp_info"):
            try:
                r = sess.get(url, timeout=8)
                if r.status_code != 200:
                    continue
                payload = r.json()
            except Exception:
                continue

            meetings = []
            def walk(node):
                if isinstance(node, dict):
                    if any(k in node for k in ('meetingdate', 'bm_date', 'meetingDate')):
                        meetings.append(node)
                    for v in node.values():
                        walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)
            walk(payload)

            dates = []
            for m in meetings:
                purpose = " ".join(str(v) for v in m.values()).lower()
                if 'result' not in purpose and 'financial' not in purpose:
                    continue
                raw = m.get('meetingdate') or m.get('bm_date') or m.get('meetingDate')
                if not raw:
                    continue
                for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y", "%d %b %Y"):
                    try:
                        dates.append(pd.Timestamp(datetime.strptime(str(raw).strip(), fmt)))
                        break
                    except Exception:
                        continue

            if dates:
                now = pd.Timestamp.now()
                future = [d for d in dates if d > now]
                past = [d for d in dates if d <= now]
                return (min(future) if future else None), (max(past) if past else None)
    except Exception:
        pass
    return None, None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_earnings_calendar(ticker, allow_nse=False, allow_estimate=True):
    """
    Next and most recent earnings dates, trying every available source.

    Source order, best first:
      1. Yahoo earnings_dates    - confirmed announcement dates
      2. Yahoo calendar          - confirmed next date
      3. Yahoo info timestamps   - free, already cached with the info dict
      4. NSE board meetings      - opt-in, often blocked from cloud hosts
      5. Quarter-end + SEBI lag  - ESTIMATE, flagged as such
    """
    out = {'next_date': None, 'days_to_next': None, 'last_date': None,
           'days_since_last': None, 'surprise_pct': None,
           'source': 'None', 'estimated': False}

    # ---- 1. Yahoo earnings_dates ----
    try:
        tk = yf.Ticker(ticker)
        try:
            df = tk.get_earnings_dates(limit=16)
        except Exception:
            df = None

        if df is not None and not df.empty:
            idx = pd.to_datetime(df.index)
            tz = getattr(idx, 'tz', None)
            now = pd.Timestamp.now(tz=tz) if tz is not None else pd.Timestamp.now()

            surprise_col = next((c for c in df.columns if 'surprise' in str(c).lower()), None)
            reported_col = next((c for c in df.columns if 'reported' in str(c).lower()), None)

            future = [d for d in idx if d > now]
            past = [d for d in idx if d <= now]

            if future:
                nxt = min(future)
                out['next_date'] = nxt
                out['days_to_next'] = int((nxt - now).days)
            if past:
                last = max(past)
                if reported_col is not None and reported_col in df.columns:
                    reported = [d for d in past if pd.notna(df.loc[d, reported_col])]
                    if reported:
                        last = max(reported)
                out['last_date'] = last
                out['days_since_last'] = int((now - last).days)
                if surprise_col is not None and surprise_col in df.columns:
                    val = df.loc[last, surprise_col]
                    if pd.notna(val):
                        out['surprise_pct'] = float(val)
            if out['next_date'] is not None or out['last_date'] is not None:
                out['source'] = 'Yahoo earnings'
    except Exception:
        pass

    # ---- 2. Yahoo calendar (next date only) ----
    if out['next_date'] is None:
        try:
            cal = yf.Ticker(ticker).calendar
            dates = None
            if isinstance(cal, dict):
                dates = cal.get('Earnings Date')
            elif cal is not None and hasattr(cal, 'index') and 'Earnings Date' in cal.index:
                dates = cal.loc['Earnings Date'].tolist()
            if dates:
                if not isinstance(dates, (list, tuple)):
                    dates = [dates]
                nxt = pd.Timestamp(min(dates))
                now = pd.Timestamp.now()
                if nxt > now:
                    out['next_date'] = nxt
                    out['days_to_next'] = int((nxt - now).days)
                    if out['source'] == 'None':
                        out['source'] = 'Yahoo calendar'
        except Exception:
            pass

    # ---- 3. Yahoo info timestamps ----
    if out['next_date'] is None or out['last_date'] is None:
        nxt, last = _earnings_from_info(ticker)
        now = pd.Timestamp.now()
        if out['next_date'] is None and nxt is not None:
            out['next_date'] = nxt
            out['days_to_next'] = int((nxt - now).days)
            if out['source'] == 'None':
                out['source'] = 'Yahoo info'
        if out['last_date'] is None and last is not None:
            out['last_date'] = last
            out['days_since_last'] = int((now - last).days)
            if out['source'] == 'None':
                out['source'] = 'Yahoo info'

    # ---- 4. NSE board meetings (opt-in) ----
    if allow_nse and (out['next_date'] is None or out['last_date'] is None):
        sym = ticker.replace('.NS', '').replace('.BO', '')
        nxt, last = _earnings_from_nse(sym)
        now = pd.Timestamp.now()
        if out['next_date'] is None and nxt is not None:
            out['next_date'] = nxt
            out['days_to_next'] = int((nxt - now).days)
            out['source'] = 'NSE'
        if out['last_date'] is None and last is not None:
            out['last_date'] = last
            out['days_since_last'] = int((now - last).days)
            if out['source'] in ('None',):
                out['source'] = 'NSE'

    # ---- 5. Quarter end + statutory filing lag (ESTIMATE) ----
    if allow_estimate and (out['next_date'] is None or out['last_date'] is None):
        est_next, est_last, q_end = _earnings_from_quarter_end(ticker)
        now = pd.Timestamp.now()
        if out['last_date'] is None and est_last is not None:
            out['last_date'] = est_last
            out['days_since_last'] = int((now - est_last).days)
            out['estimated'] = True
            out['source'] = f"≈ Q-end {q_end.strftime('%b-%Y')}" if q_end is not None else "≈ Estimated"
        if out['next_date'] is None and est_next is not None and est_next > now:
            out['next_date'] = est_next
            out['days_to_next'] = int((est_next - now).days)
            out['estimated'] = True
            if out['source'] == 'None':
                out['source'] = "≈ Estimated"

    return out


# ---------------------------------------------------------------------------
# MANUAL FAIR VALUE CALCULATOR
# ---------------------------------------------------------------------------
def render_manual_fair_value(results_key, key_prefix="mfv"):
    """
    Override the model's fair value for any row in the results table.

    The model blends a P/E and a P/B estimate off industry benchmarks. When
    those inputs are stale or distorted - a trailing EPS from a bad quarter,
    a book value that has since been written down - this lets you substitute
    your own numbers and push the result straight back into the table.
    """
    df = st.session_state.get(results_key)
    if df is None or getattr(df, 'empty', True) or 'Ticker' not in df.columns:
        return

    with st.expander("🧮 Manual Fair Value Calculator"):
        options = [f"{r['Ticker']} — {r.get('Name', '')}" for _, r in df.iterrows()]
        picked = st.selectbox("Stock", options, key=f"{key_prefix}_pick")
        ticker = picked.split(" — ")[0].strip()

        row = df[df['Ticker'] == ticker]
        if row.empty:
            return
        row = row.iloc[0]

        fundamentals = None
        try:
            fundamentals = get_stock_fundamentals(ticker)
        except Exception:
            pass

        ltp = float(row['LTP']) if pd.notna(row.get('LTP')) else 0.0
        eps_default = float(fundamentals.get('trailing_eps') or 0.0) if fundamentals else 0.0
        bv_default = float(fundamentals.get('book_value') or 0.0) if fundamentals else 0.0
        pe_default = float(fundamentals.get('trailing_pe') or 0.0) if fundamentals else 0.0

        industry = None
        try:
            si = get_stock_info(ticker)
            industry = si['category'] if si else (fundamentals.get('industry') if fundamentals else None)
        except Exception:
            pass
        bench = {}
        try:
            bench = get_industry_benchmarks(industry or 'Other',
                                            (fundamentals or {}).get('cap_type', 'Large'))
        except Exception:
            bench = {}

        st.caption(f"**{ticker}** · LTP ₹{ltp:,.2f} · Industry: {industry or 'Unknown'} · "
                   f"Current P/E {pe_default:,.2f} · Model fair value "
                   f"{'₹{:,.2f}'.format(row['Fair Value']) if pd.notna(row.get('Fair Value')) else 'N/A'}")

        c1, c2, c3 = st.columns(3)
        with c1:
            eps = st.number_input("EPS (₹)", value=float(round(eps_default, 2)),
                                  step=0.5, format="%.2f", key=f"{key_prefix}_eps")
            target_pe = st.number_input("Target P/E", value=float(round(bench.get('pe', 18.0), 2)),
                                        min_value=0.0, step=0.5, format="%.2f",
                                        key=f"{key_prefix}_pe")
        with c2:
            bv = st.number_input("Book Value / share (₹)", value=float(round(bv_default, 2)),
                                 step=1.0, format="%.2f", key=f"{key_prefix}_bv")
            target_pb = st.number_input("Target P/B", value=float(round(bench.get('pb', 2.5), 2)),
                                        min_value=0.0, step=0.1, format="%.2f",
                                        key=f"{key_prefix}_pb")
        with c3:
            pe_weight = st.slider("Weight on P/E method", 0, 100, 70, 5,
                                  key=f"{key_prefix}_w") / 100.0
            margin = st.slider("Margin of safety %", 0, 50, 0, 5,
                               key=f"{key_prefix}_mos",
                               help="Discounts the computed fair value before "
                                    "the upside is calculated.")

        pe_fv = eps * target_pe if eps and target_pe else None
        pb_fv = bv * target_pb if bv and target_pb else None

        if pe_fv is not None and pb_fv is not None:
            fv = pe_weight * pe_fv + (1 - pe_weight) * pb_fv
        else:
            fv = pe_fv if pe_fv is not None else pb_fv

        if fv is not None and fv > 0:
            fv = fv * (1 - margin / 100.0)
            upside = ((fv - ltp) / ltp * 100) if ltp else None

            r1, r2, r3 = st.columns(3)
            r1.metric("P/E fair value", f"₹{pe_fv:,.2f}" if pe_fv else "N/A")
            r2.metric("P/B fair value", f"₹{pb_fv:,.2f}" if pb_fv else "N/A")
            r3.metric("Blended fair value", f"₹{fv:,.2f}",
                      delta=f"{upside:+.1f}% vs LTP" if upside is not None else None)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ Apply to results table", key=f"{key_prefix}_apply",
                             use_container_width=True, type="primary"):
                    d = st.session_state[results_key].copy()
                    mask = d['Ticker'] == ticker
                    d.loc[mask, 'Fair Value'] = fv
                    d.loc[mask, 'Upside %'] = upside
                    d.loc[mask, 'Value Tag'] = get_valuation_tag(upside)
                    if 'FV Source' in d.columns:
                        d.loc[mask, 'FV Source'] = '🧮 Manual'
                    st.session_state[results_key] = d
                    st.rerun()
            with b2:
                if st.button("↩️ Revert this row to model", key=f"{key_prefix}_revert",
                             use_container_width=True):
                    d = st.session_state[results_key].copy()
                    mask = d['Ticker'] == ticker
                    try:
                        f2 = get_stock_fundamentals(ticker)
                        fv2 = calculate_fair_value(f2, industry or 'Other',
                                                   f2.get('cap_type', 'Large'))
                        up2 = ((fv2 - f2['price']) / f2['price'] * 100) if fv2 else None
                        d.loc[mask, 'Fair Value'] = fv2
                        d.loc[mask, 'Upside %'] = up2
                        d.loc[mask, 'Value Tag'] = get_valuation_tag(up2)
                        if 'FV Source' in d.columns:
                            d.loc[mask, 'FV Source'] = 'Model'
                        st.session_state[results_key] = d
                        st.rerun()
                    except Exception:
                        st.warning("Could not recompute the model value for this stock.")
        else:
            st.info("Enter an EPS with a target P/E, or a book value with a target P/B.")


def compute_52w_features(df):
    """Price position against the 52-week high, plus volume context."""
    try:
        if df is None or len(df) < 60:
            return None
        d = df[['High', 'Low', 'Close', 'Volume']].dropna(subset=['Close'])
        if len(d) < 60:
            return None

        window = d.iloc[-252:] if len(d) >= 252 else d
        high_52w = float(window['High'].max())
        low_52w = float(window['Low'].min())
        price = float(d['Close'].iloc[-1])
        if high_52w <= 0 or price <= 0:
            return None

        volume = d['Volume'].fillna(0)
        last_vol = float(volume.iloc[-1])
        avg_vol = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else last_vol
        prev_close = float(d['Close'].iloc[-2]) if len(d) > 1 else price

        # Negative = below the high. -2.0 means 2% under the 52-week high.
        pct_from_high = (price - high_52w) / high_52w * 100

        return {
            'price': price,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'pct_from_high': pct_from_high,
            'pct_from_low': (price - low_52w) / low_52w * 100 if low_52w > 0 else None,
            'last_volume': last_vol,
            'avg_volume': avg_vol,
            'rel_volume': (last_vol / avg_vol) if avg_vol > 0 else 0.0,
            'chg_pct': (price - prev_close) / prev_close * 100 if prev_close else 0.0,
            'last_bar': d.index[-1],
        }
    except Exception:
        return None


def earnings_window_passes(cal, mode, upcoming_days, reported_days):
    """Apply the chosen earnings-window rule. Returns (passes, status_label)."""
    d_next = cal.get('days_to_next')
    d_last = cal.get('days_since_last')

    upcoming = d_next is not None and 0 <= d_next <= upcoming_days
    reported = d_last is not None and 0 <= d_last <= reported_days

    if mode == "off":
        # No window applies here, so report the real dates rather than
        # pretending a stock 45 days from earnings has no date at all.
        if d_next is not None and d_last is not None:
            return True, (f"🔜 In {d_next}d" if d_next <= d_last else f"✅ {d_last}d ago")
        if d_next is not None:
            return True, f"🔜 In {d_next}d"
        if d_last is not None:
            return True, f"✅ {d_last}d ago"
        return True, "— No date"

    if mode == "upcoming":
        return upcoming, (f"🔜 In {d_next}d" if upcoming else "")

    if mode == "reported":
        return reported, (f"✅ {d_last}d ago" if reported else "")

    # either
    if upcoming and reported:
        return True, f"🔁 {d_last}d ago → {d_next}d"
    if upcoming:
        return True, f"🔜 In {d_next}d"
    if reported:
        return True, f"✅ {d_last}d ago"
    return False, ""


def run_earnings_value_screener(universe, near_high_pct=5.0, min_upside=15.0,
                                earnings_mode="reported", upcoming_days=30,
                                reported_days=30, min_price=20.0,
                                min_avg_volume=50000, max_results=40,
                                max_valuation_calls=150, chunk_size=25,
                                final_rank="Upside %", allow_nse=False,
                                allow_estimate=True):
    """
    Three-stage funnel, ordered cheapest first.

      1. Daily bars, batched  - 52-week high proximity, price, liquidity
      2. Fair value           - per ticker, cached, only on stage-1 survivors
      3. Earnings calendar    - per ticker, cached, only on stage-2 survivors

    Stages 2 and 3 are per-ticker calls, so the ordering matters: stage 1
    typically removes 90% of a universe for the cost of a handful of requests.
    """
    tickers = list(universe.keys())
    total = len(tickers)
    funnel = {'scanned': 0, 'with_data': 0, 'near_high': 0,
              'undervalued': 0, 'earnings_ok': 0, 'final': 0}

    if total == 0:
        return pd.DataFrame(), funnel

    # ---------------- STAGE 1: 52-week high proximity ----------------
    stage1 = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    processed = 0

    for start in range(0, total, chunk_size):
        chunk = tickers[start:start + chunk_size]
        status_text.text(f"📈 Stage 1/3 — 52-week high scan... "
                         f"{processed}/{total} | near high: {len(stage1)}")
        data_map = fetch_daily_history_batch(tuple(chunk), "1y")

        for ticker in chunk:
            processed += 1
            funnel['scanned'] += 1
            try:
                progress_bar.progress(min(processed / total * 0.5, 0.5))
            except Exception:
                pass

            df = data_map.get(ticker)
            if df is None or df.empty:
                continue
            funnel['with_data'] += 1

            feat = compute_52w_features(df)
            if not feat:
                continue
            if feat['price'] < min_price or feat['avg_volume'] < min_avg_volume:
                continue
            # pct_from_high is negative below the high; -near_high_pct is the floor
            if feat['pct_from_high'] < -abs(near_high_pct):
                continue

            funnel['near_high'] += 1
            stage1.append({'ticker': ticker, 'feat': feat})

    # Closest to the high first, then cap the per-ticker work that follows
    stage1.sort(key=lambda c: c['feat']['pct_from_high'], reverse=True)
    stage1 = stage1[:max_valuation_calls]

    # ---------------- STAGE 2: valuation ----------------
    rows = []
    for n, c in enumerate(stage1):
        ticker, feat = c['ticker'], c['feat']
        try:
            progress_bar.progress(min(0.5 + (n + 1) / max(len(stage1), 1) * 0.3, 0.8))
            status_text.text(f"💰 Stage 2/3 — valuing... {n + 1}/{len(stage1)} — {ticker}")
        except Exception:
            pass

        fair_value = upside = pe_ratio = cap_type = market_cap = None
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

        if upside is None or upside < min_upside:
            continue
        funnel['undervalued'] += 1

        rows.append({
            'ticker': ticker, 'feat': feat, 'fair_value': fair_value,
            'upside': upside, 'pe_ratio': pe_ratio, 'cap_type': cap_type,
            'market_cap': market_cap
        })

    # ---------------- STAGE 3: earnings calendar ----------------
    final_rows = []
    for n, r in enumerate(rows):
        ticker, feat = r['ticker'], r['feat']
        try:
            progress_bar.progress(min(0.8 + (n + 1) / max(len(rows), 1) * 0.2, 1.0))
            status_text.text(f"📅 Stage 3/3 — earnings dates... {n + 1}/{len(rows)} — {ticker}")
        except Exception:
            pass

        cal = fetch_earnings_calendar(ticker, allow_nse=allow_nse,
                                      allow_estimate=allow_estimate)
        passes, status = earnings_window_passes(cal, earnings_mode,
                                                upcoming_days, reported_days)
        if not passes:
            continue
        funnel['earnings_ok'] += 1

        surprise = cal.get('surprise_pct')
        if surprise is None:
            surprise_tag = "—"
        elif surprise > 0:
            surprise_tag = f"🟢 Beat {surprise:+.1f}%"
        elif surprise < 0:
            surprise_tag = f"🔴 Miss {surprise:+.1f}%"
        else:
            surprise_tag = "⚪ In line"

        final_rows.append({
            'Ticker': ticker,
            'Name': universe.get(ticker, ticker),
            'LTP': feat['price'],
            'Chg %': feat['chg_pct'],
            '52W High': feat['high_52w'],
            'From High %': feat['pct_from_high'],
            'Fair Value': r['fair_value'],
            'Upside %': r['upside'],
            'Value Tag': get_valuation_tag(r['upside']),
            'FV Source': 'Model',
            'Earnings': status,
            'Date Source': cal.get('source', 'None'),
            'Estimated': bool(cal.get('estimated')),
            'Next Earnings': cal['next_date'].strftime('%d-%b-%Y') if cal.get('next_date') is not None else 'N/A',
            'Days To': cal.get('days_to_next'),
            'Last Earnings': cal['last_date'].strftime('%d-%b-%Y') if cal.get('last_date') is not None else 'N/A',
            'Days Since': cal.get('days_since_last'),
            'Last Surprise': surprise_tag,
            'Surprise %': surprise,
            'Volume': feat['last_volume'],
            'Avg Volume': feat['avg_volume'],
            'Rel Vol': feat['rel_volume'],
            'From Low %': feat['pct_from_low'],
            'PE Ratio': r['pe_ratio'],
            'Cap Type': r['cap_type'],
            'Market Cap': r['market_cap'],
            'As Of': feat['last_bar'].strftime('%d-%b-%Y') if hasattr(feat['last_bar'], 'strftime') else str(feat['last_bar']),
            'Valuation': build_valuation_link(ticker),
        })

    try:
        progress_bar.empty()
        status_text.empty()
    except Exception:
        pass

    if not final_rows:
        return pd.DataFrame(), funnel

    df_out = pd.DataFrame(final_rows)

    if final_rank == "Closest to 52W High":
        df_out = df_out.sort_values('From High %', ascending=False)
    elif final_rank == "Earnings Soonest":
        df_out = df_out.sort_values('Days To', ascending=True, na_position='last')
    elif final_rank == "Best Surprise":
        df_out = df_out.sort_values('Surprise %', ascending=False, na_position='last')
    else:
        df_out = df_out.sort_values('Upside %', ascending=False)

    df_out = df_out.head(max_results).reset_index(drop=True)
    funnel['final'] = len(df_out)
    return df_out, funnel


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
        "📅 Earnings + Value Screener",
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
    
    elif mode == "📅 Earnings + Value Screener":
        
        st.markdown("### 📅 Earnings + Value Screener")
        st.caption("Undervalued stocks trading near their 52-week high, filtered by where "
                   "they sit in the earnings calendar. No breakout or momentum criteria.")
        
        # ---------------- Universe ----------------
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
            ev_industries = sorted(get_all_categories())
            ev_options = [f"{ind} ({len(get_stocks_by_category(ind))} stocks)" for ind in ev_industries]
            ev_selected = st.sidebar.selectbox("Industry", ev_options)
            ev_industry = ev_selected.split(" (")[0]
            universe = dict(get_stocks_by_category(ev_industry))
            universe_label = ev_industry
            scan_cap = st.sidebar.slider("Max stocks to scan", 20, 600, 200, step=20)
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
        
        # ---------------- The three criteria ----------------
        st.sidebar.markdown("### 📈 52-Week High Proximity")
        near_high_pct = st.sidebar.slider(
            "Within % of 52W high", 0.5, 25.0, 5.0, 0.5,
            help="How close to the 52-week high the stock must be trading. "
                 "5% means the price is no more than 5% below its 52-week high."
        )
        
        st.sidebar.markdown("### 💰 Valuation")
        
        st.sidebar.checkbox(
            "Industry P/E = peer average", value=True, key="use_peer_pe",
            help="Replaces the static benchmark table with the mean trailing P/E "
                 "of the stocks in that industry. Stocks with no P/E are excluded, "
                 "not counted as zero. Applies to every screen in the app."
        )
        if st.session_state.get("use_peer_pe"):
            with st.sidebar.expander("Peer P/E settings"):
                st.number_input("Max stocks sampled", 10, 300, 60, 10,
                                key="peer_pe_sample",
                                help="First run costs one cached call per stock.")
                st.number_input("Ignore P/E above", 20.0, 1000.0, 200.0, 10.0,
                                key="peer_pe_cap",
                                help="One 900x outlier moves a 20-stock mean by "
                                     "45 points. Set very high to disable.")
                st.number_input("Min stocks required", 1, 20, 3, 1,
                                key="peer_pe_min_n",
                                help="Below this, the static benchmark is kept.")
        
        min_upside = st.sidebar.slider(
            "Min Upside % vs Fair Value", 0, 100, 15, 5,
            help="Fair value uses the same model as the Industry Screener, so the "
                 "numbers reconcile between the two screens."
        )
        
        st.sidebar.markdown("### 📅 Earnings Window")
        earnings_choice = st.sidebar.selectbox(
            "Earnings filter", list(EARNINGS_MODES.keys()), index=0
        )
        earnings_mode = EARNINGS_MODES[earnings_choice]
        
        reported_days = 30
        upcoming_days = 30
        if earnings_mode in ("reported", "either"):
            reported_days = st.sidebar.slider("Reported within last N days", 1, 90, 30, 1)
        if earnings_mode in ("upcoming", "either"):
            upcoming_days = st.sidebar.slider("Due within next N days", 1, 90, 30, 1)
        
        with st.sidebar.expander("🔎 Earnings date sources"):
            st.caption("Yahoo has no earnings dates for much of the NSE mid and "
                       "small cap universe. These fallbacks fill the gaps.")
            allow_estimate = st.checkbox(
                "Estimate from quarter end", value=True,
                help="When no announcement date exists, infer one from the most "
                     "recent reported quarter plus the SEBI filing deadline "
                     "(45 days, 60 for Q4). Always flagged as an estimate."
            )
            allow_nse = st.checkbox(
                "Try NSE board meetings", value=False,
                help="Queries the NSE board-meeting calendar. NSE blocks most "
                     "datacentre IPs, so this usually fails on Streamlit Cloud "
                     "and other hosted environments. Slow when it does work."
            )
            if allow_nse:
                st.caption("⚠️ Adds a per-stock web request. Expect it to fail "
                           "silently when hosted.")
        
        if earnings_mode == "upcoming":
            st.sidebar.warning(
                "⚠️ Holding into an earnings date means holding gap risk. A gap "
                "through your stop is an uncontrolled loss, not a controlled one."
            )
        
        st.sidebar.markdown("### 🎚️ Basic Filters")
        min_price = st.sidebar.number_input("Min Price (₹)", min_value=1.0, value=20.0, step=5.0)
        min_avg_volume = st.sidebar.number_input("Min Avg Daily Volume", min_value=0,
                                                 value=50000, step=10000)
        max_results = st.sidebar.slider("Max Results", 10, 100, 40, key="ev_max_results")
        max_valuation_calls = st.sidebar.slider(
            "Max stocks to value", 25, 300, 150, 25,
            help="Caps the per-ticker work after the 52-week high filter. Lower is faster."
        )
        final_rank = st.sidebar.selectbox(
            "Rank results by",
            ["Upside %", "Closest to 52W High", "Earnings Soonest", "Best Surprise"]
        )
        
        with st.expander("📐 How this screen works, and what the two earnings windows mean"):
            st.markdown("""
Three filters, applied in this order so the expensive calls only touch survivors:

1. **Near the 52-week high** — from daily bars, batched. Breakouts into blue sky
   have better follow-through than breakouts in the middle of a range.
2. **Undervalued** — price below the fair value estimate, same model the Industry
   Screener uses.
3. **Earnings window** — where the stock sits in its reporting cycle.

**These two earnings windows are opposite trades, and it matters which you pick.**

*Reported in the last N days* is **post-earnings announcement drift** — a documented
tendency for price to keep moving in the direction of an earnings surprise for weeks
afterwards. The event risk is behind you and the surprise is known, which is why the
**Last Surprise** column matters most in this mode: drift follows the beats.

*Due in the next N days* is the **run-up** trade, and it carries the risk I would
normally tell you to screen out. You are holding through a binary event. A gap
against you passes straight through a stop. If you run this mode, size for the gap
rather than for the stop.

Combining "undervalued" with "near 52-week high" is deliberately contrarian — most
stocks near highs are not cheap. Expect few results, and treat a large `Upside %`
on a stock at its high with suspicion: check whether the fair value is being driven
by a single depressed input like a trailing EPS that has since recovered.
            """)
        
        if st.session_state.get("use_peer_pe") and universe_mode == "By Industry" and universe_label:
            _peer = compute_peer_industry_pe(
                universe_label,
                max_sample=int(st.session_state.get("peer_pe_sample", 60)),
                pe_cap=float(st.session_state.get("peer_pe_cap", 200.0))
            )
            if _peer and _peer.get('n', 0) > 0:
                _static = None
                try:
                    _static = INDUSTRY_BENCHMARKS.get(universe_label, {}).get('pe')
                except Exception:
                    pass
                pc1, pc2, pc3, pc4 = st.columns(4)
                pc1.metric("Peer P/E (mean)", f"{_peer['mean']:.2f}")
                pc2.metric("Peer P/E (median)", f"{_peer['median']:.2f}")
                pc3.metric("Stocks with P/E", f"{_peer['n']} / {_peer['sample_size']}")
                pc4.metric("Static table P/E", f"{_static:.2f}" if _static else "N/A")
                st.caption(
                    f"Excluded — no P/E: {_peer['excluded_missing']} · "
                    f"loss-making or negative: {_peer['excluded_negative']} · "
                    f"above cap: {_peer['excluded_outlier']}. "
                    f"The mean of the {_peer['n']} available P/Es is what the fair "
                    f"value model uses."
                )
                if _peer['median'] and abs(_peer['mean'] - _peer['median']) > 0.35 * _peer['median']:
                    st.warning(
                        f"⚠️ Mean ({_peer['mean']:.1f}) and median ({_peer['median']:.1f}) "
                        f"diverge sharply, so the average is being pulled by a few "
                        f"high-P/E names. Consider lowering the 'Ignore P/E above' cap."
                    )
        
        if st.sidebar.button("🔍 Run Screen", type="primary"):
            if not universe:
                st.warning("❌ No tickers in the selected universe.")
            else:
                st.markdown(f'''
                <div class="highlight-box">
                    <h3>📅 {earnings_choice}</h3>
                    <p><strong>Universe:</strong> {universe_label} ({len(universe):,} stocks)</p>
                    <p><strong>Within:</strong> {near_high_pct:.1f}% of 52W high &nbsp;•&nbsp;
                       <strong>Min Upside:</strong> {min_upside}%</p>
                </div>
                ''', unsafe_allow_html=True)
                
                with st.spinner(f"🔍 Screening {len(universe):,} stocks..."):
                    ev_df, ev_funnel = run_earnings_value_screener(
                        universe=universe,
                        near_high_pct=near_high_pct,
                        min_upside=min_upside,
                        earnings_mode=earnings_mode,
                        upcoming_days=upcoming_days,
                        reported_days=reported_days,
                        min_price=min_price,
                        min_avg_volume=min_avg_volume,
                        max_results=max_results,
                        max_valuation_calls=max_valuation_calls,
                        final_rank=final_rank,
                        allow_nse=allow_nse,
                        allow_estimate=allow_estimate
                    )
                
                st.session_state['ev_results'] = ev_df
                st.session_state['ev_funnel'] = ev_funnel
                st.session_state['ev_meta'] = {
                    'universe_label': universe_label,
                    'earnings_choice': earnings_choice,
                    'near_high_pct': near_high_pct,
                    'min_upside': min_upside
                }
        
        # ---------------- Render results ----------------
        ev_df = st.session_state.get('ev_results')
        ev_meta = st.session_state.get('ev_meta', {})
        ev_funnel = st.session_state.get('ev_funnel', {})
        
        if ev_df is not None:
            if ev_funnel:
                st.markdown("##### 🔻 Funnel")
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Scanned", ev_funnel.get('scanned', 0))
                c2.metric("Had Data", ev_funnel.get('with_data', 0))
                c3.metric("Near 52W High", ev_funnel.get('near_high', 0))
                c4.metric("Undervalued", ev_funnel.get('undervalued', 0))
                c5.metric("Earnings Match", ev_funnel.get('earnings_ok', 0))
            
            if ev_df.empty:
                st.warning(
                    "❌ Nothing passed all three filters. The binding constraint is usually "
                    "the combination of *undervalued* and *near the 52-week high* — those two "
                    "pull against each other. Widen the 52-week band, lower the minimum "
                    "upside, or check the funnel above to see which stage emptied out."
                )
            else:
                st.markdown(f'''
                <div class="success-message">
                    ✅ <strong>{len(ev_df)}</strong> undervalued stocks near their 52-week high<br>
                    📅 {ev_meta.get('earnings_choice', earnings_choice)}<br>
                    🌐 Universe: {ev_meta.get('universe_label', universe_label)}
                </div>
                ''', unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Results", len(ev_df))
                m2.metric("Avg Upside",
                          f"{ev_df['Upside %'].mean():+.1f}%"
                          if 'Upside %' in ev_df.columns and ev_df['Upside %'].notna().any() else "N/A")
                m3.metric("Avg From High",
                          f"{ev_df['From High %'].mean():.2f}%"
                          if 'From High %' in ev_df.columns and ev_df['From High %'].notna().any() else "N/A")
                if 'Surprise %' in ev_df.columns and ev_df['Surprise %'].notna().any():
                    m4.metric("Beats", int((ev_df['Surprise %'] > 0).sum()))
                else:
                    m4.metric("Beats", "N/A")
                
                ev_display = ev_df.copy()
                
                for col in ['LTP', '52W High', 'Fair Value']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(
                            lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                for col in ['Chg %', 'From High %', 'Upside %', 'From Low %']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(
                            lambda x: f"{x:+.2f}%" if pd.notna(x) else 'N/A')
                
                for col in ['Volume', 'Avg Volume']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(format_volume)
                if 'Rel Vol' in ev_display.columns:
                    ev_display['Rel Vol'] = ev_display['Rel Vol'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                if 'PE Ratio' in ev_display.columns:
                    ev_display['PE Ratio'] = ev_display['PE Ratio'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                if 'Market Cap' in ev_display.columns:
                    ev_display['Market Cap'] = ev_display['Market Cap'].apply(
                        lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A')
                for col in ['Days To', 'Days Since']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(
                            lambda x: f"{int(x)}d" if pd.notna(x) else 'N/A')
                
                ev_columns = ['Ticker', 'Name', 'LTP', 'From High %', '52W High',
                              'Fair Value', 'Upside %', 'Value Tag', 'FV Source',
                              'Earnings', 'Date Source', 'Last Earnings', 'Days Since',
                              'Last Surprise', 'Next Earnings', 'Days To',
                              'Volume', 'Avg Volume', 'Rel Vol', 'Chg %',
                              'PE Ratio', 'Cap Type', 'As Of', 'Valuation']
                ev_columns = [c for c in ev_columns if c in ev_display.columns]
                
                st.dataframe(
                    ev_display[ev_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=min(600, len(ev_display) * 35 + 100),
                    column_config=valuation_column_config()
                )
                
                render_valuation_jump(ev_df, "earnings_value")
                
                render_manual_fair_value('ev_results', key_prefix="ev_mfv")
                
                with st.expander("📅 Earnings detail"):
                    st.caption("A positive last surprise is what post-earnings drift follows. "
                               "An upcoming date inside your intended holding period is gap risk.")
                    e_cols = ['Ticker', 'Date Source', 'Estimated', 'Last Earnings',
                              'Days Since', 'Last Surprise', 'Next Earnings', 'Days To',
                              'Upside %', 'From High %']
                    e_cols = [c for c in e_cols if c in ev_df.columns]
                    st.dataframe(ev_df[e_cols], use_container_width=True, hide_index=True)
                
                ev_csv = ev_df.to_csv(index=False)
                ev_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    f"📥 Download Results ({len(ev_df)} stocks)",
                    data=ev_csv,
                    file_name=f"NYZTrade_EarningsValue_{ev_ts}.csv",
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
