import streamlit as st
import re
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Data Analyst Python Review",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validation functions
def is_valid_name(name):
    # Check if name contains only letters, spaces, and common special characters
    return bool(re.match(r'^[A-Za-z\s\'-]+$', name)) if name else False

def is_valid_email(email):
    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email)) if email else False

def is_valid_phone(phone):
    # Allow common phone number formats (including international)
    phone = re.sub(r'[\s\-\(\)]', '', phone)  # Remove spaces, hyphens, and parentheses
    return bool(re.match(r'^\+?1?\d{10,14}$', phone)) if phone else False

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
            margin-top: 0.64rem !important;
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
""", unsafe_allow_html=True)

# Initialize session state for storing answers and results
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()

# Define correct answers
CORRECT_ANSWERS = {
    'int': 'int',
    'float': 'float',
    'bool': 'bool',
    'str': 'str',
    'none': 'NoneType',
    'list': 'list',
    'tuple': 'tuple',
    'dict': 'dict',
    'set': 'set',
    'dict1': '5',
    'str1': 'nal',
    'str2': 'n',
    'func1': 'Not an even number',
    'func2': '4'
}

def grade_answers():
    # Get all answers from session state
    answers = {key: st.session_state.get(key, '') for key in CORRECT_ANSWERS.keys()}
    
    # Calculate score
    correct_count = sum(1 for key, value in answers.items() if str(value).strip() == str(CORRECT_ANSWERS[key]).strip())
    total_questions = len(CORRECT_ANSWERS)
    score = (correct_count / total_questions) * 100
    
    # Create results dictionary
    results = {
        'timestamp': datetime.now(),
        'name': st.session_state.get('name', ''),
        'email': st.session_state.get('email', ''),
        'phone': st.session_state.get('phone', ''),
        'score': score,
        'correct_answers': correct_count,
        'total_questions': total_questions
    }
    
    # Add individual question results
    for key, value in answers.items():
        results[f'q_{key}'] = value
        results[f'q_{key}_correct'] = str(value).strip() == str(CORRECT_ANSWERS[key]).strip()
    
    # Create DataFrame row
    new_row = pd.DataFrame([results])
    
    # Append to existing results
    st.session_state.results_df = pd.concat([st.session_state.results_df, new_row], ignore_index=True)
    
    # Save to CSV
    st.session_state.results_df.to_csv('quiz_results.csv', index=False)
    
    return score, correct_count, total_questions

# Main title
st.title("Data Analyst Python Review")

# Add a welcome message with markdown formatting
st.markdown("""
<div class="welcome-msg">
Welcome to the Data Analyst Python Review. This review will emphasize the core Python concepts relevant to the Data Analyst position.
</div>
""", unsafe_allow_html=True)

# Create two columns for Candidate Information and Topics
left_col, right_col = st.columns(2)

# Left column: Candidate Information
with left_col:
    st.markdown("## Candidate Information")
    st.markdown('<div class="candidate-info">', unsafe_allow_html=True)
    
    # Name input with validation
    if 'name' not in st.session_state:
        st.session_state.name = ""
        st.session_state.name_error = False
    
    def validate_name():
        if st.session_state.name and not is_valid_name(st.session_state.name):
            st.session_state.name_error = True
        else:
            st.session_state.name_error = False
    
    if st.session_state.name_error:
        st.markdown('<div class="invalid-input">', unsafe_allow_html=True)
    name = st.text_input("Enter your name:", key="name", on_change=validate_name)
    if st.session_state.name_error:
        st.markdown('</div>', unsafe_allow_html=True)
        st.error("Please enter a valid name (letters, spaces, hyphens, and apostrophes only)")
    
    # Email input with validation
    if 'email' not in st.session_state:
        st.session_state.email = ""
        st.session_state.email_error = False
    
    def validate_email():
        if st.session_state.email and not is_valid_email(st.session_state.email):
            st.session_state.email_error = True
        else:
            st.session_state.email_error = False
    
    if st.session_state.email_error:
        st.markdown('<div class="invalid-input">', unsafe_allow_html=True)
    email = st.text_input("Enter your email:", key="email", on_change=validate_email)
    if st.session_state.email_error:
        st.markdown('</div>', unsafe_allow_html=True)
        st.error("Please enter a valid email address")
    
    # Phone input with validation
    if 'phone' not in st.session_state:
        st.session_state.phone = ""
        st.session_state.phone_error = False
    
    def validate_phone():
        if st.session_state.phone and not is_valid_phone(st.session_state.phone):
            st.session_state.phone_error = True
        else:
            st.session_state.phone_error = False
    
    if st.session_state.phone_error:
        st.markdown('<div class="invalid-input">', unsafe_allow_html=True)
    phone = st.text_input("Enter your phone number:", key="phone", on_change=validate_phone)
    if st.session_state.phone_error:
        st.markdown('</div>', unsafe_allow_html=True)
        st.error("Please enter a valid phone number (10-14 digits, can include country code)")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Data Types Quiz Section
    st.markdown("## Data Types")
    st.markdown("What is the output of each of the following Python code snippets?:")
    
    # Initialize session state for storing answers
    if 'dt_answers' not in st.session_state:
        st.session_state.dt_answers = {
            'int': '', 'float': '', 'bool': '', 'str': '', 
            'list': '', 'tuple': '', 'dict': '', 'set': '', 'none': '',
            'int2': '', 'float2': '', 'bool2': '', 'str2': '', 
            'list2': '', 'tuple2': '', 'dict2': '', 'set2': '', 'none2': ''
        }
    
    # Create column for code examples
    dt_col1 = st.columns(1)[0]
    
    with dt_col1:
        st.markdown("### Basic Data Types")
        # Integer
        st.code("x = 42\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define Integer (int)", key="int")
        
        # Float
        st.code("x = 3.14\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define Float (float)", key="float")
        
        # Boolean
        st.code("x = True\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define Boolean (bool)", key="bool")
        
        # String
        st.code('x = "Hello"\ntype(x)')
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define String (str)", key="str")
        
        # NoneType
        st.code("x = None\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define NoneType", key="none")
        
        # List
        st.code("x = [1, 2, 3]\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define List", key="list")
        
        # Tuple
        st.code("x = (1, 2, 3)\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define Tuple", key="tuple")
        
        # Dictionary
        st.code("x = {'a': 1, 'b': 2}\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define Dictionary (dict)", key="dict")
        
        # Set
        st.code("x = {1, 2, 3}\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Define Set", key="set")

        # Dictionary Operations Section
        st.markdown('<div class="dict-ops-section">', unsafe_allow_html=True)
        st.markdown("## Dictionary Operations")
        st.markdown("What is the output of each of the following Python code snippets?:")
        st.code("""fruits = {
    'apple': 3,
    'banana': 5,
    'orange': 2,
    'grape': 4
}""")
        
        st.markdown("What is the output after running the line of code below?")
        st.code("fruits['banana']")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="dict1")
        

        # String Operations Section
        st.markdown('<div class="str-ops-section">', unsafe_allow_html=True)
        st.markdown("## String Operations")
        st.markdown("What is the output of each of the following Python code snippets?:")
        st.code('text = "Data Analysis"')
        
        st.markdown("What is the output after running the line of code below?")
        st.code('text[6:9]')
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="str1")
        
        st.markdown("What is the output after running the line of code below?")
        st.code('text[-7]')
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="str2")
        st.markdown('</div>', unsafe_allow_html=True)

        # Functions Section
        st.markdown('<div class="func-section">', unsafe_allow_html=True)
        st.markdown("## Functions")
        st.markdown("What is the outputs based on the below function?:")
        st.code("""def square_even(x):
     if x % 2 == 0:
          print(x**2)
     else:
          print("Not an even number")""")
        
        st.markdown("What is the output after running the line of code below?")
        st.code("square_even(3)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="func1")
        
        st.markdown("What is the output after running the line of code below?")
        st.code("square_even(2)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="func2")
        st.markdown('</div>', unsafe_allow_html=True)

        # Add submit button
        if not st.session_state.submitted:
            if st.button("Submit Answers", type="primary"):
                # Validate candidate information
                validation_errors = []
                
                # Check if fields are empty
                if not st.session_state.get('name', '').strip():
                    validation_errors.append("Name is required")
                elif not is_valid_name(st.session_state.name):
                    validation_errors.append("Please enter a valid name (letters, spaces, hyphens, and apostrophes only)")
                
                if not st.session_state.get('email', '').strip():
                    validation_errors.append("Email is required")
                elif not is_valid_email(st.session_state.email):
                    validation_errors.append("Please enter a valid email address")
                
                if not st.session_state.get('phone', '').strip():
                    validation_errors.append("Phone number is required")
                elif not is_valid_phone(st.session_state.phone):
                    validation_errors.append("Please enter a valid phone number (10-14 digits, can include country code)")
                
                # If there are validation errors, display them
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    # If validation passes, proceed with grading
                    score, correct_count, total_questions = grade_answers()
                    st.session_state.submitted = True
                    st.success(f"Quiz submitted! Your score: {score:.1f}% ({correct_count}/{total_questions} correct)")
                    
                    # Display correct answers
                    st.markdown("### Quiz Results:")
                    for key, value in CORRECT_ANSWERS.items():
                        user_answer = st.session_state.get(key, '')
                        is_correct = str(user_answer).strip() == str(value).strip()
                        status = "✅" if is_correct else "❌"
                        if is_correct:
                            st.markdown(f"{status} {key}: {value}")
                        else:
                            st.markdown(f"{status} {key}: Your answer: '{user_answer}' | Correct answer: '{value}'")

# Right column: Topics to Review
with right_col:
    st.markdown("## Topics to Review")
    st.markdown("""
    <div class="topics-list">
    <ul>
    <li>📊  -  Data Types and Variables</li>
    <li>📝  -  Lists and Dictionaries</li>
    <li>⚙️  -  Functions and Modules</li>
    <li>🐼  -  Data Manipulation with Pandas</li>
    <li>📈  -  Data Visualization with Matplotlib and Seaborn</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
