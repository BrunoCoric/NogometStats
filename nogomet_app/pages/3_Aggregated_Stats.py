import streamlit as st
import pandas as pd
import os
from nogomet_app.gdrive_setup import load_csv_from_drive, list_csvs_in_folder

def parse_player_list(player_str):
    if isinstance(player_str, str):
        return [player.strip() for player in player_str.split(",")]
    return []

# Helper function to load all game stats
def load_all_game_stats():
    all_stats = []
    all_files = list_csvs_in_folder()
    for file_title, file_id in all_files.items():
        all_stats.append(load_csv_from_drive(file_id, file_title))
    if all_stats:
        return pd.concat(all_stats, ignore_index=True)
    else:
        return None


# Aggregate Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This will give the path to the page file
all_games = load_all_game_stats()

if all_games is None:
    st.title("Aggregate Stats Dashboard")
    st.write("No games have been recorded yet.")
else:
    st.title("Aggregate Stats Dashboard")
    st.write("### Statistics Across All Matches")

    # Convert string lists to Python lists
    all_games["Team 1"] = all_games["Team 1"].apply(parse_player_list)
    all_games["Team 2"] = all_games["Team 2"].apply(parse_player_list)
    all_games["Goalscorers"] = all_games["Goalscorers"].apply(parse_player_list)
    all_games["Assisters"] = all_games["Assisters"].apply(parse_player_list)
    all_games["Own Goalscorers"] = all_games["Own Goalscorers"].apply(parse_player_list)

    # Combine all players into a single list for analysis
    all_players = set(sum(all_games["Team 1"], []) + sum(all_games["Team 2"], []))

    # Calculate Top Goalscorers
    goalscorers = sum(all_games["Goalscorers"], [])
    goalscorer_counts = pd.Series(goalscorers).value_counts()
    st.write("### Top Goalscorers")
    st.table(goalscorer_counts)

    # Calculate Top Assisters
    assisters = sum(all_games["Assisters"], [])
    assister_counts = pd.Series(assisters).value_counts()
    st.write("### Top Assisters")
    st.table(assister_counts)

    # Calculate Top Own Goalers
    own_goalers = sum(all_games["Own Goalscorers"], [])
    own_goaler_counts = pd.Series(own_goalers).value_counts()
    st.write("### Top Own Goalers")
    st.table(own_goaler_counts)

    # Calculate Players with Most Games Played
    games_played = {}
    for _, row in all_games.iterrows():
        for player in row["Team 1"] + row["Team 2"]:
            games_played[player] = games_played.get(player, 0) + 1
    games_played_counts = pd.Series(games_played).sort_values(ascending=False)
    st.write("### Players with Most Games Played")
    st.table(games_played_counts)

    player_total_games = {}
    player_wins = {}

    for _, row in all_games.iterrows():
        team1_players = row["Team 1"]
        team2_players = row["Team 2"]
        score1 = row["Score 1"]
        score2 = row["Score 2"]

        # Determine the winning team
        if score1 > score2:
            winning_team = team1_players
        elif score2 > score1:
            winning_team = team2_players
        else:
            # Draw; count games but no wins
            winning_team = []

        # Update stats for Team 1
        for player in team1_players:
            player_total_games[player] = player_total_games.get(player, 0) + 1
            if player in winning_team:
                player_wins[player] = player_wins.get(player, 0) + 1

        # Update stats for Team 2
        for player in team2_players:
            player_total_games[player] = player_total_games.get(player, 0) + 1
            if player in winning_team:
                player_wins[player] = player_wins.get(player, 0) + 1

    # Calculate winning percentages
    winning_percentages = {
        player: (player_wins.get(player, 0) / player_total_games[player]) * 100
        for player in player_total_games
    }

    # Convert to a DataFrame for display
    winning_percentage_df = pd.DataFrame([
        {"Player": player, "Winning Percentage": round(percent, 2)}
        for player, percent in winning_percentages.items()
    ])
    winning_percentage_df = winning_percentage_df.sort_values(by="Winning Percentage", ascending=False)

    # Display the result
    st.write("### Players with the Best Winning Percentage")
    st.table(winning_percentage_df)
