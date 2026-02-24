from fastapi import APIRouter, FastAPI
from app.models.schemas import PortfolioRule

app = FastAPI()
router = APIRouter()

@router.post("/evaluate-rule/", tags=["Portfolio Rule"])
def evaluate_portfolio_rule(rule: PortfolioRule):
    print(f"Received rule for: {rule.ticker}")
    return {"status": "accepted", "message": f"Rule saved for {rule.ticker}."}


app.include_router(router)