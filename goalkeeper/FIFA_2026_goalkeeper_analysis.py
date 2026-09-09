# FIFA World Cup 2026 - Goalkeeper Analysis
#
# Question: Did knockout teams have a higher save percentage
# than teams that went out in the group stage?
#
# Steps:
# 1. Load player stats and roll them up to one row per squad
# 2. Label knockout teams as those with 4 or more matches
# 3. Take a random sample of 32 squads
# 4. Descriptive statistics
# 5. 95% confidence interval
# 6. Welch t-test (knockout vs group stage)
# 7. Assumption checks and charts

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

SCRIPT_FOLDER = Path(__file__).resolve().parent
DATA_FOLDER = SCRIPT_FOLDER / "data"
OUTPUT_FOLDER = SCRIPT_FOLDER / "output"
PLAYERS_FILE = DATA_FOLDER / "wc2026_goalkeeper_players.csv"
RANDOM_SEED = 42
SAMPLE_SIZE = 32

SQUAD_COLUMNS = [
    "Squad",
    "Players_Used",
    "MP",
    "Starts",
    "Minutes",
    "Nineties",
    "GA",
    "GA90",
    "SoTA",
    "Saves",
    "Save_Pct",
    "CS",
    "CS_Pct",
    "PKatt",
    "PKA",
    "PKsv",
    "PKm",
    "PK_Save_Pct",
]


def squads_from_player_csv(path: Path) -> pd.DataFrame:
    players = pd.read_csv(path)
    players = players[players["minutes"] > 0].copy()

    grouped = players.groupby("squad", as_index=False).agg(
        Players_Used=("player", "nunique"),
        max_gp=("gp", "max"),
        Starts=("starts", "sum"),
        Minutes=("minutes", "sum"),
        GA=("ga", "sum"),
        Saves=("saves", "sum"),
        CS=("cs", "sum"),
        PKatt=("pkatt", "sum"),
        PKA=("pka", "sum"),
        PKsv=("pksv", "sum"),
    )
    grouped["MP"] = np.maximum(grouped["max_gp"], grouped["Starts"])
    grouped["Nineties"] = grouped["Minutes"] / 90
    grouped["GA90"] = grouped["GA"] / grouped["Nineties"]
    grouped["SoTA"] = grouped["Saves"] + grouped["GA"]
    grouped["Save_Pct"] = np.where(
        grouped["SoTA"] > 0,
        grouped["Saves"] / grouped["SoTA"] * 100,
        np.nan,
    )
    grouped["CS_Pct"] = np.where(
        grouped["MP"] > 0,
        grouped["CS"] / grouped["MP"] * 100,
        np.nan,
    )
    grouped["PKm"] = grouped["PKatt"] - grouped["PKA"] - grouped["PKsv"]
    grouped["PK_Save_Pct"] = np.where(
        grouped["PKatt"] > 0,
        grouped["PKsv"] / grouped["PKatt"] * 100,
        np.nan,
    )
    grouped = grouped.rename(columns={"squad": "Squad"})
    return grouped[SQUAD_COLUMNS]


