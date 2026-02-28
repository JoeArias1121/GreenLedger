from app.models.schemas import ESGResult, ESGStatus

# We'll use these values to test our rebalancing logic later
LOCAL_ESG_FEED = {
    "AAPL": {"carbon_score": 85, "labor_score": 90},
    "MSFT": {"carbon_score": 92, "labor_score": 88},
    "GOOGL": {"carbon_score": 78, "labor_score": 85},
    "AMZN": {"carbon_score": 45, "labor_score": 60},  # Low scores to trigger a 'SELL' event
    "TSLA": {"carbon_score": 95, "labor_score": 40},  # High carbon, low labor
}


def fetch_esg_data(ticker_symbol: str) -> ESGResult:

  if ticker_symbol not in LOCAL_ESG_FEED:
    return ESGResult(
      status=ESGStatus.NO_DATA,
      error_message=f"Ticker {ticker_symbol} not found in local ESG feed"
    )

  data = LOCAL_ESG_FEED[ticker_symbol]
  return ESGResult(
    status=ESGStatus.SUCCESS,
    scores=data
  )
  """
  for when api is available
  
  try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if not data:
      return ESGResult(
        status=ESGStatus.NO_DATA,
        error_message=f"No FMP data found for {ticker_symbol}"
      )

    latest = data[0]
    print("latest", latest)
    
    scores = {
      "carbon_score": int(latest.get("environmentalScore", 0)),
      "labor_score": int(latest.get("socialScore", 0))
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
  """

