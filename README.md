# Portfolio Command Center

A live, auto‑updating portfolio dashboard with **built‑in sector rotation strategy** using **official State Street Global Advisors (SSGA) Select Sector SPDR ETFs**.

## ✨ Features

- **Automated daily updates** – runs after US market close (weekdays).
- **Rich data** – price, change, company name, category.
- **Sector Rotation Insights** – analyzes all 11 GICS sectors using SSGA ETFs:
  - XLC (Communication Services), XLY (Consumer Discretionary), XLP (Consumer Staples)
  - XLE (Energy), XLF (Financials), XLV (Health Care)
  - XLI (Industrials), XLB (Materials), XLRE (Real Estate)
  - XLK (Technology), XLU (Utilities)
  - Plus XLSR (SSGA US Sector Rotation ETF) as a benchmark
- **Actionable signals** – each sector card shows **recommendation** (Overweight/Buy, Market Weight/Hold, Underweight/Avoid) and a **reason**.
- **Interactive UI** – sortable table, search filter, top gainers/losers.
- **Futuristic design** – glassmorphism, dynamic gradients.
- **Zero‑cost hosting** – deploy on GitHub Pages.

## 📋 Sector ETFs Source

All sector ETFs are sourced from **State Street Global Advisors**:
- [SSGA Sector and Industry ETFs](https://www.ssga.com/us/en/individual/capabilities/equities/sector-investing/sector-and-industry-etfs)

The dashboard fetches **live market prices** via Yahoo Finance (not delayed NAVs shown on the SSGA website).

## 🧠 How the Sector Rotation Works

- **20‑day momentum** measures short‑term strength.
- **50‑day SMA** confirms the trend (Bullish if price > SMA, Bearish if below).
- Sectors are ranked by momentum – top 1/3 get **Overweight (Buy)**, middle **Market Weight (Hold)**, bottom 1/3 **Underweight (Avoid)**.
- The reason field explains the decision (e.g., *"Strongest momentum among all 11 sectors"* or *"Below 50‑day SMA – confirming downtrend"*).
- XLSR is shown as a **benchmark** – it's SSGA's actively managed sector rotation ETF.

## 🚀 Getting Started

1. Clone your repo and add these files.
2. Enable GitHub Pages (Settings > Pages > Deploy from `main` branch).
3. Manually trigger the workflow (Actions > Update Portfolio Data > Run workflow).
4. Visit your GitHub Pages URL.

## 🔧 Customization

- Edit `CORE_TICKERS` and `SECTOR_ETFS` in `fetch_prices.py`.
- Adjust the ranking logic (top/bottom percentages) inside the ranking loop.

## 📄 License

MIT © Alam ShahJade
