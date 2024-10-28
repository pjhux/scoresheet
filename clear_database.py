import sqlite3

# Connect to the database
conn = sqlite3.connect('results.db')
cursor = conn.cursor()

# Ensure the match_results table exists before clearing it
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

# Clear all records from the match_results table
cursor.execute("DELETE FROM match_results")
conn.commit()

# Close the connection
conn.close()

print("All records have been cleared from the database.")
