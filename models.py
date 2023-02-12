"""SQLAlchemy models for Invoice App."""

from datetime import datetime
import enum

from flask_bcrypt import Bcrypt
from sqlalchemy import Table, Integer, Column, ForeignKey, Text, DateTime, Date, MetaData, Float, String, Enum
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base





Base = declarative_base()

bcrypt = Bcrypt()

meta = MetaData()


class enPaymentType(enum.Enum):
    credit_card = 1
    check = 2
    venmo = 3
    paypal = 4
    cashapp = 5


class User(Base):
    """User in the system."""

    __tablename__ = 'users'

    id = Column(
        Integer,
        primary_key=True,
    )
    email = Column(
        Text,
        nullable=False,
        unique=True,
    )
    username = Column(
        Text,
        nullable=False,
        unique=True,
    )
    password = Column(
        Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(
                Integer, 
                primary_key=True
                )
    full_name = Column(
        String(255), 
        nullable=False
        )
    address = Column(
        String(255), 
        nullable=False
        )
    tax_id = Column(
        Integer
        )
    phone = Column(
        String, 
        nullable=False, 
        unique=True
        )
    email = Column(
        String(255), 
        nullable=False, 
        unique=True
        )
    created_date = Column(
        DateTime, 
        default=datetime.utcnow
        )
    updated_date = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
        )
    deleted_date = Column(
        DateTime
        )

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(
     Integer, 
        primary_key=True
        )
    due_date = Column(
     Date, 
        nullable=False
        )
    cust_id = Column(
     Integer, 
     ForeignKey('customers.id'), 
        nullable=False
        )
    total_cost = Column(
     Float, 
        nullable=False
        )
    created_date = Column(
     DateTime, 
        default=datetime.utcnow
        )
    updated_date = Column(
     DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
        )
    deleted_date = Column( DateTime)

    service_requests =  relationship('ServiceRequest', backref="invoices")

class Payments(Base):
    __tablename__ = "payments"

    id =  Column(
         Integer, 
        primary_key=True
        )
    invoice_id =  Column(
         Integer, 
         ForeignKey('invoices.id')
        )
    amount = Column(
            Float,
            nullable=False
        )
    payment_type = Column(
        Enum(enPaymentType),
        nullable=False
        )
    reference_num = Column(
        String,
        nullable=False
        )
    created_date = Column(
        DateTime, 
        default=datetime.utcnow
        )


class ServiceRequest(Base):
    __tablename__ = 'service_request'

    id =  Column(
         Integer, 
        primary_key=True
        )
    service_id =  Column(
         Integer, 
         ForeignKey('services.id'), 
        nullable=False
        )
    invoice_id =  Column(
         Integer, 
         ForeignKey('invoices.id'), 
        nullable=False
        )
    quantity =  Column(
         Integer, 
        nullable=False
        )
    created_date =  Column(
         DateTime, 
        default=datetime.utcnow
        )
    updated_date =  Column(
         DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
        )
    deleted_date =  Column( DateTime)

    invoice =  relationship("Invoice", backref='service_request')

class Service(Base):
    __tablename__ = "services"

    id =  Column(
         Integer, 
        primary_key=True
        )
    description =  Column(
         Text, 
        nullable=False
        )
    price_per_unit =  Column(
         Float, 
        nullable=False
        )
    unit =  Column(
         String(50), 
        nullable=False
        )
    

class Discount(Base):
    __tablename__ = 'discounts'
    id =  Column(
         Integer, 
        primary_key=True
        )
    cust_id =  Column(
         Integer, 
         ForeignKey('customers.id'), 
        nullable=False
        )
    service_id =  Column(
         Integer, 
         ForeignKey('services.id'), 
        nullable=False
        )
    rate =  Column(
         Float, 
        nullable=False
        )
    date_deleted =  Column(Date)

class ServiceRequestInvoice(Base):
    __tablename__ = 'service_request_invoice'

    id =  Column(
         Integer, 
        primary_key=True
        )
    service_request_id =  Column(
         Integer, 
         ForeignKey('services.id')
        )
    invoice_id =  Column(
         Integer, 
         ForeignKey('invoices.id')
        )







