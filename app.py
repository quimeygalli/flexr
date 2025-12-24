from flask import Flask, session, render_template, request, redirect
from flask_session import Session 
from cachelib.file import FileSystemCache
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology

app = Flask(__name__)

# ONLY FOR DEVELOPMENT  ->
#---
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
#---

""" SESSION CONFIG """

app.config['SESSION_TYPE'] = "cachelib"
app.config['SESSION_PERMANENT'] = True
SESSION_CACHELIB = FileSystemCache(
    cache_dir="./sessions",
    threshold=500,              # A maximum of cached sessions
    default_timeout=10          # Amount of seconds a session will last
    )
app.config.from_object(__name__)

Session(app)

""" DB CREATION """

connection = sqlite3.connect("gyms.db") # Connection

cursor = connection.cursor() # Cursor object


cursor.execute("CREATE TABLE IF NOT EXISTS gyms (" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "gymName TEXT NOT NULL," \
            "gymEmail TEXT UNIQUE NOT NULL CHECK (gymEmail LIKE '%@%.%')," \
            "passwordHash VARCHAR(255) NOT NULL );" # VARCHAR is used for password hashes because of
                                                    # the variable lenghts of the hashes and for future-proofing 

                                                    # SQLite ignores this type because it doesn't have a limit for strings.
                                                    # It doesn't throw an error for compatibility with other DB software.
            )
connection.commit()
cursor.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        gymName = request.form.get("gymName")
        emailAddress = request.form.get("emailAddress")
        password = request.form.get("password")
        repeatPassword = request.form.get("repeatPassword")

        #TODO: not a good check. would need some JS first, and in case 
        # the HTML is edited a python safety check (apology function would work) ->

        if not gymName or not emailAddress or not password or not repeatPassword:
            return "PLEASE FILL ALL FIELDS"
        
        if password != repeatPassword:
            return "PASSWORDS MUST MATCH"

        # Hashing and salting password

        hashedPassword = generate_password_hash(password, method="scrypt", salt_length=32)
        
        """ INSERT NEW USER TO DB """

        connection = sqlite3.connect("gyms.db")
        cursor = connection.cursor()

        cursor.execute("INSERT INTO gyms (gymName, gymEmail, passwordHash) VALUES (?, ?, ?);", (gymName, emailAddress, hashedPassword))
        
        connection.commit()
        connection.close()

        return redirect("/login")
    else:
        return render_template("register.html")