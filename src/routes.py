from flask import render_template, request, flash, redirect, url_for, session, make_response
import uuid
from datetime import datetime, timedelta
from . import app
from src import db, models
from src.repository import users, parsing_file, notebook, addressbook
from src.libs.validation_schemas import RegistrationSchema, LoginSchema, NoteDateSchema, ContactSchema, EmailCheck
from src.libs.checkers import check_email, check_phone
from marshmallow import ValidationError


@app.before_request
def before_func():
    auth = True if 'username' in session else False
    if not auth:
        token_user = request.cookies.get('username')
        if token_user:
            user = users.get_user_by_token(token_user)
            if user:
                session['username'] = {'username': user.username, 'id': user.id}


@app.route('/healthcheck')
def healthcheck():
    return 'I am working'


@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    return render_template('pages/index.html', title='Home', auth=auth)


@app.route('/registration', methods=['GET', 'POST'], strict_slashes=False)
def registration():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            RegistrationSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/registration.html', messages=err.messages)
        email = request.form.get('email')
        password = request.form.get('password')
        nick = request.form.get('nick')
        user = users.create_user(email, password, nick)
        return redirect(url_for('login'))
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/registration.html', title='Sign Up')


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            LoginSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/login.html', messages=err.messages)
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') == 'on' else False
        user = users.login(email, password)
        if user is None:
            return redirect(url_for('login'))
        session['username'] = {'username': user.username, 'id': user.id}
        response = make_response(redirect(url_for('index')))
        if remember:
            token = str(uuid.uuid4())
            expire_data = datetime.now() + timedelta(days=60)
            response.set_cookie('username', token, expires=expire_data)
            users.set_token(user, token)

        return response
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/login.html', title='Sign In')


@app.route('/logout', strict_slashes=False)
def logout():
    auth = True if 'username' in session else False
    if not auth:
        return redirect('/')
    session.pop('username')
    response = make_response(redirect(url_for('index')))
    response.set_cookie('username', '', expires=-1)

    return response


@app.route('/file_parser', methods=['GET', 'POST'], strict_slashes=False)
def file_parser():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        parsing_folder = request.form.get('folder')
        result, message = parsing_file.start_fp(parsing_folder)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
    return render_template('pages/file_parser.html', title='File parser', auth=auth)


@app.route('/notebook/list', methods=['GET', 'POST'], strict_slashes=False)
def notebook_list():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    notes = notebook.show_all()
    return render_template('pages/notebook.html', title='NoteBook', auth=auth, view_list=notes)


@app.route('/notebook/new', methods=['GET', 'POST'], strict_slashes=False)
def add_note():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        note_text = request.form.get('note_text')
        note_tags = request.form.get('note_tags')
        exec_date = request.form.get('exec_date')
        result, message = notebook.create_note(note_text, note_tags, exec_date)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('notebook_list'))
    return render_template('pages/note_new.html', title='New Note', auth=auth)


@app.route('/notebook/edit/<note_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_note(note_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    note = db.session.query(models.Note).filter(models.Note.id == note_id).first()
    if request.method == 'POST':
        note_text = request.form.get('note_text')
        note_tags = request.form.get('note_tags')
        exec_date = request.form.get('exec_date')
        print(note_text, note_tags, exec_date)
        result, message = notebook.change_note(note_id, note_text, note_tags, exec_date)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('notebook_list'))
    return render_template('pages/note_edit.html', title='Edit Note', auth=auth, note=note)


@app.route('/notebook/del/<note_id>', methods=['GET', 'POST'], strict_slashes=False)
def del_note(note_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    note = db.session.query(models.Note).filter(models.Note.id == note_id).first()
    if request.method == 'POST':
        result, message = notebook.delete_note(note_id)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('notebook_list'))
    return render_template('pages/note_del.html', title='Delete Note', auth=auth, note=note)


@app.route('/notebook/archive/<note_id>')
def arch_note(note_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    print(note_id)
    result, message = notebook.archive_note(note_id)
    if result:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('notebook_list'))


