### Python

1. Unpacking
```python
def split_str(s:str, x:int, y:int) -> str:
    return s[x:y]

print(split_str("Hello, World!", 7, 12))
```

2.Loops
```python
nums = range(1, 5)
out = []
for n in nums:
    out.append(n * n)

print(out)
```

3. Lambda functions
```python
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)
```

4. pydantic / validation
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
5. NumPy
6. Pandas
7. asyncio (I/O-bound)
8. ThreadPool
9. pytest
10. Virtual ENV
11. Docker
12. FastAPI basic
13. Scikit-learn
14. pytorch

### Probability
1. A fair sided (6 sides) die is rolled twice, what is the probability of rolling a 7 on both throws? 

2. A variable has mean 50 and standard deviation 10. What is the range within 2 standard deviations of each side of the mean? 

### Exploratory Data Analysis

### Data Visualization

### Supervised & Unsupervised Learning

### Building Agents with LLM

### How Agents Use Tools, MCP, A2A, and Other Protocols