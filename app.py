from flask import Flask, session, render_template, request, redirect
from flask_session import Session 
from cachelib.file import FileSystemCache
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, createDB, dict_factory

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
        gym_name = request.form.get("gym_name")
        email_address = request.form.get("email_address")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")

        # Check if all the data was input.

        if not gym_name or not email_address or not password or not repeat_password:
            return "PLEASE FILL ALL FIELDS"
        
        connection = sqlite3.connect("gyms.db")
        connection.row_factory = dict_factory

        cursor = connection.cursor()

        cursor.execute("SELECT * " \
                        "FROM gyms " \
                        "WHERE gym_email IS ?", (email_address,))

        row = cursor.fetchone()

        print(row)

        if row != None:
            return "EMAIL IN USE"
        
        # Check if passwords match.

        if password != repeat_password:
            return "PASSWORDS MUST MATCH"
        
        # Check if password is the right length.

        if len(password) < 8:
            return "PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG"

        # Hashing and salting password.

        hashed_password = generate_password_hash(
                            password, method="scrypt", salt_length=32
                            )
        
        """ INSERT NEW USER TO DB """

        cursor.execute("INSERT INTO " \
                       "gyms " \
                       "(gym_Name, gym_email, password_hash) " \
                       "VALUES (?, ?, ?);", 
                       (gym_name, email_address, hashed_password)
                       )
        
        connection.commit()
        connection.close() 

        return redirect("/login")
    else:
        return render_template("register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        gym_email = request.form.get("email_address")
        password = request.form.get("password")

        if not gym_email or not password:
            return "PLEASE FILL ALL FIELDS"
        
        query = ("SELECT * " \
                "FROM gyms " \
                "WHERE gym_email = ?" # Will return the row with all the gym data
                )
        
        connection = sqlite3.connect("gyms.db")
        connection.row_factory = dict_factory

        cursor = connection.cursor()

        cursor.execute(query, (gym_email,)) # Must pass variables as a tuple, even if there is just a single one

        row = cursor.fetchone() 
        
        if row is None or not check_password_hash(
            row["password_hash"], password
        ):
            return "INVALID EMAIL OR PASSWORD"
        
        
        session["user_id"] = row["gym_id"]
        return redirect("/homepage") # TODO; Create the homepage


    return render_template("login.html")


@app.route("/homepage")
def homepage():
    return render_template("homepage.html")