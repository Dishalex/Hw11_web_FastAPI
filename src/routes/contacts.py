from fastapi import APIRouter, Body, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio  import AsyncSession

from src.database.db import get_db
from src.repository import contacts as repository_contacts

from src.conf import messages
from src.schemas.contact import ContactModel, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])

# @router.get('/', response_model=list[ContactResponse])
# async def get_contacts_all(
#     limit: int = Query(default=10, ge=10, le=500),
#     offset: int = Query(default=0, ge=0),
#     db: AsyncSession = Depends(get_db)
#     ):
#     contacts = await repository_contacts.get_contacts_all(limit, offset, db)
#     return contacts


@router.get('/{contact_id}', response_model=ContactResponse, name="Find contact by ID")
async def get_contact_by_id(
    contact_id: int=Path(ge=1),
    db: AsyncSession = Depends(get_db)
    ):
    contact = await repository_contacts.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return contact


@router.get("/", response_model=list[ContactResponse], name="Find contacts with or without criteria")
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, ge=10, le=500),
    offset: int = Query(default=0, ge=0),
    first_name: str = Query(default=None),
    last_name: str = Query(default=None),
    email: str = Query(default=None)):

    criteria = {'first_name': first_name, 'last_name': last_name, 'email': email}
    criteria = {k:v for k, v in criteria.items() if v is not None}
    # if first_name is None and last_name is None and email is None:
    #     contacts = await repository_contacts.get_contacts_all(limit, offset, db)
    # else:
    contacts = await repository_contacts.get_contacts_by_criteria(criteria, limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return contacts


@router.get("/birthdays/", response_model=list[ContactResponse], name="Find contacts with birthday for period")
async def get_contacts_bd(
    period: int = Query(7),
    limit: int = Query(10, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
    ):
    contacts = await repository_contacts.get_contacts_bd(period, limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts with birthday for period")
    return contacts


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED, name="Create contact")
async def create_contact(
    body: ContactModel, 
    db: AsyncSession = Depends(get_db)):
    contact = await repository_contacts.create_contact(body, db)
    return contact



@router.put('/{contact_id}', name="Change contact info")
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db)
    ):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT, name="Delete contact by ID")
async def delete_contact(
    contact_id: int=Path(ge=1),
    db: AsyncSession = Depends(get_db)
    ):
    contact = await repository_contacts.delete_contact(contact_id, db)
    return contact