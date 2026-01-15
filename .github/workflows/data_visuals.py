import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def generate_chart():
    print("🎨 Generating Box Office Chart...")

    # 1. Load Data
    if not os.path.exists("top_50_worldwide_films.csv"):
        print("❌ CSV not found. Run worldgrossscraper.py first.")
        return

    df = pd.read_csv("top_50_worldwide_films.csv")

    # 2. Data Prep: Convert "$2,000,000" (String) -> 2000000 (Number)
    # We remove '$' and ',' so Python can do math on it
    df['Gross_Numeric'] = df['Gross Collected (USD)'].astype(str).str.replace('$', '').str.replace(',', '')
    df['Gross_Numeric'] = pd.to_numeric(df['Gross_Numeric'])

    # Convert to Billions for easier reading
    df['Gross_Billions'] = df['Gross_Numeric'] / 1_000_000_000

    # take top 10 only
    df_top10 = df.head(10)

    # 3. Create Plot
    plt.figure(figsize=(12, 6))  # Size of the image
    sns.set_theme(style="whitegrid")

    # Bar Chart
    ax = sns.barplot(
        x="Gross_Billions",
        y="Film Name",
        data=df_top10,
        palette="viridis"
    )

    # 4. Styling
    plt.title('Top 10 Highest Grossing Movies (All Time)', fontsize=16, weight='bold')
    plt.xlabel('Global Gross (Billions USD)', fontsize=12)
    plt.ylabel('')

    # Add numbers at the end of bars
    for i in ax.containers:
        ax.bar_label(i, fmt=' $%.2f B', padding=3)

    plt.tight_layout()

    # 5. Save Image
    filename = "box_office_chart.png"
    plt.savefig(filename, dpi=300)  # dpi=300 makes it high quality
    print(f"✅ Chart saved as: {filename}")


if __name__ == "__main__":
    generate_chart()