def clean_squad_table(table: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [col for col in table.columns if col != "Squad"]
    table = table.copy()
    table[numeric_columns] = table[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    table = table.drop_duplicates(subset="Squad")
    table = table.dropna(subset=["MP", "Save_Pct"])

    # 2026 format: 3 group matches, 4+ means they reached knockout
    table["Stage_Group"] = np.where(
        table["MP"] >= 4, "Knockout", "Group Stage"
    )
    return table.reset_index(drop=True)


def load_squad_table() -> pd.DataFrame:
    if not PLAYERS_FILE.exists():
        raise FileNotFoundError(
            f"Missing data file: {PLAYERS_FILE.name}"
        )
    return clean_squad_table(squads_from_player_csv(PLAYERS_FILE))


def describe_save_percentage(sample: pd.DataFrame) -> pd.DataFrame:
    descriptive = sample.groupby("Stage_Group")["Save_Pct"].agg(
        n="count",
        mean="mean",
        median="median",
        standard_deviation="std",
        minimum="min",
        q1=lambda x: x.quantile(0.25),
        q3=lambda x: x.quantile(0.75),
        maximum="max",
    )
    descriptive["iqr"] = descriptive["q3"] - descriptive["q1"]
    return descriptive


def mean_confidence_interval(values: pd.Series) -> tuple[float, float, float]:
    mean = values.mean()
    ci_low, ci_high = stats.t.interval(
        confidence=0.95,
        df=len(values) - 1,
        loc=mean,
        scale=stats.sem(values),
    )
    return mean, ci_low, ci_high


def welch_test(sample: pd.DataFrame):
    knockout = sample.loc[sample["Stage_Group"] == "Knockout", "Save_Pct"]
    group_stage = sample.loc[sample["Stage_Group"] == "Group Stage", "Save_Pct"]
    test = stats.ttest_ind(knockout, group_stage, equal_var=False)
    return knockout, group_stage, test


def save_boxplot(sample: pd.DataFrame, path: Path) -> None:
    sns.set_theme(style="whitegrid")
    ax = sns.boxplot(data=sample, x="Stage_Group", y="Save_Pct")
    sns.stripplot(
        data=sample,
        x="Stage_Group",
        y="Save_Pct",
        color="black",
        alpha=0.65,
        ax=ax,
    )
    ax.set(
        title="Goalkeeper Save Percentage by Tournament Progression",
        xlabel="Tournament progression",
        ylabel="Save percentage (%)",
    )
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def save_leaderboard_plot(table: pd.DataFrame, path: Path) -> None:
    top = table.nlargest(12, "Save_Pct").sort_values("Save_Pct")
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(
        data=top,
        x="Save_Pct",
        y="Squad",
        hue="Stage_Group",
        dodge=False,
    )
    ax.set(
        title="Highest Squad Save Percentage - FIFA World Cup 2026",
        xlabel="Save percentage (%)",
        ylabel="",
    )
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    print("FIFA World Cup 2026 - Goalkeeper Analysis")
    print()

    print("Step 1: Load squad data")
    table = load_squad_table()
    print(f"File: {PLAYERS_FILE.name}")
    print(f"Squads loaded: {len(table)}")
    print()

    print("Step 2: Label knockout vs group stage")
    print(table["Stage_Group"].value_counts().to_string())
    if len(table) != 48:
        print(f"Warning: expected 48 squads, found {len(table)}")
    if not (table["MP"] >= 3).all():
        print("Warning: at least one squad has fewer than 3 matches")
    print()

    print("Step 3: Random sample of 32 squads")
    sample_n = min(SAMPLE_SIZE, len(table))
    sample = table.sample(n=sample_n, random_state=RANDOM_SEED).copy()
    print(f"Sample size: {len(sample)}")
    print()

    print("Step 4: Descriptive statistics (Save %)")
    descriptive = describe_save_percentage(sample)
    print(descriptive.round(2))
    print()

    print("Step 5: 95% confidence interval")
    mean, ci_low, ci_high = mean_confidence_interval(sample["Save_Pct"])
    print(f"Sample mean Save % = {mean:.2f}%")
    print(f"95% CI = [{ci_low:.2f}%, {ci_high:.2f}%]")
    print()

    print("Step 6: Welch t-test")
    knockout, group_stage, test = welch_test(sample)
    print(f"Knockout mean = {knockout.mean():.2f}% (n={len(knockout)})")
    print(f"Group-stage mean = {group_stage.mean():.2f}% (n={len(group_stage)})")
    print(
        f"Welch t = {test.statistic:.3f}, df = {test.df:.3f}, "
        f"p = {test.pvalue:.3f}"
    )
    if test.pvalue < 0.05:
        print("Decision: Reject H0")
    else:
        print("Decision: Fail to reject H0")
    print()

    print("Step 7: Assumption checks")
    if len(knockout) >= 3:
        print("Knockout Shapiro-Wilk:", stats.shapiro(knockout))
    if len(group_stage) >= 3:
        print("Group-stage Shapiro-Wilk:", stats.shapiro(group_stage))
    if len(knockout) >= 2 and len(group_stage) >= 2:
        print("Levene variance test:", stats.levene(knockout, group_stage))
    print()

    print("Leaders (full tournament)")
    leaders = table.nlargest(8, "Save_Pct")[
        ["Squad", "Stage_Group", "MP", "Saves", "GA", "Save_Pct", "CS"]
    ]
    print(leaders.round(2).to_string(index=False))
    print()

    box_file = OUTPUT_FOLDER / "goalkeeper_save_percentage.png"
    bar_file = OUTPUT_FOLDER / "goalkeeper_save_percentage_leaders.png"
    save_boxplot(sample, box_file)
    save_leaderboard_plot(table, bar_file)

    sample.to_csv(OUTPUT_FOLDER / "goalkeeper_selected_sample.csv", index=False)
    table.to_csv(OUTPUT_FOLDER / "goalkeeper_all_squads.csv", index=False)
    descriptive.to_csv(OUTPUT_FOLDER / "goalkeeper_descriptive_statistics.csv")
    print(f"Chart saved: {box_file.name}")
    print(f"Leaderboard saved: {bar_file.name}")


if __name__ == "__main__":
    main()
