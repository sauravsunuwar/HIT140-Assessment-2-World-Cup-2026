TASK - 1 (ATTACKING Efficiency)

*Data Source that have been used*

All the data that have been used for this asessment are from official website if the *FIFA*, *FB Ref* and *The Stat Don't Lie*. The provided data are genuine and are all credit gies to these following links.
*FIFA Official Website*: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics
*The Stats Don't Lie*: https://www.thestatsdontlie.com/football/world-cup-2026/
*FB Ref*: https://fbref.com/en/
*Squad Shooting*: https://fbref.com/en/comps/1/shooting/World-Cup-Stats
From this source I have extract the data of UEFA Nations and COMBEMOL Nations along with their matches by using the python the code to filter all the remaning nations besides these nations. 
All these are analysis through the format: Analyatic question formulation, data wrangling, data preparation & sample, descriptive statistics and t-test.


*Analytic/Researched Question*
Is there a statistically significant difference in shot conversion rate (goals per shot) between teams from UEFA and teams from CONMEBOL in the 2026 World Cup?

*Data Preparation*
Collect the raw data using the official websites and gather all the Nations in one file.
Flter out all the countries that are not in those group. 
The result was:
*CONMEBOL Nations* : 6 Teams
Argentina, Brazil, Uruguay, Colombia, Ecuador, Paraguay

*UEFA Nations* : 16 Teams
Spain, France, England, Germany, Netherlands, Belgium, Portugal, Croatia, Switzerland, Austria, Norway, Scotland, Czechia, Türkiye, Sweden, Bosnia–Herz

*Sample*: the conversion rate observed for all the UEFA teams qualifying to play in the 2026 World Cup (n=16) and all the CONMEBOL teams qualifying to play in the 2026 World Cup (n=6).

*Sampling Technique*: Since every team qualifying from each confederation has been selected for this analysis, this is a census of the 2026 World Cup participants for each confederation, and not a random sample of a larger population. However, the purpose of conducting this study is to draw inferences about the general attacking ability of each confederation based on its performance in this single event. This is one of the limitations of this study.

*Descriptive Statistics*
While the average conversion rate is higher for UEFA teams (Mean * 100% = 12.66%) compared to that of CONMEBOL teams (Mean * 100% = 8.85%), the distribution of CONMEBOL teams is wider than that of UEFA teams because of their size. This happens mostly due to Argentina’s outlier tournament (Max * 100% = 15.8%), as shown below.

Please check *Descriptive_Status* figure

*Confidence Intervels(95%)*
As shown in the data below, Hypothesis test outcome  is indicated by the fact that the confidence interval of 95% for the difference in means includes zero: It is not possible to reject the hypothesis that there is no difference between UEFA and CONMEBOL exchange rates with 95% confidence level from the sample data.

Please check *Conversion_rate_for_groups* figure

*Inferential Statistics - Two Sample t-test*
H0: μ_UEFA = μ_CONMEBOL      H1: μ_UEFA ≠ μ_CONMEBOL
H0 = Welch's t-test          H1 = Anish's t-test
These are independent samples of different teams, therefore, an independent two-sample t-test was performed. As the two sample sizes are unequal (n=16 and n=6), the t-test that does not assume equal variances is Welch's t-test. Anish's t-test is also given for comparison purposes.

please check *t-test_status* figure

As p = 0.135 > 0.05, at std dev = 0.05, we cannot reject H₀. Therefore, at 95% confidence interval, we don't have enough statistical evidence to conclude that there is any difference between the shooting success rate of CONMEBOL and UEFA teams in the 2026 FIFA World Cup.
Robustness check: due to small sample size of CONMEBOL teams, a nonparametric Mann Whitney U test was performed, where no assumption of normally distributed data is made. Both tests are consistent: U = 67.5, p = 0.161.

*Conclusion*
Although UEFA teams achieved a higher average shot conversion rate compared to CONMEBOL teams at the 2026 FIFA World Cup (12.7% versus 8.9%), the difference in the average values is not statistically significant (t(9.48)=1.63, p=0.135). Confidence interval for the difference in the mean values, [-0.014, 0.091], contains zero. Small sample size of the CONMEBOL teams (n=6), especially due to one good-performing team (Argentina) among the CONMEBOL teams, reduces the statistical power of the test; a larger sample size is required for detection of a statistically significant difference.