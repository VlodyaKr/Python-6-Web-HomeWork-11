from sqlalchemy import not_, or_, and_
from src import db, models


def show_all():
    """Повертає всі контакти"""
    contacts = db.session.query(models.Contact).order_by(models.Contact.name).all()
    return contacts


def add_contacts(name_, phone_, email_, address_, birthday_):
    contact = db.session.query(models.Contact).filter(models.Contact.name.ilike(name_)).first()
    if contact:
        return False, 'Contact now exist.'
    contact = models.Contact(name=name_)
    if address_:
        contact.address = address_
    if birthday_:
        contact.birthday = birthday_
    db.session.add(contact)
    db.session.commit()
    if phone_:
        phone = models.Phone(contact_id=contact.id, phone_number=phone_)
        db.session.add(phone)
        db.session.commit()
    if email_:
        email = models.Email(contact_id=contact.id, mail=email_)
        db.session.add(email)
        db.session.commit()
    return True, f'Contact {name_} added'


def edit_contacts(id_, name_, address_, birthday_):
    contact = db.session.query(models.Contact).filter(models.Contact.id == id_).first()
    if name_ != contact.name:
        contact_ = db.session.query(models.Contact).filter(models.Contact.name.ilike(name_)).first()
        if contact_:
            return False, 'Contact with this name now exist.'
        contact.name = name_
    if address_ != contact.address:
        contact.address = address_
    if birthday_ != contact.birthday:
        contact.birthday = birthday_
    db.session.commit()
    return True, f'Contact {name_} changed'


def delete_phone(id_, phone_):
    db.session.query(models.Phone).filter(models.Phone.id == id_).delete()
    db.session.commit()
    return True, f'Phone {phone_} deleted'


def edit_phone(phone_id, new_phone, contact_id):
    find_phone = db.session.query(models.Phone).filter(models.Phone.phone_number == new_phone).first()
    if find_phone:
        return False, f'Phone number {new_phone} now exist.'
    if phone_id:
        phone = db.session.query(models.Phone).filter(models.Phone.id == phone_id).first()
        phone.phone_number = new_phone
        db.session.commit()
        return True, f'Phone number {new_phone} changed.'
    else:
        print(contact_id)
        contact_id = int(contact_id)
        phone = models.Phone(contact_id=contact_id, phone_number=new_phone)
        db.session.add(phone)
        db.session.commit()
        return True, f'Phone number {new_phone} added.'


def delete_email(id_, mail_):
    db.session.query(models.Email).filter(models.Email.id == id_).delete()
    db.session.commit()
    return True, f'Email {mail_} deleted'


def edit_email(email_id, new_email, contact_id):
    find_email = db.session.query(models.Email).filter(models.Email.mail == new_email).first()
    if find_email:
        return False, f'Email {new_email} now exist.'
    if email_id:
        email = db.session.query(models.Email).filter(models.Email.id == email_id).first()
        email.mail = new_email
        db.session.commit()
        return True, f'Email {new_email} changed.'
    else:
        print(contact_id)
        contact_id = int(contact_id)
        email = models.Email(contact_id=contact_id, mail=new_email)
        db.session.add(email)
        db.session.commit()
        return True, f'Email {new_email} added.'


def delete_contact(id_, name_):
    db.session.query(models.Contact).filter(models.Contact.id == id_).delete()
    db.session.commit()
    db.session.query(models.Phone).filter(models.Phone.contact_id == id_).delete()
    db.session.commit()
    db.session.query(models.Phone).filter(models.Phone.contact_id == id_).delete()
    db.session.commit()
    return True, f'Contact {name_} deleted.'


def find(text_):
    """Повертає нотатки за входженням в текст"""
    contacts = db.session.query(models.Contact).join(models.Contact.emails).join(models.Contact.phones).filter(
        or_(models.Contact.name.ilike(f'%{text_}%'), models.Contact.address.ilike(f'%{text_}%'),
            models.Phone.phone_number.ilike(f'%{text_}%'), models.Email.mail.ilike(f'%{text_}%'))).order_by(
        models.Contact.name).all()
    return contacts


def birthdays(days):
    contacts = db.session.query(models.Contact).filter(models.Contact.birthday).all()
    filter_contact = [contact for contact in contacts if contact.days_to_birthday <= days]
    filter_contact = sorted(filter_contact, key=lambda x: x.days_to_birthday)
    return filter_contact