@app.route('/notebook/show_archived', methods=['GET', 'POST'], strict_slashes=False)
def notebook_archive():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    notes = notebook.show_archived()
    return render_template('pages/notebook.html', title='Archived Notes', auth=auth, view_list=notes)


@app.route('/notebook/show_date', methods=['GET', 'POST'], strict_slashes=False)
def notebook_show_date():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            NoteDateSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/note_date.html', messages=err.messages)
        note_date = request.form.get('date')
        note_days = request.form.get('days')
        notes = notebook.show_date(note_date, note_days)
        return render_template('pages/notebook.html', title='Search By Date', auth=auth, view_list=notes)
    return render_template('pages/note_date.html', title='Find By Date', auth=auth)


@app.route('/notebook/find_text', methods=['GET', 'POST'], strict_slashes=False)
def notebook_find_text():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        note_text = request.form.get('text')
        notes = notebook.find_text(note_text)
        return render_template('pages/notebook.html', title='Search By Text', auth=auth, view_list=notes)
    return render_template('pages/note_find.html', title='Find By Text', auth=auth, mode=0)


@app.route('/notebook/find_tag', methods=['GET', 'POST'], strict_slashes=False)
def notebook_find_tag():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        note_tag = request.form.get('text')
        notes = notebook.find_tag(note_tag)
        return render_template('pages/notebook.html', title='Search By Tag', auth=auth, view_list=notes)
    return render_template('pages/note_find.html', title='Find By Tag', auth=auth, mode=1)


@app.route('/notebook/sort_tags', methods=['GET', 'POST'], strict_slashes=False)
def notebook_sort_tags():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    notes = notebook.sort_tags()
    return render_template('pages/notebook.html', title='Sorted By Tags', auth=auth, view_list=notes)


@app.route('/addressbook/list', methods=['GET', 'POST'], strict_slashes=False)
def addressbook_list():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    ab = addressbook.show_all()
    if request.method == 'POST':
        contact_id = int(request.form.get('bdbutton'))
        contact = db.session.query(models.Contact).filter(models.Contact.id == contact_id).first()
        flash(f'{contact.days_to_birthday} days to Birthday of {contact.name}', 'warning')
        return redirect(url_for('addressbook_list'))
    return render_template('pages/addressbook.html', title='AddressBook', auth=auth, view_list=ab)


@app.route('/addressbook/new', methods=['GET', 'POST'], strict_slashes=False)
def add_contact():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            from_form = ContactSchema().load(request.form)
            print(from_form)
        except ValidationError as err:
            return render_template('pages/contact_add.html', messages=err.messages, auth=auth)
        name = from_form.get('contact_name')
        phone = from_form.get('phone')
        email = from_form.get('email').lower()
        address = from_form.get('address')
        birthday = from_form.get('birthday')
        if check_phone(phone):
            flash('Phone is not unique.', 'danger')
            return render_template('pages/contact_add.html')
        if check_email(email):
            flash('Email is not unique.', 'danger')
            return render_template('pages/contact_add.html')

        print(f'name: {name}, phone: {phone}, email: {email}, address: {address}, birthday: {birthday}')
        print(check_phone(phone), check_email(email))
        result, message = addressbook.add_contacts(name, phone, email, address, birthday)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('addressbook_list'))
    return render_template('pages/contact_add.html', title='New Contact', auth=auth)


@app.route('/addressbook/edit/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_contact(contact_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    contact = db.session.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if request.method == 'POST':
        try:
            from_form = ContactSchema().load(request.form)
            print(from_form)
        except ValidationError as err:
            return render_template('pages/contact_edit.html', messages=err.messages, auth=auth, contact=contact)
        name = from_form.get('contact_name').title()
        address = from_form.get('address')
        birthday = from_form.get('birthday')
        result, message = addressbook.edit_contacts(contact_id, name, address, birthday)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('addressbook_list'))
    return render_template('pages/contact_edit.html', title='Edit Contact', auth=auth, contact=contact)


