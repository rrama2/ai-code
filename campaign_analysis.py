"""
Campaign Analytics — Python Analysis Script
=============================================
Data: campaign_data.csv
Platforms: Facebook, Instagram, Pinterest, Twitter
Period: Jan–Jun 2026

Chain of Thought
----------------
Step 1: Load the raw daily data (1,831 rows, 13 columns).
Step 2: Engineer derived KPIs — ROI, ROAS, CTR, CPA, CPC, CPM, CVR.
Step 3: Aggregate by platform, campaign, goal, audience, and month.
Step 4: Rank and flag outliers (top/bottom ROI campaigns).
Step 5: Produce a monthly trend matrix for time-series insight.
Step 6: Print an insight summary for budget-reallocation decisions.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# ── 1. Load & clean ──────────────────────────────────────────────────────────

CSV_PATH = "campaign_data.csv"         # adjust path if needed
df = pd.read_csv(CSV_PATH, parse_dates=["date"])

assert not df.isnull().any().any(), "Unexpected nulls in data — check source file"

# ── 2. Derived metrics ────────────────────────────────────────────────────────

# Guard against division-by-zero in source columns
safe_clicks = df["clicks"].replace(0, np.nan)
safe_conv   = df["conversions"].replace(0, np.nan)
safe_impr   = df["impressions"].replace(0, np.nan)

df["roi_pct"]  = (df["revenue"] - df["spend"]) / df["spend"] * 100   # Return on Ad Spend %
df["roas"]     = df["revenue"] / df["spend"]                           # Revenue per $ spent
df["ctr_pct"]  = df["clicks"]  / df["impressions"] * 100              # Click-Through Rate %
df["cvr_pct"]  = df["conversions"] / safe_clicks * 100                # Conversion Rate %
df["cpa"]      = df["spend"]   / safe_conv                            # Cost per Acquisition $
df["cpc"]      = df["spend"]   / safe_clicks                          # Cost per Click $
df["cpm"]      = df["spend"]   / df["impressions"] * 1000             # Cost per 1 000 Impressions $
df["month"]    = df["date"].dt.to_period("M")
df["week"]     = df["date"].dt.to_period("W")


# ── 3. Summary helpers ────────────────────────────────────────────────────────

def agg_metrics(frame, group_cols):
    """Aggregate raw spend/revenue/clicks/impressions/conversions, then derive KPIs."""
    g = frame.groupby(group_cols).agg(
        spend       = ("spend",       "sum"),
        revenue     = ("revenue",     "sum"),
        conversions = ("conversions", "sum"),
        clicks      = ("clicks",      "sum"),
        impressions = ("impressions", "sum"),
    ).reset_index()
    g["roi_pct"]  = (g["revenue"] - g["spend"]) / g["spend"] * 100
    g["roas"]     = g["revenue"] / g["spend"]
    g["ctr_pct"]  = g["clicks"]  / g["impressions"] * 100
    g["cpa"]      = g["spend"]   / g["conversions"].replace(0, np.nan)
    g["spend_share"] = g["spend"] / g["spend"].sum() * 100
    return g


# ── 4. Overall KPIs ───────────────────────────────────────────────────────────

S  = df["spend"].sum()
R  = df["revenue"].sum()
CV = int(df["conversions"].sum())
CL = int(df["clicks"].sum())
IM = int(df["impressions"].sum())

print("=" * 62)
print("  CAMPAIGN ANALYTICS SUMMARY  |  Jan–Jun 2026")
print("=" * 62)
print(f"\n{'Overall KPIs':}")
print(f"  Total Spend       : ${S:>12,.2f}")
print(f"  Total Revenue     : ${R:>12,.2f}")
print(f"  Overall ROI       : {(R - S) / S * 100:>11.1f}%")
print(f"  Overall ROAS      : {R / S:>12.2f}x")
print(f"  Total Conversions : {CV:>12,}")
print(f"  Total Clicks      : {CL:>12,}")
print(f"  Total Impressions : {IM:>12,}")
print(f"  Avg CTR           : {CL / IM * 100:>11.2f}%")
print(f"  Avg CPA           : ${S / CV:>12.2f}")


# ── 5. Platform comparison ────────────────────────────────────────────────────

plat = agg_metrics(df, "platform").sort_values("roi_pct", ascending=False)

print(f"\n{'Platform Comparison (ranked by ROI)':}")
header = f"{'Platform':<12}  {'Spend':>10}  {'Revenue':>10}  {'ROI':>8}  {'ROAS':>6}  {'Conv':>6}  {'CTR':>6}  {'CPA':>8}  {'Budget%':>7}"
print(f"  {header}")
print("  " + "-" * (len(header) + 2))
for _, r in plat.iterrows():
    print(
        f"  {r['platform']:<12}"
        f"  ${r['spend']:>9,.0f}"
        f"  ${r['revenue']:>9,.0f}"
        f"  {r['roi_pct']:>7.1f}%"
        f"  {r['roas']:>5.2f}x"
        f"  {int(r['conversions']):>6,}"
        f"  {r['ctr_pct']:>5.2f}%"
        f"  ${r['cpa']:>7.2f}"
        f"  {r['spend_share']:>6.1f}%"
    )


# ── 6. Campaign-level performance ─────────────────────────────────────────────

camp = agg_metrics(df, ["campaign_id", "campaign_name", "platform", "goal"])

print(f"\n{'Top 5 Campaigns by ROI':}")
for _, r in camp.nlargest(5, "roi_pct").iterrows():
    print(f"  {r['campaign_id']}  {r['campaign_name']:<38}  ROI={r['roi_pct']:+.1f}%  ROAS={r['roas']:.2f}x  Spend=${r['spend']:,.0f}")

print(f"\n{'Bottom 5 Campaigns by ROI':}")
for _, r in camp.nsmallest(5, "roi_pct").iterrows():
    print(f"  {r['campaign_id']}  {r['campaign_name']:<38}  ROI={r['roi_pct']:+.1f}%  ROAS={r['roas']:.2f}x  Spend=${r['spend']:,.0f}")


# ── 7. Monthly trend (spend + revenue by platform) ───────────────────────────

monthly = agg_metrics(df, ["month", "platform"])
monthly["month_str"] = monthly["month"].astype(str)

pivot_spend = (
    monthly
    .pivot_table(index="month_str", columns="platform", values="spend", aggfunc="sum")
    .fillna(0)
    .round(0)
    .astype(int)
)

print(f"\n{'Monthly Spend by Platform ($)':}")
print(pivot_spend.to_string())

pivot_roi = (
    monthly
    .pivot_table(index="month_str", columns="platform", values="roi_pct", aggfunc="mean")
    .fillna(0)
    .round(1)
)

print(f"\n{'Monthly ROI % by Platform':}")
print(pivot_roi.to_string())


# ── 8. Goal analysis ──────────────────────────────────────────────────────────

goal_agg = agg_metrics(df, "goal").sort_values("roi_pct", ascending=False)

print(f"\n{'Campaign Goal Performance':}")
for _, r in goal_agg.iterrows():
    cpa_str = f"${r['cpa']:,.2f}" if not np.isnan(r['cpa']) else "N/A"
    print(
        f"  {r['goal']:<18}  ROI={r['roi_pct']:+.1f}%"
        f"  Spend=${r['spend']:>8,.0f}"
        f"  Conv={int(r['conversions']):>5,}"
        f"  CPA={cpa_str:>8}"
    )


# ── 9. Audience analysis ──────────────────────────────────────────────────────

aud_agg = agg_metrics(df, "audience").sort_values("roi_pct", ascending=False)

print(f"\n{'Top 5 Audience Segments by ROI':}")
for _, r in aud_agg.head(5).iterrows():
    cpa_str = f"${r['cpa']:,.2f}" if not np.isnan(r['cpa']) else "N/A"
    print(f"  {r['audience']:<25}  ROI={r['roi_pct']:+.1f}%  CPA={cpa_str}  Conv={int(r['conversions']):>4,}")


# ── 10. Actionable insights ───────────────────────────────────────────────────

best_plat  = plat.iloc[0]
worst_plat = plat.iloc[-1]
best_camp  = camp.loc[camp["roi_pct"].idxmax()]
worst_camp = camp.loc[camp["roi_pct"].idxmin()]
twitter_pct = plat.loc[plat.platform == "Twitter", "spend_share"].values[0]

print(f"\n{'Actionable Insights':}")
print("-" * 62)
print(f"  1. Best platform:   {best_plat['platform']} (ROI = {best_plat['roi_pct']:+.1f}%)")
print(f"                      Consider increasing budget allocation here.")
print(f"  2. Worst platform:  {worst_plat['platform']} (ROI = {worst_plat['roi_pct']:+.1f}%)")
print(f"                      Receives {twitter_pct:.1f}% of budget — review or pause.")
print(f"  3. Top campaign:    {best_camp['campaign_name']}")
print(f"                      ROI = {best_camp['roi_pct']:+.1f}%, scale with more budget.")
print(f"  4. Weakest campaign:{worst_camp['campaign_name']}")
print(f"                      ROI = {worst_camp['roi_pct']:+.1f}%, audit creative or audience.")
roi_pos = (camp["roi_pct"] > 0).sum()
roi_neg = (camp["roi_pct"] < 0).sum()
print(f"  5. {roi_pos}/{len(camp)} campaigns are ROI-positive; {roi_neg} are losing money.")
print()


# ── 11. Export compact JSON for dashboard ────────────────────────────────────

PLATFORMS_LIST = ["Facebook", "Instagram", "Pinterest", "Twitter"]
GOALS_LIST     = ["Awareness", "Engagement", "Lead Generation", "Sales", "Traffic"]
AUDIENCES_LIST = sorted(df["audience"].unique().tolist())
CAMP_IDS       = [f"CMP-{str(i).zfill(3)}" for i in range(1, 17)]

start = df["date"].min()

rows = []
for _, r in df.iterrows():
    rows.append([
        (r["date"] - start).days,
        PLATFORMS_LIST.index(r["platform"]),
        GOALS_LIST.index(r["goal"]),
        AUDIENCES_LIST.index(r["audience"]),
        CAMP_IDS.index(r["campaign_id"]),
        round(r["spend"], 2),
        int(r["impressions"]),
        int(r["clicks"]),
        int(r["conversions"]),
        round(r["revenue"], 2),
    ])

output = {
    "platforms":  PLATFORMS_LIST,
    "goals":      GOALS_LIST,
    "audiences":  AUDIENCES_LIST,
    "start_date": start.strftime("%Y-%m-%d"),
    "rows":       rows,
}

out_path = Path("campaign_compact.json")
with open(out_path, "w") as f:
    import json
    json.dump(output, f, separators=(",", ":"))

print(f"Compact JSON written to {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
print("  Format: [date_offset, platform_idx, goal_idx, audience_idx,")
print("           campaign_idx, spend, impressions, clicks, conversions, revenue]")
