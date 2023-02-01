from models import User, db
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