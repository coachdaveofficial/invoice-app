import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Company
from services import ServiceService, UserService, CustomerService, InvoiceService, PaymentService, CompanyService, EmployeeService
from forms import UserAddForm, LoginForm, CustomerAddForm, ServiceAddForm, InvoiceAddForm

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///invoice-app'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
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

    signup_form = UserAddForm()

    if not signup_form.validate_on_submit():
        return render_template('users/signup.html', signup_form=signup_form)

    u = UserService()

    user = u.signup(
        username=signup_form.username.data,
        email=signup_form.email.data,
        password=signup_form.password.data
        )

    if not user:
        flash("Username or Email already taken", 'danger')
        return redirect('/signup')
    
    company = CompanyService.create_company(company_name=signup_form.company_name.data, owner_id=user.id)

    if not company:
        flash("Company with that name already exists", "danger")
        UserService.delete_user(user.id)
        return redirect('/signup')
        
    do_login(user)
    EmployeeService.set_employer(user_id=user.id, company_id=company.id)
    return redirect('/')

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if not form.validate_on_submit():
        return render_template('users/login.html', form=form)

    user = UserService.authenticate(
        username=form.username.data,
        password=form.password.data
        )

    if user:
        do_login(user)
        flash(f"Hello, {user.username}!", "success")
        return redirect("/")

    flash("Invalid credentials.", 'danger')
    return redirect('/login')

@app.route('/logout')
def logout():
    """Handle logout of user."""


    do_logout()
    flash(f"Successfully logged out!", "success")
    return redirect("/login")

@app.route('/guest')
def guest_login():

    demo = UserService.find_user_by_username("Guest")
    do_login(demo)
    flash(f"Hello, {demo.username}!", "success")
    return redirect("/")

@app.route('/')
def home_page():
    print(g.user)
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")
    

    ten_recent_customers = CustomerService.get_10_customers()
    payment_history = InvoiceService.get_five_oldest_outstanding()
    yearly_revenue = PaymentService.get_yearly_revenue('2023')
    all_services = ServiceService.get_all_services()
    companies = CompanyService.get_all_companies()

    print(g.user.employer.company_id)

    invoices = InvoiceService.get_company_invoices(g.user.employer.company_id)
    print(invoices)
    

    

    return render_template('home_page.html', 
                            companies=companies, 
                            customers=ten_recent_customers, 
                            payment_history=payment_history, 
                            yearly_revenue=yearly_revenue, 
                            services=all_services, 
                            invoices=invoices)


@app.route('/customers/add', methods=["GET", "POST"])
def add_new_customer():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = CustomerAddForm()

    if not form.validate_on_submit():
        return render_template('/customers/add_customer.html', form=form)
    
    customer = CustomerService.add_customer(form)

    if not customer:
        flash("Customer with similar credentials already exists", "danger")
        return redirect('/customers/add')

    return redirect('/')

@app.route('/customers', methods=["GET"])
def show_all_customers():
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')
    
    all_customers = CustomerService.get_all_customers()

    return render_template('/customers/list_customers.html', customers=all_customers)

@app.route('/services/add', methods=["GET", "POST"])
def add_new_service():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = ServiceAddForm()

    if not form.validate_on_submit():
        return render_template('/services/add_service.html', form=form)
    
    service = ServiceService.add_service(form)

    if not service:
        flash("Service with similar credentials already exists", "danger")
        return redirect('/services/add')

    return redirect('/')

@app.route('/services', methods=["GET"])
def show_all_services():

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')
    
    all_services = ServiceService.get_all_services()

    return render_template('/services/list_services.html', services=all_services)

@app.route('/api/service/<int:service_id>')
def get_service_data(service_id):
    return ServiceService.get_service(service_id)    

@app.route('/invoices/add', methods=["GET", "POST"])
def add_new_invoice():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    