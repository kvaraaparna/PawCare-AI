"""
PawCare AI – Dog Skin Disease Detection System
==============================================
Production Flask Backend Application

Key Capabilities:
1. Serves PawCare AI Homepage (/) matching reference design.
2. Serves Detection (/detect) with drag-and-drop, sample testing, and dynamic prediction.
3. Serves Model Training & Admin (/training) for ZIP dataset upload, validation, and training.
4. Loads production PyTorch ResNet18 model (best_dog_disease_resnet18.pth) once at startup.
5. Employs lightweight ImageNet ResNet18 canine validator to filter non-dog images while
   accepting full-body, facial, ear, and close-up skin lesion photographs.
6. Returns sorted probabilities, uncertainty flags, clinical education, and veterinary disclaimer.
"""


from __future__ import annotations

import base64
import contextlib
import datetime
from functools import wraps
import io
import logging
import os
import threading
import uuid
import zipfile
from typing import Any, cast

import torch
import torch.nn.functional as F
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from torch import nn
from torchvision import models, transforms
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

from database import db, init_app
from models import Dog, DogHealth, User
from utils.gradcam import generate_gradcam, pil_to_base64
from utils.grok_analyzer import analyze_canine_condition_with_grok
from utils.pdf_report import generate_health_report



# Community routes
from community import (
    community_bp,
    comment_bp,
    community_api
)
# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger("PawCareAI")

