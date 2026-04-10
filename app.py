import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timezone, timedelta
import time

# 1. Page Configuration
st.set_page_config(page_title="Financial Literacy Quiz", page_icon="💰", layout="centered")

# --- UI STYLING TO MATCH TAILWIND REACT APP ---
st.markdown("""
    <style>
    /* 1. Aggressively Hide Streamlit branding, top/bottom menus, and badges */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    
    /* Target the Hosted with Streamlit and Created by badges */
    .viewerBadge_container { display: none !important; }
    .viewerBadge_link { display: none !important; }
    #viewerBadge { display: none !important; }
    a[href^="https://streamlit.io/cloud"] { display: none !important; }
    iframe[title="streamlit-badge"] { display: none !important; }
    iframe { display: none !important; } /* Catch-all for injected iframes */

    /* 2. Apply the Tailwind Blue Gradient Background to the whole app */
    .stApp { background: linear-gradient(to bottom right, #3b82f6, #2563eb, #1d4ed8) !important; }

    /* 3. Create the Mobile-Optimized White Card */
    div.block-container {
        background-color: #ffffff !important;
        border-radius: 1rem !important;
        padding: 2.5rem 2rem !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
        max-width: 450px !important; 
        margin: 4vh auto !important; 
    }

    /* 4. Center Align Headers & Fix text colors */
    h1, h2, h3, p { text-align: center !important; color: #0f172a !important; }
    
    .subtitle {
        color: #64748b !important;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    /* 5. Style the form inputs to look like Tailwind */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        border-radius: 0.5rem !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #f8fafc !important;
    }

    /* --- NEW FIX: Bulletproof Dark Text for Inputs AND Dropdowns --- */
    div[data-baseweb="input"] input, 
    div[data-baseweb="select"] * {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important; /* Forces color on iOS/Safari */
    }

    div[data-baseweb="input"] input::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    /* Force the opened dropdown menu list to be light with dark text */
    ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    ul[data-baseweb="menu"] li, ul[data-baseweb="menu"] li * {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }
    /* ------------------------------------------------------------------------- */

    /* 6. Style the Primary Button */
    div[data-testid="stFormSubmitButton"] > button, 
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover, 
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #2563eb !important;
    }
    
    /* 7. Style Secondary Buttons (Myth/Fact) */
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 0.5rem !important;
        border: 2px solid #e2e8f0 !important;
        color: #334155 !important;
        font-weight: 600 !important;
        background-color: white !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }
