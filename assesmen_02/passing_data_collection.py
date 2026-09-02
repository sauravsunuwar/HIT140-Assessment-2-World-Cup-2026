import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import os

output_dir = os.path.dirname(os.path.abspath(__file__))

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


def collect_passing_data(match_api_url, stage):

    # Get match information
    response = requests.get(match_api_url, headers=headers)
    response.raise_for_status()

    match_data = response.json()

    # Get internal FIFA statistics ID
    stats_id = match_data["Properties"]["IdIFES"]

    # Get team statistics
    stats_url = (
        f"https://fdh-api.fifa.com/v1/stats/match/"
        f"{stats_id}/teams.json"
    )

    stats_response = requests.get(stats_url, headers=headers)
    stats_response.raise_for_status()

    team_stats = stats_response.json()

    # Get team IDs
    home_team_id = str(match_data["HomeTeam"]["IdTeam"])
    away_team_id = str(match_data["AwayTeam"]["IdTeam"])

    # Get team names
    home_team_name = (
        match_data["HomeTeam"]["TeamName"][0]["Description"]
    )

    away_team_name = (
        match_data["AwayTeam"]["TeamName"][0]["Description"]
    )

    team_names = {
        home_team_id: home_team_name,
        away_team_id: away_team_name
    }

    opponent_names = {
        home_team_id: away_team_name,
        away_team_id: home_team_name
    }

    rows = []

    # Determine official FIFA match result
    winner_id = match_data.get("Winner")

    if winner_id is not None:
        winner_id = str(winner_id)

        if winner_id == home_team_id:
            results = {
                home_team_id: "Win",
                away_team_id: "Loss"
            }

        elif winner_id == away_team_id:
            results = {
                home_team_id: "Loss",
                away_team_id: "Win"
            }

        else:
            results = {
                home_team_id: "Draw",
                away_team_id: "Draw"
            }

    else:
        results = {
            home_team_id: "Draw",
            away_team_id: "Draw"
        }

    # Extract passing statistics
    for team_id, stats in team_stats.items():

        stats_dict = {
            item[0]: item[1]
            for item in stats
        }

        passes = stats_dict.get("Passes")
        passes_completed = stats_dict.get("PassesCompleted")

        rows.append({
            "match_id": match_data["IdMatch"],
            "team": team_names.get(team_id, team_id),
            "opponent": opponent_names.get(team_id),
            "total_passes": passes,
            "passes_completed": passes_completed,
            "result": results.get(team_id),
            "stage": stage
        })

    return rows

# Get World Cup 2026 match list from FIFA
matches_url = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=500&IdCompetition=17&IdSeason=285023"
)

matches_response = requests.get(matches_url, headers=headers)
matches_response.raise_for_status()

matches_data = matches_response.json()



# Build match URLs automatically
match_urls = []

for match in matches_data["Results"]:

    match_id = match["IdMatch"]
    stage_id = match["IdStage"]

    stage_name = match["StageName"][0]["Description"]

    match_api_url = (
        f"https://api.fifa.com/api/v3/live/football/"
        f"17/285023/{stage_id}/{match_id}?language=en"
    )

    match_urls.append({
        "url": match_api_url,
        "stage": stage_name
    })

print("Total matches found:", len(match_urls))

all_rows = []
failed_matches = []

for i, match in enumerate(match_urls, start=1):

    print(f"Collecting match {i} of {len(match_urls)}...")

    try:
        rows = collect_passing_data(
            match["url"],
            match["stage"]
        )

        all_rows.extend(rows)

    except requests.exceptions.RequestException as e:
        print("Request failed. Retrying in 5 seconds...")
        time.sleep(5)

        try:
            rows = collect_passing_data(
                match["url"],
                match["stage"]
            )

            all_rows.extend(rows)

        except requests.exceptions.RequestException as e:
            print("Skipping match:", match["url"])
            failed_matches.append(match["url"])

    time.sleep(0.5)

