import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
# Import the existing multi-key runner from your llm_manager
from llm_manager import call_model_with_keys


class StockAgent:
    def __init__(self):
        # No longer pulling an isolated OpenAI env key here.
        # We rely on llm_manager's key rotation array instead.
        pass

    # -------------------------------
    # FETCH STOCK DATA
    # -------------------------------
    def fetch_stock_data(self, symbol: str, period="6mo", interval="1d"):
        try:
            # Force multi_level_index to False to keep column headers perfectly flat
            df = yf.download(symbol, period=period, interval=interval, multi_level_index=False)

            if df.empty:
                return None, "No data found for this stock."

            df = df.dropna()
            return df, None

        except Exception as e:
            return None, str(e)

    # -------------------------------
    # ADD INDICATORS
    # -------------------------------
    def add_indicators(self, df: pd.DataFrame):
        if len(df) < 20:
            return None, "Not enough data for indicators."

        df = df.copy()
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["MA200"] = df["Close"].rolling(window=200).mean()
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        return df, None

    # -------------------------------
    # GENERATE PLOTLY CHART
    # -------------------------------
    def generate_chart(self, df, symbol):
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        ))

        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], line=dict(color="blue"), name="MA50"))
        fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], line=dict(color="orange"), name="MA200"))

        fig.update_layout(
            title=f"{symbol} Stock Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark"
        )
        return fig

    # -------------------------------
    # LLM ANALYSIS (FIXED)
    # -------------------------------
    def analyze_with_llm(self, symbol, latest_data):
        try:
            price = float(latest_data['Close'])
            rsi = float(latest_data['RSI']) if pd.notna(latest_data['RSI']) else "N/A"
            sma20 = float(latest_data['SMA_20']) if pd.notna(latest_data['SMA_20']) else "N/A"
            ema20 = float(latest_data['EMA_20']) if pd.notna(latest_data['EMA_20']) else "N/A"

            prompt = f"""
            You are a stock market AI analyst.

            Analyze the stock: {symbol}

            Latest Data:
            Price: {price:.2f}
            RSI: {rsi}
            SMA20: {sma20}
            EMA20: {ema20}

            Give:
            1. Trend (Bullish/Bearish/Sideways)
            2. Buy/Sell/Hold suggestion
            3. Short reasoning
            """

            # Route execution directly through your llm_manager API rotation pool
            # Defaults to your "qwen" configuration setup
            response_text = call_model_with_keys(prompt, model="qwen")

            if "❌ All API keys failed." in response_text:
                return None, response_text

            return response_text, None

        except Exception as e:
            return None, str(e)

    # -------------------------------
    # MAIN PIPELINE
    # -------------------------------
    def run(self, symbol: str):
        df, error = self.fetch_stock_data(symbol)
        if error:
            return None, f"Error Fetching: {error}"

        df, error = self.add_indicators(df)
        if error:
            return None, f"Error Indicators: {error}"

        latest = df.iloc[-1]

        analysis, error = self.analyze_with_llm(symbol, latest)
        if error:
            return None, f"Error Analysis: {error}"

        chart = self.generate_chart(df, symbol)
        return chart, analysis


# Global operational wrapper for app.py layout integration
agent_instance = StockAgent()


def agent_response(symbol: str):
    return agent_instance.run(symbol)