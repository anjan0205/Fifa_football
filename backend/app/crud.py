from typing import Any, Dict, TypeVar

from sqlalchemy.orm import Session

from .database import Base

ModelT = TypeVar("ModelT", bound=Base)


def save(db: Session, instance: ModelT) -> ModelT:
    """Persist a new ORM instance and return it refreshed with generated fields."""
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def apply_updates(db: Session, instance: ModelT, updates: Dict[str, Any]) -> ModelT:
    """Apply a mapping of column updates to an ORM instance and persist it."""
    for key, value in updates.items():
        setattr(instance, key, value)
    db.commit()
    db.refresh(instance)
    return instance
