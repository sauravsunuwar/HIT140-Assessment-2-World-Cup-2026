## Analytic Task 1 – Passing Performance

### Research Question
Do winning teams have significantly higher mean passing accuracy than losing teams in FIFA World Cup 2026 decisive matches?

### Data Source
Official FIFA World Cup 2026 match and team statistics were collected and processed using Python.

### Data Preparation
Passing accuracy was calculated as:

**Passing Accuracy = (Passes Completed / Total Passes) × 100**

The complete dataset contained 104 matches and 208 team-match observations. Drawn matches were excluded from the winner-versus-loser comparison, resulting in a population of 84 decisive matches.

For each decisive match, a paired difference was calculated as:

**Winner Passing Accuracy − Loser Passing Accuracy**

### Sampling
A simple random sample of 50 decisive matches was selected from the population of 84 decisive matches. A fixed random state (`random_state=42`) was used to make the sampling process reproducible.

### Statistical Analysis
The sample produced:

- Mean difference: **5.02 percentage points**
- Median difference: **5.55 percentage points**
- Standard deviation: **9.56**
- 95% confidence interval: **2.30 to 7.74 percentage points**

A one-sample t-test was conducted on the winner-minus-loser passing accuracy differences.

**H₀:** Mean difference = 0  
**H₁:** Mean difference > 0

The test produced:

- **t(49) = 3.713**
- **p = 0.00026**

Since p < 0.05, the null hypothesis was rejected.

### Conclusion
The analysis provides statistically significant evidence that winning teams had higher passing accuracy than losing teams on average in the sampled FIFA World Cup 2026 decisive matches.

The result indicates an association between passing accuracy and winning, but does not establish that higher passing accuracy causes a team to win.
