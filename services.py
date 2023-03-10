from models import User, db, Customer, Service, Invoice, Payment, Company, Employee, ServiceRequest, ServicesForCompany, ServiceRate
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
    def add_customer(self,form_data, comp_id):
        try:
            customer = Customer(
                full_name=form_data.full_name.data,
                address=form_data.address.data,
                tax_id=float(form_data.tax_id.data) if form_data.tax_id.data else None,
                phone=form_data.phone.data,
                email=form_data.email.data,
                company_id=comp_id
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
    
    @classmethod
    def get_customer_by_id(self, c_id):
        return Customer.query.get(c_id)

class ServiceService:
    @classmethod
    def add_service(self, form_data, rate_id):
        try:
            service = Service(
                        description=form_data.description.data,
                        unit=form_data.unit.data,
                        service_rate_id=rate_id
                        )
            db.session.add(service)
            db.session.commit()
            return service
        except IntegrityError:
            return None
    @classmethod
    def get_services_for_company(self, company_id):

        services = Service.query.join(ServicesForCompany).filter(ServicesForCompany.company_id == company_id).order_by(Service.description.asc()).all()

            
        return services
    @classmethod
    def get_service_data(self, id):
        service = (Service.query.get(id))
        if not service:
            return None
        return ({
            "id": service.id,
            "description": service.description,
            "rate": service.rate.amount,
            "unit": service.unit.name,
        })
    @classmethod
    def get_service_by_id(self, id):
        service = Service.query.get(id)
        return service
    @classmethod
    def get_services_for_invoice(self, invoice_id):
        invoice = InvoiceService.get_invoice_by_id(invoice_id)
        service_instances = Service.query.filter(Service.id.in_([sr.service_id for sr in invoice.service_requests])).all()
        service_by_service_id = {service.id: service for service in service_instances}
        services = []
        for sr in invoice.service_requests:
            service = service_by_service_id[sr.service_id]
            services.append((service, sr.quantity))

        prices = [s.rate.amount * q for (s, q) in services]
        invoice.total_cost = sum(prices)
        db.session.commit()
        return services

    @classmethod
    def update_service(self, service_id, form_data):
        service = Service.query.get(service_id)
        if form_data.get('description') != service.description or form_data.get('unit') != service.unit.name:
            # Create a new Service instance if the description or unit has changed
            new_service = Service(description=form_data.get('description'), unit=form_data.get('unit'))
            new_service.rate = service.rate # Copy the existing rate to the new instance
            db.session.add(new_service)
            db.session.commit()
            comp_serv = ServicesForCompanyService.add_service(serv_id=new_service.id, comp_id=form_data.get('company_id'))
            ServicesForCompanyService.remove_company_service(comp_id=form_data.get('company_id'), serv_id=service.id)
            return {'id': new_service.id,
                    'description': new_service.description,
                    'rate': new_service.rate.amount,
                    'unit': new_service.unit.name,
                    'comp_serv_id': comp_serv.id
                    }
        elif form_data.get('rate') != service.rate.amount:
            # Create a new ServiceRate instance and update the existing Service instance with the new rate id
            new_rate = ServiceRate(amount=form_data.get('rate'))
            db.session.add(new_rate)
            db.session.commit()
            service.service_rate_id = new_rate.id
            db.session.commit()
            ServicesForCompanyService.add_service(serv_id=service.id, comp_id=form_data.get('company_id'))
            return {'id': service.id,
                    'description': service.description,
                    'rate': service.rate.amount,
                    'unit': service.unit.name
                    }
        
class InvoiceService:

    @classmethod
    def get_invoice_by_id(self, id):
        return Invoice.query.get(id)


    @classmethod
    def get_company_invoices(self, company_id):
        """Get all invoices for specific company"""

        invoices = Invoice.query.filter(Invoice.company_id == company_id).filter(Invoice.is_estimate == False).all()
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
    
    @classmethod
    def create_estimate(self, cust_id, comp_id):
        est = Invoice(cust_id=cust_id,
                    company_id=comp_id)
        db.session.add(est)
        db.session.commit()
        return est
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
    @classmethod
    def get_company_by_id(self, id):
        return Company.query.get(id)
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
    def add_service_request(self, service_id, invoice_id, quantity):
        s_r = ServiceRequest(service_id=service_id,
                            invoice_id=invoice_id,
                            quantity=quantity)
        db.session.add(s_r)
        db.session.commit()

class ServicesForCompanyService:

    @classmethod
    def remove_company_service(self, comp_id, serv_id):
        comp_serv = (ServicesForCompany.query
                                        .filter(ServicesForCompany.company_id == comp_id)
                                        .filter(ServicesForCompany.service_id == serv_id)
                                        .first()
                                        )
        db.session.delete(comp_serv)
        db.session.commit()
    @classmethod
    def add_service(self, comp_id, serv_id):
        comp_serv = ServicesForCompany(company_id=comp_id, service_id=serv_id)
        db.session.add(comp_serv)
        db.session.commit()
        return comp_serv

class ServiceRateService:
    @classmethod
    def add_rate(self,rate):
        service_rate = ServiceRate(amount=rate)
        db.session.add(service_rate)
        db.session.commit()
        return service_rate
