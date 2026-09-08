"""Parse ds_questions.md into the public GET /api/questions schema.

Stops at ``# Answer Key`` so expected answers never appear in the payload.
Widget types, keys, prompts, and radio options match root app.py.
Inactive questions are wrapped in HTML comments in ds_questions.md.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_PATH = REPO_ROOT / "ds_questions.md"

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _strip_html_comments(text):
    return _HTML_COMMENT_RE.sub("", text)


# Legacy export — recomputed from ds_questions.md at import time.
QUESTION_KEYS = []

# Radio option arrays copied from app.py widgets (including quoting).
EDA_OPTIONS = ["Label Encoding", "Ordinal Encoding", "Hash Encoding", "One-Hot Encoding"]
ASYNCIO_OPTIONS = [
    '"Hello world!, Hello world!"',
    '"world! Hello, world! Hello"',
    '"Hello, Hello, world!, world!"',
    '"world!, world, Hello, Hello"',
]
PYTEST_OPTIONS = ["1 passed", "1 failed", "2 passed", "2 failed"]
ML_OPTIONS = ["'Supervised'", "'Unsupervised'"]
PYTORCH_SHAPE_OPTIONS = ["(3, 4)", "(4, 1)", "(2, 3)", "(3, 2)"]
PROBABILITY_STDDEV_OPTIONS = ["[30, 70]", "[50, 70]", "[30, 50]", "[8, 12]"]
AGENT_OPTIONS = [
    "A2A communication involves direct interaction between software agents for data sharing, while MCP focuses on ensuring reliable message delivery and error handling.",
    "MCP is used solely for agent negotiation, while A2A controls the overall system architecture.",
    "A2A is focused on message security, whereas MCP is used for task coordination between agents.",
    "A2A handles database management, and MCP is used for executing complex algorithms.",
]
VIZ_OPTIONS = ["'Bar Chart'", "'Histogram'", "'Line Chart'"]

MD_COUNTER_CATEGORIES = {
    "Supervised & Unsupervised Learning",
    "PyTorch",
    "Probability",
    "How Agents Use Tools, MCP, A2A, and Other Protocols",
    "Data Visualization",
}

TERMINAL_OUTPUT_EXCLUDED = {
    "Exploratory Data Analysis",
    "Asyncio (I/O-bound)",
    "ThreadPool",
    "pytest",
    "Virtual ENV",
    "Supervised & Unsupervised Learning",
    "PyTorch",
    "Probability",
    "How Agents Use Tools, MCP, A2A, and Other Protocols",
    "Data Visualization",
}

EDA_TABLE = {
    "type": "table",
    "columns": ["Car Type"],
    "rows": [
        ["Sedan"],
        ["SUV"],
        ["Convertible"],
        ["Sedan"],
        ["Convertible"],
        ["SUV"],
    ],
}


def _text_question(key, prompt):
    return {"key": key, "prompt": prompt, "input": "text"}


def _radio_question(key, options, prompt=""):
    return {"key": key, "prompt": prompt, "input": "radio", "options": list(options)}


def _consume_radio_line(category, stripped, question_counter, questions):
    """If this line is a radio option, maybe append a question. Return True if consumed."""
    if category == "Exploratory Data Analysis":
        if stripped in EDA_OPTIONS:
            if stripped == EDA_OPTIONS[0]:
                questions.append(_radio_question("answer_Exploratory_Data_Analysis", EDA_OPTIONS))
            return True
    elif category == "Asyncio (I/O-bound)":
        if stripped in ASYNCIO_OPTIONS:
            if stripped == ASYNCIO_OPTIONS[0]:
                questions.append(_radio_question("answer_Asyncio", ASYNCIO_OPTIONS))
            return True
    elif category == "pytest":
        if stripped in PYTEST_OPTIONS:
            if stripped == PYTEST_OPTIONS[0]:
                questions.append(_radio_question("answer_pytest", PYTEST_OPTIONS))
            return True
    elif category == "Supervised & Unsupervised Learning":
        if stripped in ML_OPTIONS:
            if stripped == ML_OPTIONS[0]:
                questions.append(_radio_question(f"answer_ML_q{question_counter}", ML_OPTIONS))
            return True
    elif category == "PyTorch":
        if stripped in PYTORCH_SHAPE_OPTIONS:
            if stripped == PYTORCH_SHAPE_OPTIONS[0]:
                questions.append(_radio_question("answer_PyTorch_shape", PYTORCH_SHAPE_OPTIONS))
            return True
    elif category == "Probability":
        if stripped in PROBABILITY_STDDEV_OPTIONS:
            if stripped == PROBABILITY_STDDEV_OPTIONS[0]:
                questions.append(_radio_question("answer_Probability_stddev", PROBABILITY_STDDEV_OPTIONS))
            return True
    elif category == "How Agents Use Tools, MCP, A2A, and Other Protocols":
        if stripped in AGENT_OPTIONS:
            if stripped == AGENT_OPTIONS[0]:
                questions.append(_radio_question("answer_A2A_vs_MCP", AGENT_OPTIONS))
            return True
    elif category == "Data Visualization":
        if stripped in VIZ_OPTIONS:
            if stripped == VIZ_OPTIONS[0]:
                questions.append(_radio_question(f"answer_DataViz_q{question_counter}", VIZ_OPTIONS))
            return True
    return False


def _docker_key(code_block, question_counter):
    if "builds all services" in code_block:
        return "answer_Docker_Build"
    if "starts all services" in code_block:
        return "answer_Docker_Start"
    if "stops just the 'web'" in code_block:
        return "answer_Docker_Stop"
    if "removes the stopped 'web'" in code_block:
        return "answer_Docker_Remove"
    return f"answer_Docker_{question_counter}"


def process_category(category, raw_lines):
    """Turn one ### category's markdown lines into blocks + questions (app.py widget map)."""
    blocks = []
    questions = []
    in_code_block = False
    code_block = ""
    code_language = None
    has_code_block = False
    last_code_language = None
    question_counter = 0

    for line in raw_lines:
        stripped = line.strip()
        if stripped.startswith("```") and not in_code_block:
            in_code_block = True
            code_block = ""
            has_code_block = True
            if stripped.startswith("```python"):
                code_language = "python"
            elif stripped.startswith("```shell"):
                code_language = "shell"
            elif stripped.startswith("```txt"):
                code_language = "text"
            elif stripped.startswith("```md"):
                code_language = "markdown"
            else:
                code_language = "text"
            last_code_language = code_language
        elif stripped.startswith("```") and in_code_block:
            in_code_block = False
            content = code_block.rstrip()
            last_code_language = code_language

            if code_language == "python":
                blocks.append({"type": "code", "language": "python", "content": content})
                if (
                    category == "Exploratory Data Analysis"
                    and "import pandas as pd" in code_block
                    and "df" in code_block
                ):
                    blocks.append(dict(EDA_TABLE))
            elif code_language == "shell":
                blocks.append({"type": "code", "language": "shell", "content": content})
            elif code_language == "markdown":
                blocks.append({"type": "code", "language": "md", "content": content})
                if category in MD_COUNTER_CATEGORIES:
                    question_counter += 1
                if category == "Docker" and "?" in code_block:
                    questions.append(_text_question(_docker_key(code_block, question_counter), "Answer:"))
                if category == "Probability" and question_counter == 1:
                    questions.append(_text_question("answer_Probability_dice", "Answer:"))
                if category == "PyTorch" and question_counter == 2:
                    questions.append(_text_question("answer_PyTorch_layers", "Answer:"))
            elif code_language == "text":
                if content.strip():
                    blocks.append({"type": "markdown", "content": content.strip()})
            code_block = ""
        elif in_code_block:
            if not line:
                code_block += "\n"
            else:
                code_block += line + "\n"
        else:
            if stripped and _consume_radio_line(category, stripped, question_counter, questions):
                continue
            if stripped:
                blocks.append({"type": "markdown", "content": stripped})

    if (
        has_code_block
        and category not in TERMINAL_OUTPUT_EXCLUDED
        and last_code_language == "python"
    ):
        answer_key = f"answer_{category.replace(' ', '_').replace('/', '_')}"
        questions.append(_text_question(answer_key, "Terminal Output:"))
    elif has_code_block and category == "ThreadPool":
        questions.append(_text_question("answer_ThreadPool", "Answer:"))
    elif has_code_block and category == "Virtual ENV":
        questions.append(_text_question("answer_Virtual_ENV", "Answer:"))

    return {"name": category, "blocks": blocks, "questions": questions}


