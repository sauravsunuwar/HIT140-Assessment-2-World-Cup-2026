# Analytic Task 1 – Passing Performance

## Research Question

**Do winning teams have significantly higher mean passing accuracy than losing teams in FIFA World Cup 2026 decisive matches?**

## Data Source

Data for this analysis were obtained from the FIFA World Cup 2026 official statistics source provided for this assessment:

FIFA World Cup 2026 Statistics:
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics

The FIFA match and team statistics were collected and processed programmatically using Python. The analysis uses team-level passing statistics, including total passes and completed passes, to calculate passing accuracy.

### FIFA Endpoints Used

- Match list: `https://api.fifa.com/api/v3/calendar/matches`
- Match information: `https://api.fifa.com/api/v3/live/football/`
- Team statistics: `https://fdh-api.fifa.com/v1/stats/match/`

The collected and processed data are available in `passing_dataset.csv`.

## Data Preparation

The complete dataset contained **104 matches**, producing **208 team-match observations**.

Passing accuracy for each team was calculated as:

**Passing Accuracy = (Passes Completed / Total Passes) × 100**

The dataset was checked for missing values and duplicate observations before analysis.

Because the research question compares winning and losing teams, drawn matches were excluded from the inferential comparison. This resulted in a population of **84 decisive matches**.

For each decisive match, a paired difference was calculated as:

**Passing Accuracy Difference = Winner Passing Accuracy − Loser Passing Accuracy**

This match-level approach directly compares the winner and loser from the same match.

## Sampling

A **simple random sample of 50 decisive matches** was selected without replacement from the population of 84 decisive matches.

A fixed random state (`random_state=42`) was used to ensure that the sampling process was reproducible.

The resulting sample is available in `passing_random_sample_50.csv`.

## Descriptive Statistics

For the random sample of 50 decisive matches, the winner-minus-loser passing accuracy differences produced the following results:

| Statistic | Result |
|---|---:|
| Sample size | 50 matches |
| Mean difference | 5.02 percentage points |
| Median difference | 5.55 percentage points |
| Standard deviation | 9.56 percentage points |
| Minimum difference | -27.29 percentage points |
| Maximum difference | 33.07 percentage points |

The positive mean indicates that winning teams had passing accuracy approximately **5.02 percentage points higher on average** than losing teams in the sampled matches.

However, the negative minimum difference shows that not every winning team had higher passing accuracy than its opponent.

## Confidence Interval

A **95% confidence interval** was calculated for the population mean winner-minus-loser passing accuracy difference.

**95% CI: 2.30 to 7.74 percentage points**

Because the entire confidence interval is above zero, the results support a positive mean difference in passing accuracy between winning and losing teams.

## Hypothesis Test

A **one-sample t-test** was conducted on the 50 match-level winner-minus-loser passing accuracy differences.

The hypotheses were:

**H₀:** Mean winner-minus-loser passing accuracy difference = 0

**H₁:** Mean winner-minus-loser passing accuracy difference > 0

The test produced:

- **t(49) = 3.713**
- **p = 0.00026**

Using a significance level of **α = 0.05**, the p-value is below 0.05. Therefore, the null hypothesis was rejected.

## Conclusion

The analysis provides **statistically significant evidence that winning teams had higher passing accuracy than losing teams on average** in the sampled FIFA World Cup 2026 decisive matches.

The estimated mean advantage for winning teams was **5.02 percentage points**, with a **95% confidence interval from 2.30 to 7.74 percentage points**.

These findings indicate an **association between higher passing accuracy and winning**. However, the analysis does not establish that higher passing accuracy causes a team to win, as match outcomes are influenced by many other factors.

## Files

- `passing_data_collection.py` – Python code used for data collection, preparation, sampling and statistical analysis
- `passing_dataset.csv` – Complete processed dataset containing 208 team-match observations
- `passing_random_sample_50.csv` – Random sample of 50 decisive matches used for inferential analysis
- `passing_accuracy_boxplot.png` – Comparison of passing accuracy for winning and losing teams
- `sample_passing_accuracy_difference.png` – Distribution of winner-minus-loser passing accuracy differences
-  `screenshots/` – VS Code execution evidence showing successful data collection, data validation and final sample statistical analysis
