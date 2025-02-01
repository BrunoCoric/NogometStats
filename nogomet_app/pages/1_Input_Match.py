import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from gdrive_setup import save_csv_to_drive, load_file_from_drive

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This will give the path to the page file
STATS = os.path.join(BASE_DIR, '..', 'stats')
ALL_PLAYERS = sorted(json.load(load_file_from_drive("1T0JDgWg4kFXYXO0xm5gR24AB8pFscqNl")))

# Save Data
def save_data(df, file_name: str):
    save_csv_to_drive(df, file_name.removesuffix('.csv')+'.csv')


# Streamlit App
st.title("Match Data Input Dashboard")
st.sidebar.header("Add Match Details")

st.sidebar.subheader("Date")
match_date = st.sidebar.date_input("Match Date", datetime.today())

# Input form
st.sidebar.subheader("Teams")
team1 = st.sidebar.multiselect("Select players for Team 1", ALL_PLAYERS)

remaining_players = [player for player in ALL_PLAYERS if player not in team1]
team2 = st.sidebar.multiselect("Select players for Team 2", remaining_players)

team1_set = set(team1)
team2_set = set(team2)

# Initialize empty lists for goalscorers, assisters, and own goalscorers
if "goalscorers" not in st.session_state:
    st.session_state.goalscorers = []
if "assisters" not in st.session_state:
    st.session_state.assisters = []
if "own_goals" not in st.session_state:
    st.session_state.own_goals = []
if "score_1" not in st.session_state:
    st.session_state.score_1 = []
if "score_2" not in st.session_state:
    st.session_state.score_2 = []

# Select players and add them to the corresponding list
st.sidebar.subheader("Add Goalscorers")
goal_select = st.sidebar.selectbox("Select a goalscorer", [*team1, *team2])
if st.sidebar.button("Add Goalscorer"):
    st.session_state.goalscorers.append(goal_select)
    if goal_select in team1_set:
        st.session_state.score_1.append(1)
    else:
        st.session_state.score_2.append(1)
if st.sidebar.button("Remove Goalscorer", disabled=len(st.session_state.goalscorers)==0):
    st.session_state.goalscorers.remove(goal_select)
    if goal_select in team1_set:
        st.session_state.score_1.append(-1)
    else:
        st.session_state.score_2.append(-1)

st.sidebar.subheader("Add Assisters")
assister_select = st.sidebar.selectbox("Select an assister", [*team1, *team2])
if st.sidebar.button("Add Assister"):
    st.session_state.assisters.append(assister_select)
if st.sidebar.button("Remove Assister", disabled=len(st.session_state.assisters)==0):
    st.session_state.assisters.remove(assister_select)

st.sidebar.subheader("Add Own Goalscorers")
own_goal_select = st.sidebar.selectbox("Select an own goalscorer", [*team1, *team2])
if st.sidebar.button("Add Own Goalscorer"):
    st.session_state.own_goals.append(own_goal_select)
    if own_goal_select in team1_set:
        st.session_state.score_2.append(+1)
    else:
        st.session_state.score_1.append(+1)
if st.sidebar.button("Remove Own Goalscorer", disabled=len(st.session_state.own_goals)==0):
    st.session_state.own_goals.remove(own_goal_select)
    if own_goal_select in team1_set:
        st.session_state.score_2.append(-1)
    else:
        st.session_state.score_1.append(-1)

# Display selected players on the main page
st.write(f"### Team 1: {', '.join(team1)}")
st.write(f"### Team 2: {', '.join(team2)}")

st.write(f"### Goalscorers: {', '.join(st.session_state.goalscorers)}")
st.write(f"### Assisters: {', '.join(st.session_state.assisters)}")
st.write(f"### Own Goalscorers: {', '.join(st.session_state.own_goals)}")

st.write(f"### Current Result: {sum(st.session_state.score_1)} - {sum(st.session_state.score_2)}")

# Add match button
if st.sidebar.button("Add Match"):
    formatted_match_date = match_date.strftime("%Y-%m-%d")
    # Prepare data
    match_data = pd.DataFrame({
        "Date": [formatted_match_date],
        "Team 1": [", ".join(team1)],
        "Team 2": [", ".join(team2)],
        "Goalscorers": [", ".join(st.session_state.goalscorers)],
        "Assisters": [", ".join(st.session_state.assisters)],
        "Own Goalscorers": [", ".join(st.session_state.own_goals)],
        "Score 1": [sum(st.session_state.score_1)],
        "Score 2": [sum(st.session_state.score_2)]
    })
    # Save data
    save_data(match_data, formatted_match_date)
    st.sidebar.success(f"Data saved")
