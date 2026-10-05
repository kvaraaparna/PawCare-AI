"""
PawCare AI - Automated Test Suite
=================================
Verifies all 8 required test scenarios:
  TEST 1: Healthy dog image -> Prediction works & probabilities returned.
  TEST 2: Dog skin disease image -> Prediction works & condition returned.
  TEST 3: Close-up dog ear/skin image -> Canine validator accepts it.
  TEST 4: Non-dog wallpaper/artwork -> Validator rejects with polite advisory.
  TEST 5: Invalid image / Corrupt file -> Friendly error (HTTP 400).
  TEST 6: Empty upload -> Friendly error (HTTP 400).
  TEST 7: Dataset ZIP -> Validation accurately counts all 4 classes:
          Healthy=119, Hypersensitivity=89, Fungal=137, Bacterial=97, Total=442.
  TEST 8: Start Training -> Initiates training only on explicit request.
"""

import io
import os
import zipfile

from app import CLASSES, app

client = app.test_client()

def test_case_1_healthy_dog():
    print("\n--- TEST 1: Healthy Dog Image (Prediction + Grad-CAM + PDF) ---")
    with open("static/samples/healthy.jpg", "rb") as f:
        res = client.post("/predict", data={"image": (f, "healthy.jpg")}, content_type="multipart/form-data")
    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert data["success"] is True, "Expected success=True"
    assert data["is_dog"] is True, "Expected is_dog=True"
    assert "predicted_friendly_name" in data
    assert "confidence_pct" in data
    assert len(data["classes_breakdown"]) == 4

    # Verify Grad-CAM
    assert data.get("gradcam_available") is True, "Expected Grad-CAM to be available"
    assert data.get("gradcam_image", "").startswith("data:image/jpeg;base64,"), "Invalid Grad-CAM base64"
    assert data.get("original_image", "").startswith("data:image/jpeg;base64,"), "Invalid original base64"
    assert "analysis_id" in data, "Expected analysis_id in response"
    print(f"Result: {data['predicted_friendly_name']} ({data['confidence_pct']}%)")
    print(f"Grad-CAM generated successfully (analysis_id={data['analysis_id'][:8]}...)")

    # Verify PDF Download for healthy dog
    pdf_res = client.get(f"/download-report?id={data['analysis_id']}")
    assert pdf_res.status_code == 200, f"PDF download failed: {pdf_res.status_code}"
    assert pdf_res.content_type == "application/pdf"
    assert pdf_res.data.startswith(b"%PDF-"), "Generated file does not have valid PDF header"
    assert len(pdf_res.data) > 3000, "PDF size suspiciously small"
    print(f"PDF Report generated successfully ({len(pdf_res.data)} bytes)")
    print(">>> TEST 1 PASSED: Healthy dog prediction, Grad-CAM, and PDF verified!")

def test_case_2_dog_skin_disease():
    print("\n--- TEST 2: Dog Skin Disease Image (Prediction + Grad-CAM + PDF) ---")
    with open("static/samples/bacterial.jpg", "rb") as f:
        res = client.post("/predict", data={"image": (f, "bacterial.jpg")}, content_type="multipart/form-data")
    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert data["success"] is True
    assert data["is_dog"] is True
    assert data["predicted_class"] in CLASSES
    assert "disease_info" in data
    assert "signs" in data["disease_info"]

    # Verify Grad-CAM
    assert data.get("gradcam_available") is True
    assert len(data.get("gradcam_image", "")) > 1000
    print(f"Result: {data['predicted_friendly_name']} ({data['confidence_pct']}%)")
    print("Grad-CAM visualization generated for predicted condition.")

    # Verify PDF Download via POST with JSON
    pdf_res = client.post("/download-report", json=data)
    assert pdf_res.status_code == 200
    assert pdf_res.content_type == "application/pdf"
    assert pdf_res.data.startswith(b"%PDF-")
    print(f"PDF Report generated via POST ({len(pdf_res.data)} bytes)")

    # Verify direct Grad-CAM image download
    cam_res = client.get(f"/download-gradcam?id={data['analysis_id']}")
    assert cam_res.status_code == 200
    assert cam_res.content_type == "image/jpeg"
    assert len(cam_res.data) > 1000
    print(f"Direct Grad-CAM image downloaded successfully ({len(cam_res.data)} bytes)")
    print(">>> TEST 2 PASSED: Disease prediction, Grad-CAM, and PDF report verified!")

