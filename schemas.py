from pydantic import BaseModel , EmailStr ,Field
from datetime import datetime
from typing import Literal
class UserCreate(BaseModel):
    name:str=Field(min_length=2,max_length=100)
    email:EmailStr
    password:str= Field(min_length=8,max_length=100)
    role: Literal["attendee", "organizer"] = "attendee"

class UserLogin(BaseModel):
    email:EmailStr
    password:str=Field(min_length=1 , max_length=100)

class EventCreate(BaseModel):
    title:str=Field(min_length=3,max_length=150)
    description:str=Field(min_length=10,max_length=50000)
    location:str=Field(min_length=2,max_length=200)
    event_date:datetime
    price:int=Field(ge=0)
    total_seats:int=Field(gt=0)

class EventUpdate(BaseModel):
    title:str|None=Field(
        default=None,
        min_length=3,
        max_length=150
    )
    description:str|None=Field(
        default=None,
        min_length=10,
        max_length=5000
    )
    location:str|None=Field(
        default=None,
        min_length=2,
        max_length=200
    )
    event_date:datetime|None=None

    price:int|None=Field(
        default=None,
        ge=0
    )
    total_seats:int|None=Field(
    default=None,
    gt=0    )



