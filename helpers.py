from flask import render_template
import sqlite3

def createDB():
    connection = sqlite3.connect("gyms.db")
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor() # Cursor object

    """ CREATE GYMS TABLE """

    cursor.execute("CREATE TABLE IF NOT EXISTS gyms (" \
                "gym_id INTEGER PRIMARY KEY AUTOINCREMENT," \
                "gym_Name TEXT NOT NULL," \
                "gym_Email TEXT UNIQUE NOT NULL CHECK (gym_Email LIKE '%@%.%')," \
                "password_Hash VARCHAR(255) NOT NULL );" # VARCHAR is used for password hashes because of
                                                        # the variable lenghts of the hashes and for future-proofing 

                                                        # SQLite ignores this type because it doesn't have a limit for strings.
                                                        # It doesn't throw an error for compatibility with other DB software.
                )

    """ CREATE MEMBERS TABLE """

    cursor.execute("CREATE TABLE IF NOT EXISTS members (" \
                "member_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                "name TEXT NOT NULL, " \
                "gym_id INTEGER NOT NULL, " \
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
                "FOREIGN KEY(member_id) REFERENCES members (member_id));"
                )
    connection.commit()

    cursor.close()

# Credits to CS50x finance pset for the apology function.
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code