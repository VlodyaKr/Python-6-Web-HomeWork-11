from src import db, models


def check_email(email_):
    return True if db.session.query(models.Email).filter(models.Email.mail == email_).first() else False


def check_phone(phone_):
    return True if db.session.query(models.Phone).filter(models.Phone.phone_number == phone_).first() else False
