# news_risk

This project attempts to construct a political uncertainty index for Spain as a response to the work of Baker, Bloom and Davis (MEASURING ECONOMIC POLICY UNCERTAINTY, Oct 2015).

In a first stage, we collect all the economy related articles from El Pais archives. We parse the body of articles and subset those that contain words related to both economy, policy, and uncertainty.

Finally we do some analysis of the relation between the index and stock market risk measures and the index and the economy. We see that in a VAR setting the index has predictive power on the economic activity, which is robust to the addition to other explanatory variables. Increases in the uncertainty index predict significant and enduring decreases in economic activity.