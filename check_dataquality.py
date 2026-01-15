import pandas as pd
import os


def audit_data():
    file_name = "top_100_worldwide_films.csv"

    # 1. CHECK IF FILE EXISTS
    if not os.path.exists(file_name):
        print(f"❌ CRITICAL: File '{file_name}' not found.")
        return

    # Load data
    df = pd.read_csv(file_name)
    print(f"📊 Auditing '{file_name}'...\n")

    # ==========================================
    # 🧪 TEST 1: MISSING DATA
    # ==========================================
    # .isnull().sum() counts empty cells in each column
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("❌ FAIL: Found missing values:")
        print(missing[missing > 0])  # Print only columns with errors
    else:
        print("✅ PASS: No missing fields.")

    # ==========================================
    # 🧪 TEST 2: DUPLICATES
    # ==========================================
    # Check if the 'Film Name' appears more than once
    duplicates = df[df.duplicated(subset=['Film Name'])]
    if not duplicates.empty:
        print(f"❌ FAIL: Found {len(duplicates)} duplicate movies:")
        print(duplicates['Film Name'].values)
    else:
        print("✅ PASS: No duplicate movies found.")

    # ==========================================
    # 🧪 TEST 3: DATA TYPES & FORMATTING
    # ==========================================
    print("\n🔍 Checking Data Logic...")

    # Check 1: Does 'Gross Collected' start with '$'?
    # We convert to string first (.astype(str)) just in case
    bad_currency = df[~df['Gross Collected (USD)'].astype(str).str.startswith('$')]

    if len(bad_currency) > 0:
        print(f"⚠️ WARNING: {len(bad_currency)} rows have bad currency format (Missing '$'):")
        print(bad_currency[['Film Name', 'Gross Collected (USD)']])
    else:
        print("✅ PASS: All currency values start with '$'.")

    # Check 2: Are years valid numbers? (Between 1900 and 2030)
    # pd.to_numeric will turn "2009" into 2009. 'coerce' turns errors into NaN.
    years = pd.to_numeric(df['Year Released'], errors='coerce')

    invalid_years = years[(years < 1900) | (years > 2030) | (years.isna())]

    if len(invalid_years) > 0:
        print(f"❌ FAIL: Found invalid years:")
        # Show the rows where the year is bad
        print(df.loc[invalid_years.index, ['Film Name', 'Year Released']])
    else:
        print("✅ PASS: All years are valid numbers.")

    # ==========================================
    # 🏁 FINAL SUMMARY
    # ==========================================
    print("-" * 30)
    print(f"Total Rows Checked: {len(df)}")
    print("-" * 30)


if __name__ == "__main__":
    audit_data()