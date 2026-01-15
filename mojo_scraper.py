import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_mojo_top_100():
    print("🎬 Starting Box Office Mojo Scraper...")

    # URL for "All Time Worldwide Box Office"
    url = "https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/"

    # CRITICAL: We must look like a real browser (Chrome on Windows)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for 403 Forbidden errors
    except Exception as e:
        print(f"❌ Connection Blocked: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the main table
    # Mojo uses specific CSS classes, but finding the first <table class="a-bordered"> is safer
    table = soup.find('table')

    if not table:
        print("❌ Could not find the data table.")
        return

    rows = table.find_all('tr')[1:]  # Skip the header row

    movies = []

    print("⛏️ Extracting Top 100 Rows...")

    for row in rows:
        # Stop if we already have 100 movies
        if len(movies) >= 100:
            break

        cols = row.find_all('td')
        if len(cols) < 3: continue  # Skip bad rows

        try:
            # Box Office Mojo Column Structure:
            # [0] Rank, [1] Title, [2] Lifetime Gross, [3] Domestic, [4] %, [5] Foreign, [6] %, [7] Year

            rank = cols[0].get_text(strip=True)
            title = cols[1].get_text(strip=True)
            gross = cols[2].get_text(strip=True)
            year = cols[7].get_text(strip=True)

            # CLEANING:
            # Mojo puts money as "$2,923,706,026". We keep it as string for now.

            movies.append({
                "Rank": rank,
                "Title": title,
                "Year": year,
                "Lifetime Gross (USD)": gross
            })

        except Exception as e:
            print(f"⚠️ Error on row: {e}")
            continue

    # Save to CSV
    filename = "mojo_top_100.csv"
    df = pd.DataFrame(movies)
    df.to_csv(filename, index=False)

    print("-" * 30)
    print(f"✅ Success! Scraped {len(df)} movies.")
    print(f"📁 Data saved to: {filename}")
    print("-" * 30)
    print(df.head())  # Show preview


if __name__ == "__main__":
    scrape_mojo_top_100()