from flask import redirect, session
from functools import wraps
import datetime
import time
import sqlite3

def createDB():

    """ Initializes the DB """

    connection = sqlite3.connect("gyms.db")
    connection.execute("PRAGMA foreign_keys = ON") # Foreign keys are turned off in sqlite3 by default.
    cursor = connection.cursor() # Cursor object

    """ CREATE GYMS TABLE """

    cursor.execute("CREATE TABLE IF NOT EXISTS gyms (" \
                "gym_id INTEGER PRIMARY KEY AUTOINCREMENT," \
                "gym_name TEXT NOT NULL," \
                "gym_email TEXT UNIQUE NOT NULL CHECK (gym_email LIKE '%@%.%')," \
                "password_hash VARCHAR(255) NOT NULL );" # VARCHAR is used for password hashes because of
                                                        # the variable lenghts of the hashes and for future-proofing .

                                                        # SQLite ignores this type because it doesn't have a limit for strings.
                                                        # It doesn't throw an error for compatibility with other DB software.
                )

    """ CREATE MEMBERS TABLE """

    # 'member_id' is the member's national ID number.

    cursor.execute("CREATE TABLE IF NOT EXISTS members (" \
                "member_id INTEGER PRIMARY KEY, " \
                "name TEXT NOT NULL, " \
                "gym_id INTEGER NOT NULL, " \
                "joined_date INTEGER NOT NULL, " \
                "end_date INTEGER NOT NULL, " \
                "status TEXT NOT NULL DEFAULT 'Inactive', " \
                "last_visit INTEGER, " \
                "FOREIGN KEY (gym_id) REFERENCES gyms (gym_id));"
                )
    
    """ CREATE ROUTINES TABLE """

    cursor.execute("CREATE TABLE IF NOT EXISTS routines (" \
                "member_id INTEGER PRIMARY KEY NOT NULL, " \
                "Monday TEXT NOT NULL DEFAULT 'Rest day', "
                "Tuesday TEXT NOT NULL DEFAULT 'Rest day', "
                "Wednesday TEXT NOT NULL DEFAULT 'Rest day', "
                "Thursday TEXT NOT NULL DEFAULT 'Rest day', "
                "Friday TEXT NOT NULL DEFAULT 'Rest day', "
                "Saturday TEXT NOT NULL DEFAULT 'Rest day', "
                "Sunday TEXT NOT NULL DEFAULT 'Rest day', " \
                "FOREIGN KEY (member_id) REFERENCES members (member_id));"
                )
    
    """ CREATE CHECK-IN AND CHECK-OUT TABLE"""  

    cursor.execute("CREATE TABLE IF NOT EXISTS access_logs( " \
                "access_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                "member_id INTEGER, " \
                "check_in_time INTEGER);" \
                )
    
    connection.commit()

    cursor.close() # Connection isn't closed in this function for future usage in 'app.py'.

def dict_factory(cursor, row):

    """ Turns the result of a query into a dict """

    result = {}

    for index, column in enumerate(cursor.description): # cursor.description returns a list of tuples with the first element being name of the column.
                                                        # enumerate(cursor.description) returns something like:
                                                        # (index, nameOfColumn) -- nameOfColumn is actually a tuple list, but in SQLite it only returns the name of the column, the others being 'None'.

        result[column[0]] = row[index]                  # column[0] is the name of the column. row[index] is the value of the row.
                                                        # Example: result["email_Address"] = "email@example.com"

    return result

def unix_to_date(timestamp):

    """ Convert Unix timestamp to a readable date """
    """ Jinja2 templates, credits to Przemek Rogala's blog"""
    """ time.strftime formatinc, credits to geeksforgeeks.org"""
    
    if timestamp is None:
        return ""
    return time.strftime("%b, %d ", time.localtime(timestamp))

def login_required(f):
    """
    Decorator for routes to require login
    
    Credit to:
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("gym_id") is None: # Slight modification to original function.
            return redirect("/login")     # 'gym_id' is used for consistent naming.
        return f(*args, **kwargs)

    return decorated_function

def is_member_active(member):

    """ Compares caducation date to current date """

    today_date = int(datetime.datetime.now().timestamp())

    return today_date < member["end_date"]

def update_member_status(gym_id): 

    """ Check all members status' and update it if necessary """

    connection = sqlite3.connect("gyms.db")
    connection.row_factory = dict_factory

    cursor = connection.cursor()

    query = "SELECT member_id, end_date, status " \
            "FROM members " \
            "WHERE gym_id = ?; "
    
    cursor.execute(query, (gym_id,))

    members = cursor.fetchall()
    
    for member in members:
        if is_member_active(member):
            query = "UPDATE members " \
                    "SET status = 'Active' " \
                    "WHERE member_id = ? AND gym_id = ?;"
            cursor.execute(query, (member["member_id"], gym_id))
            connection.commit()
        else: 
            query = "UPDATE members " \
                    "SET status = 'Inactive' " \
                    "WHERE member_id = ? AND gym_id = ?;"
            cursor.execute(query, (member["member_id"], gym_id))
            connection.commit()

    connection.close()

def days_remaining(member):

    """ Calculate how many days of subscription a member has left """
    """ Returns an int"""

    today = datetime.date.today()
    end_date = datetime.date.fromtimestamp((member["end_date"]))

    days_remaining = (end_date - today).days
    
    if days_remaining < 0:
        return "Expired"

    return (f"{days_remaining} days")