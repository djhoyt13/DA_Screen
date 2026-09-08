import streamlit as st
import re
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import Levenshtein
import styles

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Data Scientist Initial Assessment",
    page_icon="frontend/public/mantech-m.png",
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

def load_questions(md_path):
    """Load questions from markdown file (HTML-comment blocks are excluded)."""
    questions = {}
    current_section = None

    with open(md_path, 'r') as file:
        text = file.read()

    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    for line in text.splitlines():
        line = line.strip()
        if line.startswith('## '):
            current_section = line.strip('## ').strip()
            questions[current_section] = []
        elif line.startswith('# Answer Key'):
            break
        elif current_section and line:
            questions[current_section].append(line)

    return questions

# Define answer key mapping for grading
def get_answer_key():
    """Map standardized question keys to correct answers"""
    return {
        # Python Basics
        'answer_Unpacking': 'World',
        'answer_Loops': ['[1, 4, 9, 16]', '[1,4,9,16]'],
        'answer_Lambda_functions': ['[11, 22, 33]', '[11,22,33]'],
        # 'answer_Pydantic___Validation': ['"Data is not valid"', 'Data is not valid'],
        
        # Data Manipulation
        'answer_NumPy_&_Pandas': ['18.0', '18'],
        'answer_Exploratory_Data_Analysis': 'One-Hot Encoding',
        
        # Python Intermediate Topics
        'answer_ThreadPool': '4',
        'answer_Asyncio': '"Hello, Hello, world!, world!"',
        
        # Testing and Environment Setup
        'answer_pytest': '1 passed',
        'answer_Virtual_ENV': ['source .venv/bin/activate', '.venv\\Scripts\\activate'],  # Accept both
        
        # Containerization and Deployment
        'answer_Docker_Build': ['docker-compose build', 'docker compose build'],
        'answer_Docker_Start': ['docker-compose up', 'docker compose up'],
        'answer_Docker_Stop': ['docker-compose stop web', 'docker compose stop web'],
        # 'answer_Docker_Remove': ['docker-compose rm -f web', 'docker compose rm -f web'],
        
        # Machine Learning Concepts
        'answer_ML_q2': "'Supervised'",
        'answer_ML_q3': "'Unsupervised'",
        
        # Advanced Topics
        'answer_PyTorch_shape': '(2, 3)',
        'answer_PyTorch_layers': '3',
        
        # Probability
        'answer_Probability_dice': ['0.0278', '.0278'],  # Accept both formats
        # 'answer_Probability_stddev': '[30, 70]',
        
        # Systems and Protocols
        'answer_A2A_vs_MCP': 'A2A enables agents to communicate and collaborate with each other, while MCP standardizes how an agent connects to tools, data sources, and external context.',
        
        # Data Visualization
        'answer_DataViz_q2': "'Bar Chart'",
        'answer_DataViz_q3': "'Histogram'",
        # 'answer_DataViz_q4': "'Line Chart'"
    }

