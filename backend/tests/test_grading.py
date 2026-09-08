from backend.grading import get_answer_key, grade_quiz
from backend.tests.data import PERFECT_ANSWERS

ACTIVE_COUNT = len(get_answer_key())


def test_perfect_score():
    result = grade_quiz(PERFECT_ANSWERS)
    assert result["correct_count"] == ACTIVE_COUNT
    assert result["total_questions"] == ACTIVE_COUNT
    assert result["score_percentage"] == 100.0
    assert all(item["is_correct"] for item in result["detailed_results"].values())


def test_fuzzy_variants_count_as_correct():
    answers = dict(PERFECT_ANSWERS)
    answers["answer_Unpacking"] = "world"
    answers["answer_NumPy_&_Pandas"] = "18"
    answers["answer_Docker_Build"] = "docker compose build"
    result = grade_quiz(answers)
    assert result["correct_count"] == ACTIVE_COUNT
    assert result["total_questions"] == ACTIVE_COUNT
    assert result["detailed_results"]["answer_Unpacking"]["is_correct"] is True
    assert result["detailed_results"]["answer_NumPy_&_Pandas"]["is_correct"] is True
    assert result["detailed_results"]["answer_Docker_Build"]["is_correct"] is True


def test_three_wrong():
    answers = dict(PERFECT_ANSWERS)
    answers["answer_Unpacking"] = "Hello"
    answers["answer_Exploratory_Data_Analysis"] = "Label Encoding"
    answers["answer_ML_q2"] = "'Unsupervised'"
    result = grade_quiz(answers)
    assert result["correct_count"] == ACTIVE_COUNT - 3
    assert result["total_questions"] == ACTIVE_COUNT
    assert result["detailed_results"]["answer_Unpacking"]["is_correct"] is False
    assert result["detailed_results"]["answer_Exploratory_Data_Analysis"]["is_correct"] is False
    assert result["detailed_results"]["answer_ML_q2"]["is_correct"] is False


def test_empty_answers_are_not_correct():
    result = grade_quiz({})
    assert result["correct_count"] == 0
    assert result["total_questions"] == ACTIVE_COUNT
    assert all(item["is_correct"] is False for item in result["detailed_results"].values())
    assert all(item["user_answer"] == "" for item in result["detailed_results"].values())

    blank = {key: "" for key in PERFECT_ANSWERS}
    blank_result = grade_quiz(blank)
    assert blank_result["correct_count"] == 0