# -----------------------------------------------------------------------------
# Application Setup & Paths
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOG_UPLOADS_FOLDER = os.path.join(UPLOAD_FOLDER, "dogs")
DATASET_FOLDER = os.path.join(BASE_DIR, "dataset")
MODELS_FOLDER = os.path.join(BASE_DIR, "models")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOG_UPLOADS_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATES_FOLDER)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "pawcare-ai-development-key"
)
init_app(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DOG_UPLOADS_FOLDER"] = DOG_UPLOADS_FOLDER
app.config["DATASET_FOLDER"] = DATASET_FOLDER
app.config["MODELS_FOLDER"] = MODELS_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # 300 MB limit for dataset uploads
app.config["TEMPLATES_AUTO_RELOAD"] = True


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MODEL_FILENAME = "best_dog_disease_resnet18.pth"
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

# -----------------------------------------------------------------------------
# Canonical Class Ordering (STRICT - DO NOT ALTER)
# -----------------------------------------------------------------------------
CLASSES = [
    "Bacterial_dermatosis",
    "Fungal_infections",
    "Healthy",
    "Hypersensitivity_allergic_dermatosis"
]

FRIENDLY_NAMES = {
    "Bacterial_dermatosis": "Bacterial Dermatosis",
    "Fungal_infections": "Fungal Infection",
    "Healthy": "Healthy",
    "Hypersensitivity_allergic_dermatosis": "Allergic Dermatosis (Hypersensitivity)"
}

DISEASE_INFO = {
    "Bacterial_dermatosis": {
        "title": "Bacterial Dermatosis",
        "badge_class": "badge-danger",
        "message": "This result may indicate visual patterns associated with bacterial-related skin conditions. A veterinarian should confirm the cause.",
        "signs": [
            "Redness, erythema, and cutaneous inflammation",
            "Crusting, scaling, or epidermal collarettes",
            "Pustules, papules, or active skin lesions",
            "Localized irritation and follicular swelling"
        ],
        "recommendation": "Consult a qualified veterinarian for cytology, bacterial culture, and appropriate targeted antimicrobial or topical therapy."
    },
    "Fungal_infections": {
        "title": "Fungal Infection",
        "badge_class": "badge-warning",
        "message": "This result may indicate visual patterns associated with fungal skin conditions. Veterinary confirmation is recommended.",
        "signs": [
            "Circular patches of hair loss (alopecia rings)",
            "Scaly, crusty, or flaky epidermal patches",
            "Redness, hyperpigmentation, or mild lichenification",
            "Moderate to severe pruritus (itching) and irritation"
        ],
        "recommendation": "A clinical examination with fungal culture or Wood's lamp evaluation is recommended to identify dermatophytes and administer antifungal treatments."
    },
    "Healthy": {
        "title": "Healthy",
        "badge_class": "badge-success",
        "message": "No obvious visual pattern corresponding to the trained disease categories was detected. This does not guarantee that the dog is completely healthy.",
        "signs": [
            "Intact epidermal barrier without pustules or active lesions",
            "Even and consistent hair coat density",
            "Absence of evident erythema or active inflammation"
        ],
        "recommendation": "Maintain regular preventative grooming, parasite control, and routine veterinary wellness check-ups. Monitor for any future skin changes."
    },
    "Hypersensitivity_allergic_dermatosis": {
        "title": "Allergic Dermatosis (Hypersensitivity)",
        "badge_class": "badge-warning",
        "message": "This result may indicate visual patterns associated with allergic or hypersensitivity-related skin conditions. Veterinary confirmation is recommended.",
        "signs": [
            "Intense itching, scratching, paw-licking, or rubbing",
            "Redness, inflamed ear flaps, or facial irritation",
            "Secondary alopecia (hair loss) from persistent trauma",
            "Recurrent secondary infections or skin irritation"
        ],
        "recommendation": "Consult a veterinarian to identify underlying allergens (flea, food, or environmental) and discuss effective allergy management plans."
    }
}

MANDATORY_DISCLAIMER = (
    "Important: This AI result is not a veterinary diagnosis. "
    "If your dog has symptoms, discomfort, worsening skin changes, "
    "or persistent problems, consult a qualified veterinarian."
)

# -----------------------------------------------------------------------------
# Preprocessing Transforms
# -----------------------------------------------------------------------------
disease_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

validator_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# -----------------------------------------------------------------------------
# Model Initialization
# -----------------------------------------------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Hardware compute device selected: {device}")

# 1. Disease Classification Model (ResNet18)
disease_model = models.resnet18(weights=None)
disease_model.fc = nn.Linear(disease_model.fc.in_features, len(CLASSES))

if os.path.exists(MODEL_PATH):
    try:
        state_dict = torch.load(MODEL_PATH, map_location=device)
        disease_model.load_state_dict(state_dict)
        logger.info(f"Production disease model weights successfully loaded from: {MODEL_PATH}")
        disease_model_loaded = True
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to load production model weights from {MODEL_PATH}: {e}")
        disease_model_loaded = False
else:
    logger.warning(f"Production model {MODEL_PATH} not found. Normal predictions will report missing model error.")
    disease_model_loaded = False

disease_model = disease_model.to(device)
disease_model.eval()

# 2. ImageNet Canine Validator (ResNet-18)
logger.info("Initializing pretrained ImageNet ResNet-18 canine validator...")
validator_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
validator_model = validator_model.to(device)
validator_model.eval()

# ImageNet Class Categories for Canine Validation
# Domestic dogs: 151 to 268; Wild canines: 269 to 275
CANINE_CLASS_IDS = set(range(151, 276))

# Mammalian fur, skin, carnivores & microscopic biological organisms common in lesion close-ups
MAMMAL_BIO_IDS = (
    set(range(276, 294))                     # Felines & related carnivores
    .union(set(range(339, 362)))             # Small mammals, badgers, ferrets, hogs
    .union({107, 108, 109, 110, 111})        # Jellyfish, nematodes (tissue & biological structures)
    .union({398, 399, 400})                  # Scab, tick, mite parasites
    .union({565, 911})                       # Fur coat, wool textures
)

def validate_dog_presence(pil_img: Image.Image) -> tuple[bool, str]:
    """
    Validates whether the uploaded image is likely a dog or dog skin/tissue.
    Accepts:
      - Full-body dogs, dog faces, heads
      - Close-up dog ears, skin, and dermatological lesions
    Rejects:
      - Obvious non-dog images (scenery, vehicles, documents, envelopes, abstract artwork)
    """
    try:
        tensor = cast(torch.Tensor, validator_transform(pil_img)).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = validator_model(tensor)
            probs = F.softmax(logits, dim=1)[0]

        _, top_indices = torch.topk(probs, 15)
        top_indices_list = top_indices.tolist()

        canine_prob = sum(probs[cid].item() for cid in CANINE_CLASS_IDS)
        mammal_bio_prob = sum(probs[bid].item() for bid in MAMMAL_BIO_IDS)

        has_canine_top10 = any(idx in CANINE_CLASS_IDS for idx in top_indices_list[:10])
        has_bio_top10 = any(idx in MAMMAL_BIO_IDS for idx in top_indices_list[:10])

        logger.info(
            f"Canine Validator - CanineProb: {canine_prob:.4f}, "
            f"MammalBioProb: {mammal_bio_prob:.4f}, Top1: {top_indices_list[0]}"
        )

        # Condition 1: Direct canine breed match (full body / face)
        if canine_prob >= 0.03 or has_canine_top10:
            return True, "Canine breed match verified"

        # Condition 2: Close-up skin, ear, lesion, or fur texture match
        if (canine_prob + mammal_bio_prob >= 0.05) and has_bio_top10:
            return True, "Canine anatomical/tissue pattern accepted"

        # Obvious non-dog rejection
        return False, "Unable to confidently verify this as a dog image. Please upload a clear dog image."

    except Exception as e:  # noqa: BLE001
        logger.error(f"Error during canine validation: {e}")
        # Fail safe
        return True, "Validator fallback"

def is_allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# -----------------------------------------------------------------------------
# Training Background State
# -----------------------------------------------------------------------------
training_lock = threading.Lock()
training_state: dict[str, Any] = {
    "status": "idle",  # "idle", "training", "completed", "error"
    "epoch": 0,
    "total_epochs": 15,
    "train_loss": 0.0,
    "train_acc": 0.0,
    "val_loss": 0.0,
    "val_acc": 0.0,
    "best_val_acc": 0.0,
    "message": "No training in progress.",
    "model_path": None,
    "logs": []
}

def update_training_callback(update_info: dict[str, Any]):
    with training_lock:
        training_state.update(update_info)
        if "message" in update_info:
            training_state["logs"].append(update_info["message"])
            if len(training_state["logs"]) > 50:
                training_state["logs"].pop(0)

# -----------------------------------------------------------------------------
# Active Prediction Cache (For PDF Reports & Grad-CAM Downloads)
# -----------------------------------------------------------------------------
analyses_lock = threading.Lock()
ACTIVE_ANALYSES: dict[str, dict[str, Any]] = {}

def cleanup_expired_analyses():
    """Removes analysis entries older than 2 hours or limits cache size."""
    with analyses_lock:
        now = datetime.datetime.now(datetime.timezone.utc)
        expired_keys = [
            k for k, v in ACTIVE_ANALYSES.items()
            if (now - v.get("created_at", now)).total_seconds() > 7200
        ]
        for k in expired_keys:
            ACTIVE_ANALYSES.pop(k, None)
        if len(ACTIVE_ANALYSES) > 100:
            oldest_keys = sorted(
                ACTIVE_ANALYSES.keys(),
                key=lambda k: ACTIVE_ANALYSES[k].get("created_at", now)
            )[:50]
            for k in oldest_keys:
                ACTIVE_ANALYSES.pop(k, None)

# -----------------------------------------------------------------------------
# Authentication & Session Helpers
# -----------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access your profile.", "info")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_user():
    """Injects current logged-in user into all templates."""
    current_user = None
    if "user_id" in session:
        current_user = db.session.get(User, session["user_id"])
    return dict(current_user=current_user)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
    """Serves files stored in the uploads directory."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# -----------------------------------------------------------------------------
# Routes - User Authentication
# -----------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login endpoint."""
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        next_page = request.args.get("next") or url_for("index")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_email"] = user.email
            session["user_name"] = user.full_name
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(next_page)
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration endpoint."""
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        phone = (request.form.get("phone") or "").strip()
        city = (request.form.get("city") or "").strip()

        if not full_name:
            flash("Full Name is required.", "danger")
            return render_template("login.html", active_tab="register")
        if not email or "@" not in email:
            flash("A valid email address is required.", "danger")
            return render_template("login.html", active_tab="register")
        if not password or len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("login.html", active_tab="register")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please log in.", "warning")
            return render_template("login.html", active_tab="login", email=email)

        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone if phone else None,
            city=city if city else None,
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        session["user_email"] = new_user.email
        session["user_name"] = new_user.full_name
        flash("Registration successful! Welcome to PawCare AI.", "success")
        return redirect(url_for("index"))

    return render_template("login.html", active_tab="register")


@app.route("/logout")
def logout():
    """Logs out user and clears session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("login"))


