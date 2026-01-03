import sqlite3
import time

import jinja2
from cachelib.file import FileSystemCache
from flask import Flask, redirect, render_template, request, session
from flask_session import Session

from helpers import createDB, dict_factory, unix_to_MD
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# ONLY FOR DEVELOPMENT  ->
#---
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
#---

""" Configuration of session """

app.config['SESSION_TYPE'] = "cachelib"
app.config['SESSION_PERMANENT'] = True
SESSION_CACHELIB = FileSystemCache(
    cache_dir="./sessions",
    threshold=500,              # A maximum of cached sessions.
    default_timeout=10          # Amount of seconds a session will last.
    )
app.config.from_object(__name__)

Session(app)

app.jinja_env.filters["convert_date"] = unix_to_MD # 'env.filters' is a dict

""" DB creation """

# Could change to another DB in the future but there's no need to get complicated right now.

connection = sqlite3.connect("gyms.db") # Connection.
createDB()                              # Creates a DB with 'gyms', 'members' and 'routines' tables.
connection.close()


""" WEBPAGES """


@app.route("/")
def index():

    """ The presentation to our service """

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    """ Registration page """

    if request.method == "POST":

        gym_name = request.form.get("gym_name")
        email_address = request.form.get("email_address")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")

        # Check if all the data was input.

        if not gym_name or not email_address or not password or not repeat_password:
            return "PLEASE FILL ALL FIELDS" # Apology
        
        connection = sqlite3.connect("gyms.db")
        connection.row_factory = dict_factory

        cursor = connection.cursor()

        # Check if email has been used.

        cursor.execute("SELECT * " \
                        "FROM gyms " \
                        "WHERE gym_email IS ?", (email_address,))

        row = cursor.fetchone()

        # If there are rows with that email, notify the user.

        if row != None:
            return "EMAIL IN USE" # Apology
        
        # Check if passwords match.

        if password != repeat_password:
            return "PASSWORDS MUST MATCH" # Apology
        
        # Check if password is the right length.

        if len(password) < 8:
            return "PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG" # Apology

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

        cursor.close()
        connection.close() 

        return redirect("/login")
    
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    """ Login page """

    if request.method == "POST":

        gym_email = request.form.get("email_address")
        password = request.form.get("password")

        # Check if all fields have been filled.

        if not gym_email or not password:
            return "PLEASE FILL ALL FIELDS" # Apology
        
        # Get gym data from DB.

        query = ("SELECT * " \
                "FROM gyms " \
                "WHERE gym_email = ?" # Will return the row with all the gym data.
                )
        
        connection = sqlite3.connect("gyms.db")
        connection.row_factory = dict_factory

        cursor = connection.cursor()

        cursor.execute(query, (gym_email,)) # Must pass variables as a tuple, even if there is just a single one.

        # Save the whole row as a dict. (Honestly, this is unnecesary here, but if it ain't broke don't fix it).

        row = cursor.fetchone() 

        connection.close()
        
        # Check if there are any users with that email and check the password.

        if row is None or not check_password_hash(
            row["password_hash"], password
        ):
            return "INVALID EMAIL OR PASSWORD" # Apology
        
        session["gym_id"] = row["gym_id"]
        return redirect("/homepage")


    return render_template("login.html")

@app.route("/logout")
def logout():

    """ Logout the user """

    session.clear()

    return redirect("/")

@app.route("/homepage")
def homepage():

    """ Gym owner's menu """

    # Check if a session is open.

    if "gym_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect("gyms.db")
    connection.row_factory = dict_factory

    cursor = connection.cursor()

    # Show members in a list.

    query = ("SELECT * "
            "FROM members "
            "WHERE gym_id = ?;")

    cursor.execute(query, (session["gym_id"],))

    members = cursor.fetchall() 

    return render_template("homepage.html", members=members)

@app.route("/new_member", methods=["GET", "POST"])
def new_member():

    """ INSERT A NEW MEMBER TO DB """


    if request.method == "POST": 

        # Get data from form.

        member_id = request.form.get("id")
        name = request.form.get("first_name")
        last_name =request.form.get("last_name")
        gym_id = session["gym_id"]
        joined_date = int(time.time()) # Saved in UNIX timestamp
        end_date = joined_date

        # ID validation

        if isinstance(member_id, int):
            return "PLEASE INPUT A VALID ID" # Apology

        if not member_id or not name or not last_name or not gym_id or not joined_date or not end_date:
            return "Please fill all fields." # Apology

        connection = sqlite3.connect("gyms.db")
        connection.row_factory = dict_factory

        cursor = connection.cursor()

        query = ("SELECT member_id "
                "FROM members "
                "WHERE member_id = ?;"
                )
        
        cursor.execute(query, (member_id,))
        row = cursor.fetchone()

        if row is not None:
            return "Member is already registered" # Should find a better solution # Apology

        # Insert query

        query = ("INSERT INTO "
                "members ("
                        "member_id, " \
                        "name, " \
                        "gym_id, " \
                        "joined_date, " \
                        "end_date)" \
                "VALUES (?, ?, ?, ?, ?);"
                )
        
        cursor.execute(query, 
                       (member_id, name + " " + last_name, gym_id, joined_date, end_date) # Awful design honestly
                       )
        
        connection.commit()

        cursor.close()
        connection.close()
        
        return redirect("homepage")

    return render_template("new_member.html")

@app.route("/reception", methods=["GET", "POST"])
def reception():

    """ Get a member's ID and determine if it's a registered user """

    if request.method == "POST":

        member_id = request.form.get("member_id")

        query = "SELECT * " \
                "FROM members " \
                "WHERE member_id = ?" \
                "AND " \
                "gym_id = ?;"
        
        connection = sqlite3.connect("gyms.db")
        connection.row_factory = dict_factory

        cursor = connection.cursor()

        cursor.execute(query, (member_id, session["gym_id"]))

        row = cursor.fetchone()
         
        if row is None: # Should use JS here, not Python.
            return "MEMBER NOT FOUND" # Apology

    return render_template("reception.html")