def parse_markdown_sections(md_path=None):
    """Split ds_questions.md into ## sections / ### categories; stop at Answer Key."""
    path = Path(md_path) if md_path else QUESTIONS_PATH
    text = path.read_text(encoding="utf-8")
    text = _strip_html_comments(text)
    marker = "# Answer Key"
    if marker in text:
        text = text.split(marker)[0]

    sections = []
    current_section = None
    current_category = None
    for line in text.splitlines():
        if line.startswith("## "):
            current_section = {"name": line[3:].strip(), "categories": []}
            sections.append(current_section)
            current_category = None
        elif line.startswith("### ") and current_section is not None:
            current_category = {"name": line[4:].strip(), "lines": []}
            current_section["categories"].append(current_category)
        elif current_category is not None:
            current_category["lines"].append(line)
    return sections


def build_questions_payload(md_path=None):
    """Public schema for GET /api/questions (no expected answers)."""
    parsed = parse_markdown_sections(md_path)
    sections = []
    for section in parsed:
        categories = []
        for cat in section["categories"]:
            built = process_category(cat["name"], cat["lines"])
            if built["questions"] or built["blocks"]:
                categories.append(built)
        if categories:
            sections.append({"name": section["name"], "categories": categories})
    keys = []
    for section in sections:
        for category in section["categories"]:
            for question in category["questions"]:
                keys.append(question["key"])
    return {
        "title": "Data Scientist Technical Review",
        "total_questions": len(keys),
        "sections": sections,
    }


def collect_question_keys(payload=None):
    if payload is None:
        payload = build_questions_payload()
    keys = []
    for section in payload["sections"]:
        for category in section["categories"]:
            for question in category["questions"]:
                keys.append(question["key"])
    return keys


QUESTION_KEYS = collect_question_keys()
