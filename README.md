# Portfolio Command Center

A live, auto‑updating portfolio dashboard with **built‑in sector rotation strategy** using **official State Street Global Advisors (SSGA) Select Sector SPDR ETFs**.

## 🚨 First Time Setup – IMPORTANT

After pushing these files, you MUST manually trigger the workflow:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **Update Portfolio Data** on the left
4. Click **Run workflow** → **Run workflow**
5. Wait 1-2 minutes for it to complete
6. Refresh your GitHub Pages site

The workflow will then run automatically every weekday at 21:00 UTC.

## 🔍 Debugging

If prices still show `N/A`:

1. Check the workflow logs:
   - Go to **Actions** → **Update Portfolio Data** → click the latest run
   - Look for errors in the **Fetch Prices** step

2. Common issues:
   - **Rate limiting** – the script now has retry logic
   - **Network issues** – GitHub Actions has outbound internet access
   - **Ticker changes** – verify ticker symbols are still valid

3. Test locally:
   ```bash
   pip install yfinance pandas
   python scripts/fetch_prices.py
   cat data.json  # should show real prices
