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