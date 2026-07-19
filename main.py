# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import database
import model
from agent import agent_instance
from llm_manager import enhance_response

app = FastAPI(title="QuantumEdge Core API")

# Allow all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically create the PostgreSQL tables if they don't exist
model.Base.metadata.create_all(bind=database.engine)


def extract_symbol(user_input: str) -> str:
    """Map natural language company names to stock ticker symbols."""
    query = user_input.lower()
    mapping = {
        "tesla": "TSLA",
        "apple": "AAPL",
        "amazon": "AMZN",
        "google": "GOOGL",
        "microsoft": "MSFT",
        "nvidia": "NVDA",
        "meta": "META",
    }
    for key, ticker in mapping.items():
        if key in query:
            return ticker
    # Fall back: treat the whole query as the ticker
    return query.upper().strip()


# Pydantic schema for validation
class AnalysisRequest(BaseModel):
    user_query: str


@app.get("/")
def root():
    return {"status": "QuantumEdge Core API is running"}


@app.post("/api/v1/analyze")
def run_market_analysis(payload: AnalysisRequest, db: Session = Depends(database.get_db)):
    symbol = extract_symbol(payload.user_query)

    # 1. Pipeline Execution via Agent
    df, error = agent_instance.fetch_stock_data(symbol)
    if error or df is None:
        raise HTTPException(status_code=400, detail=f"Data fetching error: {error}")

    df, error = agent_instance.add_indicators(df)
    if error or df is None:
        raise HTTPException(status_code=400, detail=f"Indicator error: {error}")

    latest = df.iloc[-1]

    analysis, error = agent_instance.analyze_with_llm(symbol, latest)
    if error:
        raise HTTPException(status_code=502, detail=f"LLM Node failure: {error}")

    final_text = enhance_response(payload.user_query, analysis)

    # 2. Database Persistence
    db_record = model.StockAnalysisRecord(
        symbol=symbol,
        price=float(latest["Close"]),
        rsi=float(latest["RSI"]) if "RSI" in latest else None,
        sma20=float(latest["SMA_20"]) if "SMA_20" in latest else None,
        ema20=float(latest["EMA_20"]) if "EMA_20" in latest else None,
        analysis_synopsis=final_text
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "symbol": symbol,
        "price": db_record.price,
        "analysis": final_text
    }


@app.get("/api/v1/history")
def get_history(db: Session = Depends(database.get_db)):
    return db.query(model.StockAnalysisRecord).order_by(
        model.StockAnalysisRecord.created_at.desc()
    ).limit(5).all()