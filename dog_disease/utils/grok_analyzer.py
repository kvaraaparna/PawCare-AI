"""
PawCare AI – Grok & Groq API Canine Dermatological Analyzer
============================================================
Integrates AI LLM/Vision APIs to provide in-depth, 7-point clinical veterinary
analysis of dog skin conditions:

1. Predicted condition/category (Core ResNet-18 classification)
2. Possible specific disease name
3. AI analysis/explanation
4. Symptoms or visible signs
5. Precautions
6. Recommended care
7. When to consult a veterinarian

Supports BOTH:
- GroqCloud API keys (starts with 'gsk_', endpoint: https://api.groq.com/openai/v1/chat/completions)
- xAI Grok API keys (starts with 'xai-', endpoint: https://api.x.ai/v1/chat/completions)

Includes dynamic .env reloading so key changes take effect immediately,
plus a robust clinical veterinary fallback engine.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional
from PIL import Image
from dotenv import load_dotenv

logger = logging.getLogger("PawCareAI.GrokAnalyzer")

# Browser-grade User-Agent to avoid Cloudflare 403 blocks
REQUEST_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 PawCareAI/2026"
)

# -----------------------------------------------------------------------------
# Comprehensive Clinical Fallback Database
# -----------------------------------------------------------------------------
CLINICAL_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "Bacterial_dermatosis": {
        "specific_disease": "Canine Superficial Bacterial Pyoderma (Hot Spot / Acute Moist Dermatitis)",
        "ai_analysis": (
            "Dermatological examination reveals localized erythema, epidermal disruption, and signs "
            "of secondary bacterial colonization commonly caused by Staphylococcus pseudintermedius. "
            "The lesion displays active folliculitis, epidermal collarettes, and crusting consistent "
            "with superficial bacterial pyoderma, often triggered by underlying moisture, flea bites, or micro-trauma."
        ),
        "symptoms": [
            "Erythematous papules, pustules, and inflamed skin patches",
            "Circular epidermal collarettes with peeling crusts and scabs",
            "Hair loss (alopecia) centered around affected hair follicles",
            "Localized skin warmth, tenderness, and moderate-to-severe pruritus (itching)"
        ],
        "precautions": [
            "Fit an Elizabethan collar (e-collar) immediately to prevent continuous licking and mechanical self-trauma",
            "Isolate the dog from other household pets if purulent or weeping discharge is present",
            "Wash hands thoroughly with soap and water after handling or touching affected areas",
            "Do not apply human corticosteroid or antibiotic ointments without explicit veterinary direction"
        ],
        "recommended_care": [
            "Gently clip surrounding matted fur to allow the lesion to aerate, dry, and heal",
            "Cleanse the area twice daily with a veterinary antiseptic wash containing 2%-4% chlorhexidine",
            "Keep the pet's environment clean, cool, and change bedding every 48 hours to minimize bacterial load",
            "Apply cool, clean saline compresses for 5-10 minutes to soothe active burning sensation"
        ],
        "when_to_see_vet": [
            "Lesion rapidly enlarges or develops foul-smelling, yellow/green purulent discharge",
            "The dog develops systemic signs such as fever, lethargy, or complete loss of appetite",
            "The area becomes extremely painful or hot to the touch, causing vocalization or guarding",
            "No visible improvement or drying is noted after 48-72 hours of gentle topical cleansing"
        ]
    },
    "Fungal_infections": {
        "specific_disease": "Dermatophytosis (Ringworm) & Malassezia Dermatitis (Yeast Overgrowth)",
        "ai_analysis": (
            "The screened region exhibits characteristic annular or irregular patches of alopecia, "
            "accompanied by scaling epidermal borders, hyperpigmentation, and mild lichenification. "
            "These visual hallmarks are typical of fungal dermatophytes (Microsporum canis / Trichophyton) "
            "or opportunistic Malassezia pachydermatis yeast proliferation, often exacerbated by humidity or skin folds."
        ),
        "symptoms": [
            "Circular or patchy areas of hair loss (classic ringworm pattern) with broken hair shafts",
            "Dry, flaky, crusty epidermal scaling or greasy sebum buildup",
            "Darkened, thickened skin (hyperpigmentation/elephant skin) in chronic areas",
            "Characteristic musty or pungent odor, accompanied by face-rubbing and ear scratching"
        ],
        "precautions": [
            "Isolate the dog from young children, immunocompromised individuals, and other pets (dermatophytes are zoonotic)",
            "Wear disposable gloves when examining or administering topical treatments to the skin",
            "Disinfect pet living areas, bedding, and grooming tools thoroughly with bleach-water or veterinary disinfectant",
            "Never share brushes, towels, or clippers between multiple household animals"
        ],
        "recommended_care": [
            "Bathe dog twice weekly with a veterinary antifungal shampoo containing miconazole and chlorhexidine or ketoconazole",
            "Leave the shampoo lather in contact with the skin for 10 full minutes before thoroughly rinsing",
            "Towel dry completely after bathing; avoid hot blow dryers which aggravate fungal irritation",
            "Clean and vacuum dog resting areas and furniture daily to capture infectious fungal spores"
        ],
        "when_to_see_vet": [
            "Lesions multiply or spread across the face, paws, tail, or abdominal region",
            "Human family members or other pets in the home develop circular red, itchy ring-shaped skin lesions",
            "Secondary bacterial weeping or severe deep follicular swelling (kerion) develops",
            "Prescription oral antifungal therapy (e.g. itraconazole or terbinafine) is required for deep systemic eradication"
        ]
    },
    "Healthy": {
        "specific_disease": "Intact Epidermal Barrier & Normal Canine Coat",
        "ai_analysis": (
            "Visual examination demonstrates physiological epidermal integrity without detectable inflammatory "
            "erythema, pustular lesions, alopecia patches, or crusting. Hair follicles appear evenly distributed, "
            "and the cutaneous barrier displays uniform pigmentation, healthy dermal elasticity, and balanced natural sebum."
        ),
        "symptoms": [
            "Smooth, supple skin with normal elasticity and absence of active redness",
            "Glossy, uniform hair coat density without patchy loss or brittle breakage",
            "Absence of excoriations, weeping lesions, swellings, or foul odors",
            "Normal pet demeanor without obsessive licking, scratching, or discomfort"
        ],
        "precautions": [
            "Maintain consistent year-round parasite prevention (fleas, ticks, and mites)",
            "Avoid over-bathing with harsh or human shampoos which strip natural protective epidermal oils",
            "Perform weekly coat brushing to remove loose undercoat and stimulate cutaneous capillary circulation",
            "Inspect paws, ears, and belly after outdoor walks, hikes, or swimming"
        ],
        "recommended_care": [
            "Use a gentle, pH-balanced oatmeal or hypoallergenic dog shampoo once every 3-4 weeks as needed",
            "Provide a nutritious diet containing balanced Omega-3 (EPA/DHA) and Omega-6 fatty acids for skin hydration",
            "Ensure constant access to fresh, clean drinking water to maintain cellular hydration",
            "Schedule regular routine annual or semi-annual veterinary wellness examinations"
        ],
        "when_to_see_vet": [
            "Any sudden onset of localized redness, hives, swelling, or unexplained bald spots",
            "Behavioral shifts including excessive paw-chewing, head-shaking, or floor-scooting",
            "Noticeable changes in coat texture, heavy dandruff, or persistent oily greasiness",
            "Any new cutaneous lumps, skin tags, or rapidly changing pigmented spots"
        ]
    },
    "Hypersensitivity_allergic_dermatosis": {
        "specific_disease": "Canine Atopic Dermatitis & Flea Allergy Dermatitis (FAD)",
        "ai_analysis": (
            "The image reveals diffuse cutaneous erythema, follicular irritation, and characteristic salivary "
            "fur staining from persistent compulsive self-grooming. This visual pattern represents allergic hypersensitivity—an "
            "immunological overreaction to environmental airborne allergens (pollens, molds, dust mites), flea saliva antigens, "
            "or dietary proteins."
        ),
        "symptoms": [
            "Intense, persistent pruritus (obsessive paw-licking, belly-scratching, and face-rubbing)",
            "Diffuse erythema (redness) around the muzzle, ear flaps, paws, groin, and ventral abdomen",
            "Rusty-brown saliva staining on light-colored fur from chronic licking and gnawing",
            "Recurrent secondary yeast or bacterial flare-ups in moist interdigital spaces or skin folds"
        ],
        "precautions": [
            "Enforce strict year-round veterinary-grade flea and tick prevention on all household pets",
            "Wipe paws and ventral abdomen with a damp cloth or hypoallergenic wipe after outdoor grass walks",
            "Use an Elizabethan collar or breathable recovery suit during acute itch crises to avoid self-mutilation",
            "Do not abruptly introduce new proteins or treats if a food trial is being conducted"
        ],
        "recommended_care": [
            "Soothe acute itching with cool-water soaks or colloidal oatmeal veterinary baths",
            "Supplement the diet with veterinary-approved Omega-3 marine oils to reinforce the skin's lipid barrier",
            "Wash all dog bedding weekly in hot water using hypoallergenic, perfume-free laundry detergents",
            "Use indoor HEPA air filtration to minimize airborne pollen and house dust mite concentrations"
        ],
        "when_to_see_vet": [
            "Severe itching is relentless, preventing normal rest, sleep, or daily activities",
            "Skin breaks open, bleeds, or develops hot, weeping secondary bacterial infections (pyoderma)",
            "Ears become red, swollen, painful to touch, or produce dark waxy discharge with head shaking",
            "Targeted allergy therapies (such as Apoquel, Cytopoint, or allergen-specific immunotherapy) are indicated"
        ]
    }
}


def _get_api_config() -> tuple[Optional[str], Optional[str], Optional[str], bool, str]:
    """
    Dynamically loads .env and returns:
    (api_key, endpoint, model, is_vision, display_source_name)
    """
    load_dotenv(override=True)
    raw_key = os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("XAI_API_KEY")
    if not raw_key:
        return None, None, None, False, "Fallback"

    key = raw_key.strip()
    if not key or key == "your_grok_api_key_here" or "your_api_key" in key.lower():
        return None, None, None, False, "Fallback"

    # Auto-detect Provider
    if key.startswith("gsk_"):
        # GroqCloud Provider (https://console.groq.com)
        endpoint = "https://api.groq.com/openai/v1/chat/completions"
        model = os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
        return key, endpoint, model, False, f"Groq AI ({model.split('/')[-1]})"

    # Default to xAI Grok (https://console.x.ai)
    endpoint = "https://api.x.ai/v1/chat/completions"
    model = os.getenv("GROK_MODEL") or "grok-2-vision-1212"
    return key, endpoint, model, True, f"Grok AI ({model})"


def _pil_to_base64_jpeg(pil_image: Image.Image, max_dim: int = 768) -> str:
    """Resize image to reasonable dimension and encode as base64 JPEG."""
    img = pil_image.copy().convert("RGB")
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _get_fallback_analysis(
    predicted_class: str,
    friendly_name: str,
    confidence_pct: float
) -> Dict[str, Any]:
    """Return comprehensive, clinically accurate veterinary breakdown."""
    base_data = CLINICAL_KNOWLEDGE_BASE.get(
        predicted_class,
        CLINICAL_KNOWLEDGE_BASE["Healthy"]
    )
    return {
        "source": "PawCare AI Clinical Knowledge Engine",
        "predicted_category": friendly_name,
        "confidence_pct": confidence_pct,
        "specific_disease": base_data["specific_disease"],
        "ai_analysis": base_data["ai_analysis"],
        "symptoms": list(base_data["symptoms"]),
        "precautions": list(base_data["precautions"]),
        "recommended_care": list(base_data["recommended_care"]),
        "when_to_see_vet": list(base_data["when_to_see_vet"])
    }


def analyze_canine_condition_with_grok(
    pil_image: Image.Image,
    predicted_class_key: str,
    predicted_friendly_name: str,
    confidence_pct: float,
    timeout_seconds: float = 12.0
) -> Dict[str, Any]:
    """
    Analyzes canine dermatological condition using Groq or xAI Grok API.
    If API key is unset, invalid, or request fails, gracefully falls back
    to curated clinical veterinary database.
    """
    api_key, endpoint, model, is_vision, provider_label = _get_api_config()

    if not api_key:
        logger.info("No API key configured in .env. Utilizing PawCare AI clinical fallback engine.")
        return _get_fallback_analysis(predicted_class_key, predicted_friendly_name, confidence_pct)

    logger.info(f"Invoking {provider_label} via {endpoint}...")

    prompt_text = (
        f"You are a board-certified veterinary dermatologist analyzing a canine skin lesion. "
        f"Our ResNet-18 neural classifier categorized this condition as: '{predicted_friendly_name}' "
        f"with {confidence_pct}% model confidence.\n\n"
        f"Please provide an authoritative clinical dermatological evaluation. "
        f"You must return ONLY a strictly valid JSON object (no markdown wrapping, no backticks, no thought tags) "
        f"with these exact 6 keys:\n"
        f"{{\n"
        f'  "specific_disease": "Specific canine clinical condition name (e.g. Canine Superficial Bacterial Pyoderma, Acute Moist Dermatitis (Hot Spot), Dermatophytosis (Ringworm), Malassezia Dermatitis, Canine Atopic Dermatitis, Flea Allergy Dermatitis)",\n'
        f'  "ai_analysis": "2-3 professional sentences explaining visual features (erythema, collarettes, pustules, alopecia) and underlying etiology.",\n'
        f'  "symptoms": ["Visible sign 1", "Visible sign 2", "Visible sign 3", "Visible sign 4"],\n'
        f'  "precautions": ["Precaution 1 (e.g. cone/e-collar, hygiene)", "Precaution 2", "Precaution 3"],\n'
        f'  "recommended_care": ["Care step 1 (e.g. antiseptic wash, bathing)", "Care step 2", "Care step 3"],\n'
        f'  "when_to_see_vet": ["Emergency red flag 1", "Red flag 2", "Red flag 3"]\n'
        f"}}\n"
        f"Ensure maximum medical accuracy for canines. If healthy, reflect normal canine skin anatomy."
    )

    try:
        if is_vision:
            base64_img = _pil_to_base64_jpeg(pil_image)
            user_content = [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_img}"
                    }
                }
            ]
        else:
            user_content = prompt_text

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a board-certified veterinary dermatologist AI assistant for PawCare AI. "
                    "You must output strictly a raw JSON object with no preamble, reasoning, or markdown fences."
                )
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1000
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": REQUEST_USER_AGENT
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            resp_body = response.read().decode("utf-8")
            resp_json = json.loads(resp_body)

        content_str = resp_json["choices"][0]["message"]["content"].strip()

        # Robust JSON extraction via regex (handles markdown fences or extra reasoning text)
        json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object structure found in response content")

        parsed = json.loads(json_match.group(0))

        # Validate required keys
        required_keys = ["specific_disease", "ai_analysis", "symptoms", "precautions", "recommended_care", "when_to_see_vet"]
        for k in required_keys:
            if k not in parsed or not parsed[k]:
                raise ValueError(f"Missing or empty key '{k}' in model output")

        logger.info(f"Successfully retrieved specific disease: '{parsed['specific_disease']}' from {provider_label}")
        return {
            "source": provider_label,
            "predicted_category": predicted_friendly_name,
            "confidence_pct": confidence_pct,
            "specific_disease": str(parsed["specific_disease"]),
            "ai_analysis": str(parsed["ai_analysis"]),
            "symptoms": list(parsed["symptoms"]),
            "precautions": list(parsed["precautions"]),
            "recommended_care": list(parsed["recommended_care"]),
            "when_to_see_vet": list(parsed["when_to_see_vet"])
        }

    except Exception as exc:
        logger.warning(f"AI API call failed ({exc}); falling back gracefully to clinical knowledge base.")
        return _get_fallback_analysis(predicted_class_key, predicted_friendly_name, confidence_pct)
