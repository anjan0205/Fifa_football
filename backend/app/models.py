from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="fan") # fan, volunteer, operator
    is_active = Column(Boolean, default=True)

    tickets = relationship("Ticket", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    team_a = Column(String(50), nullable=False)
    team_b = Column(String(50), nullable=False)
    match_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="scheduled") # scheduled, live, complete
    risk_level = Column(String(20), default="low") # low, medium, high

    tickets = relationship("Ticket", back_populates="match")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    seat_sector = Column(String(10), nullable=False)
    seat_row = Column(String(10), nullable=False)
    seat_number = Column(String(10), nullable=False)
    qr_code = Column(String(255), nullable=False)
    status = Column(String(20), default="active") # active, scanned, cancelled

    owner = relationship("User", back_populates="tickets")
    match = relationship("Match", back_populates="tickets")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    category = Column(String(50)) # medical, fire, security, crowd, technical
    status = Column(String(20), default="open") # open, dispatched, closed
    location = Column(String(100), nullable=False) # e.g., "Sector 112 Concourse"
    severity = Column(String(20), default="low") # low, medium, high, critical
    assigned_volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending") # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assignee = relationship("User", back_populates="tasks")

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(String(50), nullable=False) # crowd_count, electricity, water, waste
    value = Column(Float, nullable=False)
    location = Column(String(100), nullable=False)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

class Emissions(Base):
    __tablename__ = "emissions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False) # scope1, scope2, scope3
    value = Column(Float, nullable=False) # CO2e tons
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
