from fastapi import APIRouter, Body, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio  import AsyncSession
from src.services.role import RoleAccess
from src.entity.models import Role, User

from src.database.db import get_db
from src.repository import contacts as repository_contacts

from src.conf import messages
from src.schemas.contact import ContactModel, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])

access_to_rote_all = RoleAccess([Role.admin, Role.moderator])



@router.get("/", response_model=list[ContactResponse], name="Find contacts with or without criteria")
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, ge=10, le=500),
    offset: int = Query(default=0, ge=0),
    first_name: str = Query(default=None),
    last_name: str = Query(default=None),
    email: str = Query(default=None),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The get_contacts function returns a list of contacts.

    :param db: AsyncSession: Get the database session
    :param limit: int: Limit the number of contacts returned by the api
    :param ge: Specify a minimum value for the parameter
    :param le: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param ge: Specify a minimum value for the limit parameter
    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter the contacts by last name
    :param email: str: Filter the contacts by email
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """

    criteria = {'first_name': first_name, 'last_name': last_name, 'email': email}
    criteria = {k:v for k, v in criteria.items() if v is not None}
    # if first_name is None and last_name is None and email is None:
    #     contacts = await repository_contacts.get_contacts_all(limit, offset, db)
    # else:
    contacts = await repository_contacts.get_contacts_by_criteria(criteria, limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return contacts



@router.get('/all', response_model=list[ContactResponse], name="Find all contacts", dependencies=[Depends(access_to_rote_all)])
async def get_contacts_all(
    limit: int = Query(default=10, ge=10, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The get_contacts_all function returns a list of contacts.
    
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify that the limit must be greater than or equal to 10
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Skip the first offset contacts
    :param ge: Set the minimum value for the limit parameter
    :param db: AsyncSession: Pass the database session to this function
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts_all(limit, offset, db)
    return contacts




@router.get('/{contact_id}', response_model=ContactResponse, name="Find contact by ID")
async def get_contact_by_id(
    contact_id: int=Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The get_contact_by_id function returns a contact by its id.
    
    :param contact_id: int: Get the contact id from the path
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return contact




@router.get("/birthdays/", response_model=list[ContactResponse], name="Find contacts with birthday for period")
async def get_contacts_bd(
    period: int = Query(7),
    limit: int = Query(10, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The get_contacts_bd function returns a list of contacts with birthday for period.
        The function accepts the following parameters:
            - period (int): number of days to search for contacts with birthday, default 7 days.
            - limit (int): maximum number of results to return, default 10. Maximum 1000 results can be returned at once. 
            - offset (int): pagination offset, defaults to 0.
    
    :param period: int: Filter the contacts by period
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the maximum number of contacts that can be returned
    :param offset: int: Skip the first offset contacts
    :param db: AsyncSession: Get the database connection
    :param user: User: Get the current user from the database
    :return: A list of contacts with birthday for period
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts_bd(period, limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts with birthday for period")
    return contacts



@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED, name="Create contact")
async def create_contact(
    body: ContactModel, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Get the contact information from the request body
    :param db: AsyncSession: Pass a database session to the function
    :param user: User: Get the current user from the auth_service
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact



@router.put('/{contact_id}', name="Change contact info")
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The update_contact function updates a contact in the database.
        The function takes an id, body and db as parameters.
        It returns a ContactResponse object.
    
    :param body: ContactModel: Specify the type of data that is expected in the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user from the auth_service
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return contact



@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT, name="Delete contact by ID")
async def delete_contact(
    contact_id: int=Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
    ):
    """
    The delete_contact function deletes a contact from the database.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact




