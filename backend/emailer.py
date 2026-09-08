"""SMTP recruiter email — HTML template and send path from root app.py.

Never logs SENDER_PASSWORD. Missing credentials or SMTP errors are returned as a
warning string; callers should still persist results.
"""
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")


def build_results_email_html(name, email, phone, grading_results, submitted_at=None):
    """Dark-theme HTML results report matching root app.py."""
    if submitted_at is None:
        submitted_at = datetime.now()
    timestamp = submitted_at.strftime("%Y-%m-%d %H:%M:%S")

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
            <tr><td>Name</td><td>{name}</td></tr>
            <tr><td>Email</td><td>{email}</td></tr>
            <tr><td>Phone</td><td>{phone}</td></tr>
            <tr><td>Submission Time</td><td>{timestamp}</td></tr>
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
    for question_key, result in grading_results["detailed_results"].items():
        status = '<span class="correct">✅</span>' if result["is_correct"] else '<span class="incorrect">❌</span>'
        display_name = question_key.replace("answer_", "").replace("_", " ")
        user_ans = str(result["user_answer"])
        correct_ans = str(result["correct_answer"])
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
    return email_html


def send_results_email(name, email, phone, recruiter_email, grading_results, submitted_at=None):
    """Send the dark-theme HTML report via Gmail SMTP.

    Returns (email_sent, email_warning). Never raises for SMTP/credential failures.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = recruiter_email

    if not sender_email or not sender_password:
        return False, "Email credentials not configured. Results saved to database only."

    try:
        email_html = build_results_email_html(
            name, email, phone, grading_results, submitted_at=submitted_at
        )
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = f"Data Scientist Technical Review - {name}"
        html_part = MIMEText(email_html, "html")
        msg.attach(html_part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True, None
    except Exception as email_error:
        return False, f"Email sending failed: {str(email_error)}. Results saved to database."
