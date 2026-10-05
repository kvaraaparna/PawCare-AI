# PawCare AI – Dog Skin Disease Detection

[![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2.2-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org)
[![Torchvision](https://img.shields.io/badge/Torchvision-0.17.2-EE4C2C)](https://pytorch.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Test Accuracy](https://img.shields.io/badge/Test%20Accuracy-76.06%25-success)](https://github.com)

**PawCare AI** is an AI-powered canine dermatological screening and educational web application developed as an engineering capstone / college project. The platform connects a modern, responsive web frontend with a PyTorch deep learning backend running a transfer-learned ResNet-18 model to screen canine photographs for four primary dermatological categories.

---

> [!IMPORTANT]
> **Academic & Medical Disclaimer:**  
> This application is strictly an educational tool and AI screening aid. **It does not provide certified veterinary diagnoses.** Dermatological abnormalities require in-person clinical examination, skin cytology, and culture diagnostics by a licensed veterinary doctor.

---

## 1. Key Features

- **PawCare AI Visual Identity:** Styled with a green aesthetic, responsive navbar, hero cards, 4-step workflow, and accessibility across desktop, tablet, and mobile.
- **Multilingual Support (EN / TE / HI):** Full website and PDF report translation across English, తెలుగు (Telugu), and हिन्दी (Hindi), preserving veterinary precision, tensor probabilities, and user language preference via `localStorage`.
- **Pretrained Disease Classification Model:** Evaluates images using the trained PyTorch `best_dog_disease_resnet18.pth` model weights.
- **Explainable AI with Grad-CAM:** Visualizes model attention on `model.layer4[-1]` using Jet heatmap overlays to explain which image regions drove the prediction.
- **Downloadable PDF Health Reports:** Generates professional, branded veterinary screening reports in English, Telugu, or Hindi with complete probability tables, side-by-side images, and care guidance using ReportLab.
- **ImageNet Canine Presence Validator:** Filters out non-dog imagery (landscapes, vehicles, household items, text) while accepting full-body dogs, facial profiles, canine ears, and close-up skin lesions.
- **Dynamic Probability Breakdown:** Renders animated probability distributions across all 4 canonical disease classes.
- **Uncertainty Flagging:** Identifies ambiguous images (confidence < 50% or narrow margin) and alerts the user to consult a veterinary professional.
- **Educational Clinical Insights:** Visible signs and care recommendations for each disease category.
- **Isolated Dataset Training Pipeline:** Complete dataset upload, safe ZIP inspection (preventing path traversal), class count validation, and optional background model retraining with live training dashboard.

---

## 2. Model Architecture

The disease classification model is based on **Torchvision ResNet-18**:
- **Base Architecture:** ResNet-18 (512-dimensional penultimate feature representation).
- **Classification Head:** Linear layer mapping 512 features to 4 output logits:
  ```python
  model.fc = nn.Linear(model.fc.in_features, 4)
  ```
- **Inference Preprocessing (Standardized):**
  1. Image loading & RGB conversion.
  2. Resize to $224 \times 224$ pixels.
  3. Conversion to PyTorch Tensor.
  4. Standard ImageNet Normalization:
     $$\text{mean} = [0.485, 0.456, 0.406], \quad \text{std} = [0.229, 0.224, 0.225]$$
- **Inference Mode:** Runs with `model.eval()` and `torch.no_grad()`.
- **Model Checkpoint:** `best_dog_disease_resnet18.pth` (~44.8 MB).

---

## 3. Canonical Class Ordering

The model output strictly adheres to the following index ordering:

| Index | Canonical Class Key | Friendly Display Name |
|:---:|:---|:---|
| **0** | `Bacterial_dermatosis` | **Bacterial Dermatosis** |
| **1** | `Fungal_infections` | **Fungal Infection** |
| **2** | `Healthy` | **Healthy** |
| **3** | `Hypersensitivity_allergic_dermatosis` | **Allergic Dermatosis (Hypersensitivity)** |

> [!NOTE]
> **Performance Benchmark:**  
> The model achieved **Test Accuracy = 76.06%** on our held-out validation dataset. Real-world performance may vary depending on camera quality, lighting, and fur coverage.

---

## 4. Dataset Overview

The training dataset contains **442 curated canine dermatological images** distributed as follows:

| Disease Class | Image Count | Description |
|:---|:---:|:---|
| **Healthy** | 119 | Intact epidermal barrier, even hair coat, no collarettes |
| **Fungal Infections** | 137 | Circular alopecia rings, crusting, scaling dermatophytes |
| **Bacterial Dermatosis** | 97 | Pyoderma, pustules, epidermal collarettes, inflammation |
| **Hypersensitivity Allergic Dermatosis** | 89 | Pruritus, atopic dermatitis, erythema, salivary staining |
| **Total Images** | **442** | Photographic samples standardized to $224 \times 224$ |

---

## 5. Project Directory Structure

```
dog_disease/
├── app.py                         # Main Flask web application & API routes
├── train_model.py                 # ResNet-18 training script (CLI & background worker)
├── run.sh                         # Quick launcher script using .venv
├── test_cases.py                  # Automated test suite (8 test cases)
├── requirements.txt               # Python package dependencies
├── README.md                      # Comprehensive project documentation
├── .gitignore                     # Git ignore rules
│
├── utils/
│   ├── gradcam.py                 # Grad-CAM Explainable AI generator for ResNet-18
│   └── pdf_report.py              # ReportLab PDF health report generator
│
├── models/                        # Checkpoints for newly trained models
├── dataset/                       # Staging directory for validated training datasets
├── uploads/                       # Temporary scratch space for image evaluation
│
├── templates/
│   ├── index.html                 # PawCare AI Homepage (reference UI design)
│   ├── detect.html                # Disease detection & screening interface
│   └── training.html              # Dataset upload, validation & training dashboard
│
└── static/
    ├── css/
    │   └── style.css              # Unified PawCare AI stylesheet with Telugu & Devanagari web fonts
    ├── js/
    │   ├── translations.js        # Multilingual translation dictionary & controller (EN, TE, HI)
    │   └── script.js              # Client-side preview, prediction, dynamic translation, and training logic
    ├── images/
    │   └── hero-dog.jpg           # Hero canine photograph
    └── samples/                   # 5 demo test images for live testing
        ├── healthy.jpg
        ├── bacterial.jpg
        ├── fungal.jpg
        ├── allergic.jpg
        └── nondog.jpg
```

---

## 6. Advanced Features

### Feature 1: Explainable AI with Grad-CAM

Gradient-weighted Class Activation Mapping (**Grad-CAM**) provides visual explanations for decisions made by convolutional neural networks.

- **Why It Is Used:** Deep neural networks are complex feature extractors whose internal representations are not inherently interpretable. Grad-CAM makes the model transparent by calculating gradients of the target class score with respect to the feature maps of the final convolutional block.
- **Target Layer:** ResNet-18 `model.layer4[-1]` (the last residual BasicBlock before average pooling and classification).
- **Mathematical Principle:**
  $$\alpha_k = \frac{1}{Z} \sum_i \sum_j \frac{\partial y^c}{\partial A^k_{i,j}}$$
  $$L^c_{\text{Grad-CAM}} = \text{ReLU}\left( \sum_k \alpha_k A^k \right)$$
- **What the Visualization Means:**
  - The activation map is normalized $[0, 1]$, upsampled to the original image dimensions, and colormapped using a Jet color spectrum.
  - **Red / Yellow highlights:** Regions of the photograph that contributed most strongly toward the predicted disease classification.
  - **Blue / Cyan regions:** Image regions that had negligible influence on the model's decision.
- **Critical Limitation:**
  > [!WARNING]
  > **Grad-CAM highlights visual feature importance, NOT clinical proof.**  
  > Wording used: *"Highlighted regions show areas that contributed strongly to the model's prediction."*  
  > It does **not** prove that a disease is present or that a specific area is definitively infected.

### Feature 2: Downloadable PDF AI Health Report

PawCare AI includes one-click PDF generation powered by **ReportLab**:

- **How to Generate:** After uploading and analyzing an image on `/detect`, click the **Download PDF Report** button. The server dynamically compiles the current screening into a PDF without saving temporary files.
- **What Is Included in the Report:**
  1. **PawCare AI Branding:** Clean forest-green header and typography.
  2. **Analysis Date & Time:** Live timestamp and analysis reference identifier.
  3. **Screening Summary Card:** Primary predicted condition and AI confidence percentage.
  4. **4-Class Probability Breakdown:** Table of all 4 disease classes and their exact percentage metrics.
  5. **Visual Comparison & Grad-CAM Explanation:** Side-by-side presentation of the uploaded dog image and the Grad-CAM heatmap overlay.
  6. **Educational Information:** Disease signs and symptoms.
  7. **Veterinary Care Guidance:** Recommended clinical follow-ups.
  8. **Mandatory Veterinary Disclaimer:** Prominent warning that AI screening does not replace licensed veterinary evaluation.

### Feature 3: Multi-Language Support (English, Telugu, Hindi)

PawCare AI features native, self-contained multi-language capabilities without reliance on external cloud APIs or third-party scripts:

- **Supported Languages:**
  - **English (`en`)**: Default international interface.
  - **తెలుగు (`te`)**: Complete Telugu localization with authentic regional veterinary terminology.
  - **हिन्दी (`hi`)**: Complete Hindi localization in clean Devanagari script.
- **Navbar Language Dropdown:**
  - Placed persistently in the top navigation bar across all pages as a single **`Language ▾`** button.
  - Clicking **Language** smoothly opens a dropdown menu displaying the 3 options: `English`, `తెలుగు (Telugu)`, and `हिन्दी (Hindi)`.
  - The active language is highlighted with an emerald checkmark.
  - Remembers user selection across page navigations using browser `localStorage`.
- **Dynamic Live Translation (No Re-upload Needed):**
  - Instant DOM updates across navbar, hero banners, feature cards, buttons, error messages, and 4-step workflow via `data-i18n` attributes.
  - If a user changes language *after* running an analysis, the condition badge, 4-class probability breakdown, visible signs, recommendations, and disclaimer update immediately without re-analyzing the image.
- **Strict Integrity Rules:**
  - **Unmodified Predictions:** Raw AI prediction classes, tensor values, and confidence percentages remain strictly identical across all languages.
  - **Accurate Veterinary Terminology:** Disease class names are accurately localized with clinical accuracy (e.g., `బాక్టీరియల్ డెర్మటోసిస్ (చర్మ వ్యాధి)` in Telugu and `बैक्टीरियल डर्मेटोसिस (त्वचा संक्रमण)` in Hindi) rather than literal machine translation.
- **Multilingual PDF Reports:**
  - When requesting a PDF health report, the client passes the active language (`en`, `te`, or `hi`).
  - ReportLab dynamically renders the report using macOS system Unicode fonts (`Telugu MN.ttc` for Telugu and `DevanagariMT.ttc` for Hindi) with graceful Helvetica fallbacks.
  - Localized filenames are delivered: `PawCare_AI_Health_Report_{LANG}_{TIMESTAMP}.pdf`.

---

## 7. Installation & Setup

### Prerequisites
- Python 3.9, 3.10, or 3.11
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/pawcare-ai.git
cd pawcare-ai
```

### Step 2: Create and Activate a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate       # On Linux / macOS
# .venv\Scripts\activate        # On Windows
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Ensure Production Model Weights are Placed
Verify that `best_dog_disease_resnet18.pth` is in the project root:
```bash
ls -lh best_dog_disease_resnet18.pth
```
*(The file size is ~44.8 MB and does not exceed GitHub's 100 MB commit limit.)*

---

## 8. Running the Application

Start the Flask development server using either the quick launcher or Python:
```bash
./run.sh
# or
./.venv/bin/python app.py
```

The terminal will display the active URL:
```
[2026-09-10 15:30:00] INFO in PawCareAI: Starting PawCare AI Web Application on http://127.0.0.1:5001
```

Open your browser and navigate to:
```
http://127.0.0.1:5001
```

---

## 9. Usage Guide

### A. Disease Detection & Explainable AI (`/detect`)
1. Click **Get Started** or **Detect Disease** in the top navigation.
2. Drag & drop a dog photo, click **Choose Image**, or click any of the **Quick Demo Test Samples** (`Healthy Dog`, `Bacterial Lesion`, `Fungal Infection`, `Allergic Dermatosis`, `Non-Dog Reject Test`).
3. Click **Analyze Image**.
4. The canine presence validator verifies the image is a dog or skin lesion.
5. If verified, the ResNet-18 model predicts the condition, displays animated probability distributions, visible clinical signs, and veterinary guidance.
6. Click **View AI Explanation** to smoothly reveal the side-by-side **Original Image** and **AI Attention / Grad-CAM** heatmap cards.
7. Click **Download Explanation Image** to save the Grad-CAM visualization.
8. Click **Download PDF Report** to generate and download the comprehensive official PawCare AI clinical health report.

### B. Dataset Upload, Validation & Model Training (`/training`)
1. Navigate to **Training** in the top navigation bar.
2. Select or drop a dataset archive (`.zip`) containing the 4 disease class folders.
3. Click **Validate Dataset**. The server safely validates path traversal, checks image formats, and displays the exact image counts for all 4 classes.
4. When validation passes, the **START TRAINING** button activates.
5. Click **START TRAINING** to initiate a 15-epoch training session in the background with live epoch metric updates and streaming console logs.
6. The newly trained model is saved safely to `models/dog_disease_resnet18_v2.pth` without overwriting the production model.

---

## 10. Automated Testing

To run the automated verification suite covering all 9 test cases:
```bash
./.venv/bin/python test_cases.py
```

The test suite validates:
1. Full-body healthy dog image prediction + Grad-CAM heatmap + PDF health report generation.
2. Canine dermatological lesion prediction + Grad-CAM matching + PDF health report + direct image download.
3. Close-up skin lesion acceptance by canine presence validator + Grad-CAM explainability.
4. Rejection of non-dog wallpapers/artwork without disease model or Grad-CAM invocation.
5. Graceful handling of corrupted/invalid files (HTTP 400).
6. Graceful handling of empty uploads (HTTP 400).
7. ZIP dataset validation confirming 442 images across the 4 canonical classes.
8. Explicit start-training safety trigger.
9. Multilingual PDF report generation (English, Telugu `te`, Hindi `hi`) with Unicode font registration and integrity checks.

---

## 11. GitHub Collaboration Guidelines

1. **Commit Rules:**
   - Commit code, templates, styles, and documentation.
   - Do **NOT** commit temporary upload caches (`uploads/`), extracted datasets (`dataset/`), or virtual environments (`.venv/`).
   - Keep `best_dog_disease_resnet18.pth` tracked as the baseline production model.
2. **Branching Strategy:**
   - Work in feature branches (`git checkout -b feature/your-feature`).
   - Create Pull Requests into `main` after verifying with `python test_cases.py`.

---

## 12. Veterinary Notice & Disclaimer

PawCare AI is built as an educational demonstration of applied deep transfer learning in veterinary medicine. It is not an FDA/USDA-cleared diagnostic device. Always seek direct consultation with a qualified veterinarian for diagnosis, medical tests, and treatments.
