import re
from datetime import datetime, timedelta
from sqlalchemy import not_, and_
from src import db, models


def create_note(text, tags, exec_date):
    note = models.Note(text=text)
    print(note)
    if exec_date:
        note.execution_date = exec_date
    db.session.add(note)
    db.session.commit()
    if tags:
        change_tag(note.id, tags)
    return True, f'Note ID:{note.id} added'


def change_tag(id_note, tags):
    note = db.session.query(models.Note).filter(models.Note.id == id_note).first()
    if not note:
        return False, f'Node ID:{note.id} not found!'
    note_tags = re.sub(r'[;,.!?]', ' ', tags).title().split()
    note_tags = list(set(note_tags))
    # Визначаємо існуючі теги для нотатки
    all_note_tags = []
    tag_all = db.session.query(models.Tag).filter(models.Tag.note_id == id_note).all()
    for tag_ in tag_all:
        if tag_ in note_tags:
            all_note_tags.append(tag_.tag)
        else:
            db.session.query(models.Tag).filter(models.Tag.tag == tag_.tag).delete()
            db.session.commit()
    # Додавання тегів, яких ще немає
    for tag in note_tags:
        if tag not in all_note_tags:
            new_tag = models.Tag(note_id=id_note, tag=tag)
            db.session.add(new_tag)
            db.session.commit()
    return True, f'Tags added to note ID:{id_note}'


def show_all():
    """Повертає всі нотатки"""
    notes = db.session.query(models.Note).filter(not_(models.Note.is_done)).order_by(models.Note.id).all()
    return notes


def show_archived():
    """Повертає всі нотатки"""
    notes = db.session.query(models.Note).filter(models.Note.is_done).order_by(models.Note.id).all()
    return notes


def change_note(id_, text, tags, exec_date):
    note = db.session.query(models.Note).filter(models.Note.id == id_).first()
    print(note)
    if not note:
        return False, f'Note ID:{id_} not changed'
    note.text = text
    if exec_date:
        note.execution_date = exec_date
    db.session.commit()
    change_tag(id_, tags)
    return True, f'Note ID:{id_} changed'


def delete_note(id_):
    db.session.query(models.Note).filter(models.Note.id == id_).delete()
    db.session.commit()
    db.session.query(models.Tag).filter(models.Tag.note_id == id_).delete()
    db.session.commit()
    return True, f'Note ID:{id_} deleted'


def archive_note(id_):
    note = db.session.query(models.Note).filter(models.Note.id == id_).first()
    note.is_done = not note.is_done
    db.session.commit()
    if note.is_done:
        return True, f'Note ID:{id_} archived'
    else:
        return True, f'Note ID:{id_} returned from the archive'


def show_date(date_, days_):
    try:
        exec_date = datetime.strptime(date_, '%Y-%m-%d').date()
    except ValueError:
        try:
            exec_date = datetime.strptime(date_, '%d.%m.%Y').date()
        except ValueError:
            return False, f'Date is not valid'

    days = int(days_)

    date1 = exec_date - timedelta(days=days)
    date2 = exec_date + timedelta(days=days)
    notes = db.session.query(models.Note).filter(and_(not_(models.Note.is_done), models.Note.execution_date >= date1,
                                                      models.Note.execution_date <= date2)).order_by(
        models.Note.id).all()
    return notes


def find_text(text_):
    """Повертає нотатки за входженням в текст"""
    notes = db.session.query(models.Note).filter(
        and_(not_(models.Note.is_done), models.Note.text.ilike(f'%{text_}%'))).order_by(models.Note.id).all()
    return notes


def find_tag(tag_):
    """Повертає нотатки в яких є тег"""
    notes = db.session.query(models.Note).join(models.Note.tags).filter(not_(models.Note.is_done)).filter(
        models.Tag.tag.ilike(f'%{tag_}%')).order_by(models.Note.id).all()
    return notes


def sort_tags():
    notes = db.session.query(models.Note).join(models.Note.tags).filter(not_(models.Note.is_done)).order_by(
        models.Tag.tag).all()
    return notes
