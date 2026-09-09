"""SMTP recruiter email — HTML template and send path from root app.py.

Never logs SENDER_PASSWORD. Missing credentials or SMTP errors are returned as a
warning string; callers should still persist results.
"""
import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

MANTECH_MARK = REPO_ROOT / "frontend" / "public" / "mantech-m.png"


def build_results_email_html(
    name,
    email,
    phone,
    grading_results,
    submitted_at=None,
    assessment_title="Data Scientist Initial Assessment",
):
    """MANTECH dark-theme HTML results report matching the React web app."""
    if submitted_at is None:
        submitted_at = datetime.now()
    timestamp = submitted_at.strftime("%Y-%m-%d %H:%M:%S")
    safe_title = escape(str(assessment_title))

    safe_name = escape(str(name))
    safe_email = escape(str(email))
    safe_phone = escape(str(phone))
    correct_count = grading_results["correct_count"]
    total_questions = grading_results["total_questions"]
    score_pct = f"{grading_results['score_percentage']:.1f}%"

    rows_html = []
    for question_key, result in grading_results["detailed_results"].items():
        is_correct = bool(result.get("is_correct"))
        status = (
            '<span style="color:#3dd68c;font-size:1.15em;">&#10003;</span>'
            if is_correct
            else '<span style="color:#ff5a5f;font-size:1.15em;">&#10007;</span>'
        )
        display_name = escape(
            str(question_key).replace("answer_", "").replace("_", " ")
        )
        user_ans = escape(str(result.get("user_answer", "")))
        correct_ans = escape(str(result.get("correct_answer", "")))
        row_bg = "#161d2b" if is_correct else "#1c1820"
        rows_html.append(
            f"""
                <tr>
                    <td style="padding:12px 10px;border-bottom:1px solid #2a3548;background:{row_bg};text-align:center;">{status}</td>
                    <td style="padding:12px 10px;border-bottom:1px solid #2a3548;background:{row_bg};color:#f2f4f7;">{display_name}</td>
                    <td style="padding:12px 10px;border-bottom:1px solid #2a3548;background:{row_bg};color:#c5cddb;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;">{user_ans}</td>
                    <td style="padding:12px 10px;border-bottom:1px solid #2a3548;background:{row_bg};color:#c5cddb;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;">{correct_ans}</td>
                </tr>
"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title} Results</title>
</head>
<body style="margin:0;padding:0;background-color:#0b1018;color:#f2f4f7;font-family:Montserrat,Helvetica Neue,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#0b1018;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:960px;background-color:#0b1018;">
          <!-- Brand bar -->
          <tr>
            <td style="padding:0 0 20px 0;border-bottom:2px solid #df2327;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="vertical-align:middle;">
                    <table role="presentation" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="vertical-align:middle;padding-right:12px;">
                          <img src="cid:mantech-mark" alt="MANTECH" width="42" height="42" style="display:block;border:0;border-radius:50%;" />
                        </td>
                        <td style="vertical-align:middle;">
                          <div style="font-family:Barlow Condensed,Arial Narrow,Impact,sans-serif;font-size:22px;font-weight:700;letter-spacing:0.08em;color:#ffffff;line-height:1;">MANTECH</div>
                          <div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#df2327;margin-top:4px;">Always Advancing&#8482;</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td align="right" style="vertical-align:middle;">
                    <span style="display:inline-block;padding:8px 14px;border:1px solid #75d8f0;border-radius:999px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:13px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#75d8f0;">Initial Assessment</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Title -->
          <tr>
            <td style="padding:28px 0 8px 0;">
              <h1 style="margin:0;font-family:Barlow Condensed,Arial Narrow,Impact,sans-serif;font-size:34px;font-weight:700;letter-spacing:0.02em;color:#ffffff;line-height:1.15;">
                {safe_title}
              </h1>
              <div style="width:120px;height:3px;background:linear-gradient(90deg,#df2327,rgba(223,35,39,0));margin-top:12px;"></div>
              <p style="margin:14px 0 0 0;color:#8b95a8;font-size:14px;">Results report for recruiter review</p>
            </td>
          </tr>

          <!-- Candidate info -->
          <tr>
            <td style="padding:24px 0 8px 0;">
              <h2 style="margin:0 0 14px 0;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:22px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;">
                Candidate Information
              </h2>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#161d2b;border:1px solid #2a3548;border-radius:6px;border-left:4px solid #df2327;">
                <tr>
                  <td style="padding:12px 16px;width:180px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;border-bottom:1px solid #2a3548;">Name</td>
                  <td style="padding:12px 16px;color:#f2f4f7;border-bottom:1px solid #2a3548;">{safe_name}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;border-bottom:1px solid #2a3548;">Email</td>
                  <td style="padding:12px 16px;color:#f2f4f7;border-bottom:1px solid #2a3548;">{safe_email}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;border-bottom:1px solid #2a3548;">Phone</td>
                  <td style="padding:12px 16px;color:#f2f4f7;border-bottom:1px solid #2a3548;">{safe_phone}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;">Submitted</td>
                  <td style="padding:12px 16px;color:#f2f4f7;">{escape(timestamp)}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Score summary -->
          <tr>
            <td style="padding:24px 0 8px 0;">
              <h2 style="margin:0 0 14px 0;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:22px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;">
                Score Summary
              </h2>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td width="50%" style="padding:0 8px 0 0;vertical-align:top;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#161d2b;border:1px solid #2a3548;border-radius:6px;">
                      <tr>
                        <td style="padding:20px 18px;">
                          <div style="font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:13px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#8b95a8;">Questions Correct</div>
                          <div style="margin-top:8px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:36px;font-weight:700;color:#ffffff;line-height:1;">{correct_count}/{total_questions}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td width="50%" style="padding:0 0 0 8px;vertical-align:top;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#161d2b;border:1px solid #2a3548;border-radius:6px;">
                      <tr>
                        <td style="padding:20px 18px;">
                          <div style="font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:13px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#8b95a8;">Total Score</div>
                          <div style="margin-top:8px;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:36px;font-weight:700;color:#df2327;line-height:1;">{score_pct}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Detailed breakdown -->
          <tr>
            <td style="padding:24px 0 8px 0;">
              <h2 style="margin:0 0 14px 0;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:22px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#75d8f0;">
                Detailed Breakdown
              </h2>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #2a3548;border-radius:6px;overflow:hidden;">
                <tr>
                  <th style="padding:12px 10px;background-color:#df2327;color:#ffffff;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;text-align:left;">Status</th>
                  <th style="padding:12px 10px;background-color:#df2327;color:#ffffff;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;text-align:left;">Question</th>
                  <th style="padding:12px 10px;background-color:#df2327;color:#ffffff;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;text-align:left;">Candidate Answer</th>
                  <th style="padding:12px 10px;background-color:#df2327;color:#ffffff;font-family:Barlow Condensed,Arial Narrow,sans-serif;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;text-align:left;">Correct Answer</th>
                </tr>
                {''.join(rows_html)}
              </table>
            </td>
          </tr>

          <tr>
            <td style="padding:28px 0 8px 0;border-top:1px solid #2a3548;">
              <p style="margin:0;color:#8b95a8;font-size:12px;line-height:1.5;">
                MANTECH {safe_title} &mdash; automated results notification.
                This assessment is one data point in the hiring decision and is not a pass/fail exam.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_results_email(
    name,
    email,
    phone,
    recruiter_email,
    grading_results,
    submitted_at=None,
    assessment_title="Data Scientist Initial Assessment",
):
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
            name,
            email,
            phone,
            grading_results,
            submitted_at=submitted_at,
            assessment_title=assessment_title,
        )
        msg = MIMEMultipart("related")
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = f"{assessment_title} - {name}"

        alt = MIMEMultipart("alternative")
        msg.attach(alt)
        alt.attach(MIMEText(email_html, "html", "utf-8"))

        if MANTECH_MARK.is_file():
            with open(MANTECH_MARK, "rb") as logo_file:
                logo = MIMEImage(logo_file.read(), _subtype="png")
            logo.add_header("Content-ID", "<mantech-mark>")
            logo.add_header("Content-Disposition", "inline", filename="mantech-m.png")
            msg.attach(logo)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True, None
    except Exception as email_error:
        return False, f"Email sending failed: {str(email_error)}. Results saved to database."
