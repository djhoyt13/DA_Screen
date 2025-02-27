import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Data Analyst Python Review",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set dark theme and improve text visibility
st.markdown("""
    <style>
        /* Dark mode for main app and header */
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        /* Style header/banner area */
        header {
            background-color: #0E1117 !important;
        }
        .stDeployButton {
            display: none !important;
        }
        /* Hide hamburger menu */
        button[kind="header"] {
            background-color: transparent !important;
            color: #FFFFFF !important;
        }
        .main .block-container {
            padding-top: 2rem;
        }
        h1 {
            color: #00BFFF !important;
            font-weight: bold !important;
        }
        h2 {
            color: #00CED1 !important;
            padding-top: 1rem !important;
            padding-bottom: 0.5rem !important;
        }
        .stTextInput > div > div > input {
            color: #FFFFFF;
            background-color: #262730;
        }
        /* Style for shorter input fields */
        .short-input {
            max-width: 400px !important;
        }
        div[data-testid="stHorizontalBlock"] > div:first-child {
            flex: 0 1 400px !important;
        }
        p {
            color: #E0E0E0 !important;
            font-size: 1.05rem !important;
            line-height: 1.5 !important;
        }
        .welcome-msg {
            font-size: 1.5rem !important;
            color: #E0E0E0 !important;
            margin: 2rem 0 !important;
            line-height: 1.8 !important;
            padding: 1rem !important;
            border-left: 4px solid #00BFFF !important;
            background-color: rgba(0, 191, 255, 0.1) !important;
        }
        /* Additional dark mode for all Streamlit elements */
        .stMarkdown, .stHeader, .stSidebar, .stButton, .stTextInput {
            background-color: #0E1117 !important;
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("Data Analyst Python Review")

# Add a welcome message with markdown formatting
st.markdown("""
<div class="welcome-msg">
Welcome to the Data Analyst Python Review. This review will emphasize the core Python concepts relevant to the Data Analyst position.
</div>
""", unsafe_allow_html=True)

# Add a list of topics to review with enhanced formatting
st.markdown("## Topics to Review")
st.markdown("""
* 📊 **Data Types and Variables**
* 📝 **Lists and Dictionaries**
* ⚙️ **Functions and Modules**
* 🐼 **Data Manipulation with Pandas**
* 📈 **Data Visualization with Matplotlib and Seaborn**
""")

# Create input fields for user information with better spacing
st.markdown("## User Information")
col1, col2 = st.columns([1, 2])
with col1:
    name = st.text_input("Enter your name:", key="name")
    email = st.text_input("Enter your email:", key="email")
    phone = st.text_input("Enter your phone number:", key="phone")
