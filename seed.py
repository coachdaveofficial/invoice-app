from app import app
from faker import Faker
from models import db, connect_db, User, Customer, Invoice, Payment, Service, ServiceRequest, Discount, ServiceRequestInvoice, Company, Employee, ServiceRate, ServicesForCompany, enUnit, enPaymentType
from services import UserService, CompanyService, EmployeeService
import random
from datetime import datetime, timedelta
import enum
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


fake = Faker()
connect_db(app)



def seed_companies():
    u = User.query.all()
    for i in range(3):
        company = Company(
            name="Company #" + str(i+1),
            owner_id=u[i].id
        )
        db.session.add(company)
    db.session.commit()

def seed_employees():
    companies = Company.query.all()
    users = User.query.all()
    ids = []
    for u in users:
        ids.append(u.id)
    i = 0
    for c in companies:
        employee = Employee(
            company_id=c.id,
            user_id=ids[i]
        )
        db.session.add(employee)
        i = i+1
    db.session.commit()

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
    companies = Company.query.all()
    for c in companies:
        customer = Customer(
            full_name=fake.name(),
            address=fake.address(),
            tax_id=random.randint(100000000, 999999999),
            phone=fake.phone_number(),
            email=fake.email(),
            company_id=c.id
        )
        db.session.add(customer)

    db.session.commit()


def seed_invoices():
    companies = Company.query.all()
    i = 0
    for c in companies:

        invoice = Invoice(
            due_date=fake.date_between(start_date='-30d', end_date='+30d'),
            cust_id=c.customers[0].id,
            total_cost=round(random.uniform(50, 1000), 2),
            company_id=c.id,
            is_estimate=False
        )
        db.session.add(invoice)
        i = i+1

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


def seed_service_rates():
    for r in range(10):
        service_rate = ServiceRate(
            amount=round(random.uniform(5, 50), 2)
        )
        db.session.add(service_rate)
    db.session.commit()

def seed_services():

    rates = ServiceRate.query.all()

    for i in range(3):
        service = Service(
            description=fake.sentence(),
            service_rate_id=rates[i].id,
            unit=random.choice(list(enUnit))
        )
        db.session.add(service)


    db.session.commit()

def seed_company_services():
    companies = Company.query.all()
    for i in range(len(companies)):

        comp_serv = ServicesForCompany(
            service_id=i+1,
            company_id=i+1
        )
        db.session.add(comp_serv)
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

def seed_demo_user():
    demo = UserService.signup(
        username="Guest",
        email="demouser@test.com",
        password="demouser"
    )

    c = CompanyService.create_company(
        company_name="Demo Company",
        owner_id=demo.id
        )
    EmployeeService.set_employer(user_id=demo.id, company_id=c.id)

    rates = ServiceRate.query.all()
    for i in range(10):
        customer = Customer(
                full_name=fake.name(),
                address=fake.address(),
                tax_id=random.randint(100000000, 999999999),
                phone=fake.phone_number(),
                email=fake.email(),
                company_id=c.id
            )
        service = Service(
            description=fake.sentence(),
            service_rate_id=rates[i].id,
            unit=random.choice(list(enUnit))
        )
        db.session.add(service)
        db.session.add(customer)

    db.session.commit()

    
    
    for customer in c.customers:
        invoice = Invoice(
            due_date=fake.date_between(start_date='-30d', end_date='+30d'),
            cust_id=customer.id,
            company_id=c.id,
            is_estimate=False
        )
        db.session.add(invoice)
    db.session.commit()

    services_for_company = []
    services = Service.query.all()
    for s in services:
        services_for_company.append({'service_id': s.id, 'company_id': c.id})
    db.session.execute(ServicesForCompany.__table__.insert(), services_for_company)
    db.session.commit()

    for invoice in c.invoices:
        total_cost = 0
        for i in range(random.randint(1, 2)):
            service_request = ServiceRequest(
                invoice_id=invoice.id,
                service_id=random.choice(services_for_company)['service_id'],
                quantity=random.randint(1, 4)
            )
            db.session.add(service_request)
            service = Service.query.get(service_request.service_id)
            total_cost += service.rate.amount * service_request.quantity

        invoice.total_cost = total_cost
        amount_paid = random.uniform(0, invoice.total_cost)
        payment = Payment(
            invoice_id=invoice.id,
            amount=round(amount_paid, 0),
            payment_type=random.choice(['credit_card', 'check', 'venmo', 'paypal', 'cashapp']),
            reference_num=fake.uuid4()
        )
        db.session.add(payment)
        if random.random() < 0.5:
            # create another payment for this invoice
            amount_paid = random.uniform(0, invoice.total_cost - payment.amount)
            payment = Payment(
                invoice_id=invoice.id,
                amount=round(amount_paid, 0),
                payment_type=random.choice(['credit_card', 'check', 'venmo', 'paypal', 'cashapp']),
                reference_num=fake.uuid4()
            )
            db.session.add(payment)
    db.session.commit()
        

        
     




def seed_all():
    seed_service_rates()
    print("seeded service rates")
    seed_users()
    print("seeded users")
    seed_companies()
    print("seeded companies")
    seed_employees()
    print("seeded employees")
    seed_customers()
    print("seeded customers")
    seed_invoices()
    print("seeded invoices")
    seed_payments()
    print("seeded payments")
    seed_services()
    print("seeded services")
    seed_service_requests()
    print("seeded service requests")
    seed_discounts()
    print("seeded discouts")
    seed_company_services()
    print("seeded company services")
    seed_demo_user()
    print("seeded demo user")



if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_all()
