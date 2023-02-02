"""SQLAlchemy models for Invoice App."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)


# class BaseModel(Base):
#     __abstract__ = True
#     created_date = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     deleted_date = db.Column(db.DateTime)


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False



class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(
                db.Integer, 
                primary_key=True
                )
    full_name = db.Column(
        db.String(255), 
        nullable=False
        )
    address = db.Column(
        db.String(255), 
        nullable=False
        )
    tax_id = db.Column(
        db.Integer
        )
    phone = db.Column(
        db.Integer, 
        nullable=False, 
        unique=True
        )
    email = db.Column(
        db.String(255), 
        nullable=False, 
        unique=True
        )
    created_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow
        )
    updated_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
        )
    deleted_date = db.Column(
        db.DateTime
        )

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(
        db.Integer, 
        primary_key=True
        )
    due_date = db.Column(
        db.Date, 
        nullable=False
        )
    cust_id = db.Column(
        db.Integer, 
        db.ForeignKey('customers.id'), 
        nullable=False
        )
    amount_paid = db.Column(
        db.Float, 
        nullable=False
        )
    total_cost = db.Column(
        db.Float, 
        nullable=False
        )
    created_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow
        )
    updated_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
        )
    deleted_date = db.Column(db.DateTime)

    service_requests = db.relationship('ServiceRequest', backref="invoices")

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(
        db.Integer, 
        primary_key=True
        )
    service_id = db.Column(
        db.Integer, 
        db.ForeignKey('services.id'), 
        nullable=False
        )
    quantity = db.Column(
        db.Integer, 
        nullable=False
        )
    created_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow
        )
    updated_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
        )
    deleted_date = db.Column(db.DateTime)

    invoice = db.relationship("invoices")

class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(
        db.Integer, 
        primary_key=True
        )
    description = db.Column(
        db.Text, 
        nullable=False
        )
    price_per_unit = db.Column(
        db.Float, 
        nullable=False
        )
    unit = db.Column(
        db.String(50), 
        nullable=False
        )
    

class Discount(db.Model):
    __tablename__ = 'discounts'
    id = db.Column(
        db.Integer, 
        primary_key=True
        )
    cust_id = db.Column(
        db.Integer, 
        db.ForeignKey('customers.id'), 
        nullable=False
        )
    service_id = db.Column(
        db.Integer, 
        db.ForeignKey('services.id'), 
        nullable=False
        )
    rate = db.Column(
        db.Float, 
        nullable=False
        )
    date_deleted = db.Column(db.Date)

class ServiceRequestInvoice(db.Model):
    __tablename__ = 'service_request_invoice'

    id = db.Column(
        db.Integer, 
        primary_key=True
        )
    service_request_id = db.Column(
        db.Integer, 
        db.ForeignKey('services.id')
        )
    invoice_id = db.Column(
        db.Integer, 
        db.ForeignKey('invoices.id')
        )







