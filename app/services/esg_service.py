import yfinance as yf
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from app.models.schemas import ESGResult, ESGStatus


def fetch_esg_data(ticker_symbol: str) -> ESGResult:
  try:
    ticker = yf.Ticker(ticker_symbol)
    sus_data = ticker.get_sustainability()
    print(sus_data)

    if sus_data is None or sus_data.empty:
      return ESGResult(
        status=ESGStatus.NO_DATA,
        error_message=f"No ESG data found for {ticker_symbol}"
      )
    
    scores = {
      "carbon_score": int(sus_data["socialScore"][0]),
      "labor_score": int(sus_data["governanceScore"][0])
    }

    return ESGResult(
      status=ESGStatus.SUCCESS,
      scores=scores
    )
  except Exception as e:
    return ESGResult(
      status=ESGStatus.ERROR,
      error_message=str(e)
    )