print("Failed matches:", len(failed_matches))

df = pd.DataFrame(all_rows)
print("Total dataset rows:", len(df))

df["passing_accuracy"] = (
    df["passes_completed"] / df["total_passes"] * 100
).round(2)
print(df)
df.to_csv(
    os.path.join(output_dir, "passing_dataset.csv"),
    index=False
)

print("Dataset saved successfully.")
# -----------------------------
# Data validation
# -----------------------------

print("\n--- DATA VALIDATION ---")

print("Dataset shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nResult counts:")
print(df["result"].value_counts())

print("\nStage counts:")
print(df["stage"].value_counts())

print("\nPassing accuracy range:")
print("Minimum:", df["passing_accuracy"].min())
print("Maximum:", df["passing_accuracy"].max())
# -----------------------------
# Descriptive statistics
# -----------------------------

print("\n--- DESCRIPTIVE STATISTICS ---")

# Keep only decisive matches for Win vs Loss analysis
win_loss_df = df[df["result"].isin(["Win", "Loss"])].copy()

passing_summary = (
    win_loss_df.groupby("result")["passing_accuracy"]
    .agg(["count", "mean", "median", "std", "min", "max"])
    .round(2)
)

print("\nPassing accuracy by match result:")
print(passing_summary)
# -----------------------------
# Visualisation
# -----------------------------

win_data = win_loss_df[
    win_loss_df["result"] == "Win"
]["passing_accuracy"]

loss_data = win_loss_df[
    win_loss_df["result"] == "Loss"
]["passing_accuracy"]

plt.figure(figsize=(8, 6))

plt.boxplot(
    [win_data, loss_data],
    tick_labels=["Win", "Loss"]
)

plt.title("Passing Accuracy of Winning and Losing Teams")
plt.xlabel("Match Result")
plt.ylabel("Passing Accuracy (%)")

plt.tight_layout()
plt.savefig(
    os.path.join(
        output_dir,
        "passing_accuracy_boxplot.png"
    ),
    dpi=300
)
plt.show()
# -----------------------------
# Match-level passing differences
# -----------------------------

winner_data = (
    win_loss_df[win_loss_df["result"] == "Win"]
    [["match_id", "team", "passing_accuracy"]]
    .rename(columns={
        "team": "winner",
        "passing_accuracy": "winner_accuracy"
    })
)

loser_data = (
    win_loss_df[win_loss_df["result"] == "Loss"]
    [["match_id", "team", "passing_accuracy"]]
    .rename(columns={
        "team": "loser",
        "passing_accuracy": "loser_accuracy"
    })
)

match_differences = winner_data.merge(
    loser_data,
    on="match_id"
)

match_differences["accuracy_difference"] = (
    match_differences["winner_accuracy"]
    - match_differences["loser_accuracy"]
)
match_differences["accuracy_difference"] = (
    match_differences["accuracy_difference"].round(2)
)

print("\n--- MATCH-LEVEL DIFFERENCES ---")
print("Number of decisive matches:", len(match_differences))

print(
    "Mean difference:",
    round(match_differences["accuracy_difference"].mean(), 2)
)

print(match_differences.head())
# -----------------------------
# Confidence interval and hypothesis test
# -----------------------------

differences = match_differences["accuracy_difference"]

n = len(differences)
mean_diff = differences.mean()
std_diff = differences.std(ddof=1)
standard_error = std_diff / (n ** 0.5)

# 95% confidence interval
t_critical = stats.t.ppf(0.975, df=n - 1)

margin_error = t_critical * standard_error

ci_lower = mean_diff - margin_error
ci_upper = mean_diff + margin_error

print("\n--- 95% CONFIDENCE INTERVAL ---")
print("Mean difference:", round(mean_diff, 2))
print(
    "95% CI:",
    round(ci_lower, 2),
    "to",
    round(ci_upper, 2)
)

