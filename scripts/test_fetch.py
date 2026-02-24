import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.esg_service import fetch_esg_data
from app.models.schemas import ESGStatus

def test_tickers():
  tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
  
  for symbol in tickers:
    print(f"\n--- Testing {symbol} ---")
    result = fetch_esg_data(symbol)
    
    if result.status == ESGStatus.SUCCESS:
      print(f"Scores: {result.scores}")
    elif result.status == ESGStatus.NO_DATA:
      print(f"No ESG data found for this ticker: {symbol}")
    else:
      print(f"Error: {result.error_message}")


if __name__ == "__main__":
  test_tickers()