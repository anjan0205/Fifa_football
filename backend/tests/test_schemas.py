"""Unit tests for the Pydantic validation schemas."""
import pytest
from pydantic import ValidationError

from app import schemas


def test_user_create_defaults_and_fields():
    user = schemas.UserCreate(
        username="alice", email="alice@example.com", password="secret"
    )
    assert user.role == "fan"  # default
    assert user.password == "secret"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        schemas.UserCreate(
            username="bob", email="not-an-email", password="pw"
        )


def test_user_create_requires_password():
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="bob", email="bob@example.com")


def test_user_response_from_attributes():
    class Row:
        id = 7
        username = "carol"
        email = "carol@example.com"
        role = "operator"
        is_active = True

    resp = schemas.UserResponse.model_validate(Row())
    assert resp.id == 7
    assert resp.is_active is True
    assert resp.role == "operator"


def test_match_base_defaults():
    match = schemas.MatchCreate(
        team_a="ARG", team_b="FRA", match_time="2026-06-11T18:00:00"
    )
    assert match.status == "scheduled"
    assert match.risk_level == "low"


def test_match_time_accepts_datetime_string():
    match = schemas.MatchCreate(
        team_a="BRA", team_b="GER", match_time="2026-07-01T20:30:00"
    )
    assert match.match_time.year == 2026
    assert match.match_time.hour == 20


def test_ticket_create_requires_user_id():
    with pytest.raises(ValidationError):
        schemas.TicketCreate(
            match_id=1, seat_sector="A", seat_row="1", seat_number="12"
        )


def test_incident_defaults_and_optional_description():
    inc = schemas.IncidentCreate(
        title="Smoke", category="fire", location="Sector 112"
    )
    assert inc.status == "open"
    assert inc.severity == "low"
    assert inc.description is None
    assert inc.assigned_volunteer_id is None


def test_incident_update_partial_fields():
    upd = schemas.IncidentUpdate(status="dispatched")
    dumped = upd.model_dump(exclude_unset=True)
    assert dumped == {"status": "dispatched"}


def test_sensor_data_value_coerced_to_float():
    sensor = schemas.SensorDataCreate(
        sensor_type="crowd_count", value="42", location="Gate A"
    )
    assert sensor.value == 42.0
    assert isinstance(sensor.value, float)


def test_sensor_data_rejects_non_numeric_value():
    with pytest.raises(ValidationError):
        schemas.SensorDataCreate(
            sensor_type="water", value="a-lot", location="Gate B"
        )


def test_emissions_schema_fields():
    em = schemas.EmissionsCreate(category="scope1", value=12.5)
    assert em.category == "scope1"
    assert em.value == 12.5


def test_token_schema():
    token = schemas.Token(access_token="abc", token_type="bearer")
    assert token.access_token == "abc"


def test_token_data_optional_defaults():
    data = schemas.TokenData()
    assert data.username is None
    assert data.role is None
