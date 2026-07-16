from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "fan"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Match Schemas
class MatchBase(BaseModel):
    team_a: str
    team_b: str
    match_time: datetime
    status: str = "scheduled"
    risk_level: str = "low"

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    id: int

    class Config:
        from_attributes = True

# Ticket Schemas
class TicketBase(BaseModel):
    match_id: int
    seat_sector: str
    seat_row: str
    seat_number: str

class TicketCreate(TicketBase):
    user_id: int

class TicketResponse(TicketBase):
    id: int
    user_id: int
    qr_code: str
    status: str
    match: MatchResponse

    class Config:
        from_attributes = True

# Incident Schemas
class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    status: str = "open"
    location: str
    severity: str = "low"
    assigned_volunteer_id: Optional[int] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    assigned_volunteer_id: Optional[int] = None
    severity: Optional[str] = None

class IncidentResponse(IncidentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to_user_id: int
    status: str = "pending"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Sensor Schemas
class SensorDataBase(BaseModel):
    sensor_type: str
    value: float
    location: str

class SensorDataCreate(SensorDataBase):
    pass

class SensorDataResponse(SensorDataBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True

# Emissions Schemas
class EmissionsBase(BaseModel):
    category: str
    value: float

class EmissionsCreate(EmissionsBase):
    pass

class EmissionsResponse(EmissionsBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True
