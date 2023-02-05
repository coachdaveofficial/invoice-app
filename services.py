from models import User, db, Customer, Service
from sqlalchemy.exc import IntegrityError

def signup_user(form_data):
    try:
        user = User.signup(
            username=form_data.username.data,
            password=form_data.password.data,
            email=form_data.email.data
        )
        db.session.commit()
        return user

    except IntegrityError:
        return None

def login_user(form_data):
    user = User.authenticate(form_data.username.data,
                                form_data.password.data)
    return user

def add_customer(form_data):
    try:
        customer = Customer(
            full_name=form_data.full_name.data,
            address=form_data.address.data,
            tax_id=float(form_data.tax_id.data) if form_data.tax_id.data else None,
            phone=form_data.phone.data,
            email=form_data.email.data
        )
        db.session.add(customer)
        db.session.commit()
        return customer
    except IntegrityError:
        return None

def get_10_customers():
    customers = (Customer
                .query
                .order_by(Customer.created_date.desc())
                .limit(10)
                .all())
    return customers

def get_all_customers():
    customers = (Customer
                .query
                .order_by(Customer.created_date.desc())
                .all())
    return customers

def add_service(form_data):
    try:
        service = Service(
                    description=form_data.description.data,
                    price_per_unit=form_data.price_per_unit.data,
                    unit=form_data.unit.data
                    )
        db.session.add(service)
        db.session.commit()
        return service
    except IntegrityError:
        return None

def get_all_services():
    services = (Service
                .query
                .all())
    return services