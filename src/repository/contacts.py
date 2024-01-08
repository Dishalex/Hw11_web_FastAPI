from sqlalchemy import select, extract, between
from sqlalchemy.ext.asyncio  import AsyncSession
from datetime import datetime, timedelta, date

from src.entity.models import Contact, User
from src.schemas.contact import ContactModel





async def get_contacts_all(limit: int, offset: int, db: AsyncSession):  
    """
    The get_contacts_all function returns a list of all contacts in the database.
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of rows to skip
    :param db: AsyncSession: Pass in the database session, which is used to execute sql statements
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()



async def get_contact_by_id(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact_by_id function is used to retrieve a contact from the database.
    It takes in two parameters:
    - contact_id: The id of the contact you want to retrieve. This should be an integer.
    - db: A database session object that can be used for querying and updating data in the database. 
    This should be an AsyncSession object, which is a subclass of sqlalchemy's Session class with some additional functionality added on top of it (see AsyncSession module). 
    
    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Check if the user is authorized to access this contact
    :return: A single contact from the database
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()



async def get_contacts_by_criteria(criteria: dict, limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts_by_criteria function is used to retrieve contacts from the database based on a set of criteria.
    The function takes in three arguments:
    - criteria: A dictionary containing key-value pairs that are used to filter the results. For example, if you wanted 
    all contacts with a first name of &quot;John&quot;, you would pass in {&quot;first_name&quot;: &quot;John&quot;} as your criteria. If 
    no value is passed for this argument, then it defaults to an empty dictionary (i.e., {}). This means that 
    no filtering will be done and all contacts will be returned by default (unless limited by
    
    :param criteria: dict: Filter the contacts by any number of fields
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts that match the criteria
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(**criteria, user=user).limit(limit).offset(offset)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()



async def get_contacts_bd(period: int, limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts_bd function returns a list of contacts that have birthdays in the next week.
    
    :param period: int: Define the number of days in which we want to get contacts
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first offset records
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts whose birthdays are in the specified period
    :doc-author: Trelent
    """
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
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Validate the request body and convert it to a contact object
    :param db: AsyncSession: Pass in a database session
    :param user: User: Get the user from the request
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact



async def update_contact(contact_id: int, body: ContactModel, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify which contact to update
    :param body: ContactModel: Pass in the new contact information
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user that is logged in
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The delete_contact function deletes a contact from the database.
    
    :param contact_id: int: Specify the contact to delete
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is only deleting their own contacts
    :return: The contact object if it was deleted,
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


