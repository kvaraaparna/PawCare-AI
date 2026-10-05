"""
PawCare AI – PostgreSQL Database & Relationships Verification Test Suite
========================================================================
Usage:
    python test_db.py

Tests:
1. PostgreSQL connection & dialect check (strictly asserts 'postgresql', not sqlite).
2. Verifies all 7 required tables exist in schema.
3. Tests User password hashing security (Werkzeug crypto hashing).
4. Tests User -> Dog ownership relationship.
5. Tests Dog -> DogHealth (optional fields) relationship.
6. Tests Dog -> DogGallery (multiple photos) relationship.
7. Tests Dog / User -> AnalysisHistory (probabilities, confidence, Grad-CAM path).
8. Tests AnalysisHistory -> Report relationship.
9. Tests ModelVersion query for baseline ResNet-18 v1 (76.06% accuracy).
10. Automated test data teardown ensuring production database hygiene.
"""

import logging
import sys
from typing import Any

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from database import db, init_app
from models import (
    AnalysisHistory,
    Dog,
    DogGallery,
    DogHealth,
    ModelVersion,
    Report,
    User,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("PawCareAI.TestDB")


def run_database_tests():
    print("=" * 65)
    print("RUNNING PAWCARE AI POSTGRESQL DATABASE VERIFICATION SUITE")
    print("=" * 65)

    app = Flask(__name__)
    init_app(app)

    with app.app_context():
        # TEST 1: Dialect and Connection
        print("\n--- TEST 1: PostgreSQL Dialect & Connection Verification ---")
        dialect_name = db.engine.dialect.name
        print(f"Active Database Dialect: {dialect_name}")
        if dialect_name != "postgresql":
            print(f"FAILED: Expected 'postgresql' dialect, got '{dialect_name}'.")
            sys.exit(1)
        
        # Test basic query execution
        result = db.session.execute(db.text("SELECT version();")).scalar()
        if not result or not isinstance(result, str):
            print("FAILED: PostgreSQL version query returned no result.")
            sys.exit(1)
        version_str = result.split(",")[0]
        print(f"Connected PostgreSQL Version: {version_str}")
        print(">>> TEST 1 PASSED: Connected to PostgreSQL server!")

        # TEST 2: Schema Tables Presence (All 7 Tables)
        print("\n--- TEST 2: Verifying All 7 Required Tables ---")
        inspector = db.inspect(db.engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = [
            "users",
            "dogs",
            "dog_health",
            "dog_gallery",
            "analysis_history",
            "reports",
            "model_versions",
        ]

        for tbl in required_tables:
            if tbl in existing_tables:
                cols = [c["name"] for c in inspector.get_columns(tbl)]
                print(f"  ✓ Table '{tbl}' found ({len(cols)} columns)")
            else:
                print(f"  ✗ MISSING Table '{tbl}'!")
                sys.exit(1)
        print(">>> TEST 2 PASSED: All 7 required tables confirmed in PostgreSQL!")

        # TEST 3: User Password Hashing Security
        print("\n--- TEST 3: Password Hashing Security ---")
        test_email = "test_vet_user_2026@pawcare.local"
        # Clean any preexisting test user
        existing_u = User.query.filter_by(email=test_email).first()
        if existing_u:
            db.session.delete(existing_u)
            db.session.commit()

        user = User(
            full_name="Dr. Alex Rivera",
            email=test_email,
            phone="+1-555-0199",
            city="Seattle",
        )
        plain_secret = "SecureVetPassword#2026!"
        user.set_password(plain_secret)

        assert user.password_hash != plain_secret, "Password was stored in plain-text!"
        assert user.check_password(plain_secret) is True, "Valid password check failed!"
        assert user.check_password("WrongPassword123") is False, "Invalid password was accepted!"
        assert user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:"), "Hash format unexpected!"

        db.session.add(user)
        db.session.commit()
        print(f"Created User: id={user.id}, email={user.email}")
        print(f"Password Hash: {user.password_hash[:30]}... (Cryptographically Secured)")
        print(">>> TEST 3 PASSED: Password hashing & verification works securely!")

        # TEST 4: User -> Dogs Relationship (One user, multiple dogs)
        print("\n--- TEST 4: User -> Dogs Relationship ---")
        dog1 = Dog(
            user_id=user.id,
            dog_name="Buddy",
            breed="Golden Retriever",
            age="3 years",
            gender="Male",
            weight=31.5,
            photo_path="uploads/buddy.jpg",
        )
        dog2 = Dog(
            user_id=user.id,
            dog_name="Bella",
            breed="Beagle",
            age="1.5 years",
            gender="Female",
            weight=11.2,
            photo_path="uploads/bella.jpg",
        )
        db.session.add_all([dog1, dog2])
        db.session.commit()

        # Query user dogs
        queried_user = db.session.get(User, user.id)
        assert queried_user is not None, "User not found!"
        assert len(queried_user.dogs) == 2, f"Expected 2 dogs, got {len(queried_user.dogs)}"
        assert dog1.owner.email == test_email, "Backref owner failed!"
        assert dog1.is_owned_by(user.id) is True, "Ownership check failed!"
        print(f"User '{user.full_name}' successfully owns {len(queried_user.dogs)} dogs:")
        for d in queried_user.dogs:
            print(f"  - Dog id={d.id}: {d.dog_name} ({d.breed}, {d.age}, {d.weight} kg)")
        print(">>> TEST 4 PASSED: User -> Dogs relationship verified!")

        # TEST 5: Dog -> Health Information (Optional fields)
        print("\n--- TEST 5: Dog -> Health Information ---")
        health = DogHealth(
            dog_id=dog1.id,
            previous_skin_problems="Mild seasonal flea allergy in 2025.",
            current_symptoms="Flaking erythema around left flank, scratching frequently.",
            health_notes="Owner administered oatmeal bath; scheduled clinic checkup."
        )
        db.session.add(health)
        db.session.commit()

        queried_dog = db.session.get(Dog, dog1.id)
        assert queried_dog is not None, "Dog not found!"
        assert len(queried_dog.health_info) >= 1, "Health info relationship failed!"
        assert queried_dog.health_info[0].dog_id == dog1.id
        print(f"Dog '{dog1.dog_name}' Health Profile:")
        print(f"  - Symptoms: {queried_dog.health_info[0].current_symptoms}")
        print(f"  - Notes:    {queried_dog.health_info[0].health_notes}")
        print(">>> TEST 5 PASSED: Dog -> Health Information verified!")

        # TEST 6: Dog -> Gallery Photos (Multiple photos per dog)
        print("\n--- TEST 6: Dog -> Gallery Photos ---")
        photo1 = DogGallery(dog_id=dog1.id, image_path="gallery/buddy_park.jpg", caption="Playing in the park")
        photo2 = DogGallery(dog_id=dog1.id, image_path="gallery/buddy_lesion.jpg", caption="Skin patch close-up")
        db.session.add_all([photo1, photo2])
        db.session.commit()

        assert len(queried_dog.gallery) == 2, "Gallery relationship failed!"
        print(f"Dog '{dog1.dog_name}' Gallery ({len(queried_dog.gallery)} photos):")
        for g in queried_dog.gallery:
            print(f"  - Photo id={g.id}: path='{g.image_path}', caption='{g.caption}'")
        print(">>> TEST 6 PASSED: Dog -> Gallery relationship verified!")

        # TEST 7: Analysis History Linked to User & Dog
        print("\n--- TEST 7: Analysis History & Multiclass Probabilities ---")
        analysis = AnalysisHistory(
            user_id=user.id,
            dog_id=dog1.id,
            image_path="uploads/lesion_sample.jpg",
            predicted_class="Bacterial_dermatosis",
            display_name="Bacterial Dermatosis",
            confidence=83.5,
            bacterial_probability=0.835,
            fungal_probability=0.082,
            healthy_probability=0.041,
            allergic_probability=0.042,
            gradcam_path="uploads/gradcam_sample.jpg",
        )
        db.session.add(analysis)
        db.session.commit()

        assert analysis.id is not None
        assert analysis.dog.dog_name == "Buddy"
        assert analysis.user.email == test_email
        print(f"Recorded Analysis id={analysis.id}:")
        print(f"  - Condition:  {analysis.display_name} ({analysis.confidence}%)")
        print(f"  - Linked Dog: {analysis.dog.dog_name} (Owner: {analysis.user.full_name})")
        print(f"  - Grad-CAM:   {analysis.gradcam_path}")
        print(">>> TEST 7 PASSED: Analysis History successfully linked to Dog & User!")

        # TEST 8: Analysis History -> Report Relationship
        print("\n--- TEST 8: Analysis History -> Reports Relationship ---")
        report = Report(
            analysis_id=analysis.id,
            user_id=user.id,
            dog_id=dog1.id,
            report_path="reports/PawCare_AI_Health_Report_EN_20260910.pdf"
        )
        db.session.add(report)
        db.session.commit()

        assert report.id is not None
        analysis_reports: Any = analysis.reports
        assert len(analysis_reports) == 1
        assert analysis_reports[0].report_path == report.report_path
        print(f"Generated Report id={report.id}:")
        print(f"  - Linked Analysis: id={report.analysis_id} ({report.analysis.display_name})")
        print(f"  - PDF Path:        {report.report_path}")
        print(">>> TEST 8 PASSED: Analysis -> Report linkage verified!")

        # TEST 9: Baseline Model Version Query
        print("\n--- TEST 9: Active Baseline Model Check ---")
        model = ModelVersion.query.filter_by(is_active=True).first()
        assert model is not None, "No active model version found!"
        assert model.model_name == "ResNet18", f"Unexpected model name: {model.model_name}"
        assert model.accuracy == 76.06, f"Unexpected accuracy: {model.accuracy}"
        print(f"Active Production Model: {model.model_name} (Version: {model.model_version})")
        print(f"  - Model Path:    {model.model_path}")
        print(f"  - Test Accuracy: {model.accuracy}%")
        print(f"  - Description:   {model.description}")
        print(">>> TEST 9 PASSED: Active baseline model successfully verified in PostgreSQL!")

        # TEST 10: Clean Teardown of Test Records
        print("\n--- TEST 10: Clean Teardown of Test Records ---")
        db.session.delete(user) # Cascades delete to dogs, dog_health, dog_gallery
        db.session.delete(report)
        db.session.delete(analysis)
        db.session.commit()

        # Verify clean deletion
        assert User.query.filter_by(email=test_email).first() is None
        assert Dog.query.filter_by(dog_name="Buddy").first() is None
        print("All test records cleaned up cleanly. Production state preserved.")
        print(">>> TEST 10 PASSED: Database cleanup verified!")

    print("\n" + "=" * 65)
    print("ALL 10 DATABASE TESTS COMPLETED AND PASSED SUCCESSFULLY!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_database_tests()