def test_case_3_close_up_skin_ear():
    print("\n--- TEST 3: Close-Up Dog Ear / Skin Image ---")
    with open("static/samples/fungal.jpg", "rb") as f:
        res = client.post("/predict", data={"image": (f, "fungal_close_up.jpg")}, content_type="multipart/form-data")
    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    assert res.status_code == 200
    assert data["is_dog"] is True, "Canine validator should accept close-up skin lesion"
    assert data.get("gradcam_available") is True, "Grad-CAM should generate for close-up lesion"
    print(f"Result: Canine accepted, predicted {data['predicted_friendly_name']} ({data['confidence_pct']}%)")
    print(">>> TEST 3 PASSED: Close-up lesion verified as canine with Grad-CAM!")

def test_case_4_non_dog_rejection():
    print("\n--- TEST 4: Non-Dog Wallpaper / Artwork ---")
    with open("static/samples/nondog.jpg", "rb") as f:
        res = client.post("/predict", data={"image": (f, "wallpaper.jpg")}, content_type="multipart/form-data")
    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    print("Response message:", data.get("message"))
    print("Response details:", data.get("details"))
    assert res.status_code == 200
    assert data["is_dog"] is False, "Expected is_dog=False for non-dog image"
    assert "No dog detected" in data["message"]
    assert "Unable to confidently verify this as a dog image" in data["details"]
    assert "gradcam_image" not in data or data.get("gradcam_image") is None
    print(">>> TEST 4 PASSED: Non-dog image properly rejected by validator without disease inference!")

def test_case_5_invalid_image():
    print("\n--- TEST 5: Invalid / Corrupt Image ---")
    res = client.post(
        "/predict",
        data={"image": (io.BytesIO(b"corrupt non-image byte stream"), "sample.png")},
        content_type="multipart/form-data"
    )
    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    print("Response:", data)
    assert res.status_code == 400
    assert data["success"] is False
    assert "Corrupt Image" in data["error_title"] or "supported" in data["message"]
    print(">>> TEST 5 PASSED: Corrupted image rejected with friendly HTTP 400!")

def test_case_6_empty_upload():
    print("\n--- TEST 6: Empty Upload (No File Selected) ---")
    res = client.post(
        "/predict",
        data={"image": (io.BytesIO(b""), "")},
        content_type="multipart/form-data"
    )
    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    print("Response:", data)
    assert res.status_code == 400
    assert data["success"] is False
    assert "No File Selected" in data["error_title"] or "select" in data["message"]
    print(">>> TEST 6 PASSED: Empty upload handled gracefully!")

def test_case_7_dataset_zip_validation():
    print("\n--- TEST 7: Dataset ZIP Validation (442 Images) ---")
    zip_path = "/Users/apple/Downloads/Dog.zip"
    if not os.path.exists(zip_path):
        print("Creating mock zip matching dataset structure for testing...")
        # If Dog.zip is unavailable in some environment, create test archive
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for cls_name, count in [("Healthy", 119), ("Hypersensitivity_allergic_dermatosis", 89), ("Fungal_infections", 137), ("Bacterial_dermatosis", 97)]:
                for i in range(count):
                    z.writestr(f"Dogs/{cls_name}/img_{i}.jpg", b"\xff\xd8\xff\xe0mockjpeg")
        buf.seek(0)
        res = client.post("/validate-dataset", data={"dataset": (buf, "dog_dataset.zip")}, content_type="multipart/form-data")
    else:
        with open(zip_path, "rb") as f:
            res = client.post("/validate-dataset", data={"dataset": (f, "Dog.zip")}, content_type="multipart/form-data")

    print(f"Status Code: {res.status_code}")
    data = res.get_json()
    print("Summary Output:", data.get("summary"))
    assert res.status_code == 200
    assert data["success"] is True
    summary = data["summary"]
    assert summary["Healthy"] == 119, f"Expected 119, got {summary['Healthy']}"
    assert summary["Hypersensitivity_allergic_dermatosis"] == 89, f"Expected 89, got {summary['Hypersensitivity_allergic_dermatosis']}"
    assert summary["Fungal_infections"] == 137, f"Expected 137, got {summary['Fungal_infections']}"
    assert summary["Bacterial_dermatosis"] == 97, f"Expected 97, got {summary['Bacterial_dermatosis']}"
    assert summary["Total"] == 442, f"Expected 442, got {summary['Total']}"
    print(">>> TEST 7 PASSED: Dataset ZIP validated with exact 442 image count across 4 classes!")

