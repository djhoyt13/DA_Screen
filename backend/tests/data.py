"""Shared quiz payloads for tests (not pytest fixtures)."""

PERFECT_ANSWERS = {
    "answer_Unpacking": "World",
    "answer_Loops": "[1, 4, 9, 16]",
    "answer_Lambda_functions": "[11, 22, 33]",
    # "answer_Pydantic___Validation": "Data is not valid",
    "answer_NumPy_&_Pandas": "18.0",
    "answer_Exploratory_Data_Analysis": "One-Hot Encoding",
    "answer_ThreadPool": "4",
    "answer_Asyncio": '"Hello, Hello, world!, world!"',
    "answer_pytest": "1 passed",
    "answer_Virtual_ENV": "source .venv/bin/activate",
    "answer_Docker_Build": "docker-compose build",
    "answer_Docker_Start": "docker compose up",
    "answer_Docker_Stop": "docker-compose stop web",
    # "answer_Docker_Remove": "docker-compose rm -f web",
    "answer_ML_q2": "'Supervised'",
    "answer_ML_q3": "'Unsupervised'",
    "answer_PyTorch_shape": "(2, 3)",
    "answer_PyTorch_layers": "3",
    "answer_Probability_dice": "0.0278",
    # "answer_Probability_stddev": "[30, 70]",
    "answer_A2A_vs_MCP": (
        "A2A communication involves direct interaction between software agents "
        "for data sharing, while MCP focuses on ensuring reliable message delivery "
        "and error handling."
    ),
    "answer_DataViz_q2": "'Bar Chart'",
    "answer_DataViz_q3": "'Histogram'",
    # "answer_DataViz_q4": "'Line Chart'",
}

VALID_CANDIDATE = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "5551234567",
    "recruiter_email": "recruiter@example.com",
}
