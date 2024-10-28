import streamlit as st
import pandas as pd
import sqlite3

# Load and use the transformed matches DataFrame directly
matches_df = pd.DataFrame([
    {"Round": "Round 1", "Pitch": "Pitch 1", "Team1": "School", "Team2": "Judde"},
    {"Round": "Round 1", "Pitch": "Pitch 2", "Team1": "Park", "Team2": "Hill Side"},
    # ... include all transformed rows here
])

# Database setup function
def init_db():
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round TEXT,
            pitch TEXT,
            team1 TEXT,
            team1_score INTEGER,
            team2 TEXT,
            team2_score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Insert match result into the database
def insert_match_result(round, pitch, team1, team1_score, team2, team2_score):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO match_results (round, pitch, team1, team1_score, team2, team2_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (round, pitch, team1, team1_score, team2, team2_score))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# App title
st.title("Match Score Recorder")

# Step 1: Select Round
rounds = matches_df['Round'].unique()
selected_round = st.selectbox("Select Round", rounds)

# Filter matches based on the selected round
round_matches = matches_df[matches_df['Round'] == selected_round]

# Step 2: Select Pitch
pitches = round_matches['Pitch'].unique()
selected_pitch = st.selectbox("Select Pitch", pitches)

# Filter matches for the selected pitch
pitch_matches = round_matches[round_matches['Pitch'] == selected_pitch]

# Step 3: Display Matches and Score Input
st.write(f"Matches for {selected_round}, {selected_pitch}")
match_scores = []

for _, row in pitch_matches.iterrows():
    team1 = row['Team1']
    team2 = row['Team2']
    
    st.write(f"Match: {team1} vs {team2}")
    
    # Input scores for each team
    team1_score = st.number_input(f"Enter score for {team1}", min_value=0, step=1, key=f"{team1}_{team2}_1")
    team2_score = st.number_input(f"Enter score for {team2}", min_value=0, step=1, key=f"{team1}_{team2}_2")
    
    # Append match score details to list
    match_scores.append({
        "Round": selected_round,
        "Pitch": selected_pitch,
        "Team1": team1,
        "Team1 Score": team1_score,
        "Team2": team2,
        "Team2 Score": team2_score
    })

# Step 4: Submit and Record Scores
if st.button("Submit Scores"):
    for match in match_scores:
        insert_match_result(
            match["Round"],
            match["Pitch"],
            match["Team1"],
            match["Team1 Score"],
            match["Team2"],
            match["Team2 Score"]
        )
    st.success("Scores recorded successfully in the database!")
