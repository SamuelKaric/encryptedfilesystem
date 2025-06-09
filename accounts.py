import sqlite3
import bcrypt
from encrypt.gen_certs import user_ca, validate_cert

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
            user_ca(username)
            return "Account created."
        except sqlite3.IntegrityError:
            return "Duplicate user."
        except sqlite3.Error as e:
            return f"Database error: {e}"

def verify_account(username, password, certPath):
    if not username or not password or not certPath:
        return "Username, password, and certificate path cannot be empty."
    if not validate_cert(certPath, username):
        return "Invalid certificate."   
    else:
        print("Certificate is valid.")
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
        
def get_all_users():
    with sqlite3.connect(dbfile) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM user")
        return [row[0] for row in cursor.fetchall()]
