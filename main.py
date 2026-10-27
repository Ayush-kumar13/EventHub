import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from database import Base, engine, get_db
import models
from schemas import UserLogin, UserCreate, EventCreate ,EventUpdate
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv


load_dotenv()

Bearer_scheme = HTTPBearer()

password_hash = PasswordHash.recommended()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event hub API",
    description="Backend API for eventhub event booking platform",
    version="1.0.0"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(Bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid authorization"
            )
        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    Current_user = db.query(models.User).filter(models.User.id == user_id).first()
    if Current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="USER NOT FOUND"
        )
    if not Current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user acc is inactive"
        )
    return Current_user

def create_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token






#update event deatails
@app.patch("/events{event_id}")
def update_events_here(event_id:int,event_data:EventUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    existing_event=db.query(models.Event).filter(models.Event.id==event_id).first()

    if existing_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="event not found"
        )
    if existing_event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not allowed to update this event "
        )
    updated_event_data=event_data.model_dump(exclude_unset=True)

    if len(updated_event_data)==0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one field to update "
        )
    for field_name,field_value in updated_event_data.items():
        if field_value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name}cannot be null"
            )

    if "total_seats" in updated_event_data:
        new_total_seats=updated_event_data["total_seats"]  
        booked_seats=(existing_event.total_seats - existing_event.available_seats)
        if new_total_seats<booked_seats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Total seats cannot be less than already booked seats"
            )



    for field_name,field_value in updated_event_data.items():
        setattr(
            existing_event,
            field_name,
            field_value
        )
         
    if "total_seats" in updated_event_data:
        existing_event.available_seats=(existing_event.total_seats-booked_seats)  

    try:
        db.commit()
        db.refresh(existing_event)   
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Event update failed "
        ) 
        # 11. Updated event ka response banaya

    updated_event = {

        "id": existing_event.id,

        "title": existing_event.title,

        "description": existing_event.description,

        "location": existing_event.location,

        "event_date": existing_event.event_date,

        "price": existing_event.price,

        "total_seats": existing_event.total_seats,

        "available_seats": existing_event.available_seats,

        "organizer_id": existing_event.organizer_id

    }

    # 12. Updated event return kiya

    return {

        "message": "Event updated successfully",

        "event": updated_event

    }    

     


    

# CREATE EVENT

@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if event.event_date.tzinfo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event date must include a time zone"
        )
    new_event = models.Event(
        title=event.title,
        description=event.description,
        location=event.location,
        event_date=event.event_date,
        price=event.price,
        total_seats=event.total_seats,
        available_seats=event.total_seats,
        organizer_id=current_user.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {
        "message": "event created succesfully",
        "event": {
            "id": new_event.id,
            "title": new_event.title,
            "description": new_event.description,
            "location": new_event.location,
            "event_date": new_event.event_date,
            "price": new_event.price,
            "total_seats": new_event.total_seats,
            "available_seats": new_event.available_seats,
            "organizer_id": new_event.organizer_id
        }
    }


# =========================================================
# GET ALL EVENTS
# =========================================================
@app.get("/events")
def get_all_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).filter(models.Event.is_active == True).order_by(models.Event.event_date.asc()).all()

    events_list = []
    for event in events:
        single_event = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "price": event.price,
            "available_seats": event.available_seats,  # Corrected key name
            "organizer_id": event.organizer_id
        }
        events_list.append(single_event)

    # Return statement is now OUTSIDE the for loop so all events are returned
    return {
        "total_events": len(events_list),
        "events": events_list
    }


# =========================================================
# GET SINGLE EVENT (STEP 8)
# =========================================================
@app.get("/events/{event_id}")
def get_single_event(event_id: int, db: Session = Depends(get_db)):
    # 1. Database mein event ko uski ID se search kiya
    event = (
        db.query(models.Event)
        .filter(models.Event.id == event_id)
        .filter(models.Event.is_active == True)
        .first()
    )

    # 2. Check kiya ki event database mein mila ya nahi
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # 3. Event ka data dictionary mein return kiya
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "location": event.location,
        "event_date": event.event_date,
        "price": event.price,
        "total_seats": event.total_seats,
        "available_seats": event.available_seats,
        "organizer_id": event.organizer_id
    }


# =========================================================
# USER PROFILE & AUTH
# =========================================================
@app.get("/me")
def get_my_profile(Current_user: models.User = Depends(get_current_user)):
    return {
        "id": Current_user.id,
        "name": Current_user.name,
        "email": Current_user.email
    }


@app.post("/Login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if (existing_user is None or not password_hash.verify(user.password, existing_user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password", headers={"WWW-AUTHENTICATE": "BEARER"})
    
    access_token = create_token(existing_user.id)
    return {
        "message": "Login Successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email already registered"
        )
    hashed_password = password_hash.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User registerd succesfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }