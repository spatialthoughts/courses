"""Exploratory data analysis of City of London Police street-level crime data, 2024.

Loads all 12 monthly CSVs from data/london_crime_2024/, prints a summary of
rows/columns/missing data plus data-quality flags, and saves three charts
(crime types, monthly trend, monthly trend by top crime types) to
outputs/london_crime_2024_eda/.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

DATA_DIR = Path("data/london_crime_2024")
OUT_DIR = Path("outputs/london_crime_2024_eda")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Palette (dataviz skill reference palette, light mode)
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SEQ_BLUE = "#2a78d6"  # sequential/single-series hue, step 450
CATEGORICAL = ["#2a78d6", "#1baf7a", "#eda100", "#008300",
               "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "text.color": INK_PRIMARY,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "font.family": "sans-serif",
    "font.size": 10,
})

LONDON_BBOX = {"lon_min": -0.6, "lon_max": 0.3, "lat_min": 51.2, "lat_max": 51.8}


def load_data():
    files = sorted(DATA_DIR.glob("*/*.csv"))
    frames = []
    for f in files:
        d = pd.read_csv(f)
        d["_source_file"] = f.name
        d["_source_month_folder"] = f.parent.name
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    return df, files


def print_summary(df, files):
    data_cols = [c for c in df.columns if not c.startswith("_source")]

    print("=" * 78)
    print("SHAPE")
    print("=" * 78)
    print(f"Files loaded: {len(files)} (one per month, 2024-01 .. 2024-12)")
    print(f"Total rows:   {len(df):,}")
    print(f"Total columns:{len(data_cols)}")
    print()
    print("Rows per month:")
    print(df.groupby("_source_month_folder").size().to_string())
    print()

    print("=" * 78)
    print("COLUMNS & DTYPES")
    print("=" * 78)
    print(df[data_cols].dtypes.to_string())
    print()

    print("=" * 78)
    print("MISSING DATA")
    print("=" * 78)
    missing = df[data_cols].isna().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    summary = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
    summary = summary.sort_values("missing_pct", ascending=False)
    print(summary.to_string())
    print()

    return data_cols


def print_quality_flags(df):
    print("=" * 78)
    print("DATA QUALITY FLAGS")
    print("=" * 78)

    # 1. Entirely / almost entirely null columns
    data_cols = [c for c in df.columns if not c.startswith("_source")]
    all_null = [c for c in data_cols if df[c].isna().all()]
    print(f"- Columns 100% empty: {all_null if all_null else 'none'}")

    # 2. Duplicate Crime ID (excluding blank IDs, which are expected/normal
    #    for crimes data.police.uk does not assign a public ID to)
    ids = df["Crime ID"].dropna()
    blank_id_count = df["Crime ID"].isna().sum()
    dupe_ids = ids[ids.duplicated(keep=False)]
    print(f"- Crime ID blank (normal for unmapped/anonymized crimes): "
          f"{blank_id_count:,} ({blank_id_count / len(df) * 100:.1f}%)")
    print(f"- Duplicate non-blank Crime IDs: {dupe_ids.nunique()} distinct IDs "
          f"({len(dupe_ids)} rows)")

    # 3. Missing coordinates
    missing_geo = df[["Longitude", "Latitude"]].isna().any(axis=1).sum()
    print(f"- Rows missing Longitude/Latitude: {missing_geo:,} "
          f"({missing_geo / len(df) * 100:.1f}%)")

    # 4. Coordinates outside a sane Greater London bounding box
    geo = df.dropna(subset=["Longitude", "Latitude"])
    out_of_bbox = geo[
        (geo["Longitude"] < LONDON_BBOX["lon_min"]) | (geo["Longitude"] > LONDON_BBOX["lon_max"]) |
        (geo["Latitude"] < LONDON_BBOX["lat_min"]) | (geo["Latitude"] > LONDON_BBOX["lat_max"])
    ]
    print(f"- Rows with coordinates outside Greater London bbox: {len(out_of_bbox)}")

    # 5. Reported by / Falls within should be constant
    reported_by_vals = df["Reported by"].dropna().unique()
    falls_within_vals = df["Falls within"].dropna().unique()
    print(f"- Distinct 'Reported by' values: {list(reported_by_vals)}")
    print(f"- Distinct 'Falls within' values: {list(falls_within_vals)}")

    # 6. Month column vs source folder mismatch
    mismatch = df[df["Month"] != df["_source_month_folder"]]
    print(f"- Rows where 'Month' column disagrees with its source folder: {len(mismatch)}")

    # 7. Last outcome category missingness by month (outcomes lag behind reporting)
    outcome_missing_by_month = (
        df.groupby("_source_month_folder")["Last outcome category"]
        .apply(lambda s: s.isna().mean() * 100)
        .round(1)
    )
    print("- 'Last outcome category' missing % by month:")
    print(outcome_missing_by_month.to_string())

    # 8. Crime type distribution
    print()
    print("- Crime type counts (all months):")
    print(df["Crime type"].value_counts().to_string())
    print()


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(length=0)


def chart_crime_types(df):
    counts = df["Crime type"].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(counts.index, counts.values, color=SEQ_BLUE, height=0.62)
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="x", color=GRIDLINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    style_axes(ax)
    ax.set_xlabel("Incidents (Jan–Dec 2024)", color=INK_SECONDARY)
    ax.set_title("City of London Police: incidents by crime type, 2024",
                 color=INK_PRIMARY, fontsize=13, loc="left", pad=12)
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_width() + max(counts.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", ha="left", color=INK_SECONDARY, fontsize=9)
    ax.set_xlim(0, max(counts.values) * 1.12)
    fig.tight_layout()
    out_path = OUT_DIR / "crime_types.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def chart_monthly_trend(df):
    monthly = df.groupby("Month").size().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(monthly.index, monthly.values, color=SEQ_BLUE, linewidth=2,
            marker="o", markersize=8, markerfacecolor=SEQ_BLUE, markeredgecolor=SURFACE, markeredgewidth=1.5,
            zorder=3)
    ax.grid(axis="y", color=GRIDLINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    style_axes(ax)
    ax.set_ylim(0, max(monthly.values) * 1.2)
    ax.set_ylabel("Incidents", color=INK_SECONDARY)
    ax.set_title("City of London Police: total monthly incidents, 2024",
                 color=INK_PRIMARY, fontsize=13, loc="left", pad=12)
    for x, y in zip(monthly.index, monthly.values):
        ax.annotate(f"{y:,}", (x, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=8.5, color=INK_SECONDARY)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    out_path = OUT_DIR / "monthly_trend.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


def chart_monthly_by_crime_type(df, top_n=6):
    top_types = df["Crime type"].value_counts().head(top_n).index.tolist()
    pivot = (
        df[df["Crime type"].isin(top_types)]
        .groupby(["Month", "Crime type"]).size()
        .unstack("Crime type")
        .reindex(columns=top_types)
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, crime_type in enumerate(top_types):
        ax.plot(pivot.index, pivot[crime_type], label=crime_type,
                color=CATEGORICAL[i], linewidth=2, marker="o", markersize=6, zorder=3)
    ax.grid(axis="y", color=GRIDLINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    style_axes(ax)
    ax.set_ylabel("Incidents", color=INK_SECONDARY)
    ax.set_title(f"City of London Police: monthly trend, top {top_n} crime types, 2024",
                 color=INK_PRIMARY, fontsize=13, loc="left", pad=12)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    legend = ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False,
                        fontsize=9, labelcolor=INK_SECONDARY)
    fig.tight_layout()
    out_path = OUT_DIR / "monthly_by_crime_type.png"
    fig.savefig(out_path, dpi=150, bbox_extra_artists=(legend,), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def main():
    df, files = load_data()
    print_summary(df, files)
    print_quality_flags(df)

    print("=" * 78)
    print("CHARTS")
    print("=" * 78)
    chart_crime_types(df)
    chart_monthly_trend(df)
    chart_monthly_by_crime_type(df)


if __name__ == "__main__":
    main()
