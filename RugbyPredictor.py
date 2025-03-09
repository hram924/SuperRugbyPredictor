import pandas as pd
import numpy as np

# Load historical results
historical_results = pd.read_excel('Results.xlsx')

# Load current season fixtures
fixtures = pd.read_excel('Fixtures.xlsx')

# Initialize team rankings based on last available data, with 0 adjustments
teams = ["Hurricanes", "Blues", "Brumbies", "Chiefs", "Reds", 
    "Highlanders", "Fijian Drua", "Rebels", "Crusaders", "Force", 
    "Moana Pasifika", "Waratahs"]
initial_ranking = 80  # example starting rating
team_ratings = {team: initial_ranking for team in teams}

# Load initial points for each team from points.xlsx
initial_points = pd.read_excel('points.xlsx', index_col='Team')
points_table = initial_points['Points'].to_dict()

# Define home advantage
HOME_ADVANTAGE = 3

# Calculate win probability based on team ratings
def calculate_win_probability(home_rating, away_rating):
    rating_diff = home_rating - away_rating + HOME_ADVANTAGE
    probability = 1 / (1 + 10 ** (-rating_diff / 10))
    return probability

# Apply ranking adjustment rules
def apply_ranking_adjustment(home_team, away_team, home_score, away_score):
    pre_match_home = team_ratings[home_team] + HOME_ADVANTAGE
    pre_match_away = team_ratings[away_team]
      
    # Calculate the score difference and "Modified pre-match Ranking Scores" difference D
    score_diff = home_score - away_score
    D = pre_match_home - pre_match_away
    
       # Check if the higher-rated team won and has at least a 10-point higher ranking
    if (home_score > away_score and pre_match_home >= pre_match_away + 10) or \
       (away_score > home_score and pre_match_away >= pre_match_home + 10):
        return  # Exit function with no adjustment
    
    # Determine adjustment based on the game outcome and score difference
    if home_score > away_score:  # Home team wins
        if score_diff >= 16:
            adjustment = min((10 + pre_match_away - pre_match_home) * 0.15, 3)
        else:
            adjustment = min((10 + pre_match_away - pre_match_home) * 0.1, 2)
        team_ratings[home_team] += adjustment
        team_ratings[away_team] -= adjustment
    elif away_score > home_score:  # Away team wins
        if score_diff <= -16:
            adjustment = min((10 + pre_match_home - pre_match_away) * 0.15, 3)
        else:
            adjustment = min((10 + pre_match_home - pre_match_away) * 0.1, 2)
        team_ratings[home_team] -= adjustment
        team_ratings[away_team] += adjustment
    else:  # Draw
        adjustment = min(D * 0.1, 1)
        team_ratings[home_team] += adjustment
        team_ratings[away_team] += adjustment

def calculate_expected_points(prob_win, prob_draw, prob_bonus_win, prob_bonus_lose):
    points = (prob_win * 4) + (prob_draw * 2)  # 4 for win, 2 for draw
    points += prob_bonus_win * 1  # Bonus for scoring tries
    points += prob_bonus_lose * 1  # Bonus for losing by fewer than 7 points
    return points
    
# Update team rankings based on historical results
for _, row in historical_results.iterrows():
    home_team, away_team = row['Home Team'], row['Away Team']
    home_score, away_score = row['Home Team Score'], row['Away Team Score']
    apply_ranking_adjustment(home_team, away_team, home_score, away_score)

# Generate fixture predictions
fixture_predictions = []
for _, row in fixtures.iterrows():
    home_team, away_team = row['Home Team'], row['Away Team']
    home_prob = calculate_win_probability(team_ratings[home_team], team_ratings[away_team])
    fixture_predictions.append({
        "Home Team": home_team,
        "Away Team": away_team,
        "% Home Win": round(home_prob * 100, 2)
    })
# Generate fixture predictions and calculate bonus points
for fixture in fixture_predictions:
    home_team = fixture["Home Team"]
    away_team = fixture["Away Team"]
    prob_home_win = fixture["% Home Win"] / 100
    prob_draw = 0.05  # example draw probability

    # Adjusted ranking difference (includes home advantage)
    ranking_diff = (team_ratings[home_team] + HOME_ADVANTAGE) - team_ratings[away_team]
    abs_diff = abs(ranking_diff)  # Absolute ranking difference

    # Winning Bonus Point Probability (3+ tries margin)
    if ranking_diff > 0:  # Home team is stronger
        prob_bonus_home_win = max(0.1, min(0.5, 0.2 + (abs_diff / 40)))  # Adjusted for wider gap
        prob_bonus_away_win = max(0.05, min(0.2, 0.15 - (abs_diff / 80)))  # Decrease more with widening gap
    else:  # Away team is stronger
        prob_bonus_home_win = max(0.05, min(0.2, 0.15 - (abs_diff / 80)))  # Decrease more with widening gap
        prob_bonus_away_win = max(0.1, min(0.5, 0.2 + (abs_diff / 40)))  # Adjusted for wider gap

    # Losing Bonus Point Probability (losing by ≤7 points)
    if ranking_diff > 0:  # Home team is stronger
        prob_bonus_home_lose = max(0.1, min(0.5, 0.4 - (abs_diff / 40)))  # Adjusted for wider gap
        prob_bonus_away_lose = max(0.2, min(0.6, 0.3 + (abs_diff / 30)))  # Increase with gap
    else:  # Away team is stronger
        prob_bonus_home_lose = max(0.2, min(0.6, 0.3 + (abs_diff / 30)))  # Increase with gap
        prob_bonus_away_lose = max(0.1, min(0.5, 0.4 - (abs_diff / 40)))  # Adjusted for wider gap

    # Update points table with adjusted expected points
    points_table[home_team] += calculate_expected_points(prob_home_win, prob_draw, prob_bonus_home_win, prob_bonus_home_lose)
    points_table[away_team] += calculate_expected_points(1 - prob_home_win, prob_draw, prob_bonus_away_win, prob_bonus_away_lose)

# Display output
print("Team Rankings")
sorted_rankings = sorted(
    [(team, rating) for team, rating in team_ratings.items() if team != "Rebels"],
    key=lambda x: x[1],
    reverse=True
)

for rank, (team, rating) in enumerate(sorted_rankings, start=1):
    print(f"{rank}. {team}: {rating:.2f}")

print("\nFixture Predictions:")
for fixture in fixture_predictions:
    print(f"{fixture['Home Team']} vs {fixture['Away Team']}: {fixture['% Home Win']}% chance for Home Team win")

print("\nEstimated Points Table at End of Season:")
sorted_points = sorted(points_table.items(), key=lambda x: x[1], reverse=True)
for rank, (team, points) in enumerate(sorted_points, start=1):
    print(f"{rank}. {team}: {points:.2f} points")
