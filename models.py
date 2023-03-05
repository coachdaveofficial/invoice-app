"""SQLAlchemy models for Invoice App."""

from datetime import datetime
import enum

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


class enPaymentType(enum.Enum):
    credit_card = 1
    check = 2
    venmo = 3
    paypal = 4
    cashapp = 5



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
    # company_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('companies.id')
    # )
    
    employer = db.relationship("Employee", backref="users", uselist=False)


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )
    owner_id = db.Column(
        db.ForeignKey('users.id'),
        nullable=False
        
    )
    employees = db.relationship("Employee", backref="companies")
    customers = db.relationship("Customer", backref="companies")
    invoices = db.relationship("Invoice", backref="companies")
    # services = db.relationship("Service", secondary="company_services", backref="companies")

    
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(
        db.Integer,
        primary_key=True
        )
    company_id = db.Column(
            db.Integer,
            db.ForeignKey("companies.id"),
            nullable=False
            )
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False,
        unique=True
        )
    


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
        db.String, 
        nullable=False, 
        unique=True
        )
    email = db.Column(
        db.String(255), 
        nullable=False, 
        unique=True
        )
    company_id = db.Column(
            db.Integer,
            db.ForeignKey("companies.id"),
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
    deleted_date = db.Column(
        db.DateTime
        )

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
    invoice_id = db.Column(
        db.Integer, 
        db.ForeignKey('invoices.id'), 
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


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(
        db.Integer, 
        primary_key=True
        )
    due_date = db.Column(
        db.Date
        )
    cust_id = db.Column(
        db.Integer, 
        db.ForeignKey('customers.id'), 
        nullable=False
        )
    total_cost = db.Column(
        db.Float
        )
    company_id = db.Column(
        db.Integer, 
        db.ForeignKey('companies.id'), 
        nullable=False
        )
    is_estimate = db.Column(
        db.Boolean,
        default=True
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

    service_requests = db.relationship('ServiceRequest', backref='invoices')

class Payment(db.Model):
    __tablename__ = "payments"

    id =  db.Column(
         db.Integer, 
        primary_key=True
        )
    invoice_id =  db.Column(
         db.Integer, 
         db.ForeignKey('invoices.id')
        )
    amount = db.Column(
            db.Float,
            nullable=False
        )
    payment_type = db.Column(
        db.Enum(enPaymentType),
        nullable=False
        )
    reference_num = db.Column(
        db.String,
        nullable=False
        )
    created_date = db.Column(
        db.DateTime, 
        default=datetime.utcnow
        )

    payments = db.relationship('Invoice', backref="payments")

class ServiceRate(db.Model):
    __tablename__ = 'service_rates'

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    amount = db.Column(
        db.Float
    )
class Unit(db.Model):
    __tablename__ = 'units'

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    name = db.Column(
        db.String(50),
        unique=True
    )
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
    service_rate_id = db.Column(
        db.Integer,
        db.ForeignKey('service_rates.id')
        )
    unit_id = db.Column(
        db.Integer,
        db.ForeignKey('units.id')
        )

    companies = db.relationship(
        'Company',
        secondary='company_services',
        backref='services'
    )
    unit = db.relationship('Unit', backref='services')
    rate = db.relationship('ServiceRate', backref='services')
    
class ServicesForCompany(db.Model):
    __tablename__ = 'company_services'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id')
    )
    service_id = db.Column(
        db.Integer,
        db.ForeignKey('services.id')
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







