import json

import sqlite3
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, is_password_valid

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create new database and open a database connection
connection = sqlite3.connect("hogwarts.db", check_same_thread=False)
# Access column names in query results
connection.row_factory = sqlite3.Row 
db = connection.cursor()

# Create new tables to keep track of the enrolment in subjects
db.execute("""CREATE TABLE IF NOT EXISTS enrolment (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, name TEXT NOT NULL, enrolled TEXT NOT NULL)""")
connection.commit()


@app.route("/")
def index():
    """Main website"""
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was provided
        if not username:
            return apology("must provide username")

        # Ensure name was provided
        if not name:
            return apology("must provide name")

        # Ensure password was provided
        if not password:
            return apology("must provide password")

        # Ensure confirmation was provided
        if not confirmation:
            return apology("must provide confirmation")
        
        # Ensure that user follows password requirements: at least 8 characters, at least one: lowercase letter, uppercase letter, special character [@$.!%*?&_-], and no whitespace characters
        if not is_password_valid(password):
            return apology("password must contain at least 8 characters, at least one uppercase letter, at least one number, and at least one special character")
        
        # Ensure password and confirmation match
        if password != confirmation:
            return apology("password and confirmation must match")

        # Ensure username is not already taken
        check_username = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if check_username is not None:
            return apology("username already exists")

        # Generate a hash of the password and add new user into the database
        hash_pass = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password, name) VALUES(?, ?, ?)", (username, hash_pass, name))
        new_user = db.lastrowid
        connection.commit()

        # Log the user in
        session["user_id"] = new_user

        # Redirect user to acceptance letter
        return render_template("modal.html", name=name)

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/sorting", methods=["POST"])
@login_required
def sorting():
    """Show the sorting hat quiz"""
    return render_template("sorting.html")


@app.route("/house", methods=["POST"])
@login_required
def house():
    """Get the result of the sorting hat quiz"""

    # Get id of currently logged in user
    user_id = session["user_id"]

    # Get the result in JSON from the quiz
    result = request.get_json()

    # Insert received data into the database
    db.execute("UPDATE users SET house = ? WHERE id = ?", (result, user_id))
    connection.commit()

    return render_template("studentpanel.html")


# login function - CS50, pset9, Finance
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(rows["password"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to student panel
        return render_template("studentpanel.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# logout function - CS50, pset9, Finance
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user homepage
    return redirect("/")


@app.route("/student")
@login_required
def student():
    """Show the student panel"""
    return render_template("studentpanel.html")

@app.route("/subjects")
@login_required
def subjects():
    """My Subjects"""

     # Get id of currently logged in user
    user_id = session["user_id"]

    # Get subjects' id, name, and teacher from subjects table
    enrolled_subjects = db.execute("SELECT subjects.id, subjects.subject, subjects.teacher FROM enrolment JOIN subjects ON subjects.id = enrolment.name WHERE enrolment.user_id = ? ", (user_id,)).fetchall()

    # Get curriculum for each subject 
    curriculum = db.execute("SELECT * FROM curriculum").fetchall()

    return render_template("mysubjects.html", enrolled_subjects=enrolled_subjects, curriculum=curriculum)


@app.route("/enrolment", methods=["GET", "POST"])
@login_required
def enrolment():
    """Subject Enrolment"""
    
    # Get id of currently logged in user
    user_id = session["user_id"]

    if request.method == "POST":

        # Get the subject name from JavaScript
        subject_name = request.get_json()["subject_name"]

        #Check if user is already enrolled in the subject
        check = db.execute("SELECT * FROM enrolment WHERE user_id = ? AND name = ?", (user_id, subject_name)).fetchone()

        if check is not None:
            return jsonify({"enrolled": True, "name": subject_name})

        else:
        # Insert received data into the database
            enrolled = "true"
            db.execute("INSERT INTO enrolment (user_id, name, enrolled) VALUES (?, ?, ?)", (user_id, subject_name, enrolled))
            connection.commit()

            return jsonify({"enrolled": True, "name": subject_name})
    
    else: 
        # Get all the subject names the user is enrolled in
        enrolled_subjects = db.execute("SELECT name FROM enrolment WHERE user_id = ? AND enrolled = 'true'", (user_id,)).fetchall()
        # Get the list of subject names as strings
        subjects = [subject[0] for subject in enrolled_subjects]
        # Convert the list to JSON
        subjects_json = json.dumps(subjects)

        return render_template("enrolment.html", subjects_json=subjects_json)


@app.route("/grades")
@login_required
def grades():
    """My Grades"""

    # Get id of currently logged in user
    user_id = session["user_id"]

    # Get the names of the subjects the user is enrolled in
    subjects = db.execute("SELECT subjects.subject FROM subjects JOIN enrolment ON enrolment.name = subjects.id WHERE user_id = ?", (user_id,)).fetchall()

    return render_template("grades.html", subjects=subjects)


@app.route("/schedule")
@login_required
def schedule():
    """Show the schedule"""
 
    return render_template("schedule.html")


@app.route("/list")
@login_required
def list():
    """Show the list of necessary books and equipment"""
    return render_template("list.html")


if __name__ == "__main__":
    app.run()
    connection.close()


