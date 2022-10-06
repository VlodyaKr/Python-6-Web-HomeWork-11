from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from src import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    token_cookie = db.Column(db.String(255), nullable=True, default=None)

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.email})'


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    phones = relationship('Phone', back_populates='contact')
    emails = relationship('Email', back_populates='contact')

    @hybrid_property
    def days_to_birthday(self) -> int:
        # print(self.birthday, type(self.birthday))
        if self.birthday is None:
            return -1
        this_day = date.today()
        birthday_day = date(this_day.year, self.birthday.month, self.birthday.day)
        if birthday_day < this_day:
            birthday_day = date(this_day.year + 1, self.birthday.month, self.birthday.day)
        return int((birthday_day - this_day).days)


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    contact_id = db.Column(db.Integer, ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = relationship('Contact', cascade='all, delete', back_populates='phones')


class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(254), unique=True, nullable=False)
    contact_id = db.Column(db.Integer, ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = relationship('Contact', cascade='all, delete', back_populates='emails')


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    tags = relationship('Tag', back_populates='note')
    text = db.Column(db.String(255), nullable=False)
    execution_date = db.Column(db.Date)
    is_done = db.Column(db.Boolean, default=False)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(15), nullable=False)
    note_id = db.Column(db.Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    note = relationship('Note', cascade='all, delete', back_populates='tags')