@app.route('/addressbook/phones/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_phones(contact_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    phones = db.session.query(models.Phone).filter(models.Phone.contact_id == contact_id).all()
    contact = db.session.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if request.method == 'POST':
        phone_id = int(request.form.get('subbutton'))
        new_phone = request.form.get(f'phone-{phone_id}')
        if not new_phone:
            flash('Phone number is empty.', 'danger')
            return render_template('pages/phones.html', title='Edit Phones', auth=auth, contact=contact, phones=phones)
        print('*****', phone_id, new_phone)
        try:
            new_phone = ContactSchema()._phone_check(new_phone)
        except ValidationError as err:
            return render_template('pages/phones.html', messages=err.messages, title='Edit Phones', auth=auth,
                                   contact=contact, phones=phones)

        print(phone_id, new_phone)
        result, message = addressbook.edit_phone(phone_id, new_phone, contact_id)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('edit_phones', contact_id=contact_id))
    return render_template('pages/phones.html', title='Edit Phones', auth=auth, contact=contact, phones=phones)


@app.route('/addressbook/phone_del/<phone_id>', methods=['GET', 'POST'], strict_slashes=False)
def del_phones(phone_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    phone = db.session.query(models.Phone).filter(models.Phone.id == phone_id).first()
    phone_number = phone.phone_number
    if request.method == 'POST':
        result, message = addressbook.delete_phone(phone_id, phone_number)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('addressbook_list'))
    return render_template('pages/phone_del.html', title='Delete Phone', auth=auth, phone=phone)


@app.route('/addressbook/emails/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_emails(contact_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    emails = db.session.query(models.Email).filter(models.Email.contact_id == contact_id).all()
    contact = db.session.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if request.method == 'POST':
        email_id = int(request.form.get('subbutton'))
        new_email = request.form.get(f'email-{email_id}')
        if not new_email:
            flash('Email is empty.', 'danger')
            return render_template('pages/emails.html', title='Edit Emails', auth=auth, contact=contact, emails=emails)
        try:
            EmailCheck().load({'email': new_email})
        except ValidationError as err:
            return render_template('pages/emails.html', messages=err.messages, title='Edit Emails', auth=auth,
                                   contact=contact, emails=emails)
        result, message = addressbook.edit_email(email_id, new_email, contact_id)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('edit_emails', contact_id=contact_id))
    return render_template('pages/emails.html', title='Edit Emails', auth=auth, contact=contact, emails=emails)


@app.route('/addressbook/email_del/<email_id>', methods=['GET', 'POST'], strict_slashes=False)
def del_email(email_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    email = db.session.query(models.Email).filter(models.Email.id == email_id).first()
    mail = email.mail
    if request.method == 'POST':
        result, message = addressbook.delete_email(email_id, mail)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('addressbook_list'))
    return render_template('pages/email_del.html', title='Delete Email', auth=auth, email=email)


@app.route('/addressbook/del/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def del_contact(contact_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    contact = db.session.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if request.method == 'POST':
        result, message = addressbook.delete_contact(contact_id, contact.name)
        if result:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('addressbook_list'))
    return render_template('pages/contact_del.html', title='Delete Contact', auth=auth, contact=contact)


@app.route('/addressbook/find', methods=['GET', 'POST'], strict_slashes=False)
def addressbook_find():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        find_text = request.form.get('text')
        contacts = addressbook.find(find_text)
        return render_template('pages/addressbook.html', title=f'Search by "{find_text.lower()}"', auth=auth,
                               view_list=contacts)
    return render_template('pages/contact_find.html', title='Find', auth=auth)


@app.route('/addressbook/birthdays', methods=['GET', 'POST'], strict_slashes=False)
def addressbook_birthdays():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    if request.method == 'POST':
        find_days = int(request.form.get('days'))
        contacts = addressbook.birthdays(find_days)
        return render_template('pages/addressbook.html', title=f'Search by "{find_days} days to Birthday"', auth=auth,
                               view_list=contacts)
    return render_template('pages/contact_bitrhdays.html', title='Find Birthdays', auth=auth)
