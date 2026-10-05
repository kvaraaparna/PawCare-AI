"""
PawCare AI – PostgreSQL Relational Data Models
===============================================
SQLAlchemy data models for PawCare AI with strict relationships,
cascading policies, password hashing security, and metadata auditing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from database import db


class BaseModel(db.Model):
    """Base declarative model providing dynamic keyword argument initialization."""
    __abstract__ = True
    __allow_unmapped__ = True

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)


# ==============================================================================
# 1. USERS MODEL
# ==============================================================================
class User(BaseModel):
    """
    User account model.
    Stores owner details and hashed authentication credentials.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    dogs: Mapped[list[Any]] = relationship(
        "Dog",
        backref="owner",
        cascade="all, delete-orphan",
        lazy=True,
        passive_deletes=True,
    )
    analyses: Mapped[list[Any]] = relationship(
        "AnalysisHistory",
        backref="user",
        lazy=True,
        passive_deletes=True,
    )
    reports: Mapped[list[Any]] = relationship(
        "Report",
        backref="user",
        lazy=True,
        passive_deletes=True,
    )

    def set_password(self, password: str):
        """Hash and securely store user password."""
        try:
            self.password_hash = generate_password_hash(password)
        except (AttributeError, ValueError):
            self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """Verify candidate password against stored cryptographic hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Safe serialization excluding sensitive password hash."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}'>"


# ==============================================================================
# 2. DOGS MODEL
# ==============================================================================
class Dog(BaseModel):
    """
    Dog profile model.
    Represents a canine owned by a User. One user can have multiple dogs.
    """
    __tablename__ = "dogs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dog_name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Float, nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships & Backrefs
    owner: Any
    health_info: Mapped[list[Any]] = relationship(
        "DogHealth",
        backref="dog",
        cascade="all, delete-orphan",
        lazy=True,
        passive_deletes=True,
    )
    gallery: Mapped[list[Any]] = relationship(
        "DogGallery",
        backref="dog",
        cascade="all, delete-orphan",
        lazy=True,
        passive_deletes=True,
    )
    analyses: Mapped[list[Any]] = relationship(
        "AnalysisHistory",
        backref="dog",
        lazy=True,
        passive_deletes=True,
    )
    reports: Mapped[list[Any]] = relationship(
        "Report",
        backref="dog",
        lazy=True,
        passive_deletes=True,
    )

    def is_owned_by(self, user_id: int) -> bool:
        """Security helper verifying ownership."""
        return self.user_id == user_id

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "dog_name": self.dog_name,
            "breed": self.breed,
            "age": self.age,
            "gender": self.gender,
            "weight": self.weight,
            "photo_path": self.photo_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Dog id={self.id} name='{self.dog_name}' user_id={self.user_id}>"


# ==============================================================================
# 3. DOG HEALTH MODEL
# ==============================================================================
class DogHealth(BaseModel):
    """
    Dog health history and current symptom notes.
    All fields are optional.
    """
    __tablename__ = "dog_health"

    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_skin_problems = db.Column(db.Text, nullable=True)
    current_symptoms = db.Column(db.Text, nullable=True)
    health_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Backref
    dog: Any

    def to_dict(self):
        return {
            "id": self.id,
            "dog_id": self.dog_id,
            "previous_skin_problems": self.previous_skin_problems,
            "current_symptoms": self.current_symptoms,
            "health_notes": self.health_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<DogHealth id={self.id} dog_id={self.dog_id}>"


# ==============================================================================
# 4. DOG GALLERY MODEL
# ==============================================================================
class DogGallery(BaseModel):
    """
    Dog gallery photographs and optional captions.
    A dog can have multiple gallery photos.
    """
    __tablename__ = "dog_gallery"

    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Backref
    dog: Any

    def to_dict(self):
        return {
            "id": self.id,
            "dog_id": self.dog_id,
            "image_path": self.image_path,
            "caption": self.caption,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<DogGallery id={self.id} dog_id={self.dog_id} path='{self.image_path}'>"


# ==============================================================================
# 5. ANALYSIS HISTORY MODEL
# ==============================================================================
class AnalysisHistory(BaseModel):
    """
    Records deep learning skin disease inference results, confidence,
    probabilities across all 4 classes, and Grad-CAM visualization path.
    """
    __tablename__ = "analysis_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    image_path = db.Column(db.String(255), nullable=False)
    predicted_class = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    bacterial_probability = db.Column(db.Float, nullable=False)
    fungal_probability = db.Column(db.Float, nullable=False)
    healthy_probability = db.Column(db.Float, nullable=False)
    allergic_probability = db.Column(db.Float, nullable=False)
    gradcam_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships & Backrefs
    dog: Any
    user: Any
    reports: Mapped[list[Any]] = relationship(
        "Report",
        backref="analysis",
        cascade="all, delete-orphan",
        lazy=True,
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "dog_id": self.dog_id,
            "image_path": self.image_path,
            "predicted_class": self.predicted_class,
            "display_name": self.display_name,
            "confidence": self.confidence,
            "probabilities": {
                "Bacterial_dermatosis": self.bacterial_probability,
                "Fungal_infections": self.fungal_probability,
                "Healthy": self.healthy_probability,
                "Hypersensitivity_allergic_dermatosis": self.allergic_probability,
            },
            "gradcam_path": self.gradcam_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return (
            f"<AnalysisHistory id={self.id} class='{self.predicted_class}' "
            f"conf={self.confidence:.2f}%>"
        )


# ==============================================================================
# 6. REPORTS MODEL
# ==============================================================================
class Report(BaseModel):
    """
    Generated downloadable clinical PDF screening reports.
    Linked to analysis history, user, and dog.
    """
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("analysis_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    report_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Backrefs
    analysis: Any
    user: Any
    dog: Any

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "user_id": self.user_id,
            "dog_id": self.dog_id,
            "report_path": self.report_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Report id={self.id} analysis_id={self.analysis_id} path='{self.report_path}'>"


# ==============================================================================
# 7. MODEL VERSIONS MODEL
# ==============================================================================
class ModelVersion(BaseModel):
    """
    Tracks deployed AI model checkpoints, versions, validation accuracy,
    and active status for transfer learning lifecycle management.
    """
    __tablename__ = "model_versions"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(50), nullable=False)
    model_path = db.Column(db.String(255), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_path": self.model_path,
            "accuracy": self.accuracy,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return (
            f"<ModelVersion id={self.id} name='{self.model_name}' "
            f"ver='{self.model_version}' acc={self.accuracy}% active={self.is_active}>"
        )
