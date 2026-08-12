class CalculatorService:

    def add_numbers(
        self,
        a: float,
        b: float,
    ) -> dict:
        return {
            "result": a + b
        }

    def subtract_numbers(
        self,
        a: float,
        b: float,
    ) -> dict:
        return {
            "result": a - b
        }

    def multiply_numbers(
        self,
        a: float,
        b: float,
    ) -> dict:
        return {
            "result": a * b
        }

    def divide_numbers(
        self,
        a: float,
        b: float,
    ) -> dict:

        if b == 0:
            return {
                "error": "Division by zero"
            }

        return {
            "result": a / b
        }