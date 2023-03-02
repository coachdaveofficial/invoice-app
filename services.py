from models import User, db, Customer, Service, Invoice, Payment, Company, Employee, ServiceRequest
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from datetime import datetime


bcrypt = Bcrypt()

class UserService:
    """Services for getting user info"""

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

            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            # db.rollback()
            return None
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = User.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False
    
    @classmethod
    def delete_user(self, user_id):
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()

    @classmethod
    def find_user_by_username(self, username):
        try:
            user = User.query.filter_by(username=username).first()
            return user
        except IntegrityError:
            return None
    

class CustomerService:
    """Services for getting customer info"""
    @classmethod
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
    @classmethod
    def get_10_customers(self):
        customers = (Customer
                    .query
                    .order_by(Customer.created_date.desc())
                    .limit(10)
                    .all())
        return customers

    @classmethod
    def get_all_customers(self):
        customers = (Customer
                    .query
                    .order_by(Customer.created_date.desc())
                    .all())
        return customers
    
    @classmethod
    def get_customers_for_company(self, c_id):
        """Get all customers of a specific company using the company ID (c_id)"""
        customers = (Customer
                    .query
                    .order_by(Customer.full_name)
                    .filter_by(company_id=c_id)
                    .all())
        return customers

class ServiceService:
    @classmethod
    def add_service(self, form_data, company_id):
        try:
            service = Service(
                        description=form_data.description.data,
                        price_per_unit=form_data.price_per_unit.data,
                        unit=form_data.unit.data,
                        company_id=company_id
                        )
            db.session.add(service)
            db.session.commit()
            return service
        except IntegrityError:
            return None
    @classmethod
    def get_services_for_company(self, company_id):
        services = (Service
                    .query
                    .filter_by(company_id=company_id)
                    .all())
        return services
    @classmethod
    def get_service(self, id):
        service = (Service.query.get(id))
        if not service:
            return None
        return ({
            "id": service.id,
            "description": service.description,
            "price_per_unit": service.price_per_unit,
            "unit": service.unit
        })
    

class InvoiceService:

    @classmethod
    def get_company_invoices(self, company_id):
        """Get all invoices for specific company"""

        invoices = Invoice.query.filter_by(company_id=company_id).all()
        return invoices
    
    @classmethod
    def get_invoice_payment_log(self):
        """Get the payment info for all invoices"""
        invoice_payment_info = []
        invoices = Invoice.query.all()
        payments = Payment.query.all()
        for invoice in invoices:
            total_payments = sum([p.amount for p in payments if p.invoice_id == invoice.id])
            amount_left = invoice.total_cost - total_payments
            invoice_payment_info.append(
                {
                'id': invoice.id,
                'due_date': invoice.due_date,
                'total_cost': invoice.total_cost,
                'amount_left': amount_left,
                'customer_id': invoice.cust_id
                 }
            )
        return invoice_payment_info

    @classmethod
    def get_five_oldest_outstanding(self):
        """Get 5 invoices with upcoming due dates that have not been paid in full."""
        invoice_payment_info = []
        invoices = (Invoice
                    .query
                    .order_by(Invoice.due_date.asc())
                    .all())

        payments = Payment.query.all()

        for invoice in invoices:
            total_payments = sum([p.amount for p in payments if p.invoice_id == invoice.id])
            amount_left = invoice.total_cost - total_payments
            # get 5 invoices that have not yet been paid
            if amount_left and len(invoice_payment_info) < 5:
                invoice_payment_info.append({
                    'invoice_id': invoice.id,
                    'due_date': invoice.due_date,
                    'curr_date': datetime.date(datetime.utcnow()),
                    'total_cost': invoice.total_cost,
                    'amount_left': amount_left,
                    'customer_id': invoice.cust_id
                }
            )
        return invoice_payment_info
class PaymentService:
    def get_payment_history(self):
        """Get payment history"""

        payments = Payment.query.all()
        payment_history = []
        for payment in payments:
            payment_history.append({
                'id': payment.id,
                'amount': payment.amount,
                'ref_num': payment.reference_num,
                'pay_type': payment.payment_type,
                'date': payment.created_date
            })

    def get_yearly_revenue(year: str):
        """Get revenue totals sorted by the year (yyyy) the payment was submitted"""
        
        payments = Payment.query.all()
        yearly_total = sum([p.amount for p in payments if year in p.created_date.strftime("%Y")])
        return yearly_total

class CompanyService:
    def get_all_companies():
        return Company.query.all()
    

    @classmethod
    def create_company(cls, company_name, owner_id):
        try:
            c = Company(
                name=company_name,
                owner_id=owner_id
            )

            db.session.add(c)
            db.session.commit()
            return c
        except IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def delete_company(id):
        Company.query.filter_by(id=id).delete()
        db.session.commit()
class EmployeeService:
    def get_all_employees(self):
        return Employee.query.all()
    
    @classmethod
    def set_employer(self, user_id, company_id):
        e = Employee(user_id=user_id, company_id=company_id)
        db.session.add(e)
        db.session.commit()

class ServiceRequestService:
    @classmethod
    def add_service_request(self, service_id, invoice_id):
        s_r = ServiceRequest()