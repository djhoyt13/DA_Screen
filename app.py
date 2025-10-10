import streamlit as st
import re
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import styles

# Load environment variables
load_dotenv()

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

# Use the CSS in Streamlit
st.markdown(styles.css, unsafe_allow_html=True)

# Initialize session state for storing answers and results
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()  # Start timer when page loads
if 'completion_time' not in st.session_state:
    st.session_state.completion_time = None
if 'timer_started' not in st.session_state:
    st.session_state.timer_started = False
if 'first_quiz_interaction' not in st.session_state:
    st.session_state.first_quiz_interaction = False

def load_questions_and_answers(md_path):
    questions = {}
    answers = {}
    current_section = None

    with open(md_path, 'r') as file:
        content = file.readlines()

    for line in content:
        line = line.strip()
        if line.startswith('## '):
            current_section = line.strip('## ').strip()
            questions[current_section] = []
            answers[current_section] = []
        elif line.startswith('# Answer Key'):
            break
        elif current_section:
            questions[current_section].append(line)

    # Fill answers, assuming they start after '# Answer Key'
    answer_start = content.index('# Answer Key\n')
    parsing_answers = False
    for line in content[answer_start:]:
        if line.startswith('## '):
            parsing_answers = True
            current_section = line.strip('## ').strip()
        elif parsing_answers and current_section:
            answers[current_section].append(line.strip())

    return questions, answers

# Load questions and answers
questions, answers = load_questions_and_answers('ds_questions.md')

st.title("Data Scientist Technical Review")

# Example for using questions within Streamlit sections
for section, question_list in questions.items():
    st.header(section)
    for question in question_list:
        st.markdown(question)

# Add a welcome message with markdown formatting
st.markdown("""
<div class="welcome-msg">
Welcome to the Data Scientist Technical Review. This review will emphasize the core Python concepts relevant to the Data Scientist position.
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
    
    # Recruiter Email input with validation
    if 'recruiter_email' not in st.session_state:
        st.session_state.recruiter_email = ""
        st.session_state.recruiter_email_error = False
    
    def validate_recruiter_email():
        if st.session_state.recruiter_email and not is_valid_email(st.session_state.recruiter_email):
            st.session_state.recruiter_email_error = True
        else:
            st.session_state.recruiter_email_error = False
    
    if st.session_state.recruiter_email_error:
        st.markdown('<div class="invalid-input">', unsafe_allow_html=True)
    recruiter_email = st.text_input("Recruiter's Email:", key="recruiter_email", on_change=validate_recruiter_email)
    if st.session_state.recruiter_email_error:
        st.markdown('</div>', unsafe_allow_html=True)
        st.error("Please enter a valid email address")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Move Topics to Review here, before Data Types
    st.markdown("## Topics to Review")
    st.markdown("""
    <div class="topics-list">
    <ul>
    <li>🔢  -  Data Types</li>
    <li>📚  -  Dictionaries</li>
    <li>✂️  -  String Operations</li>
    <li>⚡  -  Functions</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

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
        st.text_input("", placeholder="Enter the output", key="int")
        
        # Float
        st.code("x = 3.14\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="float")
        
        # Boolean
        st.code("x = True\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="bool")
        
        # String
        st.code('x = "Hello"\ntype(x)')
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="str")
        
        # NoneType
        st.code("x = None\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="none")
        
        # List
        st.code("x = [1, 2, 3]\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="list")
        
        # Tuple
        st.code("x = (1, 2, 3)\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="tuple")
        
        # Dictionary
        st.code("x = {'a': 1, 'b': 2}\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="dict")
        
        # Set
        st.code("x = {1, 2, 3}\ntype(x)")
        st.markdown('<p class="answer-prompt">Answer Below:</p>', unsafe_allow_html=True)
        st.text_input("", placeholder="Enter the output", key="set")

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

        # Check if user has started the quiz
        check_quiz_start()

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
                    # Grade answers
                    score, correct_count, total_questions = grade_answers()
                    st.session_state.submitted = True
                    
                    # Send email with results
                    candidate_info = {
                        'name': st.session_state.get('name', ''),
                        'email': st.session_state.get('email', ''),
                        'phone': st.session_state.get('phone', '')
                    }
                    
                    # Stop timer and get completion time
                    completion_time = stop_timer()
                    
                    # Send email and print results (only if email is configured)
                    email_configured = all([
                        EMAIL_CONFIG.get('sender_email'),
                        EMAIL_CONFIG.get('sender_password'),
                        st.session_state.get('recruiter_email')
                    ])
                    
                    if email_configured:
                        if send_quiz_results(candidate_info, score, CORRECT_ANSWERS):
                            st.success("Results have been emailed successfully!")
                        else:
                            st.warning("There was an error sending the email, but your results have been saved.")
                    else:
                        st.info("Email not configured. Results saved locally to quiz_results.csv")
                    
                    # Display results in Streamlit
                    st.markdown("## Quiz Results")
                    st.markdown(f"""
                    <div style='background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                        <h3 style='color: #00BFFF;'>Score: {score:.1f}% ({correct_count}/{total_questions} correct)</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display answers in a table format
                    results_data = []
                    for key, value in CORRECT_ANSWERS.items():
                        user_answer = st.session_state.get(key, '')
                        if key in DATA_TYPE_TARGETS:
                            user_answer_lower = str(user_answer).strip().lower()
                            similarities = [
                                calculate_similarity(user_answer_lower, target)
                                for target in DATA_TYPE_TARGETS[key]
                            ]
                            max_similarity = max(similarities)
                            is_correct = max_similarity >= 0.8
                        else:
                            is_correct = str(user_answer).strip() == str(value).strip()
                        status = "✅" if is_correct else "❌"
                        results_data.append({
                            "Question": key,
                            "Your Answer": user_answer,
                            "Correct Answer": value,
                            "Status": status
                        })
                    
                    # Create DataFrame for results
                    results_df = pd.DataFrame(results_data)
                    
                    # Display results table with custom styling
                    st.markdown("""
                        <style>
                            .stDataFrame {
                                background-color: #1E1E1E;
                                border-radius: 10px;
                                padding: 10px;
                            }
                            .stDataFrame td {
                                color: #FFFFFF;
                            }
                            .stDataFrame th {
                                color: #00BFFF;
                                font-weight: bold;
                            }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    st.success(f"Quiz submitted! Your score: {score:.1f}% ({correct_count}/{total_questions} correct)")
