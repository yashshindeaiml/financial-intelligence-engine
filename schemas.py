# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    user_query: str


class AnalysisResponse(BaseModel):
    symbol: str
    price: float
    analysis: str


class HistoryRecord(BaseModel):
    id: int
    symbol: str
    price: float
    rsi: Optional[float] = None
    sma20: Optional[float] = None
    ema20: Optional[float] = None
    analysis_synopsis: str
    created_at: datetime

    class Config:
        from_attributes = True
