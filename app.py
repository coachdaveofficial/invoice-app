import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from services import signup_user, login_user, add_customer
from forms import UserAddForm, LoginForm, CustomerAddForm

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///invoice-app'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)
# db.drop_all()
db.create_all()

CURR_USER_KEY = "curr_user"

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():

    form = UserAddForm()

    if not form.validate_on_submit():
        return render_template('users/signup.html', form=form)
    
    user = signup_user(form)
    
    if not user:
        flash("Username already taken", 'danger')
        return render_template('users/signup.html', form=form)

    return redirect('/')

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if not form.validate_on_submit():
        return render_template('users/login.html', form=form)

    user = login_user(form)

    if user:
        do_login(user)
        flash(f"Hello, {user.username}!", "success")
        return redirect("/")

    flash("Invalid credentials.", 'danger')
    return redirect('/signup')

@app.route('/')
def home_page():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

    return render_template('home_page.html')


@app.route('/customers/add', methods=["GET", "POST"])
def add_new_customer():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")
    
    form = CustomerAddForm()

    if not form.validate_on_submit():
        return render_template('/customers/add_customer.html', form=form)
    
    customer = add_customer(form)

    if not customer:
        flash("Customer with similar credentials already exists", "danger")
        return redirect('/customers/add')

    return redirect('/')
