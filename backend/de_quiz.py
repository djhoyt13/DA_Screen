"""Data Engineer Initial Assessment — public quiz payload and answer key.

Question copy is documented in ``de_questions.md``. Expected answers live only here
(and must never be included in GET /api/questions payloads).
"""

TITLE = "Data Engineer Technical Review"
ASSESSMENT_ID = "de"
DISPLAY_NAME = "Data Engineer Initial Assessment"

# Radio option sets (first option is also used as the correct answer where applicable).
JOIN_OPTIONS = [
    "An INNER JOIN returns only matching rows from both tables; a LEFT JOIN returns all rows from the left table and matching rows from the right (or NULL when there is no match).",
    "A LEFT JOIN returns only matching rows; an INNER JOIN returns all rows from both tables.",
    "INNER JOIN and LEFT JOIN always return the same number of rows.",
    "LEFT JOIN drops unmatched rows from the left table.",
]

WINDOW_OPTIONS = [
    "The average salary within each department, repeated on every employee row in that department",
    "The overall average salary across the entire company on each row",
    "Only one average row per department",
    "The running total of salary ordered by employee_id",
]

STAR_OPTIONS = [
    "Fact tables store measurable events and connect to denormalized dimension tables that describe business entities",
    "Dimension tables store transactions and fact tables store only descriptive attributes",
    "Star schemas require every dimension to be fully normalized into snowflake tables",
    "Fact tables must never contain foreign keys to dimensions",
]

SCD_OPTIONS = [
    "Insert a new dimension row version and preserve history (often with effective dates or a current flag)",
    "Overwrite the existing attribute in place and discard the prior value",
    "Create a new fact table for every attribute change",
    "Delete the old dimension row so only the latest value remains",
]

ELT_OPTIONS = [
    "When a scalable cloud warehouse can perform transformations after raw data is loaded",
    "When source systems cannot be queried at all",
    "When you must transform data before any bytes are written to object storage",
    "When you want to avoid SQL entirely",
]

IDEMPOTENT_OPTIONS = [
    "Re-running the same load with the same inputs should not create duplicate or inconsistent results",
    "Idempotent jobs always run faster than non-idempotent jobs",
    "Idempotency means the pipeline never needs monitoring",
    "Idempotent loads can only run once and then must be deleted",
]

CHUNK_OPTIONS = [
    "Process the file in chunks (or stream rows) so only a portion is in memory at once",
    "Call df = pd.read_csv(path) and rely on swap space",
    "Load the entire file into a Python list of strings first",
    "Convert the CSV to nested JSON in memory before transforming",
]

SPARK_TX_OPTIONS = [
    "Transformations are lazy and build a plan; actions trigger computation and return results",
    "Transformations always execute immediately; actions only cache data",
    "Actions never touch the cluster; transformations always write to disk",
    "map is an action and count is a transformation",
]

SPARK_SHUFFLE_OPTIONS = [
    "groupByKey / reduceByKey style aggregations that regroup data by key across partitions",
    "map that doubles each value inside a partition",
    "filter that drops nulls without repartitioning",
    "coalesce to fewer partitions without a full redistribute (narrow coalesce)",
]

DAG_OPTIONS = [
    "A Directed Acyclic Graph of tasks that defines dependencies and schedule for a workflow",
    "A database engine optimized for analytical queries",
    "A message broker topic that stores events forever",
    "A UI dashboard used only for Spark monitoring",
]

BACKFILL_OPTIONS = [
    "Clear the failed task(s) and/or backfill the affected date interval so downstream work can complete correctly",
    "Delete the entire metastore so Airflow forgets the failure",
    "Disable scheduling permanently and run jobs only from laptops",
    "Convert all tasks to sensors that never time out",
]

KAFKA_OPTIONS = [
    "Partitions enable parallelism; consumers in the same group share work so each partition is processed by one consumer in the group",
    "All consumers in a group always read the exact same messages from every partition simultaneously",
    "Topics cannot have more than one partition",
    "Offsets are stored only on the producer and never committed by consumers",
]

