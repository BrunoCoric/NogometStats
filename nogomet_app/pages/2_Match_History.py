import streamlit as st
import pandas as pd
import os
from gdrive_setup import load_csv_from_drive, list_csvs_in_folder

# Helper function to load game stats
def load_game_stats(file_id, file_path):
    try:
        return load_csv_from_drive(file_id, file_path)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


# Streamlit App
st.title("Game Stats Dashboard")
st.sidebar.header("Available Games")

# List all CSV files in the stats folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This will give the path to the page file

game_files = list_csvs_in_folder()
name2idx = {v:k for k,v in game_files.items()}

if not game_files:
    st.write("No games have been recorded yet. Please add match data first.")
else:
    # Display all game files in the sidebar
    selected_file = st.sidebar.selectbox("Select a game file", list(game_files.keys()))

    if selected_file:
        st.write(f"### Stats for Game: {selected_file.removesuffix('.csv')}")

        game_stats = load_game_stats(name2idx[selected_file], selected_file)

        if game_stats is not None:
            st.write("### Team 1")
            st.write(game_stats["Team 1"].iloc[0])
            st.write("### Team 2")
            st.write(game_stats["Team 2"].iloc[0])
            st.write("### Score")
            st.write(f"{game_stats['Score 1'].iloc[0]} - {game_stats['Score 2'].iloc[0]}")

            # Additional summary stats (optional)
            st.write("### Summary Stats")
            if "Goalscorers" in game_stats.columns:
                goalscorers = game_stats["Goalscorers"].iloc[0].split(", ")
                goalscorer_counts = pd.Series(goalscorers).value_counts()
                st.write("#### Goalscorers Count")
                st.write(goalscorer_counts)

            if "Assisters" in game_stats.columns:
                assisters = game_stats["Assisters"].iloc[0].split(", ")
                assister_counts = pd.Series(assisters).value_counts()
                st.write("#### Assisters Count")
                st.write(assister_counts)

            if "Own Goalscorers" in game_stats.columns:
                own_goals = game_stats["Own Goalscorers"].iloc[0].split(", ")
                own_goals_counts = pd.Series(own_goals).value_counts()
                st.write("#### Own Goalscorers Count")
                st.write(own_goals_counts)
