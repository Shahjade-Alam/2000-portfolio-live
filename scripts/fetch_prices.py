import yfinance as yf
import json
import datetime
import logging
import os
import pandas as pd
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------- CORE HOLDINGS --------
CORE_TICKERS = [
    "MSFT", "AVGO", "V", "MA", "SPGI", "UNH", "COST", "AAPL", "GOOGL",
    "JNJ", "VIG", "GLDM", "SPMO", "SPLG", "VXUS", "AVUV",
    "SPYI", "QQQI", "IWMI", "TSPY", "TMGN"
]

# -------- SSGA SECTOR ETFs (from ssga.com) --------
# Source: https://www.ssga.com/us/en/individual/capabilities/equities/sector-investing/sector-and-industry-etfs
SECTOR_ETFS = [
    "XLC",   # Communication Services
    "XLY",   # Consumer Discretionary
    "XLP",   # Consumer Staples
    "XLE",   # Energy
    "XLF",   # Financials
    "XLV",   # Health Care
    "XLI",   # Industrials
    "XLB",   # Materials
    "XLRE",  # Real Estate
    "XLK",   # Technology
    "XLU",   # Utilities
    "XLSR",  # SSGA US Sector Rotation ETF (actively managed)
]

# Full list to fetch
TICKERS = CORE_TICKERS + SECTOR_ETFS

# -------- CATEGORIES --------
CATEGORIES = {
    # Core holdings
    'MSFT': 'Tech / AI', 'AVGO': 'Semiconductors', 'V': 'Financials', 'MA': 'Financials',
    'SPGI': 'Financials', 'UNH': 'Healthcare', 'COST': 'Consumer', 'AAPL': 'Tech / Hardware',
    'GOOGL': 'Tech / AI', 'JNJ': 'Healthcare', 'VIG': 'Dividend ETF', 'GLDM': 'Gold',
    'SPMO': 'Momentum ETF', 'SPLG': 'S&P 500 ETF', 'VXUS': 'Intl ETF', 'AVUV': 'Small Value',
    'SPYI': 'Income ETF', 'QQQI': 'Nasdaq Income', 'IWMI': 'Income ETF', 'TSPY': 'Income ETF',
    'TMGN': 'Income ETF',
    # SSGA Sector ETFs
    'XLC': 'Communication Services', 'XLY': 'Consumer Discretionary', 'XLP': 'Consumer Staples',
    'XLE': 'Energy', 'XLF': 'Financials', 'XLV': 'Health Care',
    'XLI': 'Industrials', 'XLB': 'Materials', 'XLRE': 'Real Estate',
    'XLK': 'Technology', 'XLU': 'Utilities', 'XLSR': 'Sector Rotation ETF'
}

# Friendly names for sector ETFs (from SSGA)
SECTOR_NAMES = {
    'XLC': 'Communication Services Select Sector SPDR',
    'XLY': 'Consumer Discretionary Select Sector SPDR',
    'XLP': 'Consumer Staples Select Sector SPDR',
    'XLE': 'Energy Select Sector SPDR',
    'XLF': 'Financial Select Sector SPDR',
    'XLV': 'Health Care Select Sector SPDR',
    'XLI': 'Industrial Select Sector SPDR',
    'XLB': 'Materials Select Sector SPDR',
    'XLRE': 'Real Estate Select Sector SPDR',
    'XLK': 'Technology Select Sector SPDR',
    'XLU': 'Utilities Select Sector SPDR',
    'XLSR': 'SSGA US Sector Rotation ETF'
}

def load_previous_data() -> Dict[str, Any]:
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def fetch_ticker_info(ticker: str) -> Dict[str, Any]:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        # Use friendly name for sector ETFs, otherwise fetch from Yahoo
        if ticker in SECTOR_NAMES:
            name = SECTOR_NAMES[ticker]
        else:
            name = info.get('shortName', ticker)
        sector = info.get('sector', '')
        category = CATEGORIES.get(ticker, sector if sector else 'Equity')
        return {'name': name, 'category': category}
    except Exception as e:
        logging.warning(f"Could not fetch info for {ticker}: {e}")
        return {'name': SECTOR_NAMES.get(ticker, ticker), 'category': CATEGORIES.get(ticker, 'Unknown')}

def get_sector_rotation_signal(ticker: str, df: pd.DataFrame, current_price: float) -> Dict[str, Any]:
    """Calculate momentum and trend, then assign a recommendation for sector ETFs."""
    signal = {
        "momentum_20d": None,
        "sma_50": None,
        "trend": "Neutral",
        "recommendation": "Hold",
        "reason": "Insufficient data"
    }
    try:
        closes = df['Close'].dropna()
        if len(closes) < 30:
            return signal

        # 20-day momentum
        price_20d_ago = closes.iloc[-21] if len(closes) >= 21 else closes.iloc[0]
        momentum = ((current_price - price_20d_ago) / price_20d_ago) * 100

        # 50-day SMA
        sma_50 = closes.rolling(50).mean().iloc[-1]
        trend = "Bullish" if current_price > sma_50 else "Bearish" if current_price < sma_50 else "Neutral"

        signal["momentum_20d"] = round(momentum, 2)
        signal["sma_50"] = round(sma_50, 2)
        signal["trend"] = trend

    except Exception as e:
        logging.warning(f"Sector signal error for {ticker}: {e}")
    return signal