DELIVERY_OPTIONS = [
    "At-least-once delivery",
    "Exactly-once delivery with no duplicates under any failure mode without additional design",
    "At-most-once delivery that never retries",
    "Best-effort UDP-style delivery with no offsets",
]

QUALITY_OPTIONS = [
    "Freshness, completeness, uniqueness, validity, and consistency",
    "Only CPU utilization and disk throughput",
    "Only model F1 score and AUC",
    "Only UI color contrast and font size",
]

DBT_TEST_OPTIONS = [
    "Duplicate business keys and missing required values in transformed models",
    "Slow Spark shuffles and executor memory pressure",
    "Kafka consumer lag only",
    "Airflow UI rendering bugs",
]


def _text(key, prompt="Answer:"):
    return {"key": key, "prompt": prompt, "input": "text"}


def _radio(key, options, prompt=""):
    return {"key": key, "prompt": prompt, "input": "radio", "options": list(options)}


def build_de_questions_payload():
    """Public GET payload — never includes expected answers."""
    sections = [
        {
            "name": "SQL Fundamentals",
            "categories": [
                {
                    "name": "Joins",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "Which statement best describes the difference between an INNER JOIN and a LEFT JOIN?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Joins", JOIN_OPTIONS)],
                },
                {
                    "name": "Window Functions",
                    "blocks": [
                        {
                            "type": "code",
                            "language": "sql",
                            "content": (
                                "SELECT employee_id, salary,\n"
                                "       AVG(salary) OVER (PARTITION BY department_id) AS dept_avg\n"
                                "FROM employees;"
                            ),
                        },
                        {
                            "type": "markdown",
                            "content": "What does the window function above compute for each row?",
                        },
                    ],
                    "questions": [_radio("answer_DE_Window_Functions", WINDOW_OPTIONS)],
                },
            ],
        },
        {
            "name": "Data Modeling & Warehousing",
            "categories": [
                {
                    "name": "Star Schema",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "In dimensional modeling, which statement correctly describes a star schema?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Star_Schema", STAR_OPTIONS)],
                },
                {
                    "name": "Slowly Changing Dimensions",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "What does a Type 2 slowly changing dimension (SCD Type 2) typically do when an attribute changes?",
                        }
                    ],
                    "questions": [_radio("answer_DE_SCD_Type2", SCD_OPTIONS)],
                },
            ],
        },
        {
            "name": "ETL / ELT Pipelines",
            "categories": [
                {
                    "name": "ETL vs ELT",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "When is ELT generally preferred over classic ETL?",
                        }
                    ],
                    "questions": [_radio("answer_DE_ELT", ELT_OPTIONS)],
                },
                {
                    "name": "Idempotent Loads",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "Why should pipeline loads be idempotent?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Idempotent", IDEMPOTENT_OPTIONS)],
                },
            ],
        },
        {
            "name": "Python for Data Engineering",
            "categories": [
                {
                    "name": "Pandas Aggregation",
                    "blocks": [
                        {
                            "type": "code",
                            "language": "python",
                            "content": (
                                "import pandas as pd\n\n"
                                "df = pd.DataFrame({\n"
                                '    "region": ["East", "West", "East", "West", "East"],\n'
                                '    "orders": [10, 7, 5, 3, 8],\n'
                                "})\n"
                                'print(int(df.groupby("region")["orders"].sum().loc["East"]))'
                            ),
                        }
                    ],
                    "questions": [_text("answer_DE_Pandas_Aggregation", "Terminal Output:")],
                },
                {
                    "name": "Chunked File Processing",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": (
                                "You need to transform a multi-GB CSV on a machine with limited RAM. "
                                "Which approach is most appropriate?"
                            ),
                        }
                    ],
                    "questions": [_radio("answer_DE_Chunked_IO", CHUNK_OPTIONS)],
                },
            ],
        },
        {
            "name": "Apache Spark",
            "categories": [
                {
                    "name": "Transformations vs Actions",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "In Apache Spark, which statement is accurate?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Spark_Lazy", SPARK_TX_OPTIONS)],
                },
                {
                    "name": "Shuffles",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "Which Spark operation is most likely to cause a wide transformation (shuffle)?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Spark_Shuffle", SPARK_SHUFFLE_OPTIONS)],
                },
            ],
        },
        {
            "name": "Orchestration (Airflow)",
            "categories": [
                {
                    "name": "DAGs",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "In Apache Airflow, what is a DAG?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Airflow_DAG", DAG_OPTIONS)],
                },
                {
                    "name": "Retries and Backfills",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": (
                                "A nightly Airflow DAG failed halfway through. After you fix the bug, "
                                "what is a common next step?"
                            ),
                        }
                    ],
                    "questions": [_radio("answer_DE_Airflow_Backfill", BACKFILL_OPTIONS)],
                },
            ],
        },
        {
            "name": "Streaming (Kafka)",
            "categories": [
                {
                    "name": "Topics and Consumer Groups",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": "In Apache Kafka, which statement is correct?",
                        }
                    ],
                    "questions": [_radio("answer_DE_Kafka_Partitions", KAFKA_OPTIONS)],
                },
                {
                    "name": "Delivery Guarantees",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": (
                                "Which delivery semantic means a consumer may process the same "
                                "message more than once after failures?"
                            ),
                        }
                    ],
                    "questions": [_radio("answer_DE_Kafka_Delivery", DELIVERY_OPTIONS)],
                },
            ],
        },
        {
            "name": "Data Quality & Observability",
            "categories": [
                {
                    "name": "Quality Dimensions",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": (
                                "Which set lists common data quality dimensions used in pipeline monitoring?"
                            ),
                        }
                    ],
                    "questions": [_radio("answer_DE_Quality_Dimensions", QUALITY_OPTIONS)],
                },
                {
                    "name": "Transformation Tests",
                    "blocks": [
                        {
                            "type": "markdown",
                            "content": (
                                "In modern warehouse workflows (e.g. dbt-style testing), what do "
                                "unique and not_null tests primarily protect against?"
                            ),
                        }
                    ],
                    "questions": [_radio("answer_DE_dbt_Tests", DBT_TEST_OPTIONS)],
                },
            ],
        },
    ]

    keys = []
    for section in sections:
        for category in section["categories"]:
            for question in category["questions"]:
                keys.append(question["key"])

    return {
        "assessment": ASSESSMENT_ID,
        "title": TITLE,
        "total_questions": len(keys),
        "sections": sections,
    }


