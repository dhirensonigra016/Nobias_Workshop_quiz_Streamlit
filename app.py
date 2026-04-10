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
    </style>
""", unsafe_allow_html=True)

# 2. Connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Your Finance Quiz Questions
quiz_data = [
    {"q": "Mutual Funds Sahi Hai. All mutual funds are right for you!", "a": False, "exp": "Myth. According to NISM, 'not every financial product is suitable for every client', and recommendations must be based on the client’s specific needs, goals, and risk profile."},
    {"q": "Over 5 years Passive (Index) funds give higher returns than 80% of Active managed funds.", "a": True, "exp": "Fact. According to SPIVA® India Year-End 2025, historically, 80% of active funds underperform benchmarks over a 10 year period."},
    {"q": "If you are young you should be an aggressive investor.", "a": False, "exp": "Myth. According to NISM, investment decisions must be based on 'risk tolerance, goals, financial situation, and life-cycle stage', not age alone."}
]

# 4. Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = "landing"
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.user_data = {}
    st.session_state.answered = False
    st.session_state.user_choice = None

# --- PHASE 1: EXACT LANDING PAGE UI ---
if st.session_state.step == "landing":
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
        # Added the Organization field
        organization = st.text_input("Organization", placeholder="Organization Name", label_visibility="collapsed")
        age_range = st.selectbox("Age", ["Select Age Range", "18-25", "26-35", "36-45", "46-55", "56+"], label_visibility="collapsed")
        income_range = st.selectbox("Income", ["Monthly Income Range", "Under 25k", "25k - 50k", "50k - 1L", "1L - 2L", "2L+"], label_visibility="collapsed")
        
        # Changed button text from "Start Quiz" to "Next"
        submit = st.form_submit_button("Next", type="primary", use_container_width=True)
        
        if submit:
            if full_name and email:
                st.session_state.user_data = {
                    "Full Name": full_name, 
                    "Email Address": email, 
                    "Phone Number": phone,
                    "Organization": organization, # Storing the new input
                    "Age Range": age_range if age_range != "Select Age Range" else "",
                    "Monthly Income Range": income_range if income_range != "Monthly Income Range" else ""
                }
                # Redirect to the new expectations page instead of the quiz
                st.session_state.step = "pre_quiz"
                st.rerun()
            else:
                st.error("Please provide at least your Full Name and Email Address.")

# --- PHASE 1.5: EXPECTATIONS (NEW CHECKLIST PAGE) ---
elif st.session_state.step == "pre_quiz":
    st.markdown("<h2>Workshop Expectations</h2>", unsafe_allow_html=True)
    st.write("")
    
    with st.form("expectations_form"):
        st.write("**Which financial topics do you expect us to cover in the workshop?**")
        
        options = [
            "Budgeting", 
            "Savings & Expense Planning", 
            "Compounding", 
            "Debt Management", 
            "Investment Planning (including mutual fund basics)", 
            "Goal-based financial planning & SMART goals", 
            "Emergency funds and insurance basics", 
            "Others"
        ]
        
        # A multiselect acts as a clean checklist for users to pick multiple topics
        selected_topics = st.multiselect(
            "Select topics", 
            options, 
            label_visibility="collapsed", 
            placeholder="Select all that apply..."
        )
        
        # New Start Quiz button
        start_quiz = st.form_submit_button("Start Quiz", type="primary", use_container_width=True)
        
        if start_quiz:
            # Save the selected topics as a comma-separated string to Google Sheets
            st.session_state.user_data["Expected Topics"] = ", ".join(selected_topics) if selected_topics else "None selected"
            st.session_state.step = "quiz"
            st.rerun()

# --- PHASE 2: QUIZ INTERFACE (WITH TIMER) ---
elif st.session_state.step == "quiz":
    current_q = quiz_data[st.session_state.index]
    
    progress = (st.session_state.index) / len(quiz_data)
    st.progress(progress)
    st.markdown(f"<p class='subtitle'>Question {st.session_state.index + 1} of {len(quiz_data)}</p>", unsafe_allow_html=True)
    st.write(f"### {current_q['q']}")
    st.write("")
    
    if not st.session_state.answered:
        # Initialize timer start time
        if 'start_time' not in st.session_state:
            st.session_state.start_time = time.time()

        # Placeholder for the timer text
        timer_placeholder = st.empty()
        
        col1, col2 = st.columns(2)
        if col1.button("FACT", use_container_width=True):
            st.session_state.answered = True
            st.session_state.user_choice = True
            st.session_state.pop('start_time', None)
            st.rerun()
            
        if col2.button("MYTH", use_container_width=True):
            st.session_state.answered = True
            st.session_state.user_choice = False
            st.session_state.pop('start_time', None)
            st.rerun()
            
        # The live countdown loop
        while not st.session_state.answered:
            elapsed = time.time() - st.session_state.start_time
            remaining = 20 - int(elapsed)
            
            if remaining <= 0:
                # Time is up!
                st.session_state.answered = True
                st.session_state.user_choice = None 
                st.session_state.pop('start_time', None)
                st.rerun()
                break
                
            timer_placeholder.markdown(f"<h3 style='color: #ef4444; margin-top: 0;'>⏳ {remaining}s remaining</h3>", unsafe_allow_html=True)
            time.sleep(0.5) 
            
    else:
        # User has answered OR time ran out
        if st.session_state.user_choice is None:
            st.error("⏰ Time's up! You didn't answer fast enough.")
            is_correct = False
        else:
            is_correct = (st.session_state.user_choice == current_q['a'])
            if is_correct:
                st.success("✅ Correct!")
                st.balloons()
            else:
                st.error("❌ Not quite!")
            
        st.info(current_q['exp'])
        
        button_text = "Next Question" if st.session_state.index + 1 < len(quiz_data) else "See Final Results"
        
        if st.button(button_text, type="primary", use_container_width=True):
            if is_correct:
                st.session_state.score += 1
                
            st.session_state.answered = False
            
            if st.session_state.index + 1 < len(quiz_data):
                st.session_state.index += 1
            else:
                st.session_state.step = "saving"
            st.rerun()

# --- PHASE 3: SAVE DIRECTLY TO SHEETS ---
elif st.session_state.step == "saving":
    st.markdown("<h3>Saving Results...</h3>", unsafe_allow_html=True)
    with st.spinner("Connecting to secure database..."):
        try:
            existing_df = conn.read()
            new_row_data = st.session_state.user_data.copy()
            new_row_data["Score"] = st.session_state.score
            
            # Timestamp in IST
            ist = timezone(timedelta(hours=5, minutes=30))
            new_row_data["updated"] = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
            
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
    st.markdown("<h2>Quiz Complete!</h2>", unsafe_allow_html=True)
    st.success(f"Thank you, {st.session_state.user_data.get('Full Name', 'Participant')}!")
    
    st.metric("Your Final Score", f"{st.session_state.score} / {len(quiz_data)}")
    st.write("Your details and score have been successfully submitted.")
