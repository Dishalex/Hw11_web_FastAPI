from sqlalchemy import select, extract, between
from sqlalchemy.ext.asyncio  import AsyncSession
from datetime import datetime, timedelta, date

from src.entity.models import Contact, User
from src.schemas.contact import ContactModel





async def get_contacts_all(limit: int, offset: int, db: AsyncSession):  
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()



async def get_contact_by_id(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()



async def get_contacts_by_criteria(criteria: dict, limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(**criteria, user=user).limit(limit).offset(offset)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()



async def get_contacts_bd(period: int, limit: int, offset: int, db: AsyncSession, user: User):
    current_date = date.today()
    next_week_start = current_date
    next_week_end = current_date + timedelta(days=period)
    
    condition = between(extract('month', Contact.birth_date), next_week_start.month, next_week_end.month) & \
                between(extract('day', Contact.birth_date), next_week_start.day, next_week_end.day)
    result = (
        await db.execute(
            select(Contact)
            .filter_by(user=user)
            .filter(condition)
        )
    ).scalars().all()
    return result



async def create_contact(body: ContactModel, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact



async def update_contact(contact_id: int, body: ContactModel, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birth_date = body.birth_date
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
    return contact



async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


