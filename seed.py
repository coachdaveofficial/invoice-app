from app import app
from faker import Faker
from models import db, connect_db, User, Customer, Invoice, Payment, Service, ServiceRequest, Discount, ServiceRequestInvoice
import random
from datetime import datetime, timedelta
import enum


fake = Faker()
connect_db(app)


class enPaymentType(enum.Enum):
    credit_card = 1
    check = 2
    venmo = 3
    paypal = 4
    cashapp = 5


def seed_users():
    for i in range(5):
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            password=fake.password()
        )
        db.session.add(user)

    db.session.commit()


def seed_customers():
    for i in range(10):
        customer = Customer(
            full_name=fake.name(),
            address=fake.address(),
            tax_id=random.randint(100000000, 999999999),
            phone=fake.phone_number(),
            email=fake.email()
        )
        db.session.add(customer)

    db.session.commit()


def seed_invoices():
    customers = Customer.query.all()

    for customer in customers:
        invoice = Invoice(
            due_date=fake.date_between(start_date='-30d', end_date='+30d'),
            cust_id=customer.id,
            total_cost=round(random.uniform(50, 1000), 2)
        )
        db.session.add(invoice)

    db.session.commit()


def seed_payments():
    invoices = Invoice.query.all()

    for invoice in invoices:
        amount_paid = random.uniform(0, invoice.total_cost)
        payment = Payment(
            invoice_id=invoice.id,
            amount=round(amount_paid, 0),
            payment_type=random.choice(['credit_card', 'check', 'venmo', 'paypal', 'cashapp']),
            reference_num=fake.uuid4()
        )
        db.session.add(payment)

    db.session.commit()


def seed_services():
    for i in range(5):
        service = Service(
            description=fake.sentence(),
            price_per_unit=round(random.uniform(5, 50), 2),
            unit=fake.word()
        )
        db.session.add(service)

    db.session.commit()


def seed_service_requests():
    invoices = Invoice.query.all()
    services = Service.query.all()

    for invoice in invoices:
        for i in range(random.randint(1, 3)):
            service = random.choice(services)
            service_request = ServiceRequest(
                service_id=service.id,
                invoice_id=invoice.id,
                quantity=random.randint(1, 5)
            )
            db.session.add(service_request)

    db.session.commit()


def seed_discounts():
    customers = Customer.query.all()
    services = Service.query.all()

    for customer in customers:
        for i in range(2):
            service = random.choice(services)
            discount = Discount(
                cust_id=customer.id,
                service_id=service.id,
                rate=random.uniform(0.1, 0.5)
            )
            db.session.add(discount)

    db.session.commit()


def seed_service_request_invoices():
    service_requests = ServiceRequest.query.all()
    for service_request in service_requests:
        service_request_invoice = ServiceRequestInvoice(
            service_request_id=service_request.id,
            invoice_id=service_request.invoice_id
        )
        db.session.add(service_request_invoice)

    db.session.commit()


def seed_all():
    seed_users()
    seed_customers()
    seed_invoices()
    seed_payments()
    seed_services()
    seed_service_requests()
    seed_discounts()
    # seed_service_request_invoices()


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_all()
