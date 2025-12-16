import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ajay@8096",
        database="expense_tracker"
    )
