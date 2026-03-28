def add(a: int, b: int) -> int:
    return a + b


def multiply(a: float, b: float) -> float:
    return a * b


def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


def process_data(data: list, key: str = None) -> dict:
    if not data:
        return {"error": "empty data"}
    
    result = {"count": len(data), "items": data}
    if key:
        result["key"] = key
    return result


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


async def async_fetch(url: str) -> dict:
    return {"url": url, "status": 200}


class User:
    def __init__(self, name: str, age: int = 0):
        self.name = name
        self.age = age
        self._cache = {}
    
    def greet(self) -> str:
        return f"Hello, {self.name}!"
    
    @property
    def is_adult(self) -> bool:
        return self.age >= 18
    
    @property
    def info(self) -> dict:
        return {"name": self.name, "age": self.age}
    
    @info.setter
    def info(self, value: dict):
        self.name = value.get("name", self.name)
        self.age = value.get("age", self.age)


class Calculator:
    def __init__(self, precision: int = 2):
        self.precision = precision
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return round(result, self.precision)
    
    def subtract(self, a: float, b: float) -> float:
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return round(result, self.precision)
    
    def get_history(self) -> list:
        return self.history.copy()
