import pandas as pd
import numpy as np

# Define the teams in Super Rugby
teams = [
    'Hurricanes', 'Blues', 'Brumbies', 'Chiefs', 'Reds',
    'Highlanders', 'Drua', 'Rebels', 'Crusaders', 'Force',
    'Moana Pasifika', 'Waratahs'
]

# Initialize a DataFrame to store previous results (example data)
previous_results = pd.DataFrame({
    'team_a': ['Hurricanes', 'Blues', 'Brumbies', 'Chiefs', 'Reds'],
    'team_b': ['Blues', 'Hurricanes', 'Chiefs', 'Rebels', 'Highlanders'],
    'score_a': [30, 25, 35, 40, 20],
    'score_b': [20, 15, 30, 15, 30]
})

# Initialize user input for team skill adjustments (all set to 0)
team_adjustments = {team: 0 for team in teams}

# Function to calculate team ratings based on previous results
def calculate_ratings(previous_results):
    ratings = {team: 80 for team in teams}  # Default starting rating
    
    for index, row in previous_results.iterrows():
        team_a = row['team_a']
        team_b = row['team_b']
        score_a = row['score_a']
        score_b = row['score_b']
        
        point_difference = score_a - score_b
        
        if score_a > score_b:
            ratings[team_a] += 5
            ratings[team_b] -= 5
            if point_difference > 15:
                ratings[team_a] += 2
            elif point_difference < -15:
                ratings[team_b] += 2
        elif score_a < score_b:
            ratings[team_b] += 5
            ratings[team_a] -= 5
            if point_difference < -15:
                ratings[team_b] += 2
            elif point_difference > 15:
                ratings[team_a] += 2

    return ratings

# Function to calculate win probability based on ratings
def calculate_win_probability(team_a_rating, team_b_rating):
    prob_a = 1 / (1 + 10 ** ((team_b_rating - team_a_rating) / 400))
    prob_b = 1 - prob_a
    return prob_a, prob_b

# Function to calculate draw and bonus point probabilities based on ratings difference
def calculate_additional_probs(rating_diff):
    # Draw probability higher if rating difference is low, decreasing as difference increases
    draw_prob = max(0, 0.2 - (rating_diff / 50))
    
    # Winning bonus point probability higher for strong team if rating difference is high
    bonus_prob_win = min(0.3, max(0.1, rating_diff / 200))
    
    # Losing bonus point probability higher if ratings are close
    bonus_prob_loss = max(0.3 - (rating_diff / 100), 0.1)
    
    return draw_prob, bonus_prob_win, bonus_prob_loss

# Function to estimate points scored at the end of the season
def estimate_final_points(win_prob, bonus_prob_win, bonus_prob_loss, draw_prob):
    return (win_prob * 4) + (bonus_prob_win * 1) + (bonus_prob_loss * 1) + (draw_prob * 2)

# Calculate initial ratings based on previous results
ratings = calculate_ratings(previous_results)

# Apply user adjustments (no effect as all set to 0)
for team, adjustment in team_adjustments.items():
    if team in ratings:
        ratings[team] *= (1 + adjustment / 100)

# Display the adjusted ratings
print("Adjusted Team Ratings:")
print(ratings)

# Current fixtures for the rest of the season
fixtures = [
    ('Hurricanes', 'Crusaders'),
    ('Blues', 'Highlanders'),
    ('Brumbies', 'Drua'),
    ('Chiefs', 'Reds'),
    ('Rebels', 'Force'),
    ('Moana Pasifika', 'Waratahs'),
]

# Initialize estimated points for each team
estimated_points = {team: 0 for team in teams}

# Calculate win probabilities and estimated points
for fixture in fixtures:
    team_a, team_b = fixture
    rating_a = ratings[team_a]
    rating_b = ratings[team_b]
    rating_diff = abs(rating_a - rating_b)

    prob_a, prob_b = calculate_win_probability(rating_a, rating_b)
    
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
    print(f"{team_a} vs {team_b}:")
    print(f"  Win Probability: {prob_a:.2%} for {team_a}, {prob_b:.2%} for {team_b}")
    print(f"  Draw Probability: {draw_prob:.2%}")
    print(f"  Estimated Points: {team_a} = {final_points_a:.2f}, {team_b} = {final_points_b:.2f}")

# Display the final estimated points table at the end of fixtures
print("\nEstimated Points Table:")
for team, points in estimated_points.items():
    win_percentage = (points / len(fixtures)) * 100  # Calculate win percentage based on estimated points
    print(f"{team}: Estimated Points = {points:.2f}, Win Percentage = {win_percentage:.2f}%")
