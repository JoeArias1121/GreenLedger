import random
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.models import User, Account, Ticker, ESGRating, PortfolioHolding, InvestmentRule
from decimal import Decimal

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
        rating_data = [
            {
                "ticker": symbol,
                "carbon_score": random.randint(0, 100),
                "labor_score": random.randint(0, 100)
            }
            for symbol in ticker_symbols
        ]
        
        # Using on_conflict_do_nothing since ticker is now unique
        rating_stmt = insert(ESGRating).values(rating_data)
        rating_stmt = rating_stmt.on_conflict_do_nothing(index_elements=["ticker"])
        db.execute(rating_stmt)

        # 3. Seed Test User & Account
        print("Creating Test User...")
        user_stmt = (
            insert(User)
            .values(
                username="esg_investor",
                email="investor@greenledger.com",
                password="hashed_password_placeholder"
            )
            .on_conflict_do_nothing(index_elements=["username"])
            .returning(User.id)
        )
        user_result = db.execute(user_stmt).fetchone()
        user_id = -1
        
        if not user_result:
            user_id = db.execute(select(User.id).where(User.username == "esg_investor")).scalar_or_none()
        else:
            user_id = user_result[0]

        print(f"User ID: {user_id}")

        if user_id == -1:
            raise Exception("User ID not found")

        account_stmt = (
            insert(Account)
            .values(
                name="Impact Portfolio",
                user_id=user_id,
                balance=Decimal("10000.00")
            )
            .on_conflict_do_nothing(index_elements=["id"])
            .returning(Account.id)
        )
        account_result = db.execute(account_stmt).fetchone()
        account_id = -1

        if not account_result:
            account_id = db.execute(select(Account.id).where(Account.user_id == user_id)).scalar_or_none()
        else:
            account_id = account_result[0]

        print(f"Account ID: {account_id}")

        if account_id == -1:
            raise Exception("Account ID not found")

        # 4. Seed Investment Rule
        print("Setting Investment Rules...")
        db.execute(
            insert(InvestmentRule).values({
                "account_id": account_id,
                "min_carbon_score": 70,
                "min_labor_score": 70
            }).on_conflict_do_nothing(index_elements=["id"])
        )


        # 5. Seed Initial Holdings
        print("Placing Initial Holdings...")
        holdings_data = [
            {"account_id": account_id, "ticker": "AMZN", "quantity": Decimal(random.randint(0, 1000))},
            {"account_id": account_id, "ticker": "MSFT", "quantity": Decimal(random.randint(0, 1000))},
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
