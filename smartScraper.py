import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def clean_currency(value):
    """
    Converts '₹2,000 crore' -> 2000.0
    Handles ranges like '₹1,968–2,200 crore' by taking the higher number.
    """
    if not isinstance(value, str):
        return 0.0

    # 1. Remove references like [3]
    value = re.sub(r'\[.*?\]', '', value)

    # 2. Find all numbers in the string
    # This finds patterns like '2,000' or '1968.03'
    matches = re.findall(r'([\d,]+\.?\d*)', value)

    if matches:
        try:
            # Clean commas and convert all found numbers to floats
            numbers = [float(m.replace(',', '')) for m in matches]
            # If there is a range (e.g. 1900-2000), take the max value
            return max(numbers)
        except:
            return 0.0
    return 0.0


def scrape_data():
    print("1. 🕷️ Fetching Wikipedia Data...")
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_Indian_films"

    try:
        # User-Agent is required to stop Wikipedia blocking us
        headers_ua = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers_ua)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

    # --- ROBUST TABLE FINDER ---
    target_table = None
    tables = soup.find_all('table', class_='wikitable')

    print(f"   (Found {len(tables)} tables. Scanning headers...)")

    for t in tables:
        # Get all headers in lowercase
        headers = [th.get_text(strip=True).lower() for th in t.find_all('tr')[0].find_all('th')]

        # Check if this table has BOTH "Title" (or "Film") AND "Worldwide Gross"
        has_title = any(x in headers for x in ['title', 'film'])
        has_gross = any(x in headers for x in ['worldwide gross', 'gross'])

        if has_title and has_gross:
            target_table = t
            print("   ✅ Found the correct table!")
            break

    if target_table is None:
        print("❌ Could not find the table. Headers might have changed again.")
        return None

    # --- MAP COLUMNS AUTOMATICALLY ---
    header_row = target_table.find_all('tr')[0]
    headers = [th.get_text(strip=True).lower() for th in header_row.find_all('th')]

    try:
        # Find column index dynamically
        # Next() finds the first match in the list
        idx_title = next(i for i, h in enumerate(headers) if h in ['title', 'film'])
        idx_gross = next(i for i, h in enumerate(headers) if 'gross' in h)
        idx_year = next(i for i, h in enumerate(headers) if 'year' in h)
    except StopIteration:
        print("❌ Error: Could not map columns. Table structure is unexpected.")
        return None

    movies = []
    rows = target_table.find_all('tr')[1:]  # Skip header

    for row in rows:
        cols = row.find_all(['td', 'th'])

        # Skip if row is too short
        if len(cols) <= max(idx_title, idx_gross, idx_year):
            continue

        try:
            title = cols[idx_title].get_text(strip=True)
            gross_raw = cols[idx_gross].get_text(strip=True)
            year = cols[idx_year].get_text(strip=True)

            # Cleaning
            title_clean = re.sub(r'\[.*?\]', '', title)
            year_clean = re.sub(r'\[.*?\]', '', year)
            gross_value = clean_currency(gross_raw)

            # Logic: If gross is 0, it's likely a header row repeated or empty
            if gross_value == 0: continue

            movies.append({
                "Title": title_clean,
                "Year": year_clean,
                "Gross_Raw": gross_raw,
                "Gross_Value": gross_value
            })

        except Exception as e:
            continue

    # --- SAVE ---
    df = pd.DataFrame(movies)

    # Sort Highest to Lowest
    df = df.sort_values(by='Gross_Value', ascending=False)

    # Save Top 50
    df = df.head(50)

    print(f"2. ✅ Processed {len(df)} movies.")
    print("\n--- TOP 5 PREVIEW ---")
    print(df[['Title', 'Gross_Value']].head())

    df.to_csv("top_indian_movies.csv", index=False)
    print("\n💾 Saved to 'top_indian_movies.csv'")


if __name__ == "__main__":
    scrape_data()
