import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

# Email configuration
def send_email(subject, body):
    sender_email = "pjhuxley@gmail.com"  # Replace with your Gmail address
    receiver_email = "pjh@tonbridge-school.org"
    password = "awif kltn wdpa ngpt"  # Replace with your app-specific password

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Enable security
            server.login(sender_email, password)
            server.send_message(msg)
        st.success("Scores emailed successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

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
        width: 100%;
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
            pass  # Moving to step 2 without experimental rerun

# Step 2: Select Pitch
elif st.session_state.step == 2:
    st.title(f"Select a Pitch for Round {st.session_state.selected_round}")
    round_matches = matches_df[matches_df['Round'] == st.session_state.selected_round]
    pitches = round_matches['Pitch'].unique()
    
    for pitch in pitches:
        if st.button(pitch, key=f"pitch_{pitch}", on_click=lambda p=pitch: st.session_state.update({'selected_pitch': p, 'step': 3})):
            pass  # Moving to step 3 without experimental rerun

# Step 3: Enter Scores and Email Results
elif st.session_state.step == 3:
    st.title(f"Enter Scores for {st.session_state.selected_round} - {st.session_state.selected_pitch}")
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

    # Submit scores and send email
    if st.button("Submit Scores", key="submit_button"):
        # Format the email body
        email_body = f"Scores for {st.session_state.selected_round} - {st.session_state.selected_pitch}:\n\n"
        for match in match_scores:
            email_body += (f"{match['Team1']} vs {match['Team2']}:\n"
                           f"  {match['Team1']} Score: {match['Team1 Score']}\n"
                           f"  {match['Team2']} Score: {match['Team2 Score']}\n\n")

        # Send the email
        send_email(subject=f"Scores for Round {st.session_state.selected_round}, {st.session_state.selected_pitch}", body=email_body)

        # Reset the app state without rerunning
        st.session_state.step = 1
        st.session_state.selected_round = None
        st.session_state.selected_pitch = None
        st.success("Scores have been submitted and the form is reset.")