def test_case_8_start_training_explicit():
    print("\n--- TEST 8: Explicit Start Training Trigger ---")
    # Status before starting
    status_res = client.get("/training-status")
    status_data = status_res.get_json()
    print("Initial Training Status:", status_data["status"])
    assert status_data["status"] in ["idle", "completed"]

    # Start training trigger
    start_res = client.post("/start-training")
    start_data = start_res.get_json()
    print("Start Training Response:", start_data)
    assert start_res.status_code == 200
    assert start_data["success"] is True

    # Immediate status check
    status_res_after = client.get("/training-status")
    status_data_after = status_res_after.get_json()
    print("Training Status After Explicit Trigger:", status_data_after["status"])
    assert status_data_after["status"] in ["training", "completed"]
    print(">>> TEST 8 PASSED: Training starts only after explicit user POST invocation!")

def test_case_9_multilingual_reports():
    print("\n--- TEST 9: Multi-Language PDF Report Generation (EN, TE, HI) ---")
    with open("static/samples/healthy.jpg", "rb") as f:
        res = client.post("/predict", data={"image": (f, "healthy.jpg")}, content_type="multipart/form-data")
    assert res.status_code == 200
    data = res.get_json()
    analysis_id = data["analysis_id"]

    # 1. English PDF
    en_res = client.get(f"/download-report?id={analysis_id}&lang=en")
    assert en_res.status_code == 200, f"EN PDF failed: {en_res.status_code}"
    assert en_res.data.startswith(b"%PDF-"), "Invalid EN PDF header"
    print(f"English PDF Report verified ({len(en_res.data)} bytes)")

    # 2. Telugu PDF
    te_res = client.get(f"/download-report?id={analysis_id}&lang=te")
    assert te_res.status_code == 200, f"Telugu PDF failed: {te_res.status_code}"
    assert te_res.data.startswith(b"%PDF-"), "Invalid Telugu PDF header"
    print(f"Telugu PDF Report (తెలుగు) verified ({len(te_res.data)} bytes)")

    # 3. Hindi PDF
    hi_res = client.get(f"/download-report?id={analysis_id}&lang=hi")
    assert hi_res.status_code == 200, f"Hindi PDF failed: {hi_res.status_code}"
    assert hi_res.data.startswith(b"%PDF-"), "Invalid Hindi PDF header"
    print(f"Hindi PDF Report (हिन्दी) verified ({len(hi_res.data)} bytes)")

    print(">>> TEST 9 PASSED: All 3 language reports (EN, TE, HI) generated successfully!")

if __name__ == "__main__":
    print("=========================================================")
    print("RUNNING PAWCARE AI COMPLETE 9-TEST VERIFICATION SUITE")
    print("=========================================================")
    test_case_1_healthy_dog()
    test_case_2_dog_skin_disease()
    test_case_3_close_up_skin_ear()
    test_case_4_non_dog_rejection()
    test_case_5_invalid_image()
    test_case_6_empty_upload()
    test_case_7_dataset_zip_validation()
    test_case_8_start_training_explicit()
    test_case_9_multilingual_reports()
    print("\n=========================================================")
    print("ALL 9 TEST CASES COMPLETED AND PASSED SUCCESSFULLY!")
    print("=========================================================")
