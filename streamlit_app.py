import streamlit as st
import pandas as pd
import sqlite3

# Load and clean the fixtures data from CSV
def load_and_clean_fixtures():
    fixtures_path = 'fixtures.csv'
    df = pd.read_csv(fixtures_path)
    cleaned_matches = []
    for i in range(3, len(df)):
        round_num = df.iloc[i, 0]
        for pitch in range(1, 6, 2):
            team1 = df.iloc[i, pitch]
            team2 = df.iloc[i, pitch + 1]
            pitch_num = f"Pitch {(pitch // 2) + 1}"
            if pd.notna(team1) and pd.notna(team2) and pd.notna(round_num):
                cleaned_matches.append({
                    "Round": int(round_num),
                    "Pitch": pitch_num,
                    "Team1": team1,
                    "Team2": team2
                })
    return pd.DataFrame(cleaned_matches)

matches_df = load_and_clean_fixtures()

# Initialize database connection
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

init_db()

# Helper function to insert match results into the database
def insert_match_result(round, pitch, team1, team1_score, team2, team2_score):
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO match_results (round, pitch, team1, team1_score, team2, team2_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (round, pitch, team1, team1_score, team2, team2_score))
    conn.commit()
    conn.close()

# Navigation state management
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_round' not in st.session_state:
    st.session_state.selected_round = None
if 'selected_pitch' not in st.session_state:
    st.session_state.selected_pitch = None

# Custom styling
st.markdown(
    """
    <style>
    .round-button, .pitch-button, .submit-button {
        background-color: #4a5bdc;
        color: white;
        border: none;
        width: 100px;
        padding: 10px;
        margin-top: 10px;
        border-radius: 8px;
        font-size: 18px;
        text-align: center;
        cursor: pointer;
    }
    .round-button:hover, .pitch-button:hover, .submit-button:hover {
        background-color: #3e4db8;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Step 1: Select Round
if st.session_state.step == 1:
    st.title("Select a Round")
    rounds = matches_df['Round'].unique()
    
    for round_num in rounds:
        if st.button(f"Round {round_num}", key=f"round_{round_num}", on_click=lambda r=round_num: st.session_state.update({'selected_round': r, 'step': 2})):
            st.experimental_rerun()  # Ensures immediate navigation

# Step 2: Select Pitch
elif st.session_state.step == 2:
    st.title(f"Select a Pitch for Round {st.session_state.selected_round}")
    round_matches = matches_df[matches_df['Round'] == st.session_state.selected_round]
    pitches = round_matches['Pitch'].unique()
    
    for pitch in pitches:
        if st.button(pitch, key=f"pitch_{pitch}", on_click=lambda p=pitch: st.session_state.update({'selected_pitch': p, 'step': 3})):
            st.experimental_rerun()  # Ensures immediate navigation

# Step 3: Enter Scores
elif st.session_state.step == 3:
    st.title(f"Enter Scores for Round {st.session_state.selected_round} - {st.session_state.selected_pitch}")
    pitch_matches = matches_df[
        (matches_df['Round'] == st.session_state.selected_round) & 
        (matches_df['Pitch'] == st.session_state.selected_pitch)
    ]
    
    match_scores = []
    for _, row in pitch_matches.iterrows():
        team1 = row['Team1']
        team2 = row['Team2']
        
        st.write(f"Match: {team1} vs {team2}")
        team1_score = st.number_input(f"Enter score for {team1}", min_value=0, step=1, key=f"{team1}_{team2}_1")
        team2_score = st.number_input(f"Enter score for {team2}", min_value=0, step=1, key=f"{team1}_{team2}_2")
        
        match_scores.append({
            "Round": st.session_state.selected_round,
            "Pitch": st.session_state.selected_pitch,
            "Team1": team1,
            "Team1 Score": team1_score,
            "Team2": team2,
            "Team2 Score": team2_score
        })

    # Submit scores
    if st.button("Submit Scores", key="submit_button"):
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
        # Reset the app state after submission
        st.session_state.step = 1
        st.session_state.selected_round = None
        st.session_state.selected_pitch = None

    # Button to view all recorded scores
    if st.button("View All Recorded Scores"):
        # Query and display all recorded scores from the database
        conn = sqlite3.connect('results.db')
        scores_df = pd.read_sql_query("SELECT * FROM match_results", conn)
        conn.close()
        
        st.write("All Recorded Scores")
        st.dataframe(scores_df)
