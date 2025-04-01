This script predicts Super Rugby match outcomes using team ratings and ranking adjustments based on historical results. It also estimates the expected points table at the end of the season.

How It Works

Loads Data:

Historical results (past match outcomes and scores).

Current season fixtures (upcoming matches).

Initial team points from points.xlsx.

Team Ratings & Home Advantage:

Each team starts with an initial rating.

Home teams receive a small advantage (+3 points).

Win Probability Calculation:

Uses team ratings and home advantage to determine the probability of a home win.

Ranking Adjustments:

Ratings are adjusted based on match results and score differences.

Ensures fair adjustments when lower-rated teams outperform expectations.

Fixture Predictions:

Generates predicted match outcomes based on team ratings.

Includes probabilities for bonus points (winning margin and losing within 7 points).

Expected Points Table:

Updates the season points table based on predicted outcomes.
