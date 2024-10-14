import pandas as pd
import numpy as np

# Constants for initial ranking and adjustment factor
INITIAL_RATING = 80  # Starting point for all teams
K_FACTOR = 2         # Determines how much ranking points change after each game
STANDARD_HOME_ADVANTAGE = 3  # Points advantage for home teams
REDUCED_HOME_ADVANTAGE = 2   # Reduced advantage when teams from the same country play

# Load data from CSV files
def load_data(prev_seasons_path, current_season_path, fixtures_path):
    # Load previous seasons' data, current season data, and future fixtures
    prev_seasons = pd.read_csv(prev_seasons_path)
    current_season = pd.read_csv(current_season_path)
    fixtures = pd.read_csv(fixtures_path)
    return prev_seasons, current_season, fixtures

# Calculate points exchange based on the ranking system
def calculate_points_exchange(team_a_rank, team_b_rank, result, home_team, same_country):
    # Determine home advantage, reducing it if teams are from the same country
    home_advantage = STANDARD_HOME_ADVANTAGE if not same_country else REDUCED_HOME_ADVANTAGE
    team_a_advantage = home_advantage if home_team == "team_a" else -home_advantage
    
    # Calculate the rating difference between the two teams and add home advantage
    rating_diff = team_a_rank - team_b_rank + team_a_advantage
    
    # Use a logistic function to determine win probability
    win_prob = 1 / (1 + 10 ** (-rating_diff / 10))
    
    # Calculate points change based on the result of the match
    if result == "team_a_win":
        points_change = K_FACTOR * (1 - win_prob)  # Team A wins, gets more points
    elif result == "team_b_win":
        points_change = K_FACTOR * (-win_prob)     # Team B wins, Team A loses points
    else:
        points_change = 0  # No points change for a draw (can be expanded if needed)
    
    return points_change

# Update team rankings after a match
def update_rankings(rankings, team_a, team_b, result, home_team, same_country):
    # Get the current rankings of both teams
    team_a_rank = rankings[team_a]
    team_b_rank = rankings[team_b]
    
    # Calculate points exchange based on match result
    points_change = calculate_points_exchange(team_a_rank, team_b_rank, result, home_team, same_country)
    
    # Update rankings: team A gains or loses points, and team B mirrors that change
    rankings[team_a] += points_change
    rankings[team_b] -= points_change

# Predict match win probability based on rankings and home advantage
def predict_match_win_prob(rankings, team_a, team_b, home_team, same_country):
    # Adjust home advantage based on whether the teams are from the same country
    home_advantage = STANDARD_HOME_ADVANTAGE if not same_country else REDUCED_HOME_ADVANTAGE
    team_a_advantage = home_advantage if home_team == team_a else -home_advantage
    
    # Calculate the rating difference including the home advantage
    rating_diff = rankings[team_a] - rankings[team_b] + team_a_advantage
    
    # Use the logistic function to calculate the probability of team A winning
    win_prob = 1 / (1 + 10 ** (-rating_diff / 10))
    return win_prob

# Simulate the remaining fixtures, updating team rankings as we go
def simulate_remaining_fixtures(rankings, fixtures, same_country_teams):
    # Loop through each match in the remaining fixtures
    for idx, match in fixtures.iterrows():
        team_a = match['team_a']
        team_b = match['team_b']
        home_team = match['home_team']
        
        # Check if the teams are from the same country (to adjust home advantage)
        same_country = team_a in same_country_teams and team_b in same_country_teams
        
        # Predict the win probability based on current rankings
        win_prob = predict_match_win_prob(rankings, team_a, team_b, home_team, same_country)
        
        # Simulate match result using the win probability (Team A vs Team B)
        result = np.random.choice(["team_a_win", "team_b_win"], p=[win_prob, 1-win_prob])
        
        # Update the rankings based on the result of the simulated match
        update_rankings(rankings, team_a, team_b, result, home_team, same_country)

# Run a Monte Carlo simulation to estimate each team's probability of winning the championship
def championship_probabilities(rankings, fixtures, num_simulations, same_country_teams):
    # Track the number of times each team wins the championship
    championship_wins = {team: 0 for team in rankings.keys()}
    
    # Simulate the rest of the season multiple times
    for _ in range(num_simulations):
        # Create a copy of the rankings to simulate without affecting the original data
        simulated_rankings = rankings.copy()
        
        # Simulate the remaining matches and update rankings
        simulate_remaining_fixtures(simulated_rankings, fixtures, same_country_teams)
        
        # Determine the team with the highest ranking after the simulations (the "winner")
        winner = max(simulated_rankings, key=simulated_rankings.get)
        
        # Increment the win count for the team that won the simulation
        championship_wins[winner] += 1
    
    # Convert the championship win counts to probabilities (percentage chance of winning)
    probabilities = {team: wins / num_simulations for team, wins in championship_wins.items()}
    return probabilities

# Main program to run the entire simulation
def main(prev_seasons_path, current_season_path, fixtures_path, num_simulations=10000):
    # Load previous season, current season, and fixture data
    prev_seasons, current_season, fixtures = load_data(prev_seasons_path, current_season_path, fixtures_path)
    
    # Initialize all teams with the same starting ranking
    teams = set(prev_seasons['team_a']).union(set(prev_seasons['team_b']))
    rankings = {team: INITIAL_RATING for team in teams}
    
    # Simulate past seasons to bring rankings up to the present
    for idx, match in prev_seasons.iterrows():
        team_a = match['team_a']
        team_b = match['team_b']
        result = "team_a_win" if match['score_a'] > match['score_b'] else "team_b_win"
        home_team = match['home_team']
        same_country = match['same_country']  # True if teams from same country
        
        # Update rankings based on past match results
        update_rankings(rankings, team_a, team_b, result, home_team, same_country)
    
    # Apply current season matches to further update rankings
    for idx, match in current_season.iterrows():
        team_a = match['team_a']
        team_b = match['team_b']
        result = "team_a_win" if match['score_a'] > match['score_b'] else "team_b_win"
        home_team = match['home_team']
        same_country = match['same_country']
        
        # Update rankings based on current season results
        update_rankings(rankings, team_a, team_b, result, home_team, same_country)
    
    # Define teams from the same country to apply the reduced home advantage
    same_country_teams = {"NZL_team1", "NZL_team2", "AUS_team1", "AUS_team2", "RSA_team1", "RSA_team2"}
    
    # Run Monte Carlo simulations to estimate championship probabilities
    probabilities = championship_probabilities(rankings, fixtures, num_simulations, same_country_teams)
    
    # Output the championship probabilities for each team
    print("Championship Win Probabilities:")
    for team, prob in probabilities.items():
        print(f"{team}: {prob*100:.2f}%")

# Example usage
if __name__ == "__main__":
    # Paths to the dataset files
    prev_seasons_path = 'path_to_previous_seasons.csv'
    current_season_path = 'path_to_current_season.csv'
    fixtures_path = 'path_to_fixtures.csv'
    
    # Run the main function with the data
    main(prev_seasons_path, current_season_path, fixtures_path)
