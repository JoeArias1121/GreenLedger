from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, text, ForeignKey, Integer, DateTime, Numeric, func
from datetime import datetime
from app.core.database import Base

class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
  email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
  password: Mapped[str] = mapped_column(String(120), nullable=False)
  accounts: Mapped[list["Account"]] = relationship(foreign_keys="Account.user_id")


class Account(Base):
  __tablename__ = "accounts"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default=text("0.00"), nullable=False)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)


class Ticker(Base):
  __tablename__ = "ticker"

  symbol: Mapped[str] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class PortfolioHolding(Base):
  __tablename__ = "portfolio_holding"

  id: Mapped[int] = mapped_column(primary_key=True)
  ticker: Mapped[str] = mapped_column(ForeignKey("ticker.symbol"), nullable=False)
  account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
  quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class InvestmentRule(Base):
  __tablename__ = "investment_rule"

  id: Mapped[int] = mapped_column(primary_key=True)
  account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
  min_carbon_score: Mapped[int] = mapped_column(Integer, nullable=False)
  min_labor_score: Mapped[int] = mapped_column(Integer, nullable=False)


class ESGRating(Base):
  __tablename__ = "esg_rating"

  id: Mapped[int] = mapped_column(primary_key=True)
  ticker: Mapped[str] = mapped_column(String(5), ForeignKey("ticker.symbol"), nullable=False)
  carbon_score: Mapped[int] = mapped_column(Integer, nullable=False)
  labor_score: Mapped[int] = mapped_column(Integer, nullable=False)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
  


