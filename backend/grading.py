"""Quiz grading — get_answer_key, calculate_similarity, and grade_quiz copied from root app.py."""
import Levenshtein


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