# One-sample t-test
# H0: mean winner-loser difference = 0
# H1: mean winner-loser difference > 0

t_statistic, two_sided_p = stats.ttest_1samp(
    differences,
    popmean=0
)

# Convert to one-sided p-value
if t_statistic > 0:
    p_value = two_sided_p / 2
else:
    p_value = 1 - (two_sided_p / 2)

print("\n--- ONE-SAMPLE T-TEST ---")
print("t-statistic:", round(t_statistic, 3))
print("p-value:", round(p_value, 5))
print("Degrees of freedom:", n - 1)
# -----------------------------
# Random sampling
# -----------------------------

sample_size = 50

sampled_matches = match_differences.sample(
    n=sample_size,
    random_state=42
)

print("\n--- RANDOM SAMPLE ---")
print("Population decisive matches:", len(match_differences))
print("Sample size:", len(sampled_matches))

print("\nSample preview:")
print(sampled_matches.head())
# -----------------------------
# Sample-based analysis
# -----------------------------

sample_diff = sampled_matches["accuracy_difference"]

print("\n--- SAMPLE DESCRIPTIVE STATISTICS ---")
print("Sample mean difference:", round(sample_diff.mean(), 2))
print("Sample median difference:", round(sample_diff.median(), 2))
print("Sample standard deviation:", round(sample_diff.std(ddof=1), 2))
print("Sample minimum:", round(sample_diff.min(), 2))
print("Sample maximum:", round(sample_diff.max(), 2))

# 95% confidence interval
sample_n = len(sample_diff)
sample_mean = sample_diff.mean()
sample_std = sample_diff.std(ddof=1)
sample_se = sample_std / (sample_n ** 0.5)

sample_t_critical = stats.t.ppf(
    0.975,
    df=sample_n - 1
)

sample_margin_error = (
    sample_t_critical * sample_se
)

sample_ci_lower = (
    sample_mean - sample_margin_error
)

sample_ci_upper = (
    sample_mean + sample_margin_error
)

print("\n--- SAMPLE 95% CONFIDENCE INTERVAL ---")
print("Mean difference:", round(sample_mean, 2))
print(
    "95% CI:",
    round(sample_ci_lower, 2),
    "to",
    round(sample_ci_upper, 2)
)

# One-sample t-test
sample_t_statistic, sample_two_sided_p = stats.ttest_1samp(
    sample_diff,
    popmean=0
)

if sample_t_statistic > 0:
    sample_p_value = sample_two_sided_p / 2
else:
    sample_p_value = 1 - (sample_two_sided_p / 2)

print("\n--- SAMPLE ONE-SAMPLE T-TEST ---")
print(
    "t-statistic:",
    round(sample_t_statistic, 3)
)
print(
    "p-value:",
    round(sample_p_value, 5)
)
print(
    "Degrees of freedom:",
    sample_n - 1
)
# -----------------------------
# Final sample-based visualisation
# -----------------------------

plt.figure(figsize=(8, 6))

plt.hist(
    sampled_matches["accuracy_difference"],
    bins=10,
    edgecolor="black"
)

plt.axvline(
    sampled_matches["accuracy_difference"].mean(),
    linestyle="--",
    label="Mean difference"
)

plt.axvline(
    0,
    linestyle=":",
    label="No difference"
)

plt.title(
    "Winner–Loser Passing Accuracy Differences\n"
    "Random Sample of 50 Decisive Matches"
)

plt.xlabel(
    "Passing Accuracy Difference "
    "(Winner % - Loser %)"
)

plt.ylabel("Number of Matches")

plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        output_dir,
        "sample_passing_accuracy_difference.png"
    ),
    dpi=300
)

plt.show()

sampled_matches.to_csv(
    os.path.join(
        output_dir,
        "passing_random_sample_50.csv"
    ),
    index=False
)

print("Random sample saved successfully.")