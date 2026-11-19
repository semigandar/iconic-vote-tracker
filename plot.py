import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load and clean data (ignores any blank rows from server outages)
df = pd.read_csv("votes.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp (EAT)"].str.replace(" EAT", "", regex=False))
candidates = ["HON. MINISTER OF ENJOYMENT", "JB ON HIS BIKE", "1TRABO", "JAWADU SONKO"]

for c in candidates:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=candidates).sort_values("Timestamp")

if len(df) >= 2:
    # 1. Cumulative Total Votes Curve
    plt.figure(figsize=(11, 5))
    for c in candidates:
        plt.plot(df["Timestamp"], df[c], marker="o", linewidth=2, label=c)
    plt.title("Total Votes Over Time (EAT)", fontsize=14, fontweight="bold")
    plt.xlabel("Time (EAT)")
    plt.ylabel("Total Votes")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("total_votes.png", dpi=150)
    plt.close()

    # 2. Votes Gained Per Interval (Spike Detector Curve)
    plt.figure(figsize=(11, 5))
    for c in candidates:
        gains = df[c].diff()
        plt.plot(df["Timestamp"], gains, marker="o", linewidth=2, label=c)
    plt.title("New Votes Added Per Check (Spike Detector)", fontsize=14, fontweight="bold")
    plt.xlabel("Time (EAT)")
    plt.ylabel("Votes Gained Since Last Check")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("vote_spikes.png", dpi=150)
    plt.close()
