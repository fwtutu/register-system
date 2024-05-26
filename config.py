import mysql.connector

# Database credentials
DB_SERVER = 'localhost'
DB_USERNAME = 'root'
DB_PASSWORD = ''
DB_NAME = 'test'

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host=DB_SERVER,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.set_charset_collation('utf8mb4')
        if conn.is_connected():
            print("Connected to the database.")
            return conn
    except mysql.connector.Error as e:
        print("ERROR: Could not connect. ", e)
        return None