def fetch_prices() -> Dict[str, Any]:
    previous = load_previous_data()
    portfolio = {}
    logging.info(f"Downloading 60 days of data for {len(TICKERS)} tickers...")
    data = yf.download(TICKERS, period="60d", group_by='ticker', progress=False)

    # 1. Fetch basic price & change for all tickers
    for ticker in TICKERS:
        try:
            if len(TICKERS) > 1:
                df = data[ticker]
            else:
                df = data

            if df.empty:
                logging.warning(f"No data for {ticker} – keeping previous if exists")
                if ticker in previous and ticker != 'last_updated':
                    portfolio[ticker] = {k: v for k, v in previous[ticker].items() if k not in ['name','category']}
                else:
                    portfolio[ticker] = {"price": None, "change": None, "prev_close": None}
                continue

            closes = df['Close'].dropna()
            if len(closes) < 2:
                current_price = float(closes.iloc[-1])
                prev_close = current_price
                change_pct = 0.0
            else:
                current_price = float(closes.iloc[-1])
                prev_close = float(closes.iloc[-2])
                change_pct = ((current_price - prev_close) / prev_close) * 100

            portfolio[ticker] = {
                "price": round(current_price, 2),
                "change": round(change_pct, 2),
                "prev_close": round(prev_close, 2)
            }

            # If it's a sector ETF, add rotation metrics
            if ticker in SECTOR_ETFS:
                sector_signal = get_sector_rotation_signal(ticker, df, current_price)
                portfolio[ticker].update(sector_signal)

        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")
            if ticker in previous and ticker != 'last_updated':
                portfolio[ticker] = {k: v for k, v in previous[ticker].items() if k not in ['name','category']}
            else:
                portfolio[ticker] = {"price": None, "change": None, "prev_close": None}

    # 2. Enrich with name / category
    for ticker in TICKERS:
        info = fetch_ticker_info(ticker)
        if ticker in portfolio:
            portfolio[ticker].update(info)
        else:
            portfolio[ticker] = info
            portfolio[ticker].update({"price": None, "change": None, "prev_close": None})

    # 3. Sector Rotation Ranking & Recommendations
    sector_data = {t: portfolio[t] for t in SECTOR_ETFS if t in portfolio and portfolio[t].get("momentum_20d") is not None}
    if sector_data:
        sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1].get("momentum_20d", -999), reverse=True)
        total = len(sorted_sectors)
        for idx, (ticker, data) in enumerate(sorted_sectors):
            # Top 1/3 -> Buy, Middle -> Hold, Bottom 1/3 -> Avoid
            if idx < max(1, total // 3):
                rec = "Overweight (Buy)"
                reason = f"Strongest 20-day momentum ({data['momentum_20d']}%) among all 11 sectors."
            elif idx >= total - max(1, total // 3):
                rec = "Underweight (Avoid)"
                reason = f"Weakest 20-day momentum ({data['momentum_20d']}%) – lagging the market."
            else:
                rec = "Market Weight (Hold)"
                reason = f"Neutral momentum ({data['momentum_20d']}%) – in line with sector averages."

            # Add trend nuance
            if data.get("trend") == "Bullish" and "Buy" in rec:
                reason += " Also above 50-day SMA, confirming uptrend."
            elif data.get("trend") == "Bearish" and "Avoid" in rec:
                reason += " Also below 50-day SMA, confirming downtrend."
            elif data.get("trend") == "Bearish" and "Buy" in rec:
                reason = f"Caution: high momentum ({data['momentum_20d']}%) but below 50-day SMA – potential rebound play."
            elif data.get("trend") == "Bullish" and "Avoid" in rec:
                reason = f"Despite bullish trend, momentum is weak ({data['momentum_20d']}%) – wait for confirmation."

            # Special note for XLSR (the actively managed rotation ETF)
            if ticker == "XLSR":
                reason += " XLSR is SSGA's actively managed sector rotation ETF – use as a benchmark for your own rotation strategy."

            portfolio[ticker]["recommendation"] = rec
            portfolio[ticker]["reason"] = reason

    # 4. Add overall rotation summary for the UI
    if sector_data:
        sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1].get("momentum_20d", -999), reverse=True)
        portfolio["sector_rotation_summary"] = {
            "top_sector": sorted_sectors[0][0] if sorted_sectors else "N/A",
            "top_momentum": sorted_sectors[0][1].get("momentum_20d") if sorted_sectors else None,
            "last_updated_rotation": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    portfolio["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return portfolio

if __name__ == "__main__":
    try:
        data = fetch_prices()
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
        logging.info("data.json successfully updated.")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        exit(1)
