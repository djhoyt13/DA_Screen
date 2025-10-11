# Data Scientist Technical Review

A Streamlit-based technical assessment application for evaluating Data Scientist candidates.

## Features

- **Interactive Quiz**: 24 questions covering Python, Data Manipulation, Machine Learning, and more
- **Auto-Grading**: Automatic scoring with detailed results
- **Progress Tracking**: Real-time progress bar showing completion status
- **Email Notifications**: Sends results to recruiters via SMTP
- **Dark Mode UI**: Professional dark theme with blue accents
- **CSV Export**: Detailed results saved with correct/incorrect marking

## Setup

### Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/djhoyt13/DA_Screen.git
cd DA_Screen
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables** (optional, for email):
Create a `.env` file in the root directory:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

5. **Run the application**:
```bash
streamlit run app.py
```

## Deployment

The app is deployed on Streamlit Cloud. Make sure to add `SENDER_EMAIL` and `SENDER_PASSWORD` as secrets in Streamlit Cloud settings for email functionality.

## File Structure

- `app.py` - Main Streamlit application
- `ds_questions.md` - Question bank and answer key
- `styles.py` - Custom CSS styling
- `quiz_results.csv` - Stores submission results
- `requirements.txt` - Python dependencies

## Question Categories

1. Python Basics
2. Data Manipulation
3. Python Intermediate Topics
4. Testing and Environment Setup
5. Containerization and Deployment
6. Machine Learning Concepts
7. Advanced Topics (PyTorch)
8. Probability
9. Systems and Protocols
10. Data Visualization

## Grading

The quiz automatically grades submissions and provides:
- Overall score (percentage and fraction)
- Detailed breakdown table showing correct/incorrect answers
- Email report to recruiter with full results

## License

Private repository for internal use.
