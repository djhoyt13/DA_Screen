css = """
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
        padding-top: 2rem !important;
        padding-bottom: 0.5rem !important;
    }
    h3 {
        color: #00CED1 !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
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
    /* Style for Answer Below text */
    .answer-prompt {
        color: #00CED1 !important;
        font-size: 1.1rem !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        font-style: italic !important;
    }
    /* Style for code and input spacing */
    .stCodeBlock {
        margin-bottom: 0.125rem !important;
        max-width: 400px !important;
    }
    .stTextInput {
        margin-top: 0 !important;
        margin-bottom: 0.75rem !important;
        padding-top: 0 !important;
    }
    /* Style for Topics list */
    .topics-list {
        font-size: 1.4rem !important;
        line-height: 2.5 !important;
        padding: 0.64rem !important;
        margin-top: 1.28rem !important;
        margin-bottom: 1.28rem !important;
        background-color: #0E1117 !important;
        border-radius: 8px !important;
    }
    /* Style for Dictionary Operations section */
    .dict-ops-section {
        padding-top: 2rem !important;
    }
    /* Style for String Operations section */
    .str-ops-section {
        padding-top: 2rem !important;
    }
    /* Style for Functions section */
    .func-section {
        padding-top: 2rem !important;
    }
    .topics-list ul {
        list-style-type: none !important;
        padding-left: 0 !important;
    }
    .topics-list li {
        margin-bottom: 0.432rem !important;
    }
    /* Style for Candidate Information */
    .candidate-info {
        padding: 1.005rem !important;
        background-color: #0E1117 !important;
        border-radius: 8px !important;
        margin-top: 1rem !important;
    }
    /* Style for input field spacing */
    .candidate-info .stTextInput {
        margin-bottom: 3.5rem !important;
    }
    /* Remove extra margin from the last input field */
    .candidate-info .stTextInput:last-child {
        margin-bottom: 0.5rem !important;
    }
    .invalid-input {
        border: 1px solid red;
        padding: 0.5rem;
        border-radius: 4px;
        background-color: rgba(255, 0, 0, 0.1);
    }
</style>
"""
