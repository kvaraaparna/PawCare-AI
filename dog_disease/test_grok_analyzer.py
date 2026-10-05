"""
PawCare AI – Grok AI Clinical Analysis Verification Suite
==========================================================
Automated test suite verifying:
1. utils.grok_analyzer standalone execution and fallback logic.
2. Return of all 7 clinical analysis items:
   - 1. Predicted condition/category
   - 2. Possible specific disease name
   - 3. AI analysis/explanation
   - 4. Symptoms or visible signs
   - 5. Precautions
   - 6. Recommended Care
   - 7. When to consult a veterinarian
3. Flask /predict integration with real sample canine images.
4. Professional PDF health report generation with detailed diagnosis and care.
"""

import io
import json
import os
import sys
from PIL import Image

from app import app
from utils.grok_analyzer import (
    analyze_canine_condition_with_grok,
    CLINICAL_KNOWLEDGE_BASE
)
from utils.pdf_report import generate_health_report


def run_grok_tests():
    print("=" * 70)
    print("RUNNING GROK AI CLINICAL ANALYSIS VERIFICATION SUITE")
    print("=" * 70)

    # TEST 1: Clinical Knowledge Base Completeness
    print("\n--- TEST 1: Clinical Knowledge Base Completeness ---")
    required_classes = [
        "Bacterial_dermatosis",
        "Fungal_infections",
        "Healthy",
        "Hypersensitivity_allergic_dermatosis"
    ]
    for ckey in required_classes:
        assert ckey in CLINICAL_KNOWLEDGE_BASE, f"Missing {ckey} in knowledge base"
        kb = CLINICAL_KNOWLEDGE_BASE[ckey]
        assert kb.get("specific_disease"), f"Missing specific_disease in {ckey}"
        assert kb.get("ai_analysis"), f"Missing ai_analysis in {ckey}"
        assert len(kb.get("symptoms", [])) >= 3, f"Symptoms too short in {ckey}"
        assert len(kb.get("precautions", [])) >= 3, f"Precautions too short in {ckey}"
        assert len(kb.get("recommended_care", [])) >= 3, f"Recommended care too short in {ckey}"
        assert len(kb.get("when_to_see_vet", [])) >= 3, f"When to see vet too short in {ckey}"
        print(f"✓ {ckey}: specific_disease = '{kb['specific_disease']}'")
    print("✓ All 4 core categories have complete 7-point clinical data.")

    # TEST 2: Standalone analyze_canine_condition_with_grok Execution
    print("\n--- TEST 2: Standalone Grok Analyzer Fallback Execution ---")
    test_img = Image.new("RGB", (256, 256), color=(180, 120, 80))
    res = analyze_canine_condition_with_grok(
        pil_image=test_img,
        predicted_class_key="Bacterial_dermatosis",
        predicted_friendly_name="Bacterial Dermatosis",
        confidence_pct=94.2
    )
    assert res["predicted_category"] == "Bacterial Dermatosis"
    assert res["confidence_pct"] == 94.2
    assert "Canine Superficial" in res["specific_disease"]
    assert len(res["symptoms"]) >= 3
    assert len(res["precautions"]) >= 3
    assert len(res["recommended_care"]) >= 3
    assert len(res["when_to_see_vet"]) >= 3
    print(f"✓ Standalone execution returned source: {res.get('source')}")
    print(f"✓ Specific Disease: {res.get('specific_disease')}")
    print(f"✓ Symptoms ({len(res['symptoms'])} items): {res['symptoms'][0]}")
    print(f"✓ Precautions ({len(res['precautions'])} items): {res['precautions'][0]}")
    print(f"✓ Recommended Care ({len(res['recommended_care'])} items): {res['recommended_care'][0]}")
    print(f"✓ When to See Vet ({len(res['when_to_see_vet'])} items): {res['when_to_see_vet'][0]}")

    # TEST 3: Full /predict Endpoint with Sample Image
    print("\n--- TEST 3: Flask /predict Endpoint Integration ---")
    client = app.test_client()
    sample_path = os.path.join(os.path.dirname(__file__), "static", "samples", "bacterial.jpg")

    if not os.path.exists(sample_path):
        # Create a test jpeg if static sample doesn't exist
        buf = io.BytesIO()
        test_img.save(buf, format="JPEG")
        sample_bytes = buf.getvalue()
    else:
        with open(sample_path, "rb") as f:
            sample_bytes = f.read()

    data = {
        "image": (io.BytesIO(sample_bytes), "sample_test.jpg")
    }
    pred_res = client.post("/predict", data=data, content_type="multipart/form-data")
    assert pred_res.status_code == 200, f"Expected 200, got {pred_res.status_code}"
    res_json = pred_res.get_json()

    assert res_json["success"] is True, "Expected success=True"
    assert res_json["is_dog"] is True, "Expected is_dog=True"
    print(f"✓ Model Primary Prediction: {res_json.get('predicted_friendly_name')} ({res_json.get('confidence_pct')}%)")

    # Verify all 7 user-requested items
    assert "predicted_friendly_name" in res_json, "Missing 1. Predicted condition/category"
    assert "specific_disease" in res_json and res_json["specific_disease"], "Missing 2. Possible specific disease name"
    assert "ai_analysis" in res_json and res_json["ai_analysis"], "Missing 3. AI analysis/explanation"
    assert "symptoms" in res_json and len(res_json["symptoms"]) > 0, "Missing 4. Symptoms or visible signs"
    assert "precautions" in res_json and len(res_json["precautions"]) > 0, "Missing 5. Precautions"
    assert "recommended_care" in res_json and len(res_json["recommended_care"]) > 0, "Missing 6. Recommended Care"
    assert "when_to_see_vet" in res_json and len(res_json["when_to_see_vet"]) > 0, "Missing 7. When to consult a veterinarian"

    print("✓ 1. Predicted category:", res_json["predicted_friendly_name"])
    print("✓ 2. Specific disease:", res_json["specific_disease"])
    print("✓ 3. AI analysis:", res_json["ai_analysis"][:65] + "...")
    print("✓ 4. Symptoms count:", len(res_json["symptoms"]))
    print("✓ 5. Precautions count:", len(res_json["precautions"]))
    print("✓ 6. Recommended care count:", len(res_json["recommended_care"]))
    print("✓ 7. When to see vet count:", len(res_json["when_to_see_vet"]))
    print("✓ Analysis Source:", res_json.get("analysis_source"))

    # TEST 4: PDF Health Report Generation with Detailed Diagnosis
    print("\n--- TEST 4: PDF Health Report Generation with Detailed Diagnosis ---")
    pdf_bytes = generate_health_report(
        prediction_data=res_json,
        original_pil=test_img,
        gradcam_pil=test_img,
        lang="en"
    )
    assert len(pdf_bytes) > 1000, f"Generated PDF too small: {len(pdf_bytes)} bytes"
    assert pdf_bytes.startswith(b"%PDF"), "Generated file does not start with PDF magic bytes"
    print(f"✓ PDF successfully compiled ({len(pdf_bytes)} bytes) with detailed Grok sections!")

    print("\n" + "=" * 70)
    print("ALL 4 GROK AI VERIFICATION SUITE TESTS PASSED 100%!")
    print("=" * 70)


if __name__ == "__main__":
    run_grok_tests()
