import yfinance as yf
import json
import datetime
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKERS = [
    "MSFT", "AVGO", "V", "MA", "SPGI", "UNH", "COST", "AAPL", "GOOGL",
    "JNJ", "VIG", "GLDM", "SPMO", "SPLG", "VXUS", "AVUV",
    "SPYI", "QQQI", "IWMI", "TSPY", "TMGN"
]

# Category mapping (for display)
CATEGORIES = {
    'MSFT': 'Tech / AI', 'AVGO': 'Semiconductors', 'V': 'Financials', 'MA': 'Financials',
    'SPGI': 'Financials', 'UNH': 'Healthcare', 'COST': 'Consumer', 'AAPL': 'Tech / Hardware',
    'GOOGL': 'Tech / AI', 'JNJ': 'Healthcare', 'VIG': 'Dividend ETF', 'GLDM': 'Gold',
    'SPMO': 'Momentum ETF', 'SPLG': 'S&P 500 ETF', 'VXUS': 'Intl ETF', 'AVUV': 'Small Value',
    'SPYI': 'Income ETF', 'QQQI': 'Nasdaq Income', 'IWMI': 'Income ETF', 'TSPY': 'Income ETF',
    'TMGN': 'Income ETF'
}

def fetch_ticker_info(ticker: str) -> Dict[str, Any]:
    """Fetch short name and category for a ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        name = info.get('shortName', ticker)
        sector = info.get('sector', '')
        # Use category from mapping if available, else sector
        category = CATEGORIES.get(ticker, sector if sector else 'Equity')
        return {'name': name, 'category': category}
    except Exception as e:
        logging.warning(f"Could not fetch info for {ticker}: {e}")
        return {'name': ticker, 'category': CATEGORIES.get(ticker, 'Unknown')}

def fetch_prices() -> Dict[str, Any]:
    """Fetch price data for all tickers with robust error handling."""
    portfolio = {}
    # Download 5 days to ensure at least two closes (for change calculation)
    logging.info(f"Downloading data for {len(TICKERS)} tickers...")
    data = yf.download(TICKERS, period="5d", group_by='ticker', progress=False)

    for ticker in TICKERS:
        try:
            if len(TICKERS) > 1:
                df = data[ticker]
            else:
                df = data

            if df.empty:
                logging.warning(f"No data for {ticker}")
                portfolio[ticker] = {"price": None, "change": None, "prev_close": None}
                continue

            # Get the last two closes (if available)
            closes = df['Close'].dropna()
            if len(closes) < 2:
                # Only one day -> change = 0
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
            portfolio[ticker] = {"price": None, "change": None, "prev_close": None}

    # Enrich with name and category
    for ticker in TICKERS:
        info = fetch_ticker_info(ticker)
        portfolio[ticker].update(info)

    # Add timestamp
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