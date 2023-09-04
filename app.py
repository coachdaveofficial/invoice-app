import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Company
from services import ServiceService, UserService, CustomerService, InvoiceService, PaymentService, CompanyService, EmployeeService, ServiceRequestService, ServicesForCompanyService, ServiceRateService
from forms import UserAddForm, LoginForm, CustomerAddForm, ServiceAddForm, InvoiceAddForm, PaymentForm
from functools import wraps
import json
import datetime


app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://', 1) or 'postgresql:///invoice-app')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///invoice-app'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)
# db.drop_all()
db.create_all()

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('signup'))
        return view_func(*args, **kwargs)
    return wrapped_view

def check_user_auth(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('Access unauthorized. Please sign in as the correct user.', 'danger')
            return redirect(url_for('home_page'))
        return view_func(*args, **kwargs)
    return wrapped_view

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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# LOGIN AND SIGNUP ROUTES 
# START ********************************
@app.route('/about', methods=["GET"])
def about_invoyz():
    return render_template('about.html')

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
@login_required
def home_page():
    
    now = datetime.datetime.utcnow()
    company_id = g.user.employer.company_id
    invoices = InvoiceService.get_company_invoices(company_id)
    services = ServiceService.get_services_for_company(company_id)
    customers = CustomerService.get_customers_for_company(company_id)
    payment_form = PaymentForm()
    return render_template('home_page.html',  
                            invoices=invoices,
                            services=services,
                            customers=customers,
                            payment_form=payment_form,
                            now=now)

# END ********************************

# CUSTOMERS ROUTES
# START ********************************

@app.route('/customers/add', methods=["GET", "POST"])
@check_user_auth
def add_new_customer():
    
    
    form = CustomerAddForm()

    if not form.validate_on_submit():
        return render_template('/customers/add_customer.html', form=form)
    
    customer = CustomerService.add_customer(form)

    if not customer:
        flash("Customer with similar credentials already exists", "danger")
        return redirect('/customers/add')

    return redirect('/')

@app.route('/customers', methods=["GET", "POST"])
@check_user_auth
def show_all_customers():
    
    form = CustomerAddForm()
    company_customers = CustomerService.get_customers_for_company(g.user.employer.company_id)
    company = CompanyService.get_company_by_id(g.user.employer.company_id)

    if not form.validate_on_submit():
        return render_template('/customers/list_customers.html', customers=company_customers, company=company, form=form)
    
    CustomerService.add_customer(form_data=form, comp_id=g.user.employer.company_id)
    return redirect('/customers')

@app.route('/customers/<int:cust_id>/delete', methods=["POST"])
@check_user_auth
def delete_customer(cust_id):
    CustomerService.set_delete_date_for_customer_by_id(cust_id)
    return {}

@app.route('/customers/<int:cust_id>/edit', methods=["POST"])
@check_user_auth
def edit_customer(cust_id):
    edit_form = json.loads(request.data)
    customer_info = CustomerService.edit_customer(cust_id=cust_id, form_data=edit_form)
    return customer_info

# END ********************************

# SERVICES ROUTES
# START ********************************

@app.route('/services', methods=["GET", "POST"])
@check_user_auth
def services_menu():
    form = ServiceAddForm()
    if not form.validate_on_submit():
        # services are alphabetized by default
        all_services = ServiceService.get_services_for_company(g.user.employer.company_id)
        company = CompanyService.get_company_by_id(g.user.employer.company_id)
        return render_template('/services/list_services.html', services=all_services, company=company, form=form)

    
    rate = ServiceRateService.add_rate(float(form.rate.data))
    service = ServiceService.add_service(form_data=form, rate_id=rate.id)
    # link service to user's company
    ServicesForCompanyService.add_service(comp_id=g.user.employer.company_id, serv_id=service.id)
    return redirect('/services')

@app.route('/services/<int:service_id>/edit', methods=["POST"])
@check_user_auth
def edit_service(service_id):
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')
    service = ServiceService.update_service(service_id=service_id, form_data=(json.loads(request.data)))
    return service

@app.route('/api/service/<int:service_id>')
@check_user_auth
def get_service_data(service_id):
    return ServiceService.get_service_data(service_id) 

@app.route('/services/<int:service_id>/delete', methods=["POST"])
@check_user_auth
def delete_service(service_id):
    
    service = ServiceService.get_service_by_id(service_id)
    if not service:
        return render_template('404.html'), 404
    company_ids = [c.id for c in service.companies]
    if g.user.employer.company_id not in company_ids:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    ServicesForCompanyService.remove_company_service(serv_id=service_id, comp_id=g.user.employer.company_id)
    
    return {}

# END ********************************  

# INVOICES ROUTES
# START ********************************

@app.route('/invoices/', methods=["POST"])
@check_user_auth
def add_new_estimate():
    
    cust_id = json.loads(request.data)['customerId']
    comp_id = g.user.employer.company_id  
    
    estimate = InvoiceService.create_estimate(cust_id=cust_id, comp_id=comp_id)



    services_and_quantity = json.loads(request.data)['services']
    for service in services_and_quantity:
        ServiceRequestService.add_service_request(
                                service_id=service['serviceId'], 
                                quantity=service['quantity'], 
                                invoice_id=estimate.id)
    return {'id': estimate.id}

@app.route('/invoices/<int:estimate_id>/finalize', methods=["POST"])
@check_user_auth
def finalize_invoice(estimate_id):
    
    invoice = InvoiceService.get_invoice_by_id(estimate_id)
    if not invoice:
        return render_template('404.html'), 404
    if g.user.employer.company_id != invoice.company_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    due_date = json.loads(request.data)['due']
    invoice.due_date = due_date
    invoice.is_estimate = False
    db.session.commit()
    # JavaScript handles the redirect here
    return redirect(f'/estimates/{estimate_id}')

@app.route('/invoices/<int:invoice_id>')
@check_user_auth
def display_invoice(invoice_id):
    
    invoice = InvoiceService.get_invoice_by_id(invoice_id)
    if not invoice:
        return render_template('404.html'), 404
    if g.user.employer.company_id != invoice.company_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    if invoice.is_estimate:
        flash("Invoice does not exist. Make sure your finalize your invoice before trying to view.", "danger")
        return redirect("/")
    
    company = CompanyService.get_company_by_id(invoice.company_id)
    customer = CustomerService.get_customer_by_id(invoice.cust_id)
    service_descriptions = ServiceService.get_services_for_invoice(invoice.id)

    
    
    return render_template('invoices/invoice.html', 
                            invoice=invoice,
                            company=company,
                            customer=customer,
                            services=service_descriptions)

@app.route('/invoices/<int:invoice_id>/payment/data')
@check_user_auth
def get_invoice_data(invoice_id):
    
    invoice = InvoiceService.get_invoice_by_id(invoice_id)
    if not invoice:
        return render_template('404.html'), 404
    if invoice.company_id != g.user.employer.company_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    return {
            'customer_name': invoice.customer.full_name,
            'customer_phone': invoice.customer.phone,
            'customer_email': invoice.customer.email,
            'invoice_id': invoice.id,
            'total_cost': invoice.total_cost,
            'payment_info': [{'ref_num': p.reference_num,'amount': p.amount,'date': p.created_date} for p in invoice.payments]
            }

# END ********************************

# ESTIMATES ROUTES
# START ********************************

@app.route('/estimates/<int:estimate_id>')
@check_user_auth
def show_estimate_info(estimate_id):
    
    estimate = InvoiceService.get_invoice_by_id(estimate_id)
    if not estimate:
        return render_template('404.html'), 404
    if estimate.company_id != g.user.employer.company_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    company = CompanyService.get_company_by_id(estimate.company_id)
    service_descriptions = ServiceService.get_services_for_invoice(estimate.id)
    customer = CustomerService.get_customer_by_id(estimate.cust_id)

    return render_template('invoices/estimate.html', 
                            estimate=estimate, 
                            company=company, 
                            services=service_descriptions, 
                            customer=customer)

@app.route('/estimates')
@check_user_auth
def show_all_estimates():

    estimates = InvoiceService.get_company_estimates(g.user.employer.company_id)
    company = CompanyService.get_company_by_id(g.user.employer.company_id)
    services = ServiceService.get_services_for_company(company.id)
    customers = CustomerService.get_customers_for_company(company.id)

    return render_template('invoices/list_estimates.html', estimates=estimates, company=company, services=services, customers=customers)

# END ********************************

# PAYMENTS ROUTES 
# START ********************************
@app.route('/payments/<int:invoice_id>', methods=["POST"])
@check_user_auth
def add_payment(invoice_id):
    PaymentService.add_payment(invoice_id=invoice_id, form_data=request.form)
    return redirect('/')

# END ********************************

if __name__ == "__main__":
    app.run()