import sqlite3
import bcrypt

sqlfile = "./test.sql"
dbfile = "accounts.db"

def create_table():
    with sqlite3.connect(dbfile) as connection:
        with open(sqlfile, 'r') as source:
            connection.executescript(source.read())

def create_account(username, password):
    if not username or not password:
        return "Username and password cannot be empty."
    hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with sqlite3.connect(dbfile) as connection:
        try:
            connection.execute("INSERT INTO user (username, password_hash) VALUES (?, ?)", (username, hash))
            connection.commit()
            return "Account created."
        except sqlite3.IntegrityError:
            return "Duplicate user."
        except sqlite3.Error as e:
            return f"Database error: {e}"

def verify_account(username, password):
    if not username or not password:
        return "Username and password cannot be empty."
    with sqlite3.connect(dbfile) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT password_hash FROM user WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result is None:
                return "User not found."
            if bcrypt.checkpw(password.encode(), result[0]):
                return "Password validated."
            else:
                return "Incorrect password."
        except sqlite3.Error as e:
            return f"Database error: {e}"
