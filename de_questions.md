# Questions

Data Engineer Initial Assessment — basic and intermediate questions across
core data engineering topics. Two questions per topic.

## SQL Fundamentals

### Joins
```md
Which statement best describes the difference between an INNER JOIN and a LEFT JOIN?
```

An INNER JOIN returns only matching rows from both tables; a LEFT JOIN returns all rows from the left table and matching rows from the right (or NULL when there is no match).
A LEFT JOIN returns only matching rows; an INNER JOIN returns all rows from both tables.
INNER JOIN and LEFT JOIN always return the same number of rows.
LEFT JOIN drops unmatched rows from the left table.

### Window Functions
```sql
SELECT employee_id, salary,
       AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
FROM employees;
```
```md
What does the window function above compute for each row?
```

The average salary within each department, repeated on every employee row in that department
The overall average salary across the entire company on each row
Only one average row per department
The running total of salary ordered by employee_id

## Data Modeling & Warehousing

### Star Schema
```md
In dimensional modeling, which statement correctly describes a star schema?
```

Fact tables store measurable events and connect to denormalized dimension tables that describe business entities
Dimension tables store transactions and fact tables store only descriptive attributes
Star schemas require every dimension to be fully normalized into snowflake tables
Fact tables must never contain foreign keys to dimensions

### Slowly Changing Dimensions
```md
What does a Type 2 slowly changing dimension (SCD Type 2) typically do when an attribute changes?
```

Insert a new dimension row version and preserve history (often with effective dates or a current flag)
Overwrite the existing attribute in place and discard the prior value
Create a new fact table for every attribute change
Delete the old dimension row so only the latest value remains

## ETL / ELT Pipelines

### ETL vs ELT
```md
When is ELT generally preferred over classic ETL?
```

When a scalable cloud warehouse can perform transformations after raw data is loaded
When source systems cannot be queried at all
When you must transform data before any bytes are written to object storage
When you want to avoid SQL entirely

### Idempotent Loads
```md
Why should pipeline loads be idempotent?
```

Re-running the same load with the same inputs should not create duplicate or inconsistent results
Idempotent jobs always run faster than non-idempotent jobs
Idempotency means the pipeline never needs monitoring
Idempotent loads can only run once and then must be deleted

## Python for Data Engineering

### Pandas Aggregation
```python
import pandas as pd

df = pd.DataFrame({
    "region": ["East", "West", "East", "West", "East"],
    "orders": [10, 7, 5, 3, 8],
})
print(int(df.groupby("region")["orders"].sum().loc["East"]))
```

### Chunked File Processing
```md
You need to transform a multi-GB CSV on a machine with limited RAM. Which approach is most appropriate?
```

Process the file in chunks (or stream rows) so only a portion is in memory at once
Call df = pd.read_csv(path) and rely on swap space
Load the entire file into a Python list of strings first
Convert the CSV to nested JSON in memory before transforming

## Apache Spark

### Transformations vs Actions
```md
In Apache Spark, which statement is accurate?
```

Transformations are lazy and build a plan; actions trigger computation and return results
Transformations always execute immediately; actions only cache data
Actions never touch the cluster; transformations always write to disk
map is an action and count is a transformation

### Shuffles
```md
Which Spark operation is most likely to cause a wide transformation (shuffle)?
```

groupByKey / reduceByKey style aggregations that regroup data by key across partitions
map that doubles each value inside a partition
filter that drops nulls without repartitioning
coalesce to fewer partitions without a full redistribute (narrow coalesce)

## Orchestration (Airflow)

### DAGs
```md
In Apache Airflow, what is a DAG?
```

A Directed Acyclic Graph of tasks that defines dependencies and schedule for a workflow
A database engine optimized for analytical queries
A message broker topic that stores events forever
A UI dashboard used only for Spark monitoring

### Retries and Backfills
```md
A nightly Airflow DAG failed halfway through. After you fix the bug, what is a common next step?
```

Clear the failed task(s) and/or backfill the affected date interval so downstream work can complete correctly
Delete the entire metastore so Airflow forgets the failure
Disable scheduling permanently and run jobs only from laptops
Convert all tasks to sensors that never time out

## Streaming (Kafka)

### Topics and Consumer Groups
```md
In Apache Kafka, which statement is correct?
```

Partitions enable parallelism; consumers in the same group share work so each partition is processed by one consumer in the group
All consumers in a group always read the exact same messages from every partition simultaneously
Topics cannot have more than one partition
Offsets are stored only on the producer and never committed by consumers

### Delivery Guarantees
```md
Which delivery semantic means a consumer may process the same message more than once after failures?
```

At-least-once delivery
Exactly-once delivery with no duplicates under any failure mode without additional design
At-most-once delivery that never retries
Best-effort UDP-style delivery with no offsets

## Data Quality & Observability

### Quality Dimensions
```md
Which set lists common data quality dimensions used in pipeline monitoring?
```

Freshness, completeness, uniqueness, validity, and consistency
Only CPU utilization and disk throughput
Only model F1 score and AUC
Only UI color contrast and font size

### Transformation Tests
```md
In modern warehouse workflows (e.g. dbt-style testing), what do unique and not_null tests primarily protect against?
```

Duplicate business keys and missing required values in transformed models
Slow Spark shuffles and executor memory pressure
Kafka consumer lag only
Airflow UI rendering bugs

# Answer Key

## SQL Fundamentals
1. Joins: "An INNER JOIN returns only matching rows from both tables; a LEFT JOIN returns all rows from the left table and matching rows from the right (or NULL when there is no match)."
2. Window Functions: "The average salary within each department, repeated on every employee row in that department"

## Data Modeling & Warehousing
3. Star Schema: "Fact tables store measurable events and connect to denormalized dimension tables that describe business entities"
4. Slowly Changing Dimensions: "Insert a new dimension row version and preserve history (often with effective dates or a current flag)"

## ETL / ELT Pipelines
5. ETL vs ELT: "When a scalable cloud warehouse can perform transformations after raw data is loaded"
6. Idempotent Loads: "Re-running the same load with the same inputs should not create duplicate or inconsistent results"

## Python for Data Engineering
7. Pandas Aggregation: 23
8. Chunked File Processing: "Process the file in chunks (or stream rows) so only a portion is in memory at once"

## Apache Spark
9. Transformations vs Actions: "Transformations are lazy and build a plan; actions trigger computation and return results"
10. Shuffles: "groupByKey / reduceByKey style aggregations that regroup data by key across partitions"

## Orchestration (Airflow)
11. DAGs: "A Directed Acyclic Graph of tasks that defines dependencies and schedule for a workflow"
12. Retries and Backfills: "Clear the failed task(s) and/or backfill the affected date interval so downstream work can complete correctly"

## Streaming (Kafka)
13. Topics and Consumer Groups: "Partitions enable parallelism; consumers in the same group share work so each partition is processed by one consumer in the group"
14. Delivery Guarantees: "At-least-once delivery"

## Data Quality & Observability
15. Quality Dimensions: "Freshness, completeness, uniqueness, validity, and consistency"
16. Transformation Tests: "Duplicate business keys and missing required values in transformed models"
