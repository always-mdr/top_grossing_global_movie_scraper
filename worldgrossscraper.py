import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def scrape_global_blockbusters():
    print("1. 🕷️ Connecting to Wikipedia...")
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- FIND TABLE ---
    target_table = None
    all_tables = soup.find_all('table', class_='wikitable')

    for t in all_tables:
        headers = [th.get_text(strip=True).lower() for th in t.find_all('tr')[0].find_all('th')]
        if 'worldwide gross' in headers and 'title' in headers:
            target_table = t
            print("   ✅ Found the main chart!")
            break

    if target_table is None:
        print("❌ Could not find table.")
        return

    # --- MAP COLUMNS ---
    header_row = target_table.find_all('tr')[0]
    headers = [th.get_text(strip=True).lower() for th in header_row.find_all('th')]

    idx_title = next(i for i, h in enumerate(headers) if 'title' in h)
    idx_gross = next(i for i, h in enumerate(headers) if 'gross' in h)
    idx_year = next(i for i, h in enumerate(headers) if 'year' in h)

    movies = []
    rows = target_table.find_all('tr')[1:]

    print("2. ⛏️ Extracting & Cleaning Data...")

    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(movies) >= 50: break
        if len(cols) < 3: continue

        try:
            # RAW DATA
            rank = cols[0].get_text(strip=True)
            title = cols[idx_title].get_text(strip=True)
            gross_raw = cols[idx_gross].get_text(strip=True)
            year = cols[idx_year].get_text(strip=True)

            # --- CLEANING STEP (UPDATED) ---

            # 1. Remove [1], [2] citations
            rank = re.sub(r'\[.*?\]', '', rank)
            title = re.sub(r'\[.*?\]', '', title)
            year = re.sub(r'\[.*?\]', '', year)

            # 2. Strict Currency Cleaning
            # logic: Find the first '$' and everything after it until the end of the number
            # "T$2,257..." -> "$2,257..."
            # "NZ$2,215..." -> "$2,215..."

            # Step A: Remove any letters (A-Z, a-z) completely
            gross_clean = re.sub(r'[a-zA-Z]', '', gross_raw)

            # Step B: Remove [citations] again just in case
            gross_clean = re.sub(r'\[.*?\]', '', gross_clean)

            # Step C: Ensure it has exactly one '$' at the start
            # First, strip whitespace
            gross_clean = gross_clean.strip()
            # If no '$', add it. If multiple '$$', fix it.
            if "$" not in gross_clean:
                gross_clean = "$" + gross_clean

            # Final check: sometimes it leaves weird symbols like "F$".
            # This regex says: "Keep only $, digits, and commas"
            # (Note: we use a simpler approach: remove anything that isn't $, digit, or comma)
            gross_clean = re.sub(r'[^\d$,]', '', gross_clean)

            # But we must ensure the $ is at the front
            if not gross_clean.startswith('$'):
                gross_clean = "$" + gross_clean.replace('$', '')

            movies.append({
                "Rank": rank,
                "Film Name": title,
                "Year Released": year,
                "Gross Collected (USD)": gross_clean
            })

        except Exception as e:
            continue

    # --- SAVE ---
    df = pd.DataFrame(movies)
    df.to_csv("top_50_worldwide_films.csv", index=False)
    print(f"3. ✅ Saved clean data (Rows: {len(df)})")


if __name__ == "__main__":
    scrape_global_blockbusters()

