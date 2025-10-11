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
    /* Style for code and input spacing */
    .stCodeBlock {
        margin-bottom: 0.125rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    /* Ensure code blocks preserve whitespace */
    .stCodeBlock pre {
        white-space: pre !important;
        font-family: monospace !important;
        tab-size: 4 !important;
        -moz-tab-size: 4 !important;
    }
    
    /* Ensure proper line height in code blocks */
    .stCodeBlock code {
        line-height: 1.5 !important;
    }
    .stTextInput {
        margin-top: 0 !important;
        margin-bottom: 0.75rem !important;
        padding-top: 0 !important;
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
    /* Style for radio buttons - blue */
    /* Radio button outer circle */
    div[data-testid="stRadio"] label div[role="radio"] {
        border-color: #888888 !important;
    }
    /* Radio button outer circle when selected */
    div[data-testid="stRadio"] label div[role="radio"][aria-checked="true"] {
        border-color: #0066CC !important;
    }
    /* Radio button inner dot/fill when selected */
    div[data-testid="stRadio"] label div[role="radio"][aria-checked="true"]::after {
        background-color: #0066CC !important;
        content: "" !important;
        display: block !important;
        width: 10px !important;
        height: 10px !important;
        border-radius: 50% !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }
    /* Remove blue highlight from radio button labels */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: transparent !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    /* Style for primary button - blue (multiple selectors for compatibility) */
    button[kind="primary"],
    button[data-testid="baseButton-primary"],
    .stButton > button[kind="primary"] {
        background-color: #0066CC !important;
        border-color: #0066CC !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: #0052A3 !important;
        border-color: #0052A3 !important;
    }
    button[kind="primary"]:active,
    button[data-testid="baseButton-primary"]:active,
    .stButton > button[kind="primary"]:active {
        background-color: #003D7A !important;
        border-color: #003D7A !important;
    }
    /* Sticky progress bar - using more compatible selectors */
    div[data-testid="stProgress"] {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background-color: #0E1117 !important;
        padding: 0.5rem 0 1rem 0 !important;
        margin: 0 !important;
        border-bottom: 2px solid #00BFFF !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important;
    }
    /* Ensure parent allows stickiness */
    section.main,
    [data-testid="stAppViewContainer"],
    [data-testid="stVerticalBlock"] {
        position: relative !important;
    }
</style>
"""
