from tools.decorator_tool import tool


@tool
def multiple(a: int, b: int) -> int:
    """Multiple two integer"""
    return a * b


@tool
def divide(a: int, b: int) -> int:
    """Divide two integer"""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a // b


@tool
def add(a: int, b: int) -> int:
    """Add two integer"""
    return a + b


@tool
def sub(a: int, b: int) -> int:
    """Subtraction two integer"""
    return a - b
