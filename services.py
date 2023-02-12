from models import User, Customer, Service, Invoice
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from database import SessionLocal


bcrypt = Bcrypt()
db = SessionLocal()


class UserService:
    '''Services for getting user info'''

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        try:
            user = User(
                username=username,
                email=email,
                password=hashed_pwd
            )

            db.add(user)
            db.commit()
            db.close()
            return user
        except IntegrityError:
            db.rollback()
            return None
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = db.query(User).filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        db.rollback()
        return False

   
    

class CustomerService:
    '''Services for getting customer info'''
    @classmethod
    def add_customer(self, form_data):
        try:
            customer = Customer(
                full_name=form_data.full_name.data,
                address=form_data.address.data,
                tax_id=float(form_data.tax_id.data) if form_data.tax_id.data else None,
                phone=form_data.phone.data,
                email=form_data.email.data
            )
            db.add(customer)
            db.commit()
            return customer
        except IntegrityError:
            return None
    @classmethod
    def get_10_customers(self):
        customers = (db.query(Customer)
                    .order_by(Customer.created_date.desc())
                    .limit(10)
                    .all())
        return customers

    @classmethod
    def get_all_customers(self):
        customers = (db.query(Customer)
                    .order_by(Customer.created_date.desc())
                    .all())
        return customers

class ServiceService:
    @classmethod
    def add_service(self, form_data):
        try:
            service = Service(
                        description=form_data.description.data,
                        price_per_unit=form_data.price_per_unit.data,
                        unit=form_data.unit.data
                        )
            db.add(service)
            db.commit()
            
            return service
        except IntegrityError:
            return None
    @classmethod
    def get_all_services(self):
        services = (db.query(Service)
                    .all())
        return services

