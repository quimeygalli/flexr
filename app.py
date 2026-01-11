import sqlite3

from cachelib.file import FileSystemCache
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from flask import Flask, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session

from helpers import createDB, dict_factory, unix_to_date, login_required, update_member_status, days_remaining
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

app.jinja_env.filters["convert_date"] = unix_to_date # 'env.filters' is a dict

""" DB creation """

# Could change to another DB in the future but there's no need to get complicated right now.

connection = sqlite3.connect("gyms.db") # Connection.
createDB()                              # Creates a DB with 'gyms', 'members' and 'routines' tables.
connection.close()


""" WEBPAGES: """


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
@login_required
def logout():

    """ Logout the user """

    session.clear()

    return redirect("/")

@app.route("/homepage")
@login_required
def homepage():

    """ Gym owner's menu """

    update_member_status(session["gym_id"])

    connection = sqlite3.connect("gyms.db")
    connection.row_factory = dict_factory

    cursor = connection.cursor()

    query = "SELECT * " \
            "FROM members " \
            "WHERE gym_id = ?;"

    cursor.execute(query, (session["gym_id"],))

    members = cursor.fetchall() 

    query = "SELECT * " \
            "FROM members " \
            "WHERE gym_id = ?;"

    cursor.execute(query, (session["gym_id"],))

    members = cursor.fetchall() 
    connection.close()

    return render_template("homepage.html", members=members)

@app.route("/members/<int:member_id>", methods=["GET", "POST"])
@login_required
def member_detail(member_id):

    """ Show member information """

    connection = sqlite3.connect("gyms.db")
    connection.row_factory = dict_factory

    cursor = connection.cursor()

    query = "SELECT * " \
            "FROM members " \
            "WHERE member_id = ?;"
    
    cursor.execute(query, (member_id,))
    member_row = cursor.fetchone()

    # Member data

    name = member_row["name"]
    gym_id = member_row["gym_id"]
    joined_date = member_row["joined_date"]
    end_date = member_row["end_date"]
    status = member_row["status"]
    last_visit = member_row["last_visit"]
    days_left = days_remaining(member_row)

    # Routine data

    query = "SELECT * " \
            "FROM routines " \
            "WHERE member_id = ?;"
    
    cursor.execute(query, (member_id,))
    routine_row = cursor.fetchone()

    cursor.close()
    connection.close()

    monday = routine_row["Monday"]
    tuesday = routine_row["Tuesday"]
    wednesday = routine_row["Wednesday"]
    thursday = routine_row["Thursday"]
    friday = routine_row["Friday"]
    saturday = routine_row["Saturday"]
    sunday = routine_row["Sunday"]

    # Delete button

    if request.method == "POST":

        if request.form.get("delete_member"):
            connection = sqlite3.connect("gyms.db")
            cursor = connection.cursor()

            query = "DELETE FROM members " \
                    "WHERE member_id = ? AND gym_id = ?;"
            cursor.execute(query, (member_id, gym_id))
            connection.commit()

            query = "DELETE FROM routines " \
                    "WHERE member_id = ?;"
            cursor.execute(query, (member_id,))
            connection.commit()

            connection.close()
            
            return redirect("/homepage")
            

    return render_template("member_details.html", 
                           name=name,
                           gym_id=gym_id,
                           joined_date=joined_date,
                           end_date=end_date,
                           status=status,
                           last_visit=last_visit,
                           member_id=member_id,
                           days_left=days_left,
                           
                           monday=monday,
                           tuesday=tuesday,
                           wednesday=wednesday,
                           thursday=thursday,
                           friday=friday,
                           saturday=saturday,
                           sunday=sunday)

