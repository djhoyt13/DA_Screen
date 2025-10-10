
# Questions

## Python Basics

### Unpacking
```python
def split_str(s:str, x:int, y:int) -> str:
    return s[x:y]

print(split_str("Hello, World!", 7, 12))
```

### Loops
```python
nums = range(1, 5)
out = []
for n in nums:
    out.append(n * n)

print(out)
```

### Lambda functions
```python
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)
```

### Pydantic / Validation
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int | None = None

sample_data = {
    "name": "John Doe",
    "email": 1234
}

try:
    user = User(**sample_data)
    print(user.name)
except:
    print("Data is not valid")
```

## Data Manipulation

### NumPy & Pandas
```python
import numpy as np
import pandas as pd

# Given DataFrame
data = {
    'product': ['apple', 'banana', 'apple', 'banana', 'cherry'],
    'units_sold': [10, 5, 8, 7, 3],
    'price_per_unit': [1.0, 0.5, 1.0, 0.6, 2.0]
}
df = pd.DataFrame(data)

df['revenue'] = np.multiply(df['units_sold'], df['price_per_unit'])

total_revenue_per_product = df.groupby('product')['revenue'].sum()

print(total_revenue_per_product.apple)
```

### Exploratory Data Analysis
```txt
   ID      Car Type
0   1         Sedan
1   2           SUV
2   3  Convertible
3   4         Sedan
4   5  Convertible
5   6           SUV
```

Given the above dataset, what is the most appropriate form of encoding?

Label Encoding
Ordinal Encoding
Hash Encoding
One-Hot Encoding


## Python Intermediate Topics

### ThreadPool
```python
from concurrent.futures import ThreadPoolExecutor
import time
import threading

def worker(n):
    print(f"Thread {n} starting (thread id: {threading.get_ident()})")
    time.sleep(1)
    print(f"Thread {n} finished")

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(worker, range(1, 5))
```
How many threads are running concurrently?

### Asyncio (I/O-bound)
```python
import asyncio

async def say_hello():
    print("Hello")
    await asyncio.sleep(1)
    print("world!")

async def main():
    await asyncio.gather(
        say_hello(),
        say_hello()
    )

asyncio.run(main())
```
"Hello world!, Hello world!"
"world! Hello, world! Hello"
"Hello, Hello, world!, world!"
"world!, world, Hello, Hello"

## Testing and Environment Setup

### pytest
```python
def is_even(n):
    """Return True if n is even, otherwise False."""
    return n % 2 == 0

def test_is_even():
    assert is_even(4) is True
    assert is_even(5) is False
```
What will the output of `pytest --cov=. test_questions.py` be?

1 passed
1 failed


### Virtual ENV
```shell
$ python3 -m venv .venv

# what command would you use to activate the above virtual enviornment (Linux or Windows)
```

## Containerization and Deployment

### Docker
```python
# docker-compose.yml
version: '3.9'

services:
  web:
    build: ./web
    ports:
      - "8000:8000"
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: mysecret
      POSTGRES_DB: exampledb
```

Given the docker-compose.yml above, answer the following:

1. What command builds all services defined in the file?

2. What command starts all services in the background?

3. What command stops just the 'web' service (but leaves 'db' running)?

4. What command removes the stopped 'web' service container only (not the running db)?

## Machine Learning Concepts

### Supervised & Unsupervised Learning
You are consulting for a company that wants to understand its customer base better and predict customer spending based on historical data.
What is the most approprate machine learning approach for each of the below questions?
A. Predicting the future spending of customers based on their past behavior and known attributes such as age, location, and income.
    'Supervised'
    'Unsupervised'
B. Grouping customers into distinct segments based on purchasing patterns to identify different types of shoppers.
    'Supervised'
    'Unsupervised'

## Advanced Topics

### PyTorch
```python
import torch
import torch.nn as nn

# Given the following code:

x = torch.randn(2, 3)

model = nn.Sequential(
    nn.Linear(3, 4),
    nn.ReLU(),
    nn.Linear(4, 1)
)
```
1. What is the shape of the tensor x?
    (3, 4)
    (4, 1)
    (2, 3)
    (3, 2)
2. How many layers (including activation) does 'model' have?


### Probability
1. A fair sided (6 sides) die is rolled twice, what is the probability of rolling a 6 on both throws (rounded to 4 decimals)? 

2. A variable has mean 50 and standard deviation 10. What is the range within 2 standard deviations of each side of the mean? 
    [30, 70]
    [50, 70]
    [30, 50]
    [8, 12]
## Systems and Protocols

### How Agents Use Tools, MCP, A2A, and Other Protocols
Which of the following statements accurately describes a key difference between A2A (Agent-to-Agent) communication and MCP (Message Control Protocol)?

A2A communication involves direct interaction between software agents for data sharing, while MCP focuses on ensuring reliable message delivery and error handling.
MCP is used solely for agent negotiation, while A2A controls the overall system architecture.
A2A is focused on message security, whereas MCP is used for task coordination between agents.
A2A handles database management, and MCP is used for executing complex algorithms.

### Data Visualization
You are given a dataset containing the following columns:
* Product Category: A list of product types (laptops, smartphones, tablets)
* Monthly Sales: The number of units sold each month
* Region: The geographic region of the sales (North, South, East, West)
* Customer Satisfaction: A score from 1 to 10

Which of the following visualization methods would be most appropriate for each type of analysis, and why?

1. Compare the average monthly sales for each product category.
    'Bar Chart'
    'Histogram'
    'Line Chart'

2. Display the distribution of customer satisfaction scores.
    'Bar Chart'
    'Histogram'
    'Line Chart'

3. Show the trend of sales over time for each region.
    'Bar Chart'
    'Histogram'
    'Line Chart'


# Answer Key

## Python Basics
1. Unpacking: "World"
2. Loops: [1, 4, 9, 16]
3. Lambda_Function: [11, 22, 33]
4. Pydantic_Validation: "Data is not valid"

## Data Manipulation
5. Pandas: 18.0
6. EDA: "One-Hot Encoding"

## Python Intermediate Topics
6. ThreadPool: 4
7. Asyncio: "Hello, Hello, world!, world!"

## Testing and Environment Setup
8. pytest: "1 passed"
9. Virtual_ENV: "source .venv/bin/activate" or ".venv\Scripts\activate"

## Containerization and Deployment
10. Docker_Build: "docker-compose build"
11. Docker_Start: "docker-compose up -d"
12. Docker_Stop: "docker-compose stop web"
13. Docker_Remove: "docker-compose rm -f web"

## Machine Learning Concepts
14. Customer_spending: "Supervised"
15. Grouping_customers: "Unsupervised"

## Advanced Topics
16. PyTorch: "(2, 3)"
17. PyTorch: Number of Layers in Model: 3

## Probability
18. rolling_7: 0.0278 or .0278
19. 2_SD_of_mean: [30, 70]

## Systems and Protocols
20. A2A_vs_MCP: "A2A communication involves direct interaction between software agents for data sharing, while MCP focuses on ensuring reliable message delivery and error handling."

## Data Visualization
21. Compare_Sales: "Bar Chart"
21. Satisfaction_Scores: "Histogram"
23. Sales_Trend: "Line Chart"
