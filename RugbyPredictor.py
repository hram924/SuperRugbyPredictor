import pandas as pd
import numpy as np

# Load datasets from a single Excel file
results_data = pd.read_excel('results.xlsx')  # This file should contain results for the last 2 years
fixtures = pd.read_excel('fixtures.xlsx')  # Fixtures for the upcoming matches

# Define the teams in Super Rugby
teams = [
    'Hurricanes', 'Blues', 'Brumbies', 'Chiefs', 'Reds',
    'Highlanders', 'Drua', 'Rebels', 'Crusaders', 'Force',
    'Moana Pasifika', 'Waratahs'
]

# Initialize user input for team skill adjustments (all set to 0)
team_adjustments = {team: 0 for team in teams}

# Function to calculate team ratings based on previous results
def calculate_ratings(match_data):
    ratings = {team: 80 for team in teams}  # Default starting rating
    
    for index, row in match_data.iterrows():
        team_a = row['team_a']
        team_b = row['team_b']
        score_a = row['score_a']
        score_b = row['score_b']
        team_a_home = row.get('team_a_home', True)  # Assuming the row specifies if team_a is home

        # Determine if home advantage applies
        home_advantage = 3 if team_a_home else 0
        
        # Point difference and match outcome
        point_difference = score_a - score_b
        
        if score_a > score_b:  # Team A wins
            ratings[team_a] += 5
            ratings[team_b] -= 5
            if point_difference > 15:
                ratings[team_a] += 2
            elif point_difference < -15:
                ratings[team_b] += 2
        elif score_a < score_b:  # Team B wins
            ratings[team_b] += 5
            ratings[team_a] -= 5
            if point_difference < -15:
                ratings[team_b] += 2
            elif point_difference > 15:
                ratings[team_a] += 2
            
        # Adjust for home advantage in the rating
        if team_a_home:
            ratings[team_a] += home_advantage
        else:
            ratings[team_b] += home_advantage

    return ratings

# Calculate initial ratings based on results data
ratings = calculate_ratings(results_data)

# Apply user adjustments (no effect as all set to 0)
for team, adjustment in team_adjustments.items():
    if team in ratings:
        ratings[team] *= (1 + adjustment / 100)

# Display the adjusted ratings
print("Adjusted Team Ratings:")
print(ratings)

# Function to calculate win probability based on ratings, with home advantage
def calculate_win_probability(team_a_rating, team_b_rating, team_a_home):
    home_advantage = 3 if team_a_home else 0  # Add 3 points to the home team rating
    prob_a = 1 / (1 + 10 ** ((team_b_rating - (team_a_rating + home_advantage)) / 400))
    prob_b = 1 - prob_a
    return prob_a, prob_b

# Function to calculate draw and bonus point probabilities based on ratings difference
def calculate_additional_probs(rating_diff):
    draw_prob = max(0, 0.2 - (rating_diff / 50))
    bonus_prob_win = min(0.3, max(0.1, rating_diff / 200))
    bonus_prob_loss = max(0.3 - (rating_diff / 100), 0.1)
    return draw_prob, bonus_prob_win, bonus_prob_loss

# Function to estimate points scored at the end of the season
def estimate_final_points(win_prob, bonus_prob_win, bonus_prob_loss, draw_prob):
    return (win_prob * 4) + (bonus_prob_win * 1) + (bonus_prob_loss * 1) + (draw_prob * 2)

# Initialize estimated points for each team
estimated_points = {team: 0 for team in teams}

# Calculate win probabilities and estimated points for each fixture
for index, row in fixtures.iterrows():
    team_a = row['team_a']
    team_b = row['team_b']
    rating_a = ratings[team_a]
    rating_b = ratings[team_b]
    rating_diff = abs(rating_a - rating_b)
    
    # Determine if Team A is the home team (add a 'team_a_home' column in fixtures if necessary)
    team_a_home = row.get('team_a_home', False)  # True if Team A is home, otherwise False

    # Calculate probabilities with home advantage considered
    prob_a, prob_b = calculate_win_probability(rating_a, rating_b, team_a_home)
    
    # Calculate draw and bonus probabilities based on rating difference
    draw_prob, bonus_prob_win_a, bonus_prob_loss_a = calculate_additional_probs(rating_diff)
    draw_prob_b, bonus_prob_win_b, bonus_prob_loss_b = calculate_additional_probs(rating_diff)
    
    # Estimate final points for Team A
    final_points_a = estimate_final_points(prob_a, bonus_prob_win_a, bonus_prob_loss_a, draw_prob)
    final_points_b = estimate_final_points(prob_b, bonus_prob_win_b, bonus_prob_loss_b, draw_prob)

    # Update estimated points for each team
    estimated_points[team_a] += final_points_a
    estimated_points[team_b] += final_points_b

    # Output results for the current fixture
    print(f"{team_a} vs {team_b} (Home: {team_a_home}):")
    print(f"  Win Probability: {prob_a:.2%} for {team_a}, {prob_b:.2%} for {team_b}")
    print(f"  Draw Probability: {draw_prob:.2%}")
    print(f"  Estimated Points: {team_a} = {final_points_a:.2f}, {team_b} = {final_points_b:.2f}")

# Display the final estimated points table at the end of fixtures
print("\nEstimated Points Table:")
for team, points in estimated_points.items():
    win_percentage = (points / len(fixtures)) * 100
    print(f"{team}: Estimated Points = {points:.2f}, Win Percentage = {win_percentage:.2f}%")
