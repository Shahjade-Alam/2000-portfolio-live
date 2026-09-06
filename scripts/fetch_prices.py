import yfinance as yf
import json
import datetime
import logging
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKERS = [
    "MSFT", "AVGO", "V", "MA", "SPGI", "UNH", "COST", "AAPL", "GOOGL",
    "JNJ", "VIG", "GLDM", "SPMO", "SPLG", "VXUS", "AVUV",
    "SPYI", "QQQI", "IWMI", "TSPY", "TMGN"
]

CATEGORIES = {
    'MSFT': 'Tech / AI', 'AVGO': 'Semiconductors', 'V': 'Financials', 'MA': 'Financials',
    'SPGI': 'Financials', 'UNH': 'Healthcare', 'COST': 'Consumer', 'AAPL': 'Tech / Hardware',
    'GOOGL': 'Tech / AI', 'JNJ': 'Healthcare', 'VIG': 'Dividend ETF', 'GLDM': 'Gold',
    'SPMO': 'Momentum ETF', 'SPLG': 'S&P 500 ETF', 'VXUS': 'Intl ETF', 'AVUV': 'Small Value',
    'SPYI': 'Income ETF', 'QQQI': 'Nasdaq Income', 'IWMI': 'Income ETF', 'TSPY': 'Income ETF',
    'TMGN': 'Income ETF'
}

def load_previous_data() -> Dict[str, Any]:
    """Load existing data.json to preserve values if fetch fails."""
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
        name = info.get('shortName', ticker)
        sector = info.get('sector', '')
        category = CATEGORIES.get(ticker, sector if sector else 'Equity')
        return {'name': name, 'category': category}
    except Exception as e:
        logging.warning(f"Could not fetch info for {ticker}: {e}")
        return {'name': ticker, 'category': CATEGORIES.get(ticker, 'Unknown')}

def fetch_prices() -> Dict[str, Any]:
    previous = load_previous_data()
    portfolio = {}
    logging.info(f"Downloading data for {len(TICKERS)} tickers...")
    # Use a longer period to ensure at least two closes
    data = yf.download(TICKERS, period="10d", group_by='ticker', progress=False)

    for ticker in TICKERS:
        try:
            if len(TICKERS) > 1:
                df = data[ticker]
            else:
                df = data

            if df.empty:
                logging.warning(f"No data for {ticker} – keeping previous value if exists")
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
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")
            if ticker in previous and ticker != 'last_updated':
                portfolio[ticker] = {k: v for k, v in previous[ticker].items() if k not in ['name','category']}
            else:
                portfolio[ticker] = {"price": None, "change": None, "prev_close": None}

    # Enrich with name and category (always fetch fresh)
    for ticker in TICKERS:
        info = fetch_ticker_info(ticker)
        if ticker in portfolio:
            portfolio[ticker].update(info)
        else:
            # fallback: use previous or dummy
            portfolio[ticker] = info
            portfolio[ticker].update({"price": None, "change": None, "prev_close": None})

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