def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings using Levenshtein distance"""
    if not str1 or not str2:
        return 0.0
    # Normalize strings: lowercase and strip
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    # Calculate Levenshtein distance
    distance = Levenshtein.distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    # Return similarity ratio (1.0 = identical, 0.0 = completely different)
    similarity = 1 - (distance / max_len)
    return similarity

def grade_quiz(user_answers):
    """Grade the quiz and return score and detailed results"""
    answer_key = get_answer_key()
    total_questions = len(answer_key)
    correct_count = 0
    detailed_results = {}
    
    # Define which questions use text input (require fuzzy matching)
    text_input_questions = [
        'answer_Unpacking', 'answer_Loops', 'answer_Lambda_functions',
        # 'answer_Pydantic___Validation',
        'answer_NumPy_&_Pandas', 'answer_ThreadPool', 'answer_Virtual_ENV',
        'answer_Docker_Build', 'answer_Docker_Start', 'answer_Docker_Stop',
        # 'answer_Docker_Remove',
        'answer_PyTorch_layers', 'answer_Probability_dice'
    ]
    
    # Similarity threshold for fuzzy matching (80% similar = correct)
    SIMILARITY_THRESHOLD = 0.80
    
    for question_key, correct_answer in answer_key.items():
        user_answer = user_answers.get(question_key, '').strip()
        is_correct = False
        
        # Handle multiple acceptable answers
        if isinstance(correct_answer, list):
            # Check exact match first
            if user_answer in correct_answer:
                is_correct = True
            # If text input question, use fuzzy matching
            elif question_key in text_input_questions:
                for correct_option in correct_answer:
                    similarity = calculate_similarity(user_answer, correct_option)
                    if similarity >= SIMILARITY_THRESHOLD:
                        is_correct = True
                        break
        else:
            # Check exact match first
            if user_answer == correct_answer:
                is_correct = True
            # If text input question, use fuzzy matching
            elif question_key in text_input_questions:
                similarity = calculate_similarity(user_answer, correct_answer)
                if similarity >= SIMILARITY_THRESHOLD:
                    is_correct = True
        
        if is_correct:
            correct_count += 1
        
        detailed_results[question_key] = {
            'user_answer': user_answer,
            'correct_answer': correct_answer if not isinstance(correct_answer, list) else correct_answer[0],
            'is_correct': is_correct
        }
    
    score_percentage = (correct_count / total_questions) * 100
    
    return {
        'score_percentage': score_percentage,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'detailed_results': detailed_results
    }

# Load questions and answers
questions = load_questions('ds_questions.md')

st.title("Data Scientist Technical Review")

# Add progress bar based on answered questions
expected_keys = list(get_answer_key().keys())
total_questions = len(expected_keys)
answered_count = 0

# Count how many questions have been answered
for key in expected_keys:
    value = st.session_state.get(key, '')
    if value is not None and (not isinstance(value, str) or value.strip() != ''):
        answered_count += 1

# Display progress bar using Streamlit's native widget
progress_percentage = answered_count / total_questions
st.progress(progress_percentage, text=f"Progress: {answered_count}/{total_questions} questions answered")

# Add a welcome message with markdown formatting
st.markdown("""
<div class="welcome-msg">
Welcome to the Data Scientist technical review. The results of this review are only one data point in our team's hiring decision. This is <strong><u>NOT</u></strong> a pass/fail exam; it is used to assess your current strengths and areas for improvement in the domains of Data Science that are relevant to our organization.
</div>
""", unsafe_allow_html=True)

# Candidate Information Section
st.markdown("## Candidate Information")

# Create a single column that takes up half the width
col1, col2 = st.columns([1, 1])

with col1:
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

# Define the order of sections
section_order = [
    "Python Basics", 
    "Data Manipulation", 
    "Python Intermediate Topics",
    "Testing and Environment Setup",
    "Containerization and Deployment",
    "Machine Learning Concepts",
    "Advanced Topics",
    "Systems and Protocols",
    "Data Visualization"
]

# Display sections in the defined order
for section_idx, section_name in enumerate(section_order):
    if section_name in questions:
        section_questions = questions[section_name]
        st.header(section_name)
        
        # Group questions by category
        categories = {}
        current_category = "General"
        
        for line in section_questions:
            if line.startswith('### '):
                current_category = line.strip('### ').strip()
                if current_category not in categories:
                    categories[current_category] = []
            else:
                if current_category not in categories:
                    categories[current_category] = []
                categories[current_category].append(line)
        
        # Display each category
        for category_idx, (category, content) in enumerate(categories.items()):
            if category != "General":
                st.subheader(category)
            
            # Process content in this category
            code_block = ""
            in_code_block = False
            has_code_block = False  # Track if this category has a code block
            last_code_language = None  # Track the language of the last code block
            question_counter = 0  # Track which question we're on for categories with multiple questions
            
            for line in content:
                if line.startswith('```python'):
                    in_code_block = True
                    code_block = ""
                    code_language = "python"
                    has_code_block = True
                    last_code_language = "python"
                elif line.startswith('```shell'):
                    in_code_block = True
                    code_block = ""
                    code_language = "shell"
                    has_code_block = True
                    last_code_language = "shell"
                elif line.startswith('```txt'):
                    in_code_block = True
                    code_block = ""
                    code_language = "text"
                    has_code_block = True
                    last_code_language = "text"
                elif line.startswith('```md'):
                    in_code_block = True
                    code_block = ""
                    code_language = "markdown"
                    has_code_block = True
                    last_code_language = "markdown"
                elif line.startswith('```') and not in_code_block:
                    in_code_block = True
                    code_block = ""
                    code_language = "text"
                    has_code_block = True
                    last_code_language = "text"
                elif line.startswith('```') and in_code_block:
                    in_code_block = False
                    # Display code blocks based on their language
                    if code_language == "python":
                        st.code(code_block.rstrip(), language=code_language)
                    elif code_language == "shell":
                        st.code(code_block.rstrip(), language="bash")
                    elif code_language == "markdown":
                        # Display markdown blocks as code blocks with plain text (no syntax highlighting)
                        st.code(code_block.rstrip(), language="text")
                        
                        # Increment question counter for categories that use it
                        if category in ["Supervised & Unsupervised Learning", "PyTorch", "Probability", 
                                       "How Agents Use Tools, MCP, A2A, and Other Protocols", "Data Visualization"]:
                            question_counter += 1
                        
                        # Add answer box for Docker questions (but not for the instruction text)
                        if category == "Docker" and "?" in code_block:
                            st.markdown("**Answer:**")
                            # Map Docker questions to standardized keys
                            if "builds all services" in code_block:
                                docker_key = "answer_Docker_Build"
                            elif "starts all services" in code_block:
                                docker_key = "answer_Docker_Start"
                            elif "stops just the 'web'" in code_block:
                                docker_key = "answer_Docker_Stop"
                            elif "removes the stopped 'web'" in code_block:
                                docker_key = "answer_Docker_Remove"
                            else:
                                docker_key = f"answer_Docker_{question_counter}"
                            st.text_input("", key=docker_key, 
                                        label_visibility="collapsed")
                        
                        # Add answer box for Probability question 1 (dice question)
                        if category == "Probability" and question_counter == 1:
                            st.markdown("**Answer:**")
                            st.text_input("", key="answer_Probability_dice", 
                                        label_visibility="collapsed")
                        
                        # Add answer box for PyTorch question 2 (layers question)
                        if category == "PyTorch" and question_counter == 2:
                            st.markdown("**Answer:**")
                            st.text_input("", key="answer_PyTorch_layers", 
                                        label_visibility="collapsed")
                    elif code_language == "text":
                        # Display txt blocks as markdown instead of code blocks (only if not empty)
                        if code_block.strip():
                            st.markdown(f"**{code_block.strip()}**")
                    
                    # Special handling for pandas DataFrame display in Exploratory Data Analysis section
                    if "import pandas as pd" in code_block and "df" in code_block and category == "Exploratory Data Analysis":
                        # Execute the pandas code to display the DataFrame
                        try:
                            # Create a local environment to execute the code
                            local_env = {}
                            exec(code_block, globals(), local_env)
                            # If df exists in the environment, display it
                            if 'df' in local_env:
                                st.dataframe(local_env['df'])
                        except Exception as e:
                            st.error(f"Error displaying DataFrame: {str(e)}")
                            # Fallback to regular text input if there's an error
                            st.markdown("**Given the dataset, what is the most appropriate form of encoding?**")
                            st.text_input("", key=f"answer_{section_idx}_{category_idx}_{category.replace(' ', '_')}", 
                                          label_visibility="collapsed")
                    # Only show Terminal Output for code blocks that aren't the EDA pandas DataFrame or txt question
                    elif category != "Exploratory Data Analysis":
                        # We'll add Terminal Output and answer boxes at the end of processing all content for this category
                        pass
                elif in_code_block:
                    # Preserve exact indentation and line spacing
                    if not line:  # If it's an empty line
                        code_block += "\n"  # Add a newline
                    else:
                        # Keep original indentation
                        code_block += line + "\n"
                else:
                    # Regular text - display if not empty
                    if line and not line.startswith('```'):
                        # Special handling for multiple choice options
                        if category == "Exploratory Data Analysis":
                            # If this is one of the encoding options, don't display it here (will be handled by radio buttons)
                            if line.strip() in ["Label Encoding", "Ordinal Encoding", "Hash Encoding", "One-Hot Encoding"]:
                                # If this is the first encoding option, add the radio buttons
                                if line.strip() == "Label Encoding":
                                    encoding_options = ["Label Encoding", "Ordinal Encoding", "Hash Encoding", "One-Hot Encoding"]
                                    selected_encoding = st.radio(
                                        "", 
                                        encoding_options,
                                        index=None,
                                        key="answer_Exploratory_Data_Analysis",
                                        label_visibility="collapsed"
                                    )
                            # For all other text, display normally
                            else:
                                st.markdown(line)
                        elif category == "Asyncio (I/O-bound)":
                            # If this is one of the asyncio output options, don't display it here (will be handled by radio buttons)
                            if line.strip() in ['"Hello world!, Hello world!"', '"world! Hello, world! Hello"', '"Hello, Hello, world!, world!"', '"world!, world, Hello, Hello"']:
                                # If this is the first option, add the text and radio buttons
                                if line.strip() == '"Hello world!, Hello world!"':
                                    # The text is now in a code block in the markdown file
                                    
                                    asyncio_options = ['"Hello world!, Hello world!"', '"world! Hello, world! Hello"', '"Hello, Hello, world!, world!"', '"world!, world, Hello, Hello"']
                                    selected_option = st.radio(
                                        "", 
                                        asyncio_options,
                                        index=None,
                                        key="answer_Asyncio",
                                        label_visibility="collapsed"
                                    )
                            # For all other text, display normally
                            else:
                                st.markdown(line)
                        elif category == "pytest":
                            # If this is one of the pytest answer options, don't display it here (will be handled by radio buttons)
                            if line.strip() in ["1 passed", "1 failed", "2 passed", "2 failed"]:
                                # If this is the first option, add the radio buttons
                                if line.strip() == "1 passed":
                                    pytest_options = ["1 passed", "1 failed", "2 passed", "2 failed"]
                                    selected_option = st.radio(
                                        "", 
                                        pytest_options,
                                        index=None,
                                        key="answer_pytest",
                                        label_visibility="collapsed"
                                    )
                            # For all other text, display normally
                            else:
                                st.markdown(line)
                        elif category == "Supervised & Unsupervised Learning":
                            # Handle Supervised/Unsupervised radio buttons
                            if line.strip() in ["'Supervised'", "'Unsupervised'"]:
                                if line.strip() == "'Supervised'":
                                    ml_options = ["'Supervised'", "'Unsupervised'"]
                                    selected_option = st.radio(
                                        "", 
                                        ml_options,
                                        index=None,
                                        key=f"answer_ML_q{question_counter}",
                                        label_visibility="collapsed"
                                    )
                            else:
                                st.markdown(line)
                        elif category == "PyTorch":
                            # Handle PyTorch shape radio buttons (only for question 1)
                            if line.strip() in ["(3, 4)", "(4, 1)", "(2, 3)", "(3, 2)"]:
                                if line.strip() == "(3, 4)":
                                    shape_options = ["(3, 4)", "(4, 1)", "(2, 3)", "(3, 2)"]
                                    selected_option = st.radio(
                                        "", 
                                        shape_options,
                                        index=None,
                                        key="answer_PyTorch_shape",
                                        label_visibility="collapsed"
                                    )
                            else:
                                st.markdown(line)
                        elif category == "Probability":
                            # Handle Probability radio buttons (for question 2)
                            if line.strip() in ["[30, 70]", "[50, 70]", "[30, 50]", "[8, 12]"]:
                                if line.strip() == "[30, 70]":
                                    prob_options = ["[30, 70]", "[50, 70]", "[30, 50]", "[8, 12]"]
                                    selected_option = st.radio(
                                        "", 
                                        prob_options,
                                        index=None,
                                        key="answer_Probability_stddev",
                                        label_visibility="collapsed"
                                    )
                            else:
                                st.markdown(line)
                        elif category == "How Agents Use Tools, MCP, A2A, and Other Protocols":
                            # Handle A2A/MCP radio buttons
                            agent_options = [
                                "A2A enables agents to communicate and collaborate with each other, while MCP standardizes how an agent connects to tools, data sources, and external context.",
                                "MCP is used solely for agent negotiation, while A2A controls the overall system architecture.",
                                "A2A is focused on message security, whereas MCP is used for task coordination between agents.",
                                "A2A handles database management, and MCP is used for executing complex algorithms."
                            ]
                            if line.strip() in agent_options:
                                if line.strip() == agent_options[0]:
                                    selected_option = st.radio(
                                        "", 
                                        agent_options,
                                        index=None,
                                        key="answer_A2A_vs_MCP",
                                        label_visibility="collapsed"
                                    )
                            else:
                                st.markdown(line)
                        elif category == "Data Visualization":
                            # Handle Data Visualization radio buttons
                            if line.strip() in ["'Bar Chart'", "'Histogram'", "'Line Chart'"]:
                                if line.strip() == "'Bar Chart'":
                                    viz_options = ["'Bar Chart'", "'Histogram'", "'Line Chart'"]
                                    selected_option = st.radio(
                                        "", 
                                        viz_options,
                                        index=None,
                                        key=f"answer_DataViz_q{question_counter}",
                                        label_visibility="collapsed"
                                    )
                            else:
                                st.markdown(line)
                        else:
                            st.markdown(line)
                            
            # After processing all content for this category, add Terminal Output and answer box if needed
            # Only for categories with Python code blocks and no special handling
            if (has_code_block and 
                category not in ["Exploratory Data Analysis", "Asyncio (I/O-bound)", "ThreadPool", "pytest", "Virtual ENV",
                                "Supervised & Unsupervised Learning", "PyTorch", "Probability", 
                                "How Agents Use Tools, MCP, A2A, and Other Protocols", "Data Visualization"] and 
                last_code_language == "python"):
                st.markdown("**Terminal Output:**")
                # Add an answer box for this category with standardized key
                answer_key = f"answer_{category.replace(' ', '_').replace('/', '_')}"
                st.text_input("", key=answer_key, 
                            label_visibility="collapsed")
            # Special handling for ThreadPool question (has txt code block for question)
            elif has_code_block and category == "ThreadPool":
                st.markdown("**Answer:**")
                # Add an answer box for ThreadPool question
                st.text_input("", key="answer_ThreadPool", 
                            label_visibility="collapsed")
            # Special handling for Virtual ENV (has txt code block for question)
            elif has_code_block and category == "Virtual ENV":
                st.markdown("**Answer:**")
                # Add an answer box for Virtual ENV question
                st.text_input("", key="answer_Virtual_ENV", 
                            label_visibility="collapsed")

# Add submit button at the end
st.markdown("---")
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
        
        if not st.session_state.get('recruiter_email', '').strip():
            validation_errors.append("Recruiter's email is required")
        elif not is_valid_email(st.session_state.recruiter_email):
            validation_errors.append("Please enter a valid recruiter email address")
        
        # Check if all questions are answered
        all_questions_answered = True
        
        # List of all expected answer keys (must match active questions in ds_questions.md)
        expected_keys = list(get_answer_key().keys())
        
        # Check all answer keys in session state
        for key in expected_keys:
            value = st.session_state.get(key, '')
            # Check if the value is empty or None
            if value is None or (isinstance(value, str) and value.strip() == ''):
                all_questions_answered = False
                break
        
        if not all_questions_answered:
            validation_errors.append("Please make sure you have answered all of the questions")
        
        # If there are validation errors, display them
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            # Collect all answers
            answers_dict = {}
            for key, value in st.session_state.items():
                if key.startswith('answer_'):
                    answers_dict[key] = value
            
            # Grade the quiz
            grading_results = grade_quiz(answers_dict)
            
            # Create results data with candidate info and score
            results_data = {
                'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'Name': [st.session_state.name],
                'Email': [st.session_state.email],
                'Phone': [st.session_state.phone],
                'Recruiter_Email': [st.session_state.recruiter_email],
                'Score_Percentage': [f"{grading_results['score_percentage']:.2f}%"],
                'Correct_Count': [f"{grading_results['correct_count']}/{grading_results['total_questions']}"]
            }
            
            # Add each answer with correct/incorrect marking
            for question_key, result in grading_results['detailed_results'].items():
                # Add the user's answer
                results_data[question_key] = [str(result['user_answer'])]
                # Add correct/incorrect status
                results_data[f"{question_key}_Correct"] = ['Yes' if result['is_correct'] else 'No']
                # Add the correct answer for reference
                results_data[f"{question_key}_Expected"] = [str(result['correct_answer'])]
            
            # Create DataFrame
            results_df = pd.DataFrame(results_data)
            
            # Save to CSV
            try:
                results_df.to_csv('quiz_results.csv', mode='a', header=not pd.io.common.file_exists('quiz_results.csv'), index=False)
            except Exception as e:
                st.error(f"Error saving results: {str(e)}")
            
            # Send email to recruiter
            try:
                # Create HTML email content with candidate info and table (dark mode matching Streamlit)
                email_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #0E1117; color: #FFFFFF; }}
        .container {{ max-width: 1000px; margin: 0 auto; background-color: #0E1117; padding: 30px; }}
        h1 {{ color: #00BFFF; border-bottom: 3px solid #00BFFF; padding-bottom: 10px; font-weight: bold; }}
        h2 {{ color: #00CED1; margin-top: 30px; border-bottom: 2px solid #00CED1; padding-bottom: 8px; }}
        .info-table {{ width: 100%; margin: 20px 0; border-collapse: collapse; background-color: #262730; }}
        .info-table td {{ padding: 12px; border-bottom: 1px solid #3a3a3a; color: #E0E0E0; }}
        .info-table td:first-child {{ font-weight: bold; width: 200px; color: #00CED1; }}
        .score-box {{ background-color: #262730; padding: 30px; border-radius: 8px; margin: 20px 0; text-align: center; border: 2px solid #00BFFF; }}
        .score-box h3 {{ margin: 15px 0; color: #00BFFF; font-size: 1.8em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #262730; }}
        th {{ background-color: #0066CC; color: white; padding: 12px; text-align: left; font-weight: bold; }}
        td {{ padding: 10px; border-bottom: 1px solid #3a3a3a; color: #E0E0E0; }}
        tr:hover {{ background-color: #1a1a24; }}
        .correct {{ color: #4CAF50; font-size: 1.2em; }}
        .incorrect {{ color: #f44336; font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Scientist Technical Review Results</h1>
        
        <h2>Candidate Information</h2>
        <table class="info-table">
            <tr><td>Name</td><td>{st.session_state.name}</td></tr>
            <tr><td>Email</td><td>{st.session_state.email}</td></tr>
            <tr><td>Phone</td><td>{st.session_state.phone}</td></tr>
            <tr><td>Submission Time</td><td>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
        </table>
        
        <h2>Score Summary</h2>
        <div class="score-box">
            <h3>Questions Correct: {grading_results['correct_count']}/{grading_results['total_questions']}</h3>
            <h3>Total Score: {grading_results['score_percentage']:.1f}%</h3>
        </div>
        
        <h2>Detailed Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Question</th>
                    <th>Your Answer</th>
                    <th>Correct Answer</th>
                </tr>
            </thead>
            <tbody>
"""
                # Add each question as a row in the HTML table
                for question_key, result in grading_results['detailed_results'].items():
                    status = '<span class="correct">✅</span>' if result['is_correct'] else '<span class="incorrect">❌</span>'
                    display_name = question_key.replace('answer_', '').replace('_', ' ')
                    user_ans = str(result['user_answer'])
                    correct_ans = str(result['correct_answer'])
                    email_html += f"""
                <tr>
                    <td>{status}</td>
                    <td>{display_name}</td>
                    <td>{user_ans}</td>
                    <td>{correct_ans}</td>
                </tr>
"""
                
                email_html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
                
                # Email configuration from environment variables
                sender_email = os.getenv('SENDER_EMAIL')
                sender_password = os.getenv('SENDER_PASSWORD')
                receiver_email = st.session_state.recruiter_email
                
                # Create email message with HTML
                msg = MIMEMultipart('alternative')
                msg['From'] = sender_email
                msg['To'] = receiver_email
                msg['Subject'] = f"Data Scientist Technical Review - {st.session_state.name}"
                
                # Attach HTML content
                html_part = MIMEText(email_html, 'html')
                msg.attach(html_part)
                
                # Send email via SMTP
                if sender_email and sender_password:
                    try:
                        with smtplib.SMTP('smtp.gmail.com', 587) as server:
                            server.starttls()
                            server.login(sender_email, sender_password)
                            server.sendmail(sender_email, receiver_email, msg.as_string())
                    except Exception as email_error:
                        st.warning(f"Email sending failed: {str(email_error)}. Results saved to CSV.")
                else:
                    st.warning("Email credentials not configured. Results saved to CSV only.")
                
                st.session_state.submitted = True
                st.session_state.grading_results = grading_results  # Store for display later
                st.success(f"Quiz submitted successfully! Results have been sent to {st.session_state.recruiter_email}")
                
                # Display results immediately after submission
                st.markdown("---")
                st.markdown("## Your Results")
                
                # Display score summary
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Questions Correct",
                        value=f"{grading_results['correct_count']}/{grading_results['total_questions']}"
                    )
                with col2:
                    st.metric(
                        label="Total Score",
                        value=f"{grading_results['score_percentage']:.1f}%"
                    )
                
                # Display detailed results in table format
                st.markdown("### Detailed Breakdown")
                
                # Create data for the table
                table_data = []
                for question_key, result in grading_results['detailed_results'].items():
                    # Clean up the key name for display
                    display_name = question_key.replace('answer_', '').replace('_', ' ')
                    
                    # Add row to table
                    table_data.append({
                        'Status': '✅' if result['is_correct'] else '❌',
                        'Question': display_name,
                        'Your Answer': result['user_answer'],
                        'Correct Answer': result['correct_answer']
                    })
                
                # Create and display DataFrame - use st.table() to show all rows without scrolling
                results_df = pd.DataFrame(table_data)
                st.table(results_df)
                
            except Exception as e:
                st.warning(f"Results saved but email notification failed: {str(e)}")
                st.session_state.submitted = True
                st.session_state.grading_results = grading_results  # Store for display later
else:
    st.success("Thank you! Your quiz has been submitted.")
    
    # Display results if available
    if 'grading_results' in st.session_state:
        st.markdown("---")
        st.markdown("## Your Results")
        
        grading_results = st.session_state.grading_results
        
        # Display score summary
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Questions Correct",
                value=f"{grading_results['correct_count']}/{grading_results['total_questions']}"
            )
        with col2:
            st.metric(
                label="Total Score",
                value=f"{grading_results['score_percentage']:.1f}%"
            )
        
        # Display detailed results in table format
        st.markdown("### Detailed Breakdown")
        
        # Create data for the table
        table_data = []
        for question_key, result in grading_results['detailed_results'].items():
            # Clean up the key name for display
            display_name = question_key.replace('answer_', '').replace('_', ' ')
            
            # Add row to table
            table_data.append({
                'Status': '✅' if result['is_correct'] else '❌',
                'Question': display_name,
                'Your Answer': result['user_answer'],
                'Correct Answer': result['correct_answer']
            })
        
        # Create and display DataFrame - use st.table() to show all rows without scrolling
        results_df = pd.DataFrame(table_data)
        st.table(results_df)

