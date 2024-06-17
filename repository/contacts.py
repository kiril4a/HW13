from sqlalchemy.orm import Session
from database.models import Contact
from schemas import ContactCreate, ContactUpdate

def create_contact(db: Session, contact: ContactCreate):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Contact).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int):
    return db.query(Contact).filter(Contact.id == contact_id).first()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def search_contacts(db: Session, query: str):
    return db.query(Contact).filter(
        (Contact.first_name.contains(query)) | 
        (Contact.last_name.contains(query)) | 
        (Contact.email.contains(query))
    ).all()

def get_upcoming_birthdays(db: Session):
    from datetime import date, timedelta, datetime
    
    today = date.today()
    next_week = today + timedelta(days=7)
    
    contacts = db.query(Contact).all()
    upcoming_birthdays = []

    for contact in contacts:
        # Конвертувати дату народження до поточного року
        birthday_this_year = contact.birthday.replace(year=today.year)
        
        # Якщо день народження вже пройшов цього року, то додати рік
        if birthday_this_year < today:
            birthday_this_year = contact.birthday.replace(year=today.year + 1)
        
        # Додати контакт до списку, якщо день народження в межах наступних 7 днів
        if today <= birthday_this_year <= next_week:
            upcoming_birthdays.append(contact)

    return upcoming_birthdays

