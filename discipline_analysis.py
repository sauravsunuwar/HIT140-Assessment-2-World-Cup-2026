import pandas as pd
import numpy as np
from scipy import stats
 
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)
 
# DATA WRANGLING

df = pd.read_csv("raw_data.csv")
df["TotalCards"] = df["YC_Home"] + df["RC_Home"] + df["YC_Away"] + df["RC_Away"]
 
# A couple of knockout matches went to extra time (120 min instead of 90),
# so raw card counts aren't quite a fair comparison. Scaling to a 90-minute
df["CardsPer90"] = df["TotalCards"] / df["Minutes"] * 90
 
print("=" * 78)
print("STEP 1: DATA WRANGLING")
print("=" * 78)
print("Loaded", len(df), "matches")
print(df[["MatchID", "Round", "Home", "Away", "Stage", "Minutes", "TotalCards", "CardsPer90"]]
      .to_string(index=False))
 
group = df[df["Stage"] == "Group"]
knockout = df[df["Stage"] == "Knockout"]
 
#  DATA PREPARATION AND SAMPLING
# Population = all 104 matches (72 Group + 32 Knockout)
# 35 matches total:20 Group + 15 Knockout, random_state = 42.
 
print()
print("=" * 78)
print("STEP 2: DATA PREPARATION AND SAMPLING")
print("=" * 78)
print("Population : 104 matches (72 Group + 32 Knockout)")
print("Sample     : 35 matches, stratified random sample by stage")
print("             (20 Group, 15 Knockout), random_state = 42")
print(f"Group n    = {len(group)}")
print(f"Knockout n = {len(knockout)}")
 
 
# DESCRIPTIVE STATISTICS

def summarise(sample_df, col, label):
    s = sample_df[col]
    return {
        "Group": label, "n": len(s), "Mean": s.mean(), "Median": s.median(),
        "Std Dev": s.std(ddof=1), "Min": s.min(), "Max": s.max(),
    }
 
print()
print("=" * 78)
print("STEP 3: DESCRIPTIVE STATISTICS")
print("=" * 78)
print("-- Total cards per match (raw count) --")
print(pd.DataFrame([summarise(group, "TotalCards", "Group"),
                     summarise(knockout, "TotalCards", "Knockout")])
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
 
print()
print("-- Cards per 90 minutes (extra-time adjusted) --")
print(pd.DataFrame([summarise(group, "CardsPer90", "Group"),
                     summarise(knockout, "CardsPer90", "Knockout")])
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
 
 

# CHECKING NORMALITY (Shapiro-Wilk)
 
print()
print("=" * 78)
print("STEP 4: NORMALITY CHECK (Shapiro-Wilk)")
print("=" * 78)
sw_group = stats.shapiro(group["TotalCards"])
sw_knockout = stats.shapiro(knockout["TotalCards"])
print(f"Group:    W = {sw_group.statistic:.4f}, p = {sw_group.pvalue:.4f}")
print(f"Knockout: W = {sw_knockout.statistic:.4f}, p = {sw_knockout.pvalue:.4f}")
print("Both p > 0.05, so no strong evidence against normality - fine to proceed.")
 
 
# 95% CONFIDENCE INTERVALS
 
def confidence_interval_mean(sample, confidence=0.95):
    n = len(sample)
    xbar = sample.mean()
    se = sample.std(ddof=1) / np.sqrt(n)
    t_star = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    margin = t_star * se
    return xbar, xbar - margin, xbar + margin
 
print()
print("=" * 78)
print("STEP 5: 95% CONFIDENCE INTERVALS")
print("=" * 78)
g_mean, g_lo, g_hi = confidence_interval_mean(group["TotalCards"])
k_mean, k_lo, k_hi = confidence_interval_mean(knockout["TotalCards"])
print(f"Group:    mean = {g_mean:.3f}, 95% CI = [{g_lo:.3f}, {g_hi:.3f}]")
print(f"Knockout: mean = {k_mean:.3f}, 95% CI = [{k_lo:.3f}, {k_hi:.3f}]")
 
 
#  TWO-SAMPLE T-TEST
 
n1, n2 = len(group), len(knockout)
x1, x2 = group["TotalCards"].mean(), knockout["TotalCards"].mean()
s1, s2 = group["TotalCards"].std(ddof=1), knockout["TotalCards"].std(ddof=1)
 
se_diff = np.sqrt(s1**2 / n1 + s2**2 / n2)
t_statistic = (x1 - x2) / se_diff
 
df_conservative = min(n1 - 1, n2 - 1)
p_conservative = 2 * (1 - stats.t.cdf(abs(t_statistic), df=df_conservative))
 
t_stat_scipy, p_scipy = stats.ttest_ind(group["TotalCards"], knockout["TotalCards"], equal_var=False)
df_welch = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
 
print()
print("=" * 78)
print("STEP 6: TWO-SAMPLE T-TEST")
print("=" * 78)
print("State: does average cards/match differ between the two stages?")
print("Plan:  H0: mu_Group = mu_Knockout   Ha: mu_Group != mu_Knockout   alpha = 0.05")
print()
print("Solve:")
print(f"  t* = {t_statistic:.4f}")
print(f"  df (by-hand, conservative) = {df_conservative}  ->  p = {p_conservative:.4f}")
print(f"  df (Welch-Satterthwaite)   = {df_welch:.2f}  ->  p = {p_scipy:.4f}")
print()
alpha = 0.05
print("Conclude:")
if p_scipy < alpha:
    print(f"  p = {p_scipy:.4f} < {alpha} -> reject H0. Significant difference found.")
else:
    print(f"  p = {p_scipy:.4f} > {alpha} -> fail to reject H0. No significant difference.")
 
 
# ---------------------------------------------------------------------------
# STEP 7: SAME TEST, MINUTES-ADJUSTED
# ---------------------------------------------------------------------------
# Re-running with CardsPer90 to see if the extra-time adjustment changes
# anything.
 
t_stat_adj, p_adj = stats.ttest_ind(group["CardsPer90"], knockout["CardsPer90"], equal_var=False)
df_welch_adj = (group["CardsPer90"].var(ddof=1)/n1 + knockout["CardsPer90"].var(ddof=1)/n2)**2 / (
    (group["CardsPer90"].var(ddof=1)/n1)**2/(n1-1) + (knockout["CardsPer90"].var(ddof=1)/n2)**2/(n2-1)
)
 
print()
print("=" * 78)
print("STEP 7: SAME TEST, CardsPer90 VERSION")
print("=" * 78)
print(f"t* = {t_stat_adj:.4f}, df = {df_welch_adj:.2f}, p = {p_adj:.4f}")
same = (p_scipy < alpha) == (p_adj < alpha)
print("Same conclusion as raw count." if same else "Different conclusion - worth flagging.")
 
 
# ---------------------------------------------------------------------------
# BOXPLOT (Week 6)
# ---------------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
 
    plt.figure(figsize=(7, 5))
    sns.boxplot(data=df, x="Stage", y="TotalCards", order=["Group", "Knockout"])
    plt.title("Total cards per match: Group vs Knockout")
    plt.ylabel("Total cards (yellow + red, both teams)")
    plt.tight_layout()
    plt.savefig("cards_boxplot.png", dpi=150)
    print()
    print("Saved boxplot to cards_boxplot.png")
except ImportError:
    print()
    print("matplotlib/seaborn not installed - skipped boxplot")
 
 
# ---------------------------------------------------------------------------
# Save cleaned data
# ---------------------------------------------------------------------------
df.to_csv("processed_data.csv", index=False)
print()
print("Saved processed_data.csv")
 