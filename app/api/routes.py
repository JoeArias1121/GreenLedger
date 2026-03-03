from fastapi import APIRouter, FastAPI
from app.models.schemas import PortfolioRule
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


app = FastAPI()
router = APIRouter()

@router.post("/evaluate-rule/", tags=["Portfolio Rule"])
def evaluate_portfolio_rule(rule: PortfolioRule, db: Session = Depends(get_db)):
    print(f"Received rule for: {rule.ticker}")
    return {"status": "accepted", "message": f"Rule saved for {rule.ticker}."}


app.include_router(router)