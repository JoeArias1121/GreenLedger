from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class PortfolioRule(BaseModel):
  ticker: str
  min_carbon_score: int = Field(ge=0, le=100)
  min_labor_score: int = Field(ge=0, le=100)

class ESGStatus(Enum):
  SUCCESS = "success"
  NO_DATA = "no_data"
  ERROR = "error"

class ESGResult(BaseModel):
  status: ESGStatus
  scores: Optional[dict[str, int]] = None
  error_message: Optional[str] = None

