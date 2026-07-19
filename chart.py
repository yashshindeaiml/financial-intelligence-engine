import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


def get_stock_data(symbol, period="6mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)

    if df is None or df.empty:
        return None

    df = df.dropna()
    return df


def add_indicators(df):
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    # RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df


def generate_chart(df, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA50"],
        line=dict(color="blue"),
        name="MA50"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA200"],
        line=dict(color="orange"),
        name="MA200"
    ))

    fig.update_layout(
        title=f"{symbol} Stock Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    return fig