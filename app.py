from flask import Flask, session, render_template, request, redirect
from flask_session import Session 
from cachelib.file import FileSystemCache
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, createDB

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
    threshold=500,              # A maximum of cached sessions.
    default_timeout=10          # Amount of seconds a session will last.
    )
app.config.from_object(__name__)

Session(app)

""" DB CREATION """

connection = sqlite3.connect("gyms.db") # Connection.
createDB()                              # Creates a DB with 'gyms', 'members' and 'routines' tables.
connection.close()

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

        # Check if all the data was input.

        if not gymName or not emailAddress or not password or not repeatPassword:
            return "PLEASE FILL ALL FIELDS"
        
        # Check if passwords match.

        if password != repeatPassword:
            return "PASSWORDS MUST MATCH"
        
        # Check if password is the right length.

        if len(password) < 8:
            return "PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG"

        # Hashing and salting password.

        hashedPassword = generate_password_hash(
                            password, method="scrypt", salt_length=32
                            )
        
        """ INSERT NEW USER TO DB """

        connection = sqlite3.connect("gyms.db")
        cursor = connection.cursor()

        cursor.execute("INSERT INTO " \
                       "gyms " \
                       "(gym_Name, gym_Email, password_Hash) " \
                       "VALUES (?, ?, ?);", 
                       (gymName, emailAddress, hashedPassword)
                       )
        
        connection.commit()
        connection.close() # TODO: Check where to close the connection.

        return redirect("/login")
    else:
        return render_template("register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        gym_Email = request.form.get("emailAddress")
        password = request.form.get("password")

        if not gym_Email or not password:
            return "PLEASE FILL ALL FIELDS"
        
        query = ("SELECT * " \
                "FROM gyms " \
                "WHERE gym_Email = ?" # Will return the row with all the gym data
                )
        
        connection = sqlite3.connect("gyms.db")
        cursor = connection.cursor()

        cursor.execute(query, (gym_Email,)) # Must pass variables as a tuple, even if there is just a single one

        result = cursor.fetchone() 
        
        if result[0]["gym_Email"] and check_password_hash(result[0]["password_Hash"]): # TODO; Fix checking of user
            session["user_id"] = result[0]["gym_id"]


    return render_template("login.html")