def get_de_answer_key():
    return {
        "answer_DE_Joins": JOIN_OPTIONS[0],
        "answer_DE_Window_Functions": WINDOW_OPTIONS[0],
        "answer_DE_Star_Schema": STAR_OPTIONS[0],
        "answer_DE_SCD_Type2": SCD_OPTIONS[0],
        "answer_DE_ELT": ELT_OPTIONS[0],
        "answer_DE_Idempotent": IDEMPOTENT_OPTIONS[0],
        "answer_DE_Pandas_Aggregation": ["23"],
        "answer_DE_Chunked_IO": CHUNK_OPTIONS[0],
        "answer_DE_Spark_Lazy": SPARK_TX_OPTIONS[0],
        "answer_DE_Spark_Shuffle": SPARK_SHUFFLE_OPTIONS[0],
        "answer_DE_Airflow_DAG": DAG_OPTIONS[0],
        "answer_DE_Airflow_Backfill": BACKFILL_OPTIONS[0],
        "answer_DE_Kafka_Partitions": KAFKA_OPTIONS[0],
        "answer_DE_Kafka_Delivery": DELIVERY_OPTIONS[0],
        "answer_DE_Quality_Dimensions": QUALITY_OPTIONS[0],
        "answer_DE_dbt_Tests": DBT_TEST_OPTIONS[0],
    }


DE_TEXT_INPUT_QUESTIONS = ["answer_DE_Pandas_Aggregation"]

DE_QUESTION_KEYS = list(get_de_answer_key().keys())
