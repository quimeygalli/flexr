from flask import Flask, session, render_template, request
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

# Session config ->

app.config['SESSION_TYPE'] = "cachelib"
app.config['SESSION_PERMANENT'] = True
SESSION_CACHELIB = FileSystemCache(
    cache_dir="./sessions",
    threshold=500,              # A maximum of cached sessions
    default_timeout=10          # Amount of seconds a session will last
    ),
app.config.from_object(__name__)

Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        gymName = request.form.get("gymName")
        ownerName = request.form.get("gymName")
        emailAddress = request.form.get("emailAddress")
        password = request.form.get("password")
        repeatPassword = request.form.get("repeatPassword")

        # Hashing and salting password

        hashedPassword = generate_password_hash(password, method="scrypt", salt_length=32)

        #TODO: not a good check. would need some JS first, and in case 
        # the HTML is edited a python safety check (apology function would work) ->

        if not gymName or not ownerName or not emailAddress or not password or not repeatPassword:
            return apology("Please fill all fields", 100)
        
        if password != repeatPassword:
            return apology("Passwords must match")
    else:
        return render_template("register.html")


    return render_template("register.html")