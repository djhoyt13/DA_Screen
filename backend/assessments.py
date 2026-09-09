"""Assessment registry — Data Scientist (ds) and Data Engineer (de)."""

from backend import de_quiz
from backend.grading import get_answer_key as get_ds_answer_key
from backend.grading import grade_quiz as grade_with_key
from backend.questions import QUESTION_KEYS as DS_QUESTION_KEYS
from backend.questions import build_questions_payload as build_ds_questions_payload

ASSESSMENTS = {
    "ds": {
        "id": "ds",
        "slug": "ds",
        "path": "/data-scientist",
        "display_name": "Data Scientist Initial Assessment",
        "title": "Data Scientist Technical Review",
        "welcome_role": "Data Scientist",
    },
    "de": {
        "id": "de",
        "slug": "de",
        "path": "/data-engineer",
        "display_name": de_quiz.DISPLAY_NAME,
        "title": de_quiz.TITLE,
        "welcome_role": "Data Engineer",
    },
}


def normalize_assessment_id(value):
    if value is None or value == "":
        return "ds"
    key = str(value).strip().lower()
    if key in ("ds", "data-scientist", "data_scientist", "scientist"):
        return "ds"
    if key in ("de", "data-engineer", "data_engineer", "engineer"):
        return "de"
    return None


def list_assessments():
    return [
        {
            "id": meta["id"],
            "slug": meta["slug"],
            "path": meta["path"],
            "display_name": meta["display_name"],
            "title": meta["title"],
        }
        for meta in ASSESSMENTS.values()
    ]


def get_assessment_meta(assessment_id):
    normalized = normalize_assessment_id(assessment_id)
    if normalized is None:
        return None
    return ASSESSMENTS[normalized]


def build_questions_payload(assessment_id="ds"):
    normalized = normalize_assessment_id(assessment_id)
    if normalized is None:
        raise ValueError(f"Unknown assessment: {assessment_id}")
    if normalized == "de":
        return de_quiz.build_de_questions_payload()
    payload = build_ds_questions_payload()
    payload["assessment"] = "ds"
    return payload


def get_answer_key_for(assessment_id="ds"):
    normalized = normalize_assessment_id(assessment_id)
    if normalized == "de":
        return de_quiz.get_de_answer_key()
    return get_ds_answer_key()


def question_keys_for(assessment_id="ds"):
    normalized = normalize_assessment_id(assessment_id)
    if normalized == "de":
        return list(de_quiz.DE_QUESTION_KEYS)
    return list(DS_QUESTION_KEYS)


def text_input_questions_for(assessment_id="ds"):
    normalized = normalize_assessment_id(assessment_id)
    if normalized == "de":
        return list(de_quiz.DE_TEXT_INPUT_QUESTIONS)
    return None  # grading defaults to DS text-input list


def grade_assessment(assessment_id, answers):
    normalized = normalize_assessment_id(assessment_id) or "ds"
    return grade_with_key(
        answers,
        answer_key=get_answer_key_for(normalized),
        text_input_questions=text_input_questions_for(normalized),
    )
