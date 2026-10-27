from sqlalchemy import  Boolean,Column, Integer, String,DateTime,ForeignKey,Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), nullable=False, unique=True, index=True)

    hashed_password = Column(String(250), nullable=False)
    
    is_active = Column(Boolean, default=True)


class Event(Base):
    __tablename__="events"

    id=Column(Integer,primary_key=True,index=True)

    title=Column(String(150),nullable=False)

    description=Column(Text,nullable=False)

    location=Column(String(200),nullable=False)

    event_date=Column(DateTime(timezone=True),nullable=False)

    price=Column(Integer,nullable=False,default=0)

    total_seats=Column(Integer,nullable=False)

    available_seats=Column(Integer,nullable=False)

    organizer_id=Column(Integer,ForeignKey("users.id"),nullable=False)

    is_active=Column(Boolean,default=True,nullable=False)

    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
