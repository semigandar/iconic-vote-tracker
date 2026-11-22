import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load and clean data
df = pd.read_csv("votes.csv")
df["Timestamp"] = pd.to_datetime(
    df["Timestamp (EAT)"].str.replace(" EAT", "", regex=False)
)

candidates = [
    "HON. MINISTER OF ENJOYMENT",
    "JB ON HIS BIKE",
    "1TRABO",
    "JAWADU SONKO"
]

for c in candidates:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=candidates).sort_values("Timestamp")

if len(df) >= 2:

    # 1. Total votes over time
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

    # Calculate votes added since the previous check
    gains_df = df[["Timestamp"]].copy()

    for c in candidates:
        gains_df[c] = df[c].diff()

    # 2. Full spike detector — retains every unusual spike
    plt.figure(figsize=(11, 5))

    for c in candidates:
        plt.plot(gains_df["Timestamp"], gains_df[c], marker="o", linewidth=2, label=c)

    plt.title("New Votes Added Per Check (All Spikes)", fontsize=14, fontweight="bold")
    plt.xlabel("Time (EAT)")
    plt.ylabel("Votes Gained Since Last Check")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("vote_spikes.png", dpi=150)
    plt.close()

    # 3. JB surge zoom — makes the orange line clearly visible
    zoom_start = pd.Timestamp("2026-11-21 14:00:00")
    zoom_df = gains_df[gains_df["Timestamp"] >= zoom_start].copy()

    plt.figure(figsize=(12, 6))

    for c in candidates:
        plt.plot(
            zoom_df["Timestamp"],
            zoom_df[c],
            marker="o",
            linewidth=2,
            markersize=4,
            label=c
        )

    plt.title("JB Vote Surge Zoom — New Votes Per Check", fontsize=14, fontweight="bold")
    plt.xlabel("Time (EAT)")
    plt.ylabel("Votes Gained Since Last Check")

    # This is the key: makes JB's 30–45-vote pattern visible
    plt.ylim(0, 60)

    plt.text(
        0.98,
        0.95,
        "Large blue outlier is intentionally outside this zoom.",
        transform=plt.gca().transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="#1f77b4",
        bbox=dict(facecolor="white", alpha=0.9, edgecolor="#1f77b4")
    )

    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("jb_surge_zoom.png", dpi=200)
    plt.close()
