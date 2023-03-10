from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, ValidationError, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length
import phonenumbers

def check_if_valid_phone(form, field):
    if '-' in field.data:
        raise ValidationError('Field cannot contain spaces or the "-" character. Please resubmit.')

def validate_phone(form, field):
        if "-" in field.data:
            raise ValidationError('Field cannot contain spaces or the "-" character. Please resubmit.')
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    company_name = StringField('Company Name')
class LoginForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class InvoiceAddForm(FlaskForm):
    """Form for making invoices"""
    due_date = DateField("Due date", validators=[DataRequired()])
    cust_id = SelectField("Customer", validators=[DataRequired()])
    total_cost = FloatField("Total cost", validators=[DataRequired()])


class ServiceAddForm(FlaskForm):
    """Form for creating new services"""
    description = StringField('Description', validators= [DataRequired()])
    rate = FloatField("Price per unit", validators=[DataRequired()])
    unit = SelectField('Unit', choices=[("hr", "Hourly"), ("sq_ft", "Square Feet"), ("weight", "Weight"), ("qty", "Quantity")], validators=[DataRequired()])

class CustomerAddForm(FlaskForm):
    """Form for adding a new customer"""
    full_name = StringField("Full Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    tax_id = StringField("Tax ID")
    phone = StringField("Phone", validators=[DataRequired(), validate_phone])
    email = StringField("Email", validators=[DataRequired()])
