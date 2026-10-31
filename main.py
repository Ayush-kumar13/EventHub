import os
from pathlib import Path
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from database import Base, engine, get_db
import models
from schemas import UserLogin, UserCreate, EventCreate ,EventUpdate
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


env_file = Path(__file__).resolve().parent / ".env"
if env_file.is_file():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        value = value.strip().strip("\"'")
        os.environ.setdefault(name.strip(), value)

Bearer_scheme = HTTPBearer()

password_hash = PasswordHash.recommended()

Base.metadata.create_all(bind=engine)

# create_all() creates missing tables but does not add columns to existing ones.
user_columns = {column["name"] for column in inspect(engine).get_columns("users")}
with engine.begin() as connection:
    if "role" not in user_columns:
        connection.execute(text(
            "ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'attendee'"
        ))
    if "organizer_status" not in user_columns:
        connection.execute(text(
            "ALTER TABLE users ADD COLUMN organizer_status VARCHAR NOT NULL DEFAULT 'not_applicable'"
        ))

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

#sort
# =========================================================
# STEP 11: GET EVENTS WITH SEARCH, FILTER, SORTING AND PAGINATION
# =========================================================

@app.get("/events")
def get_events(
    search: str = None,
    location: str = None,
    min_price: int = None,
    max_price: int = None,
    sort_by: str = "event_date",
    sort_order: str = "asc",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Basic Validation
    # -----------------------------------------------------

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page number must be at least 1"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Page size must be between 1 and 100"
        )

    if min_price is not None and min_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Minimum price cannot be negative"
        )

    if max_price is not None and max_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum price cannot be negative"
        )

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=400,
            detail="Minimum price cannot be greater than maximum price"
        )

    # -----------------------------------------------------
    # 2. Database Query Start
    # -----------------------------------------------------

    events_query = db.query(models.Event)

    # Sirf active events dikhane hain
    events_query = events_query.filter(
        models.Event.is_active == True
    )

    # -----------------------------------------------------
    # 3. Search By Event Title
    # -----------------------------------------------------

    if search is not None and search.strip() != "":
        search_text = search.strip()

        events_query = events_query.filter(
            models.Event.title.ilike(f"%{search_text}%")
        )

    # -----------------------------------------------------
    # 4. Filter By Location
    # -----------------------------------------------------

    if location is not None and location.strip() != "":
        location_text = location.strip()

        events_query = events_query.filter(
            models.Event.location.ilike(f"%{location_text}%")
        )

    # -----------------------------------------------------
    # 5. Filter By Minimum Price
    # -----------------------------------------------------

    if min_price is not None:
        events_query = events_query.filter(
            models.Event.price >= min_price
        )

    # -----------------------------------------------------
    # 6. Filter By Maximum Price
    # -----------------------------------------------------

    if max_price is not None:
        events_query = events_query.filter(
            models.Event.price <= max_price
        )

    # -----------------------------------------------------
    # 7. Count Total Matching Events
    # -----------------------------------------------------

    total_events = events_query.count()

    # -----------------------------------------------------
    # 8. Sorting
    # -----------------------------------------------------

    if sort_by == "event_date":
        sort_column = models.Event.event_date

    elif sort_by == "price":
        sort_column = models.Event.price

    elif sort_by == "title":
        sort_column = models.Event.title

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by. Use event_date, price or title"
        )

    if sort_order == "asc":
        events_query = events_query.order_by(sort_column.asc())

    elif sort_order == "desc":
        events_query = events_query.order_by(sort_column.desc())

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_order. Use asc or desc"
        )

    # -----------------------------------------------------
    # 9. Pagination
    # -----------------------------------------------------

    records_to_skip = (page - 1) * page_size

    events = (
        events_query
        .offset(records_to_skip)
        .limit(page_size)
        .all()
    )

    # -----------------------------------------------------
    # 10. Prepare Response
    # -----------------------------------------------------

    events_list = []

    for event in events:
        single_event = {
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

        events_list.append(single_event)

    # -----------------------------------------------------
    # 11. Return Final Response
    # -----------------------------------------------------

    total_pages = (total_events + page_size - 1) // page_size

    return {
        "total_events": total_events,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "events": events_list
    }








#DELETE EVENT

@app.delete("/events/{event_id}")
def delete_event( 
    event_id:int,
    db:Session=Depends(get_db),
    current_user:models.User=Depends(get_current_user)
):
    existing_event=db.query(models.Event).filter(models.Event.id==event_id).first()
    
    if existing_event is None:
        raise HTTPException(
            status_code=404,
            detail="event not found"
        )
    if existing_event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="you are not allowed to delete this event"
        )
    if existing_event.is_active==False:
        raise HTTPException(
            status_code=400,
            detail="event is already inactive"
        )
    existing_event.is_active=False


    try:
        db.commit()
        db.refresh(existing_event)
    except Exception:
        db.rollback() 
        raise HTTPException(
            status_code=500,
            detail="event deletion failed "
        )
    return{
        "message":"Event deleted successfully",
        "event_id":existing_event.id,
        "is_active":existing_event.is_active
    }   






#update event deatails
@app.patch("/events/{event_id}")
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


# GET SINGLE EVENT (STEP 8)

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

# register 
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
        hashed_password=hashed_password,
        role=user.role,organizer_status=(
         "pending"
        if user.role == "organizer"
        else "not_applicable"
)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User registerd succesfully",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,"role":new_user.role,
        "organizer_status":new_user.organizer_status
    }
