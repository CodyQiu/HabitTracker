from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = "supersecretkey"  # Replace with a secure key in production, ensures that sessions are secure and tamper-proof


# Configure login manager
login_manager = LoginManager() # create instance of login manager
login_manager.init_app(app) # initialize with app
login_manager.login_view = "login" # where to redirect for @login_required

# User class for flask-login
class User(UserMixin): 
    def __init__(self, id=None, username=None):
        self.id = id
        self.username = username
@login_manager.user_loader # callback to reload user object
def load_user(user_id): # given user identifier
    db = get_db() # connect to db
    rows = db.execute("SELECT * FROM users WHERE id = ?", (user_id, )).fetchone() # fetchall() returns a list of all results and the username is unique so we expect one result. also, comma after username is necessary to make it a tuple
    if rows is None: # if user not found
        return None # return None
     # else, create user object and set id
    return User(id=str(rows[0]), username=rows[1]) # return user object with id and username



# Configure database
DATABASE = 'myapp.db'
def get_db():
    if "db" not in g:  # if no db connection yet for this request
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us access columns by name
    return g.db
@app.teardown_appcontext # closes down db connection after request
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Basic route to render index page
@app.route("/")
#@login_required
def index():
    db=get_db()
    rows = db.execute("SELECT * FROM habits").fetchall()
    #print(rows)
    return render_template("index.html")


#Basic login system
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        db = get_db()
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username, )).fetchall() # fetchall() returns a list of all results and the username is unique so we expect one result. also, comma after username is necessary to make it a tuple
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], password):
            flash("Invalid username and/or password", "danger")
            return redirect('/login')


        session['username'] = username
        user = User()
        user.id = str(rows[0][0]) # set user id to the id from the database
        login_user(user) # log in user through flask-login

        flash('Login successful!', 'success') # later, will try to make flash fade out
        return redirect('/')
    else:
        return render_template('login.html')


#Basic logout system
@app.route("/logout")
def logout():
    session.clear()
    logout_user() # log out user through flask-login
    flash('Logged out successfully!', 'success') # later, will try to make flash fade out
    return redirect('/')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Here you would normally save the user to the database
        # Also make sure to hash the password before storing it
        username = request.form.get('username')
        password = request.form.get('password')
        hash = generate_password_hash(password, method="pbkdf2:sha256")
        confirm_password = request.form.get('confirmation')
        if not password == confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect('/register')
        flash("Registration successful! Please log in.", "success")

        db=get_db()
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
        db.commit()

        return redirect('/login')
    else:
        return render_template('login.html')
    

@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")
    
@app.route("/addHabits", methods = ['GET', 'POST'])
@login_required
def addHabits():
    if request.method == 'POST':
        # Here you would normally save the habit to the database
        habit = request.form.get('habit')
        duration = request.form.get('duration')
 
        db = get_db()
        db.execute("INSERT INTO habits (habit, duration, user_id) VALUES (?, ?, ?)", (habit, duration, int(current_user.get_id())))
        db.commit()


        flash(f"Habit '{habit}' with duration '{duration}' added!", "success")
        return redirect('/')
    else:
        return render_template("addHabits.html")

@app.route("/start")
@login_required
def start():
    db=get_db()
    rows = db.execute("SELECT * FROM habits").fetchall()
    return render_template("start.html", habits=rows)