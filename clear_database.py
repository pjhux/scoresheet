import sqlite3

# Connect to the database
conn = sqlite3.connect('results.db')
cursor = conn.cursor()

# Clear all records from the match_results table
cursor.execute("DELETE FROM match_results")
conn.commit()

# Close the connection
conn.close()
print("All records have been cleared from the database.")
