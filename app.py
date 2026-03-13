import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Financial Literacy Quiz", page_icon="💰", layout="centered")

# --- UI STYLING TO MATCH TAILWIND REACT APP ---
st.markdown("""
    <style>
    /* 1. Hide the default Streamlit top header */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Apply the Tailwind Blue Gradient Background to the whole app */
    .stApp {
        background: linear-gradient(to bottom right, #3b82f6, #2563eb, #1d4ed8) !important;
    }

    /* 3. Create the Mobile-Optimized White Card */
    div.block-container {
        background-color: #ffffff !important;
        border-radius: 1rem !important;
        padding: 2.5rem 2rem !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
        max-width: 450px !important; /* Perfect width for mobile apps */
        margin: 4vh auto !important; /* Centers the box */
    }

    /* 4. Center Align Headers & Fix text colors */
    h1, h2, h3, p {
        text-align: center !important;
        color: #0f172a !important; /* Dark text for readability on white */
    }
    
    /* Subtle subtitle color */
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
    </style>
""", unsafe_allow_html=True)

# 2. Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Your Finance Quiz Questions
quiz_data = [
    {"q": "Credit cards are always bad for your financial health.", "a": False, "exp": "Myth! When used responsibly, they build credit scores and offer rewards."},
    {"q": "Investing in the stock market is the same as gambling.", "a": False, "exp": "Myth! Investing is based on company ownership and long-term growth, not pure chance."},
    {"q": "You need a lot of money to start investing.", "a": False, "exp": "Myth! Many platforms allow you to start with as little as $1."},
    {"q": "Inflation reduces the purchasing power of your money over time.", "a": True, "exp": "Fact! This is why investing is crucial to stay ahead of rising costs."},
    {"q": "A higher salary automatically means you are wealthier.", "a": False, "exp": "Myth! Wealth is what you keep (assets), not just what you earn (income)."}
]

# 4. Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = "landing"
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.user_data = {}

# --- PHASE 1: EXACT LANDING PAGE UI ---
if st.session_state.step == "landing":
    
    # Render Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.markdown("<h1 style='background-color: #3b82f6; color: white; padding: 10px; border-radius: 8px;'>N Ø B I A S</h1>", unsafe_allow_html=True)
    
    st.markdown("<h2>Financial Literacy Quiz</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>Test your knowledge with {len(quiz_data)} myth vs fact questions</p>", unsafe_allow_html=True)
    st.write("")

    with st.form("landing_form"):
        full_name = st.text_input("Name", placeholder="Full Name", label_visibility="collapsed")
        email = st.text_input("Email", placeholder="Email Address", label_visibility="collapsed")
        phone = st.text_input("Phone", placeholder="Phone Number", label_visibility="collapsed")
        
        age_range = st.selectbox(
            "Age", 
            ["Select Age Range", "18-25", "26-35", "36-45", "46-55", "56+"],
            label_visibility="collapsed"
        )
        
        income_range = st.selectbox(
            "Income", 
            ["Monthly Income Range", "Under 25k", "25k - 50k", "50k - 1L", "1L - 2L", "2L+"],
            label_visibility="collapsed"
        )
        
        submit = st.form_submit_button("Start Quiz", type="primary", use_container_width=True)
        
        if submit:
            if full_name and email:
                st.session_state.user_data = {
                    "Full Name": full_name,
                    "Email Address": email,
                    "Phone Number": phone,
                    "Age Range": age_range if age_range != "Select Age Range" else "",
                    "Monthly Income Range": income_range if income_range != "Monthly Income Range" else ""
                }
                st.session_state.step = "quiz"
                st.rerun()
            else:
                st.error("Please provide at least your Full Name and Email Address.")

# --- PHASE 2: QUIZ INTERFACE ---
elif st.session_state.step == "quiz":
    current_q = quiz_data[st.session_state.index]
    
    progress = (st.session_state.index) / len(quiz_data)
    st.progress(progress)
    
    st.markdown(f"<p class='subtitle'>Question {st.session_state.index + 1} of {len(quiz_data)}</p>", unsafe_allow_html=True)
    st.write(f"### {current_q['q']}")
    st.write("")
    
    col1, col2 = st.columns(2)
    
    def process_answer(user_answer):
        if user_answer == current_q['a']:
            st.session_state.score += 1
            st.toast("Correct!", icon="✅")
        else:
            st.toast("Not quite!", icon="❌")
        
        if st.session_state.index + 1 < len(quiz_data):
            st.session_state.index += 1
        else:
            st.session_state.step = "saving"
        st.rerun()

    if col1.button("FACT", use_container_width=True): process_answer(True)
    if col2.button("MYTH", use_container_width=True): process_answer(False)

# --- PHASE 3: SAVE DIRECTLY TO SHEETS ---
elif st.session_state.step == "saving":
    st.markdown("<h3>Saving Results...</h3>", unsafe_allow_html=True)
    with st.spinner("Connecting to secure database..."):
        try:
            existing_df = conn.read()
            
            new_row_data = st.session_state.user_data.copy()
            new_row_data["Score"] = st.session_state.score
            
            new_record = pd.DataFrame([new_row_data])
            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
            conn.update(data=updated_df)
            
            st.session_state.step = "complete"
            st.rerun()
        except Exception as e:
            st.error("There was an issue saving to the database.")
            st.write(e)

# --- PHASE 4: COMPLETE ---
elif st.session_state.step == "complete":
    st.balloons()
    st.markdown("<h2>Quiz Complete!</h2>", unsafe_allow_html=True)
    st.success(f"Thank you, {st.session_state.user_data.get('Full Name', 'Participant')}!")
    
    st.metric("Your Final Score", f"{st.session_state.score} / {len(quiz_data)}")
    st.write("Your details and score have been successfully submitted.")
    st.write("")
    
    if st.button("Start Over (New User)", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
