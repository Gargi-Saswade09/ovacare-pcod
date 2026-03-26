import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="pcod_system",
        user="postgres",
        password="Gargi@1905",
        port="5432"
    )
    print("Database connected successfully!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)