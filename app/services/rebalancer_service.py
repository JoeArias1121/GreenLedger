from decimal import Decimal
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, delete, insert, func
from app.models.models import Account, PortfolioHolding, InvestmentRule, ESGRating, Ticker
import logging

logger = logging.getLogger(__name__)

class RebalancerService:
    def __init__(self, db: Session):
        self.db = db

    def rebalance_account(self, account_id: int):
        """
        The core rebalancing loop for a single account.
        Follows the Scan-Decide-Execute pattern.
        """
        try:
            # --- PHASE 1: SCAN ---
            # We fetch account and its rules together using joinedload
            account = self.db.execute(
                select(Account)
                .options(joinedload(Account.investment_rule))
                .where(Account.id == account_id)
            ).scalar_one_or_none()

            if not account:
                logger.error(f"Account {account_id} not found.")
                return

            rules = account.investment_rule

            if not rules:
                logger.info(f"No investment rules found for account {account_id}. Skipping.")
                return

            # Get current holdings and their scores
            # We use a join here to avoid "N+1" query problems
            holdings_with_scores = self.db.execute(
                select(PortfolioHolding, ESGRating)
                .join(ESGRating, PortfolioHolding.ticker == ESGRating.ticker_symbol)
                .where(PortfolioHolding.account_id == account_id)
            ).all()

            # --- PHASE 2: DECIDE ---
            non_compliant_holdings = []
            total_liquidation_value = Decimal("0.00")

            for holding, rating in holdings_with_scores:
                is_compliant = (
                    rating.carbon_score >= rules.min_carbon_score and
                    rating.labor_score >= rules.min_labor_score
                )

                if not is_compliant:
                    logger.info(f"VIOLATION: {holding.ticker} failed rules (C:{rating.carbon_score}/{rules.min_carbon_score}, L:{rating.labor_score}/{rules.min_labor_score})")
                    non_compliant_holdings.append(holding)
                    total_liquidation_value += holding.amount

            if not non_compliant_holdings:
                logger.info(f"Account {account_id} is already 100% compliant.")
                return

            # Find the best compliant stocks to buy as replacements
            # We pick the highest-rated stocks that the user doesn't already own
            current_tickers = [h.ticker for h, r in holdings_with_scores]
            
            replacement_candidates = self.db.execute(
                select(ESGRating)
                .where(ESGRating.ticker_symbol.notin_(current_tickers))
                .where(ESGRating.carbon_score >= rules.min_carbon_score)
                .where(ESGRating.labor_score >= rules.min_labor_score)
                .order_by((ESGRating.carbon_score + ESGRating.labor_score).desc())
                .limit(1) # For simplicity, we re-invest everything into the top pick
            ).scalar_one_or_none()

            if not replacement_candidates:
                logger.warning("No suitable replacement stocks found in the universe!")
                return

            # --- PHASE 3: EXECUTE (Atomic Transaction) ---
            logger.info(f"Liquidating {len(non_compliant_holdings)} stocks for {total_liquidation_value}...")
            
            with self.db.begin_nested(): # Using a sub-transaction for safety
                # 1. Sell non-compliant
                for holding in non_compliant_holdings:
                    self.db.delete(holding)
                
                # 2. Update Cash Balance
                account.balance += total_liquidation_value
                
                # 3. Buy Replacement
                new_holding = PortfolioHolding(
                    account_id=account.id,
                    ticker=replacement_candidates.ticker_symbol,
                    amount=total_liquidation_value
                )
                self.db.add(new_holding)
                
            self.db.commit()
            logger.info(f"Successfully rebalanced Account {account_id}. Replaced with {replacement_candidates.ticker_symbol}.")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Rebalance failed for Account {account_id}: {str(e)}")
            raise e
