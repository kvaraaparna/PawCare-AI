"""
PawCare AI – Profile & Authentication Verification Suite
=========================================================
Automated end-to-end tests for:
1. User registration & cryptographic password hashing
2. User authentication & session management
3. Profile access protection (login_required redirect)
4. Profile submission with Owner Information, Dog Information, and Dog Photo
5. PostgreSQL persistence across 'users', 'dogs', and 'dog_health' tables
6. Healthy dog scenario: leaving health info blank
7. Clean teardown of test records
"""

import io
import os
import sys
from flask import Flask

from app import app
from database import db
from models import Dog, DogHealth, User


def run_tests():
    print("=" * 65)
    print("RUNNING PAWCARE AI PROFILE & AUTHENTICATION VERIFICATION SUITE")
    print("=" * 65)

    client = app.test_client()

    with app.app_context():
        test_email = "test_profile_owner_2026@pawcare.local"
        test_password = "SecurePassword#2026!"

        # Teardown any preexisting test records
        existing_u = User.query.filter_by(email=test_email).first()
        if existing_u:
            db.session.delete(existing_u)
            db.session.commit()

        # TEST 1: Website open displays landing page (Home) with top-right Login button
        print("\n--- TEST 1: Opening Website Directly Shows Landing Page with Login Button ---")
        root_res = client.get("/", follow_redirects=False)
        assert root_res.status_code == 200, f"Expected 200 for root landing page, got {root_res.status_code}"
        root_text = root_res.get_data(as_text=True)
        assert "PawCare" in root_text, "PawCare branding missing from landing page"
        assert "/login" in root_text, "Login link missing from landing page navbar"
        assert "nav-login-btn" in root_text, "nav-login-btn class missing from landing page navbar"
        print("✓ First website open directly renders landing page with top-right Login button")

        # Protected route /profile still redirects to /login when unauthenticated
        profile_res = client.get("/profile", follow_redirects=False)
        assert profile_res.status_code == 302, f"Expected 302 redirect for profile, got {profile_res.status_code}"
        assert "/login" in profile_res.location, f"Expected redirect to /login, got {profile_res.location}"
        print("✓ Unauthenticated access to /profile cleanly redirects to /login")

        # TEST 2: User Registration & Post-Login Home Redirect
        print("\n--- TEST 2: User Registration & Post-Login Home Redirect ---")
        reg_res = client.post("/register", data={
            "full_name": "Sarah Connor",
            "email": test_email,
            "password": test_password,
            "phone": "+1-206-555-0144",
            "city": "Austin",
        }, follow_redirects=False)
        assert reg_res.status_code == 302, f"Expected 302 redirect after register, got {reg_res.status_code}"
        assert reg_res.location == "/" or reg_res.location.endswith("/"), f"Expected redirect to home '/', got {reg_res.location}"

        # Now follow redirect to Home
        home_res = client.get("/")
        assert home_res.status_code == 200
        assert "PawCare" in home_res.get_data(as_text=True)
        print("✓ Successful login/register immediately opens Home page ('/')")

        user = User.query.filter_by(email=test_email).first()
        assert user is not None, "User record was not created in PostgreSQL!"
        assert user.full_name == "Sarah Connor", f"Full name mismatch: {user.full_name}"
        assert user.phone == "+1-206-555-0144"
        assert user.city == "Austin"
        assert user.check_password(test_password) is True, "Password hash check failed"
        print(f"✓ Registered User: id={user.id}, email={user.email}, full_name='{user.full_name}'")

        # TEST 3: Create Dog Profile & Health Information
        print("\n--- TEST 3: Saving Profile with Owner, Dog, and Health Data ---")
        mock_photo = (io.BytesIO(b"fake-image-bytes-jpeg"), "rocky_test.jpg")
        prof_res = client.post("/profile", data={
            "full_name": "Sarah Connor-Smith",
            "phone": "+1-206-555-9999",
            "city": "Dallas",
            "dog_name": "Rocky",
            "breed": "German Shepherd",
            "age": "2 years",
            "gender": "Male",
            "weight": "34.5",
            "dog_photo": mock_photo,
            "previous_skin_problems": "Mild rash in puppyhood",
            "current_symptoms": "Occasional scratching near ears",
            "health_notes": "Up to date on rabies vaccines; high protein diet",
        }, follow_redirects=True)
        assert prof_res.status_code == 200

        # Assert PostgreSQL persistence
        db.session.refresh(user)
        assert user.full_name == "Sarah Connor-Smith", "User name not updated in DB!"
        assert user.phone == "+1-206-555-9999"
        assert user.city == "Dallas"

        dog = Dog.query.filter_by(user_id=user.id).first()
        assert dog is not None, "Dog record was not created in PostgreSQL!"
        assert dog.dog_name == "Rocky", f"Dog name mismatch: {dog.dog_name}"
        assert dog.breed == "German Shepherd"
        assert dog.age == "2 years"
        assert dog.gender == "Male"
        assert dog.weight == 34.5
        assert dog.photo_path is not None and dog.photo_path.startswith("uploads/dogs/dog_")
        assert dog.photo_path.endswith(".jpg")
        print(f"✓ Created Dog: id={dog.id}, name='{dog.dog_name}', breed='{dog.breed}', photo='{dog.photo_path}'")

        health = DogHealth.query.filter_by(dog_id=dog.id).first()
        assert health is not None, "DogHealth record was not created in PostgreSQL!"
        assert "Mild rash" in (health.previous_skin_problems or "")
        assert "Occasional scratching" in (health.current_symptoms or "")
        assert "rabies vaccines" in (health.health_notes or "")
        print(f"✓ Created DogHealth: id={health.id}, dog_id={health.dog_id}")

        # TEST 4: Healthy Dog Scenario (Health section left blank)
        print("\n--- TEST 4: Healthy Dog Scenario (Health fields left blank) ---")
        client.post("/profile", data={
            "full_name": "Sarah Connor-Smith",
            "phone": "+1-206-555-9999",
            "city": "Dallas",
            "dog_name": "Rocky",
            "breed": "German Shepherd",
            "age": "2 years",
            "gender": "Male",
            "weight": "34.5",
            "previous_skin_problems": "",
            "current_symptoms": "",
            "health_notes": "",
        }, follow_redirects=True)

        db.session.refresh(health)
        assert health.previous_skin_problems is None
        assert health.current_symptoms is None
        assert health.health_notes is None
        print("✓ Health section correctly left blank for healthy dog")

        # TEST 5: GET /profile verifies pre-populated data
        print("\n--- TEST 5: GET /profile Pre-population Check ---")
        get_res = client.get("/profile")
        assert get_res.status_code == 200
        html = get_res.get_data(as_text=True)
        assert 'value="Sarah Connor-Smith"' in html
        assert 'value="Rocky"' in html
        assert 'value="German Shepherd"' in html
        assert 'Optional: You can provide health information now, or add it later if your dog develops any symptoms.' in html
        print("✓ GET /profile correctly rendered with pre-populated values and required health note banner")

        # TEST 6: Teardown
        print("\n--- TEST 6: Test Data Cleanup ---")
        if dog.photo_path and os.path.exists(dog.photo_path):
            try:
                os.remove(dog.photo_path)
            except OSError:
                pass
        db.session.delete(user)
        db.session.commit()
        assert User.query.filter_by(email=test_email).first() is None
        assert Dog.query.filter_by(user_id=user.id).first() is None
        print("✓ Cascade cleanup confirmed in PostgreSQL")

    print("\n" + "=" * 65)
    print("ALL PROFILE & AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
