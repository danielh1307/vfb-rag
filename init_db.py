import psycopg2
import uuid

# Database connection parameters
db_params = {
    'dbname': 'vfb_db',
    'user': 'vfb_user',
    'password': 'vfb_password',
    'host': 'localhost',
    'port': '5432'
}

# Connect to the database
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Create the PLAYER_PROFILES table
cur.execute('''
    CREATE TABLE IF NOT EXISTS PLAYER_PROFILES (
        ID UUID PRIMARY KEY,
        FIRST_NAME VARCHAR(255),
        NAME VARCHAR(255),
        PROFILE TEXT
    )
''')

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Table PLAYER_PROFILES created successfully.") 