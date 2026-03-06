import sys
import os
import random
from decimal import Decimal

# Add the project root to sys.path so we can import from 'app'
sys.path.append(os.getcwd())

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func, text
from app.core.database import SessionLocal
from app.models.models import User, Account, Ticker, ESGRating, PortfolioHolding, InvestmentRule

def seed_db():
    # This creates the tables if they don't exist (though Alembic should have handled this)
    # Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Tickers
        print("Seeding Tickers...")
        ticker_data = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corp."},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "name": "Tesla, Inc."},
        ]
        ticker_stmt = insert(Ticker).values(ticker_data)
        ticker_stmt = ticker_stmt.on_conflict_do_nothing(index_elements=["symbol"])
        db.execute(ticker_stmt)

        # Retrieve all ticker symbols from DB
        ticker_symbols = db.execute(select(Ticker.symbol)).scalars().all()

        # 2. Seed ESG Ratings (Randomized scores)
        print(f"Seeding Randomized ESG Ratings for {len(ticker_symbols)} tickers...")
        rating_data = []
        for symbol in ticker_symbols:
            # For the demo, we make AAPL a "Superstar" so the rebalancer has a target
            if symbol == "AAPL":
                carbon = 100
                labor = 100
            else:
                carbon = random.randint(0, 100)
                labor = random.randint(0, 100)
                
            rating_data.append({
                "ticker_symbol": symbol,
                "carbon_score": carbon,
                "labor_score": labor
            })
        
        # Using on_conflict_do_nothing since ticker is now unique
        # We use a custom upsert here to ensure the scores actually update if we re-run
        stmt = insert(ESGRating).values(rating_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker_symbol"],
            set_={
                "carbon_score": stmt.excluded.carbon_score,
                "labor_score": stmt.excluded.labor_score
            }
        )
        db.execute(stmt)

        # --- CLEANUP (Ensures a fresh start for the demo) ---
        print("Cleaning up stale test data...")
        # Delete by dependency order:
        # 1. Clear rules/holdings for any existing test accounts
        db.execute(text("""
            DELETE FROM investment_rule 
            WHERE account_id IN (SELECT id FROM accounts WHERE name = 'Impact Portfolio')
        """))
        db.execute(text("""
            DELETE FROM portfolio_holding 
            WHERE account_id IN (SELECT id FROM accounts WHERE name = 'Impact Portfolio')
        """))
        # 2. Clear the accounts
        db.execute(text("DELETE FROM accounts WHERE name = 'Impact Portfolio'"))
        # 3. Clear the test user
        db.execute(text("DELETE FROM users WHERE username = 'esg_investor'"))
        db.commit()

        # 3. Seed Test User & Account
        print("Creating Test User...")
        user_stmt = (
            insert(User)
            .values(
                id=1,
                username="esg_investor",
                email="investor@greenledger.com",
                password="hashed_password_placeholder"
            )
            .on_conflict_do_nothing(index_elements=["id"])
            .returning(User.id)
        )
        user_result = db.execute(user_stmt).fetchone()
        user_id = user_result[0] if user_result else 1
        print(f"User ID: {user_id}")

        account_stmt = (
            insert(Account)
            .values(
                id=1,
                name="Impact Portfolio",
                user_id=user_id,
                balance=Decimal("10000.00")
            )
            .on_conflict_do_nothing(index_elements=["id"])
            .returning(Account.id)
        )
        account_result = db.execute(account_stmt).fetchone()
        account_id = account_result[0] if account_result else 1

        print(f"Account ID: {account_id}")

        # 4. Seed Investment Rule
        print("Setting Investment Rules...")
        db.execute(
            insert(InvestmentRule).values({
                "id": 1,
                "account_id": account_id,
                "min_carbon_score": 70,
                "min_labor_score": 70
            }).on_conflict_do_nothing(index_elements=["id"])
        )

        # 5. Seed Initial Holdings
        print("Placing Initial Holdings...")
        holdings_data = [
            {"id": 1, "account_id": account_id, "ticker": "AMZN", "amount": Decimal(random.randint(50, 1000))},
            {"id": 2, "account_id": account_id, "ticker": "MSFT", "amount": Decimal(random.randint(50, 1000))},
        ]
        db.execute(insert(PortfolioHolding).values(holdings_data).on_conflict_do_nothing(index_elements=["id"]))
        
        db.commit()
        print("Database Seeded Successfully with Randomized Data!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
