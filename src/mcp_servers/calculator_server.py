from mcp.server import MCPServer

mcp = MCPServer("Calculator Server")


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def subtract_numbers(a: float, b: float) -> float:
    """Subtract the second number from the first number."""
    return a - b


@mcp.tool()
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@mcp.tool()
def divide_numbers(a: float, b: float) -> float:
    """Divide the first number by the second number."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a / b