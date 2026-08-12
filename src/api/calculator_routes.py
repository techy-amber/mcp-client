from fastapi import APIRouter
from services.calculator_service import CalculatorService

router = APIRouter(
    prefix="/calculator",
    tags=["Calculator"],
)

calculator_service = CalculatorService()


@router.get("/add")
def add(a: float, b: float):
    return calculator_service.add_numbers(a, b)