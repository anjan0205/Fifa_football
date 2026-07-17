"""Unit tests for the SQLAlchemy ORM models.

These run against an isolated in-memory SQLite database so no PostgreSQL
instance is required.
"""
import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_user_column_defaults(session):
    user = models.User(
        username="dana", email="dana@example.com", hashed_password="x"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.id is not None
    assert user.role == "fan"
    assert user.is_active is True


def test_match_default_status_and_risk(session):
    match = models.Match(
        team_a="ESP",
        team_b="ITA",
        match_time=datetime.datetime(2026, 6, 20, 16, 0),
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    assert match.status == "scheduled"
    assert match.risk_level == "low"


def test_ticket_relationships(session):
    user = models.User(
        username="erin", email="erin@example.com", hashed_password="x"
    )
    match = models.Match(
        team_a="POR",
        team_b="NED",
        match_time=datetime.datetime(2026, 6, 25, 19, 0),
    )
    session.add_all([user, match])
    session.commit()

    ticket = models.Ticket(
        user_id=user.id,
        match_id=match.id,
        seat_sector="112",
        seat_row="R",
        seat_number="7",
        qr_code="FIFA-2026-1",
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    assert ticket.status == "active"
    assert ticket.owner.username == "erin"
    assert ticket.match.team_a == "POR"
    assert user.tickets[0].id == ticket.id
    assert match.tickets[0].id == ticket.id


def test_incident_defaults_and_created_at(session):
    inc = models.Incident(
        title="Medical", category="medical", location="Section 109"
    )
    session.add(inc)
    session.commit()
    session.refresh(inc)
    assert inc.status == "open"
    assert inc.severity == "low"
    assert isinstance(inc.created_at, datetime.datetime)


def test_task_assignee_relationship(session):
    user = models.User(
        username="finn", email="finn@example.com", hashed_password="x"
    )
    session.add(user)
    session.commit()

    task = models.Task(
        title="Sweep concourse",
        assigned_to_user_id=user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    assert task.status == "pending"
    assert task.assignee.username == "finn"
    assert user.tasks[0].id == task.id


def test_sensor_and_emissions_persist(session):
    sensor = models.SensorData(
        sensor_type="electricity", value=1234.5, location="Grid A"
    )
    emission = models.Emissions(category="scope2", value=98.2)
    session.add_all([sensor, emission])
    session.commit()
    session.refresh(sensor)
    session.refresh(emission)
    assert sensor.value == 1234.5
    assert isinstance(sensor.recorded_at, datetime.datetime)
    assert emission.category == "scope2"