@app.route("/demo-login")
def demo_login():
    """One-click demo login for fast testing and review."""
    demo_email = "alex.rivera@pawcare.local"
    demo_user = User.query.filter_by(email=demo_email).first()
    if not demo_user:
        demo_user = User(
            full_name="Dr. Alex Rivera",
            email=demo_email,
            phone="+1-555-0199",
            city="Seattle",
        )
        demo_user.set_password("PawCareDemo#2026")
        db.session.add(demo_user)
        db.session.commit()

        # Seed demo dog
        demo_dog = Dog(
            user_id=demo_user.id,
            dog_name="Buddy",
            breed="Golden Retriever",
            age="3 years",
            gender="Male",
            weight=31.5,
        )
        db.session.add(demo_dog)
        db.session.commit()

    session["user_id"] = demo_user.id
    session["user_email"] = demo_user.email
    session["user_name"] = demo_user.full_name
    flash(f"Logged in as demo user {demo_user.full_name}.", "success")
    return redirect(url_for("index"))


# -----------------------------------------------------------------------------
# Routes - Profile Management
# -----------------------------------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User and Dog Profile management page."""
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    dog = Dog.query.filter_by(user_id=user.id).order_by(Dog.id.asc()).first()
    health = DogHealth.query.filter_by(dog_id=dog.id).first() if dog else None

    if request.method == "POST":
        # 1. Owner Information
        full_name = (request.form.get("full_name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        city = (request.form.get("city") or "").strip()

        if not full_name:
            flash("Owner Full Name is required.", "danger")
            return render_template("profile.html", user=user, dog=dog, health=health)

        user.full_name = full_name
        user.phone = phone if phone else None
        user.city = city if city else None
        session["user_name"] = full_name

        # 2. Dog Information
        dog_name = (request.form.get("dog_name") or "").strip()
        breed = (request.form.get("breed") or "").strip()
        age = (request.form.get("age") or "").strip()
        gender = (request.form.get("gender") or "").strip()
        weight_str = (request.form.get("weight") or "").strip()

        if not dog_name:
            flash("Dog Name is required.", "danger")
            return render_template("profile.html", user=user, dog=dog, health=health)
        if not breed:
            flash("Dog Breed is required.", "danger")
            return render_template("profile.html", user=user, dog=dog, health=health)
        if not age:
            flash("Dog Age is required.", "danger")
            return render_template("profile.html", user=user, dog=dog, health=health)
        if not gender:
            flash("Dog Gender is required.", "danger")
            return render_template("profile.html", user=user, dog=dog, health=health)

        weight_val = None
        if weight_str:
            try:
                weight_val = float(weight_str)
            except ValueError:
                flash("Weight must be a valid numeric value.", "danger")
                return render_template("profile.html", user=user, dog=dog, health=health)

        if not dog:
            dog = Dog(
                user_id=user.id,
                dog_name=dog_name,
                breed=breed,
                age=age,
                gender=gender,
                weight=weight_val,
            )
            db.session.add(dog)
            db.session.flush()
        else:
            dog.dog_name = dog_name
            dog.breed = breed
            dog.age = age
            dog.gender = gender
            dog.weight = weight_val

        # Dog Photo (optional)
        if "dog_photo" in request.files:
            file = request.files["dog_photo"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
                if ext in ALLOWED_IMAGE_EXTENSIONS:
                    safe_name = f"dog_{dog.id}_{uuid.uuid4().hex[:8]}.{ext}"
                    save_path = os.path.join(DOG_UPLOADS_FOLDER, safe_name)
                    file.save(save_path)
                    dog.photo_path = f"uploads/dogs/{safe_name}"
                else:
                    flash("Dog photo must be a JPG, PNG, or WEBP image.", "warning")

        # 3. Health Information (all optional)
        prev_problems = (request.form.get("previous_skin_problems") or "").strip()
        curr_symptoms = (request.form.get("current_symptoms") or "").strip()
        notes = (request.form.get("health_notes") or "").strip()

        has_health_info = bool(prev_problems or curr_symptoms or notes)

        if has_health_info:
            if not health:
                health = DogHealth(
                    dog_id=dog.id,
                    previous_skin_problems=prev_problems if prev_problems else None,
                    current_symptoms=curr_symptoms if curr_symptoms else None,
                    health_notes=notes if notes else None,
                )
                db.session.add(health)
            else:
                health.previous_skin_problems = prev_problems if prev_problems else None
                health.current_symptoms = curr_symptoms if curr_symptoms else None
                health.health_notes = notes if notes else None
        elif health:
            health.previous_skin_problems = None
            health.current_symptoms = None
            health.health_notes = None

        db.session.commit()
        flash("Profile successfully updated!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user, dog=dog, health=health)


# -----------------------------------------------------------------------------
# Routes - User Interface
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    """PawCare AI Homepage / Public Landing Page."""
    return render_template("index.html")

@app.route("/detect")
def detect():
    """Detection & Screening Page matching PawCare AI visual theme."""
    if "user_id" not in session:
        return redirect(url_for("login", next=request.url))
    return render_template("detect.html")

@app.route("/training")
def training_page():
    """Separate Training & Admin Interface."""
    if "user_id" not in session:
        return redirect(url_for("login", next=request.url))
    return render_template("training.html")

# -----------------------------------------------------------------------------
# Routes - Disease Prediction
# -----------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    """
    Main disease screening endpoint.
    1. Validates file presence and format.
    2. Runs ImageNet canine presence validation.
    3. If valid dog, processes via ResNet18 disease model.
    4. Computes all 4 class probabilities, uncertainty flags, and returns educational metadata.
    """
    if not os.path.exists(MODEL_PATH):
        return jsonify({
            "success": False,
            "error_title": "Model Missing",
            "message": "Trained model not found. Please place best_dog_disease_resnet18.pth in the project root."
        }), 500

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error_title": "Missing File",
            "message": "No image file was included in the upload."
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "error_title": "No File Selected",
            "message": "Please select a valid image file."
        }), 400

    if not file.filename or not is_allowed_image(file.filename):
        return jsonify({
            "success": False,
            "error_title": "Unsupported Format",
            "message": "Only JPG, JPEG, PNG, and WEBP image formats are supported."
        }), 400

    filepath = None
    try:
        ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)

        # Verify image can be decoded
        try:
            pil_image = Image.open(filepath).convert("RGB")
        except (UnidentifiedImageError, OSError):
            return jsonify({
                "success": False,
                "error_title": "Corrupt Image",
                "message": "The uploaded file could not be decoded as a valid image."
            }), 400

        # Canine Presence Validation Gate
        is_dog, _ = validate_dog_presence(pil_image)
        if not is_dog:
            return jsonify({
                "success": False,
                "is_dog": False,
                "dog_detected": False,
                "message": "No dog detected",
                "details": "No dog detected. Please upload or capture a clear image of a dog."
            }), 200

        # ResNet18 Disease Classification Inference
        input_tensor = cast(torch.Tensor, disease_transform(pil_image)).unsqueeze(0).to(device)

        with torch.no_grad():
            logits = disease_model(input_tensor)
            probs = F.softmax(logits, dim=1)[0]

        probs_list = probs.cpu().tolist()

        # Highest probability prediction
        top_prob, top_idx = torch.max(probs, 0)
        top_prob_pct = round(top_prob.item() * 100, 2)
        top_class_key = CLASSES[int(top_idx.item())]
        top_friendly_name = FRIENDLY_NAMES[top_class_key]

        # Formulate probabilities in canonical order and sorted order
        canonical_breakdown = []
        for i, ckey in enumerate(CLASSES):
            pct = round(probs_list[i] * 100, 2)
            canonical_breakdown.append({
                "class_index": i,
                "class_key": ckey,
                "friendly_name": FRIENDLY_NAMES[ckey],
                "probability_pct": pct
            })

        sorted_breakdown = sorted(canonical_breakdown, key=lambda x: x["probability_pct"], reverse=True)

        # Uncertainty Evaluation (< 50% or narrow top-2 separation)
        top1_pct = sorted_breakdown[0]["probability_pct"]
        top2_pct = sorted_breakdown[1]["probability_pct"] if len(sorted_breakdown) > 1 else 0.0

        is_uncertain = False
        uncertainty_message = ""
        if top1_pct < 50.0 or (top1_pct - top2_pct) < 14.0:
            is_uncertain = True
            uncertainty_message = (
                "Low-confidence result. The image may not clearly match the conditions "
                "represented in the training data. Please upload a clearer image or consult a veterinarian."
            )

        # ---------------------------------------------------------------------
        # Feature 1: Explainable AI with Grad-CAM (Target Layer: model.layer4[-1])
        # ---------------------------------------------------------------------
        gradcam_res = None
        gradcam_available = False
        gradcam_error = ""
        try:
            gradcam_res = generate_gradcam(
                model=disease_model,
                pil_image=pil_image,
                target_class=int(top_idx.item()),
                device=device
            )
            if gradcam_res is not None and "overlay_pil" in gradcam_res:
                gradcam_available = True
            else:
                gradcam_error = "AI explanation is temporarily unavailable, but the prediction result is still available."
        except Exception as cam_err:  # noqa: BLE001
            logger.warning(f"Grad-CAM generation failed gracefully: {cam_err}")
            gradcam_available = False
            gradcam_error = "AI explanation is temporarily unavailable, but the prediction result is still available."

        # ---------------------------------------------------------------------
        # Feature: Detailed Canine Dermatological Analysis via Grok AI
        # ---------------------------------------------------------------------
        grok_analysis = analyze_canine_condition_with_grok(
            pil_image=pil_image,
            predicted_class_key=top_class_key,
            predicted_friendly_name=top_friendly_name,
            confidence_pct=top_prob_pct
        )

        # Cache session data for dynamic PDF health report and image downloads
        analysis_id = uuid.uuid4().hex
        cleanup_expired_analyses()

        orig_base64 = pil_to_base64(pil_image)
        gradcam_base64 = gradcam_res["overlay_base64"] if (gradcam_res and gradcam_available) else None

        prediction_payload = {
            "analysis_id": analysis_id,
            "predicted_condition": top_class_key,
            "predicted_friendly_name": top_friendly_name,
            "confidence_pct": top_prob_pct,
            "is_uncertain": is_uncertain,
            "uncertainty_message": uncertainty_message,
            "classes_breakdown": sorted_breakdown,
            "clinical_info": DISEASE_INFO[top_class_key],
            "detailed_analysis": grok_analysis,
            "specific_disease": grok_analysis.get("specific_disease"),
            "ai_analysis": grok_analysis.get("ai_analysis"),
            "symptoms": grok_analysis.get("symptoms"),
            "precautions": grok_analysis.get("precautions"),
            "recommended_care": grok_analysis.get("recommended_care"),
            "when_to_see_vet": grok_analysis.get("when_to_see_vet"),
            "analysis_source": grok_analysis.get("source"),
            "disclaimer": MANDATORY_DISCLAIMER
        }

        with analyses_lock:
            ACTIVE_ANALYSES[analysis_id] = {
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "prediction_data": prediction_payload,
                "original_pil": pil_image.copy(),
                "gradcam_pil": gradcam_res["overlay_pil"].copy() if (gradcam_res and gradcam_available) else None,
                "gradcam_available": gradcam_available
            }

        return jsonify({
            "success": True,
            "is_dog": True,
            "dog_detected": True,
            "dog_status_text": "Dog detected ✓",
            "analysis_id": analysis_id,
            "predicted_class": top_class_key,
            "predicted_friendly_name": top_friendly_name,
            "confidence_pct": top_prob_pct,
            "is_uncertain": is_uncertain,
            "uncertainty_message": uncertainty_message,
            "classes_breakdown": canonical_breakdown,
            "sorted_breakdown": sorted_breakdown,
            "disease_info": DISEASE_INFO[top_class_key],
            "detailed_analysis": grok_analysis,
            "specific_disease": grok_analysis.get("specific_disease"),
            "ai_analysis": grok_analysis.get("ai_analysis"),
            "symptoms": grok_analysis.get("symptoms"),
            "precautions": grok_analysis.get("precautions"),
            "recommended_care": grok_analysis.get("recommended_care"),
            "when_to_see_vet": grok_analysis.get("when_to_see_vet"),
            "analysis_source": grok_analysis.get("source"),
            "disclaimer": MANDATORY_DISCLAIMER,
            "gradcam_available": gradcam_available,
            "gradcam_error": gradcam_error,
            "gradcam_image": gradcam_base64,
            "original_image": orig_base64
        }), 200

    except Exception:
        logger.exception("Inference error occurred")
        return jsonify({
            "success": False,
            "error_title": "Server Error",
            "message": "An error occurred during prediction analysis. Please try again."
        }), 500

    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

# -----------------------------------------------------------------------------
# Routes - Feature 2: PDF AI Health Report & Grad-CAM Download
# -----------------------------------------------------------------------------
@app.route("/download-report", methods=["GET", "POST"])
def download_report():
    """
    Dynamically generates and downloads the official PawCare AI PDF Health Report.
    Accepts GET with ?id=<analysis_id> or POST with JSON payload.
    """
    analysis_id = None
    json_payload = None
    lang = "en"

    if request.method == "POST":
        if request.is_json:
            json_payload = request.get_json() or {}
            analysis_id = json_payload.get("analysis_id")
            lang = json_payload.get("lang", "en")
        else:
            analysis_id = request.form.get("analysis_id")
            lang = request.form.get("lang", "en")
    else:
        analysis_id = request.args.get("id")
        lang = request.args.get("lang", "en")

    if lang not in ["en", "te", "hi"]:
        lang = "en"

    record = None
    if analysis_id:
        with analyses_lock:
            record = ACTIVE_ANALYSES.get(analysis_id)

    if record:
        pred_data = record["prediction_data"]
        orig_img = record.get("original_pil")
        gradcam_img = record.get("gradcam_pil")
    elif json_payload:
        pred_data = json_payload
        orig_img = None
        gradcam_img = None
        if json_payload.get("original_image"):
            with contextlib.suppress(Exception):
                raw_orig = base64.b64decode(json_payload["original_image"].split(",")[-1])
                orig_img = Image.open(io.BytesIO(raw_orig)).convert("RGB")
        if json_payload.get("gradcam_image"):
            with contextlib.suppress(Exception):
                raw_cam = base64.b64decode(json_payload["gradcam_image"].split(",")[-1])
                gradcam_img = Image.open(io.BytesIO(raw_cam)).convert("RGB")
    else:
        return jsonify({
            "success": False,
            "error_title": "Report Not Found",
            "message": "The requested analysis report has expired or does not exist. Please run an image screening first."
        }), 404

    try:
        pdf_bytes = generate_health_report(
            prediction_data=pred_data,
            original_pil=orig_img,
            gradcam_pil=gradcam_img,
            lang=lang
        )
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
        filename = f"PawCare_AI_Health_Report_{lang.upper()}_{timestamp_str}.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )
    except Exception:
        logger.exception("Error generating PDF health report")
        return jsonify({
            "success": False,
            "error_title": "Generation Failed",
            "message": "Failed to create PDF health report. Please try again."
        }), 500

@app.route("/download-gradcam", methods=["GET"])
def download_gradcam():
    """Downloads the generated Grad-CAM explanation image for a given analysis ID."""
    analysis_id = request.args.get("id")
    if not analysis_id:
        return jsonify({"error": "Missing analysis ID."}), 400

    with analyses_lock:
        record = ACTIVE_ANALYSES.get(analysis_id)

    if not record or not record.get("gradcam_pil"):
        return jsonify({
            "error": "Grad-CAM explanation visualization is not available or has expired."
        }), 404

    img_io = io.BytesIO()
    record["gradcam_pil"].save(img_io, format="JPEG", quality=95)
    img_io.seek(0)

    timestamp_str = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    return send_file(
        img_io,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name=f"PawCare_AI_GradCAM_{timestamp_str}.jpg"
    )

# -----------------------------------------------------------------------------
# Routes - Dataset Upload, Validation & Optional Training
# -----------------------------------------------------------------------------
@app.route("/upload-dataset", methods=["POST"])
def upload_dataset():
    """Uploads a dataset ZIP file securely to the dataset directory."""
    if "dataset" not in request.files:
        return jsonify({"success": False, "message": "No file part in upload request."}), 400

    file = request.files["dataset"]
    if not file.filename:
        return jsonify({"success": False, "message": "No file was selected."}), 400

    if not file.filename.lower().endswith(".zip"):
        return jsonify({"success": False, "message": "Invalid file format. Please upload a .zip archive."}), 400

    try:
        filename = secure_filename(file.filename)
        dest_path = os.path.join(app.config["DATASET_FOLDER"], filename)
        file.save(dest_path)
        file_size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)

        return jsonify({
            "success": True,
            "message": "Dataset ZIP uploaded successfully.",
            "filename": filename,
            "file_size_mb": file_size_mb,
            "path": dest_path
        }), 200
    except Exception as e:
        logger.exception("Dataset upload error")
        return jsonify({"success": False, "message": f"Failed to save uploaded file: {e}"}), 500

@app.route("/validate-dataset", methods=["POST"])
def validate_dataset():
    """
    Safely inspects and extracts the dataset ZIP:
    1. Checks for path traversal and security issues.
    2. Identifies class folders and images.
    3. Counts images per class and returns summary statistics.
    """
    data = request.get_json(silent=True) or request.form
    filename = data.get("filename")

    if not filename:
        # Check if file sent directly in request
        if "dataset" in request.files:
            file = request.files["dataset"]
            if not file.filename or not file.filename.lower().endswith(".zip"):
                return jsonify({"success": False, "message": "Uploaded file must be a .zip file."}), 400
            filename = secure_filename(file.filename)
            dest_path = os.path.join(app.config["DATASET_FOLDER"], filename)
            file.save(dest_path)
        else:
            return jsonify({"success": False, "message": "No dataset file specified for validation."}), 400
    else:
        dest_path = os.path.join(app.config["DATASET_FOLDER"], secure_filename(filename))

    if not os.path.exists(dest_path):
        return jsonify({"success": False, "message": "Specified dataset file does not exist on server."}), 404

    try:
        extract_dir = os.path.join(app.config["DATASET_FOLDER"], "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        class_counts = {cls_name: 0 for cls_name in CLASSES}
        total_images = 0

        with zipfile.ZipFile(dest_path, "r") as z:
            # Security: Path traversal verification
            for member in z.namelist():
                norm = os.path.normpath(member)
                if norm.startswith("..") or os.path.isabs(norm):
                    return jsonify({
                        "success": False,
                        "message": f"Security alert: Malicious path traversal detected in archive member: {member}"
                    }), 400

            # Safe extraction of allowed image files only
            for member in z.infolist():
                if member.is_dir():
                    continue

                filename_part = os.path.basename(member.filename)
                ext = filename_part.rsplit(".", 1)[-1].lower() if "." in filename_part else ""
                if ext not in ALLOWED_IMAGE_EXTENSIONS:
                    continue

                # Identify class from path parts
                parts = member.filename.strip("/").split("/")
                matched_class = None
                for part in parts[:-1]:
                    if part in CLASSES:
                        matched_class = part
                        break

                if matched_class:
                    class_counts[matched_class] += 1
                    total_images += 1
                    # Extract securely
                    target_class_dir = os.path.join(extract_dir, matched_class)
                    os.makedirs(target_class_dir, exist_ok=True)
                    target_file = os.path.join(target_class_dir, filename_part)
                    with z.open(member) as source, open(target_file, "wb") as target:
                        target.write(source.read())

        summary = {
            "Healthy": class_counts.get("Healthy", 0),
            "Hypersensitivity_allergic_dermatosis": class_counts.get("Hypersensitivity_allergic_dermatosis", 0),
            "Fungal_infections": class_counts.get("Fungal_infections", 0),
            "Bacterial_dermatosis": class_counts.get("Bacterial_dermatosis", 0),
            "Total": total_images
        }

        # Check for missing classes
        missing_classes = [c for c, count in class_counts.items() if count == 0]
        if missing_classes:
            return jsonify({
                "success": False,
                "message": f"Dataset validation failed: The following class folders have 0 images: {', '.join(missing_classes)}",
                "summary": summary
            }), 400

        return jsonify({
            "success": True,
            "message": "Dataset successfully validated and extracted.",
            "summary": summary,
            "extract_dir": extract_dir
        }), 200

    except zipfile.BadZipFile:
        return jsonify({"success": False, "message": "Corrupted or invalid ZIP archive."}), 400
    except Exception as e:
        logger.exception("Dataset validation error")
        return jsonify({"success": False, "message": f"Validation error: {e}"}), 500

@app.route("/start-training", methods=["POST"])
def start_training():
    """
    Initiates model training ONLY upon explicit user request.
    Executes in a background thread and updates training_state.
    Checkpoints are saved to models/dog_disease_resnet18_v2.pth.
    """
    from train_model import train_dog_disease_model

    extract_dir = os.path.join(app.config["DATASET_FOLDER"], "extracted")
    if not os.path.exists(extract_dir) or len(os.listdir(extract_dir)) == 0:
        return jsonify({
            "success": False,
            "message": "No validated dataset found. Please upload and validate a dataset first."
        }), 400

    with training_lock:
        if training_state["status"] == "training":
            return jsonify({
                "success": False,
                "message": "A training session is already currently in progress."
            }), 409

        training_state["status"] = "training"
        training_state["epoch"] = 0
        training_state["train_loss"] = 0.0
        training_state["train_acc"] = 0.0
        training_state["val_loss"] = 0.0
        training_state["val_acc"] = 0.0
        training_state["best_val_acc"] = 0.0
        training_state["logs"] = ["Training session initialized..."]
        training_state["message"] = "Training started in background..."

    def run_training_worker():
        try:
            train_dog_disease_model(
                dataset_dir=extract_dir,
                epochs=15,
                batch_size=16,
                learning_rate=0.0001,
                output_path=os.path.join(app.config["MODELS_FOLDER"], "dog_disease_resnet18_v2.pth"),
                progress_callback=update_training_callback
            )
        except Exception as e:
            logger.exception("Background training execution failed")
            with training_lock:
                training_state["status"] = "error"
                training_state["message"] = f"Training encountered an error: {e}"
                training_state["logs"].append(f"ERROR: {e}")

    worker_thread = threading.Thread(target=run_training_worker, daemon=True)
    worker_thread.start()

    return jsonify({
        "success": True,
        "message": "Training started successfully. Monitor progress on the dashboard."
    }), 200

@app.route("/training-status", methods=["GET"])
def get_training_status():
    """Returns current live progress and metrics of the training process."""
    with training_lock:
        return jsonify(training_state), 200

# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error_title": "File Too Large",
        "message": "The uploaded payload exceeds the maximum allowed file size limit."
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Requested resource not found."
    }), 404



#============================================================
#chatbot
#============================================================
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# ============================================================
# COMMUNITY
# ============================================================

app.register_blueprint(
    community_bp
)

app.register_blueprint(
    comment_bp
)

app.register_blueprint(
    community_api
)

if __name__ == "__main__":
    import socket

    def is_port_in_use(p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", p)) == 0

    port = 5001 if is_port_in_use(5000) else 5000
    while is_port_in_use(port):
        port += 1

    logger.info(f"Starting PawCare AI Web Application on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
