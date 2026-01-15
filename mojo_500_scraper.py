import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_mojo_500():
    print("🎬 Starting Multi-Page Scraper (Target: 500 Movies)...")

    base_url = "https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/"
    movies = []

    # Mojo shows 200 rows per page. We need offsets 0, 200, 400 to get top 600, then we slice to 500.
    offsets = [0, 200, 400]

    # Headers to look like a real browser (Critical!)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for offset in offsets:
        print(f"   ⏳ Scraping page starting at Rank {offset + 1}...")

        # Add the offset parameter to the URL
        if offset == 0:
            url = base_url
        else:
            url = f"{base_url}?offset={offset}"

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"❌ Error loading page {offset}: Status {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')

            if not table:
                print("❌ Table not found!")
                continue

            rows = table.find_all('tr')[1:]  # Skip header

            for row in rows:
                if len(movies) >= 500:  # STOP exactly at 500
                    break

                cols = row.find_all('td')
                if len(cols) < 3: continue

                try:
                    # Extract Data
                    rank = cols[0].get_text(strip=True)
                    title = cols[1].get_text(strip=True)
                    gross = cols[2].get_text(strip=True)
                    year = cols[7].get_text(strip=True)  # Year is in column 8 (index 7)

                    movies.append({
                        "Rank": rank,
                        "Title": title,
                        "Year": year,
                        "Lifetime Gross (USD)": gross
                    })
                except:
                    continue

            # Be polite to the server, wait 2 seconds between pages
            time.sleep(2)

        except Exception as e:
            print(f"⚠️ Network Error: {e}")

    # --- SAVE ---
    filename = "mojo_top_500.csv"
    df = pd.DataFrame(movies)
    df.to_csv(filename, index=False)

    print("-" * 30)
    print(f"✅ DONE! Scraped {len(df)} movies.")
    print(f"📁 Saved to: {filename}")
    print("-" * 30)
    print(df.tail())  # Show the last few rows to prove we hit 500


if __name__ == "__main__":
    scrape_mojo_500()