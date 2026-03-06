import sys
import os
from decimal import Decimal

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.services.rebalancer_service import RebalancerService
from app.models.models import Account, PortfolioHolding, ESGRating
from sqlalchemy import select

def test_rebalance():
    db = SessionLocal()
    try:
        # Find our test account
        account = db.execute(select(Account).where(Account.name == "Impact Portfolio")).scalar_one_or_none()
        if not account:
            print("Test account not found. Did you run seed_db.py?")
            return

        print(f"\n===== INITIAL STATE (Account: {account.id}) =====")
        print(f"Cash Balance: ${account.balance}")
        
        holdings = db.execute(select(PortfolioHolding).where(PortfolioHolding.account_id == account.id)).scalars().all()
        for h in holdings:
            rating = db.execute(select(ESGRating).where(ESGRating.ticker_symbol == h.ticker)).scalar_one_or_none()
            print(f"- {h.ticker}: ${h.amount} (Scores: Carbon {rating.carbon_score}, Labor {rating.labor_score})")

        # Run Rebalancer
        print("\n===== RUNNING REBALANCER =====")
        rebalancer = RebalancerService(db)
        rebalancer.rebalance_account(account.id)

        # Verify Final State
        db.expire_all() # Refresh from DB
        print("\n===== FINAL STATE =====")
        # Note: In our current seed, AMZN is usually low-rated and should be sold.
        
        holdings = db.execute(select(PortfolioHolding).where(PortfolioHolding.account_id == account.id)).scalars().all()
        for h in holdings:
            rating = db.execute(select(ESGRating).where(ESGRating.ticker_symbol == h.ticker)).scalar_one_or_none()
            print(f"- {h.ticker}: ${h.amount} (Scores: Carbon {rating.carbon_score}, Labor {rating.labor_score})")

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_rebalance()