@app.route("/edit_routine/<int:member_id>", methods=["GET", "POST"])
@login_required
def edit_routine(member_id):

    """ Allows trainers to add and edit a member's routine """

    connection = sqlite3.connect("gyms.db")
    connection.row_factory = dict_factory

    cursor = connection.cursor()

    query = "SELECT * " \
            "FROM routines " \
            "WHERE member_id = ?;"
    
    cursor.execute(query, (member_id,))

    current_routine = cursor.fetchone()

    if request.method == "POST":
        print("POSTED")
        monday = request.form.get("monday")
        tuesday = request.form.get("tuesday")
        wednesday = request.form.get("wednesday")
        thursday = request.form.get("thursday")
        friday = request.form.get("friday")
        saturday = request.form.get("saturday")
        sunday = request.form.get("sunday")
        print(monday)

        query = "UPDATE routines " \
                "SET " \
                "Monday = ?, " \
                "Tuesday = ?, " \
                "Wednesday = ?, " \
                "Thursday = ?, " \
                "Friday = ?, " \
                "Saturday = ?, " \
                "Sunday = ? " \
                "WHERE member_id = ?;"
        
        cursor.execute(query, (monday,
                                tuesday,
                                wednesday,
                                thursday,
                                friday ,
                                saturday,
                                sunday,
                                member_id))
        
        connection.commit()
        return redirect(url_for("member_detail", member_id=member_id))

    connection.close
    
    return render_template("edit_routine.html",
                           routine=current_routine,
                           member_id=member_id)

@app.route("/new_member", methods=["GET", "POST"])
@login_required
def new_member():

    """ INSERT A NEW MEMBER TO DB """

    if request.method == "POST": 

        # Get data from form.

        member_id = request.form.get("id")
        name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        subscription_months = int(request.form.get("subscription_months"))

        # Implicit data from gym/date.

        gym_id = session["gym_id"]
        joined_date = datetime.now()

        end_date = joined_date + relativedelta(months=subscription_months)

        # ID validation.

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
            return "Member is already registered" # Apology

        # Insert member into members table.

        query = ("INSERT INTO "
                "members ("
                        "member_id, " \
                        "name, " \
                        "gym_id, " \
                        "joined_date, " \
                        "end_date)" \
                "VALUES (?, ?, ?, ?, ?);"
                )
        
        joined_unix_timestamp = int(joined_date.timestamp())
        end_unix_timestamp = int(end_date.timestamp())

        cursor.execute(query, 
                       (member_id, name + " " + last_name, gym_id, joined_unix_timestamp, end_unix_timestamp) # Awful design honestly
                       )
        
        connection.commit()
        
        # Insert member into routines table

        query = "INSERT INTO routines (member_id) " \
                "VALUES (?) ;"

        cursor.execute(query, (member_id,))        
        connection.commit()

        cursor.close()
        connection.close()
        
        return redirect("homepage")

    return render_template("new_member.html")


@app.route("/reception")
@login_required
def reception():

    """ Render reception """

    update_member_status(session["gym_id"]) # Update members status. Not the best design.

    return render_template("reception.html")


@app.route("/api/check_member", methods=["POST"]) # Handle the JS. Helps prevent page from reloading. Calling it /api... is convention.
def check_member_api():

    """ Check if input id exists and use JS as an intermediary to modify HTML """

    # Get JSON data sent from JavaScript.
    id = request.get_json()
    member_id = id.get("member_id") # This matches the key sent frm JS.
    
    connection = sqlite3.connect("gyms.db")
    connection.row_factory = dict_factory
    cursor = connection.cursor()

    query = "SELECT * " \
            "FROM members " \
            "WHERE member_id = ? AND gym_id = ?;"

    cursor.execute(query, (member_id, session["gym_id"]))
    row = cursor.fetchone()

    if row is None: # If no id has been found, return false.
        # Return a JSON
        connection.close()
        return jsonify({"exists": False})
    
    elif row["status"] == "Inactive":
        connection.close()
        return jsonify({"exists": True,
                        "status": row["status"]})

    # Log the last visit of member

    last_visit = int(datetime.now().timestamp()) 
 
    query = "UPDATE members " \
            "SET last_visit = ? " \
            "WHERE member_id = ?;"

    cursor.execute(query, (last_visit, member_id))
    connection.commit()

    query = "INSERT INTO " \
            "access_logs (member_id, check_in_time) " \
            "VALUES (?, ?);"
    
    cursor.execute(query, (member_id, last_visit))
    connection.commit()

    connection.close()
    
    return jsonify({
        "exists": True, 
        "status": row["status"],
        "name": row["name"] # Send the name to the JS.
    })