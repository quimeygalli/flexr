from flask import Flask, session, render_template, request
from flask_session import Session 
from cachelib.file import FileSystemCache

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
    threshold=500, # A maximum of cached sessions
    default_timeout=10 # Seconds a session will last
    ),
app.config.from_object(__name__)

Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    gymName = request.form.get("gymName")
    ownerName = request.form.get("gymName")
    emailAddress = request.form.get("emailAddress")
    password = request.form.get("password")
    repeatPassword = request.form.get("repeatPassword")

    app.logger.info(gymName)
    return render_template("register.html")