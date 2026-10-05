/**
 * PawCare AI – Frontend Application Logic
 * ========================================
 * Handles interactive file drag-and-drop, preview rendering,
 * one-click demo samples, asynchronous disease screening inference,
 * animated probability displays, dataset validation, and training monitoring.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Initialize multilingual language selector
    if (typeof initLanguageSelector === "function") {
        initLanguageSelector();
    }

    // Determine current page context
    initDetectionPage();
    initTrainingPage();
});

/* ==========================================================================
   1. DETECTION & PREDICTION LOGIC
   ========================================================================== */
function initDetectionPage() {
    const dropzone = document.getElementById("uploadDropzone");
    const fileInput = document.getElementById("imageInput");
    const previewCard = document.getElementById("previewCard");
    const previewThumb = document.getElementById("previewThumb");
    const previewName = document.getElementById("previewName");
    const previewSize = document.getElementById("previewSize");
    const removeBtn = document.getElementById("removeBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const loadingBox = document.getElementById("loadingBox");
    const resultCard = document.getElementById("resultCard");
    const rejectionCard = document.getElementById("rejectionCard");
    const retryBtn = document.getElementById("retryBtn");

    // Dual Input Mode Elements
    const modeUploadBtn = document.getElementById("modeUploadBtn");
    const modeCameraBtn = document.getElementById("modeCameraBtn");
    const cameraContainer = document.getElementById("cameraContainer");
    const cameraVideo = document.getElementById("cameraVideo");
    const capturePhotoBtn = document.getElementById("capturePhotoBtn");
    const flipCameraBtn = document.getElementById("flipCameraBtn");
    const closeCameraBtn = document.getElementById("closeCameraBtn");
    const cameraNotice = document.getElementById("cameraNotice");
    const cameraNoticeText = document.getElementById("cameraNoticeText");
    const dogVerifiedBanner = document.getElementById("dogVerifiedBanner");
    const dogVerifiedText = document.getElementById("dogVerifiedText");
    const initialGuideState = document.getElementById("initialGuideState");

    if (!dropzone || !fileInput) return;

    let currentSelectedFile = null;
    let activeCameraStream = null;
    let currentFacingMode = "environment"; // default to rear camera on mobile

    // Helper: format file size
    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
    }

    // Process Selected File
    function handleFileSelection(file) {
        if (!file) return;

        const allowedExtensions = ["jpg", "jpeg", "png", "webp"];
        const ext = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(ext)) {
            alert("Unsupported File Format: Please upload a JPG, JPEG, PNG, or WEBP image.");
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            alert("File Too Large: Please select an image under 16MB.");
            return;
        }

        currentSelectedFile = file;

        // Render preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewThumb.src = e.target.result;
            previewName.textContent = file.name;
            previewSize.textContent = formatBytes(file.size);
            previewCard.style.display = "block";
            dropzone.style.display = "none";
            if (cameraContainer) cameraContainer.style.display = "none";
            resultCard.style.display = "none";
            rejectionCard.style.display = "none";
            if (dogVerifiedBanner) dogVerifiedBanner.style.display = "none";
            if (initialGuideState) initialGuideState.style.display = "block";
        };
        reader.readAsDataURL(file);
    }

    // Drag and Drop Events
    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("dragover");
        });
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    dropzone.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            handleFileSelection(fileInput.files[0]);
        }
    });

    // Camera Lifecycle Management
    async function startCamera(facingMode = currentFacingMode) {
        currentFacingMode = facingMode;
        if (cameraNotice) cameraNotice.style.display = "none";
        if (capturePhotoBtn) capturePhotoBtn.disabled = true;

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            if (cameraNotice && cameraNoticeText) {
                cameraNoticeText.textContent = "Camera access is not supported by your browser or environment (requires HTTPS or localhost). Please use the Upload Image option.";
                cameraNotice.style.display = "flex";
            }
            return;
        }

        stopCamera();

        try {
            const constraints = {
                video: {
                    facingMode: { ideal: currentFacingMode },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            activeCameraStream = stream;

            if (cameraVideo) {
                cameraVideo.srcObject = stream;
                cameraVideo.onloadedmetadata = () => {
                    cameraVideo.play().catch((err) => console.warn("Autoplay error:", err));
                    if (capturePhotoBtn) capturePhotoBtn.disabled = false;
                };
            }
        } catch (err) {
            console.error("Camera access error:", err);
            let msg = "Could not access camera. Please allow camera permissions in your browser settings, or use the Upload Image option.";
            if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
                msg = "Camera permission was denied. Please allow camera access in your browser settings to scan with your camera.";
            } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
                msg = "No camera found on your device. Please use the Upload Image option.";
            }
            if (cameraNotice && cameraNoticeText) {
                cameraNoticeText.textContent = msg;
                cameraNotice.style.display = "flex";
            }
            if (capturePhotoBtn) capturePhotoBtn.disabled = true;
        }
    }

    function stopCamera() {
        if (activeCameraStream) {
            activeCameraStream.getTracks().forEach((track) => {
                try {
                    track.stop();
                } catch (e) {
                    console.warn("Track stop error:", e);
                }
            });
            activeCameraStream = null;
        }
        if (cameraVideo) {
            cameraVideo.srcObject = null;
        }
    }

    function capturePhoto() {
        if (!cameraVideo || !activeCameraStream) return;

        const videoWidth = cameraVideo.videoWidth || 640;
        const videoHeight = cameraVideo.videoHeight || 480;

        const canvas = document.createElement("canvas");
        canvas.width = videoWidth;
        canvas.height = videoHeight;
        const ctx = canvas.getContext("2d");

        ctx.drawImage(cameraVideo, 0, 0, videoWidth, videoHeight);

        canvas.toBlob((blob) => {
            if (!blob) {
                alert("Failed to capture photo frame. Please try again.");
                return;
            }

            const fileName = `pawcare_scan_${Date.now()}.jpg`;
            const capturedFile = new File([blob], fileName, { type: "image/jpeg" });

            stopCamera();

            // Switch UI state to show captured preview
            if (cameraContainer) cameraContainer.style.display = "none";
            if (modeUploadBtn) modeUploadBtn.classList.add("active");
            if (modeCameraBtn) modeCameraBtn.classList.remove("active");

            handleFileSelection(capturedFile);
        }, "image/jpeg", 0.95);
    }

    // Input Mode Switching
    if (modeUploadBtn) {
        modeUploadBtn.addEventListener("click", () => {
            stopCamera();
            modeUploadBtn.classList.add("active");
            if (modeCameraBtn) modeCameraBtn.classList.remove("active");
            if (cameraContainer) cameraContainer.style.display = "none";

            if (currentSelectedFile) {
                previewCard.style.display = "block";
                dropzone.style.display = "none";
            } else {
                dropzone.style.display = "block";
                previewCard.style.display = "none";
            }
        });
    }

    if (modeCameraBtn) {
        modeCameraBtn.addEventListener("click", () => {
            modeCameraBtn.classList.add("active");
            if (modeUploadBtn) modeUploadBtn.classList.remove("active");
            dropzone.style.display = "none";
            previewCard.style.display = "none";
            if (cameraContainer) cameraContainer.style.display = "block";
            startCamera();
        });
    }

    if (capturePhotoBtn) {
        capturePhotoBtn.addEventListener("click", capturePhoto);
    }

    if (flipCameraBtn) {
        flipCameraBtn.addEventListener("click", () => {
            currentFacingMode = (currentFacingMode === "environment") ? "user" : "environment";
            startCamera(currentFacingMode);
        });
    }

    if (closeCameraBtn) {
        closeCameraBtn.addEventListener("click", () => {
            stopCamera();
            if (modeUploadBtn) modeUploadBtn.classList.add("active");
            if (modeCameraBtn) modeCameraBtn.classList.remove("active");
            if (cameraContainer) cameraContainer.style.display = "none";
            if (currentSelectedFile) {
                previewCard.style.display = "block";
            } else {
                dropzone.style.display = "block";
            }
        });
    }

    // Stop camera if user navigates away
    window.addEventListener("beforeunload", () => {
        stopCamera();
    });

    // Remove Selected Image
    function clearSelection() {
        stopCamera();
        currentSelectedFile = null;
        fileInput.value = "";
        previewCard.style.display = "none";
        if (cameraContainer) cameraContainer.style.display = "none";
        dropzone.style.display = "block";
        if (modeUploadBtn) modeUploadBtn.classList.add("active");
        if (modeCameraBtn) modeCameraBtn.classList.remove("active");

        resultCard.style.display = "none";
        rejectionCard.style.display = "none";
        if (dogVerifiedBanner) dogVerifiedBanner.style.display = "none";
        if (initialGuideState) initialGuideState.style.display = "block";

        const explanationSection = document.getElementById("explanationSection");
        const viewAiExplanationBtn = document.getElementById("viewAiExplanationBtn");
        if (explanationSection) explanationSection.style.display = "none";
        if (viewAiExplanationBtn) {
            viewAiExplanationBtn.innerHTML = '<i class="fa-solid fa-brain"></i> View AI Explanation';
            viewAiExplanationBtn.classList.remove("active");
        }
    }

    if (removeBtn) removeBtn.addEventListener("click", clearSelection);
    if (retryBtn) retryBtn.addEventListener("click", clearSelection);

    // One-Click Demo Sample Chips
    const sampleChips = document.querySelectorAll(".sample-chip");
    sampleChips.forEach((chip) => {
        chip.addEventListener("click", async () => {
            const sampleUrl = chip.getAttribute("data-sample");
            const sampleName = chip.getAttribute("data-name");
            if (!sampleUrl) return;

            try {
                chip.style.opacity = "0.6";
                const response = await fetch(sampleUrl);
                if (!response.ok) throw new Error("Could not load sample image");
                const blob = await response.blob();
                const file = new File([blob], sampleName, { type: blob.type || "image/jpeg" });
                handleFileSelection(file);
            } catch (err) {
                console.error("Error loading sample:", err);
                alert("Failed to load sample image. Please try uploading a file directly.");
            } finally {
                chip.style.opacity = "1";
            }
        });
    });

    // Analyze Image Submission
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async () => {
            if (!currentSelectedFile) {
                alert("Please select or drop an image first.");
                return;
            }

            // UI state transition
            previewCard.style.display = "none";
            if (cameraContainer) cameraContainer.style.display = "none";
            loadingBox.style.display = "block";
            resultCard.style.display = "none";
            rejectionCard.style.display = "none";
            if (initialGuideState) initialGuideState.style.display = "none";
            if (dogVerifiedBanner) dogVerifiedBanner.style.display = "none";

            const formData = new FormData();
            formData.append("image", currentSelectedFile);

            try {
                const res = await fetch("/predict", {
                    method: "POST",
                    body: formData
                });

                const data = await res.json();
                loadingBox.style.display = "none";

                if (res.status === 400 || res.status === 500) {
                    alert(data.message || "An error occurred while evaluating the image.");
                    previewCard.style.display = "block";
                    return;
                }

                // Case 1: Non-Dog Rejection Gate (Image -> Dog Scanner -> Rejection)
                if (data.is_dog === false) {
                    rejectionCard.style.display = "block";
                    if (dogVerifiedBanner) dogVerifiedBanner.style.display = "none";
                    if (initialGuideState) initialGuideState.style.display = "none";
                    const rejectionReasonEl = document.getElementById("rejectionReason");
                    if (rejectionReasonEl) {
                        rejectionReasonEl.textContent =
                            data.details || (typeof t === "function" ? t("detect.rejection_desc") : "No dog detected. Please upload or capture a clear image of a dog.");
                    }
                    rejectionCard.scrollIntoView({ behavior: "smooth", block: "start" });
                    return;
                }

                // Case 2: Canine Accepted & Disease Inferred (Image -> Dog Scanner -> Disease Analysis)
                if (data.success === true && data.is_dog === true) {
                    if (dogVerifiedBanner) {
                        dogVerifiedBanner.style.display = "flex";
                        if (dogVerifiedText) {
                            dogVerifiedText.textContent = typeof t === "function"
                                ? t("detect.dog_verified", "Dog detected ✓")
                                : "Dog detected ✓";
                        }
                    }
                    if (initialGuideState) initialGuideState.style.display = "none";
                    renderPredictionResults(data);
                    resultCard.style.display = "block";
                    // Scroll smoothly to results
                    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
                }

            } catch (err) {
                loadingBox.style.display = "none";
                previewCard.style.display = "block";
                console.error("Prediction fetch error:", err);
                alert("Failed to reach the prediction server. Please make sure the Flask application is running.");
            }
        });
    }

    let latestPredictionData = null;

    // Listen for language switch events to instantly update live results if open
    window.addEventListener("pawcare_language_changed", () => {
        if (latestPredictionData && resultCard && resultCard.style.display !== "none") {
            renderPredictionResults(latestPredictionData);
        }
    });

    function renderPredictionResults(data) {
        latestPredictionData = data;

        if (dogVerifiedText) {
            dogVerifiedText.textContent = typeof t === "function"
                ? t("detect.dog_verified", "Dog detected ✓")
                : "Dog detected ✓";
        }

        const condTitle = document.getElementById("conditionTitle");
        const condBadge = document.getElementById("conditionBadge");
        const confValue = document.getElementById("confidenceValue");
        const uncertaintyBox = document.getElementById("uncertaintyBox");
        const uncertaintyMsg = document.getElementById("uncertaintyMsg");
        const probBarsContainer = document.getElementById("probBarsContainer");

        // 7 Detailed Clinical Elements
        const specificDiseaseName = document.getElementById("specificDiseaseName");
        const analysisSourcePill = document.getElementById("analysisSourcePill");
        const aiAnalysisText = document.getElementById("aiAnalysisText");
        const symptomsList = document.getElementById("symptomsList");
        const precautionsList = document.getElementById("precautionsList");
        const recommendedCareList = document.getElementById("recommendedCareList");
        const whenToSeeVetList = document.getElementById("whenToSeeVetList");

        // Feature 1 & 2 UI Elements
        const downloadPdfBtn = document.getElementById("downloadPdfBtn");
        const viewAiExplanationBtn = document.getElementById("viewAiExplanationBtn");
        const explanationSection = document.getElementById("explanationSection");
        const explanationGrid = document.getElementById("explanationGrid");
        const explanationFallback = document.getElementById("explanationFallback");
        const explanationFallbackMsg = document.getElementById("explanationFallbackMsg");
        const explanationOrigImg = document.getElementById("explanationOrigImg");
        const explanationGradcamImg = document.getElementById("explanationGradcamImg");
        const downloadGradcamBtn = document.getElementById("downloadGradcamBtn");

        // Localized Disease Information
        const localizedInfo = typeof getLocalizedDiseaseInfo === "function"
            ? getLocalizedDiseaseInfo(data.predicted_class)
            : { name: data.predicted_friendly_name, signs: data.disease_info?.signs, recommendation: data.disease_info?.recommendation };

        // 1. Primary Condition Category & Confidence
        if (condTitle) condTitle.textContent = localizedInfo.name || data.predicted_friendly_name;
        if (confValue) confValue.textContent = `${data.confidence_pct}%`;

        // Badge styling
        if (condBadge) {
            condBadge.className = "prediction-badge " + (data.disease_info?.badge_class || "badge-success");
            condBadge.textContent = localizedInfo.name || data.predicted_friendly_name;
        }

        // Uncertainty Alert
        if (data.is_uncertain && uncertaintyBox) {
            uncertaintyBox.style.display = "flex";
            if (uncertaintyMsg) {
                uncertaintyMsg.textContent = data.uncertainty_message || (typeof t === "function" ? t("detect.awaiting_desc") : "Low-confidence result.");
            }
        } else if (uncertaintyBox) {
            uncertaintyBox.style.display = "none";
        }

        // Detailed Grok Data Extraction
        const detailed = data.detailed_analysis || {};
        const specificDisease = data.specific_disease || detailed.specific_disease || "Canine Dermatological Lesion";
        const analysisNarrative = data.ai_analysis || detailed.ai_analysis || data.disease_info?.message || "";
        const symptomsArr = data.symptoms || detailed.symptoms || localizedInfo.signs || data.disease_info?.signs || [];
        const precautionsArr = data.precautions || detailed.precautions || [
            "Prevent scratching and mechanical self-trauma using an e-collar if necessary.",
            "Maintain strict hand hygiene after touching or inspecting the dog's skin.",
            "Avoid administering human topical medication without veterinary approval."
        ];
        const careArr = data.recommended_care || detailed.recommended_care || [
            localizedInfo.recommendation || data.disease_info?.recommendation || "Consult your veterinarian for diagnostic cytology and targeted treatment."
        ];
        const vetTriggersArr = data.when_to_see_vet || detailed.when_to_see_vet || [
            "Lesion spreads, becomes ulcerated, or produces purulent foul-smelling discharge.",
            "Dog displays lethargy, loss of appetite, fever, or severe localized tenderness.",
            "Condition fails to improve or worsens within 48 to 72 hours."
        ];
        const sourceLabel = data.analysis_source || detailed.source || "Grok AI Analysis";

        // 2. Possible Specific Disease Name
        if (specificDiseaseName) {
            specificDiseaseName.textContent = specificDisease;
        }
        if (analysisSourcePill) {
            const isGrok = sourceLabel.toLowerCase().includes("grok");
            analysisSourcePill.innerHTML = isGrok
                ? `<i class="fa-solid fa-sparkles"></i> <span>${sourceLabel}</span>`
                : `<i class="fa-solid fa-brain"></i> <span>${sourceLabel}</span>`;
        }

        // 3. AI Analysis / Explanation
        if (aiAnalysisText) {
            aiAnalysisText.textContent = analysisNarrative;
        }

        // 4. Symptoms or Visible Signs List
        if (symptomsList) {
            symptomsList.innerHTML = "";
            symptomsArr.forEach((s) => {
                const li = document.createElement("li");
                li.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${s}</span>`;
                symptomsList.appendChild(li);
            });
        }

        // 5. Precautions List
        if (precautionsList) {
            precautionsList.innerHTML = "";
            precautionsArr.forEach((p) => {
                const li = document.createElement("li");
                li.innerHTML = `<i class="fa-solid fa-shield-halved"></i> <span>${p}</span>`;
                precautionsList.appendChild(li);
            });
        }

        // 6. Recommended Care List
        if (recommendedCareList) {
            recommendedCareList.innerHTML = "";
            careArr.forEach((c) => {
                const li = document.createElement("li");
                li.innerHTML = `<i class="fa-solid fa-heart-pulse"></i> <span>${c}</span>`;
                recommendedCareList.appendChild(li);
            });
        }

        // 7. When to Consult a Veterinarian List
        if (whenToSeeVetList) {
            whenToSeeVetList.innerHTML = "";
            vetTriggersArr.forEach((v) => {
                const li = document.createElement("li");
                li.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <span>${v}</span>`;
                whenToSeeVetList.appendChild(li);
            });
        }

        // Animated Probability Breakdown Bars (4 classes)
        if (probBarsContainer) {
            probBarsContainer.innerHTML = "";
            (data.classes_breakdown || []).forEach((item) => {
                const isTop = item.class_key === data.predicted_class;
                const localizedClassName = typeof t === "function" ? t(`disease.${item.class_key}.name`, item.friendly_name) : item.friendly_name;
                const row = document.createElement("div");
                row.className = "prob-row";
                row.innerHTML = `
                    <div class="prob-meta">
                        <span>${localizedClassName}</span>
                        <span>${item.probability_pct}%</span>
                    </div>
                    <div class="prob-bar-track">
                        <div class="prob-bar-fill ${isTop ? "highlight" : ""}" style="width: 0%"></div>
                    </div>
                `;
                probBarsContainer.appendChild(row);

                // Trigger animation
                setTimeout(() => {
                    const fill = row.querySelector(".prob-bar-fill");
                    if (fill) fill.style.width = `${item.probability_pct}%`;
                }, 100);
            });
        }

        // ---------------------------------------------------------------------
        // FEATURE 1: Grad-CAM Explainable AI Interaction Logic
        // ---------------------------------------------------------------------
        const viewExplanationText = typeof t === "function" ? t("result.btn_view_explanation", "View AI Explanation") : "View AI Explanation";
        const hideExplanationText = typeof t === "function" ? t("result.btn_hide_explanation", "Hide AI Explanation") : "Hide AI Explanation";

        if (viewAiExplanationBtn) {
            const isCurrentlyOpen = explanationSection && explanationSection.style.display === "block";
            viewAiExplanationBtn.innerHTML = isCurrentlyOpen
                ? `<i class="fa-solid fa-eye-slash"></i> <span>${hideExplanationText}</span>`
                : `<i class="fa-solid fa-brain"></i> <span>${viewExplanationText}</span>`;

            // Remove prior listeners by cloning
            const newExplanationBtn = viewAiExplanationBtn.cloneNode(true);
            viewAiExplanationBtn.parentNode.replaceChild(newExplanationBtn, viewAiExplanationBtn);

            newExplanationBtn.addEventListener("click", () => {
                if (explanationSection.style.display === "none" || explanationSection.style.display === "") {
                    explanationSection.style.display = "block";
                    newExplanationBtn.innerHTML = `<i class="fa-solid fa-eye-slash"></i> <span>${hideExplanationText}</span>`;
                    newExplanationBtn.classList.add("active");
                    explanationSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
                } else {
                    explanationSection.style.display = "none";
                    newExplanationBtn.innerHTML = `<i class="fa-solid fa-brain"></i> <span>${viewExplanationText}</span>`;
                    newExplanationBtn.classList.remove("active");
                }
            });
        }

        // Configure Grad-CAM Image Cards
        if (data.gradcam_available && data.gradcam_image) {
            if (explanationGrid) explanationGrid.style.display = "grid";
            if (explanationFallback) explanationFallback.style.display = "none";
            if (explanationOrigImg) {
                explanationOrigImg.src = data.original_image || previewThumb.src;
            }
            if (explanationGradcamImg) {
                explanationGradcamImg.src = data.gradcam_image;
            }
            if (downloadGradcamBtn) {
                downloadGradcamBtn.style.display = "inline-flex";
                downloadGradcamBtn.innerHTML = `<i class="fa-solid fa-download"></i> <span>${typeof t === "function" ? t("explanation.btn_download", "Download Explanation Image") : "Download Explanation Image"}</span>`;
                const newDownloadBtn = downloadGradcamBtn.cloneNode(true);
                downloadGradcamBtn.parentNode.replaceChild(newDownloadBtn, downloadGradcamBtn);

                newDownloadBtn.addEventListener("click", () => {
                    const link = document.createElement("a");
                    link.download = `PawCare_AI_GradCAM_${Date.now()}.jpg`;
                    link.href = data.gradcam_image;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                });
            }
        } else {
            // Graceful error handling if Grad-CAM unavailable
            if (explanationGrid) explanationGrid.style.display = "none";
            if (explanationFallback) explanationFallback.style.display = "flex";
            if (explanationFallbackMsg) {
                explanationFallbackMsg.textContent =
                    data.gradcam_error || (typeof t === "function" ? t("explanation.fallback_msg") : "AI explanation is temporarily unavailable.");
            }
            if (downloadGradcamBtn) downloadGradcamBtn.style.display = "none";
        }

        // ---------------------------------------------------------------------
        // FEATURE 2: PDF AI Health Report Download Interaction Logic
        // ---------------------------------------------------------------------
        if (downloadPdfBtn) {
            downloadPdfBtn.innerHTML = `<i class="fa-solid fa-file-pdf"></i> <span>${typeof t === "function" ? t("result.btn_download_pdf", "Download PDF Report") : "Download PDF Report"}</span>`;
            const newPdfBtn = downloadPdfBtn.cloneNode(true);
            downloadPdfBtn.parentNode.replaceChild(newPdfBtn, downloadPdfBtn);

            newPdfBtn.addEventListener("click", async () => {
                const originalBtnContent = newPdfBtn.innerHTML;
                const loadingText = typeof t === "function" ? t("result.btn_download_pdf_loading", "Generating PDF Report...") : "Generating PDF Report...";
                const currentLang = typeof getCurrentLanguage === "function" ? getCurrentLanguage() : "en";

                try {
                    newPdfBtn.disabled = true;
                    newPdfBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${loadingText}`;

                    // Request report generation with selected language
                    const response = await fetch("/download-report", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            analysis_id: data.analysis_id,
                            lang: currentLang,
                            predicted_friendly_name: localizedInfo.name,
                            confidence_pct: data.confidence_pct,
                            classes_breakdown: data.classes_breakdown,
                            disease_info: {
                                signs: localizedInfo.signs,
                                recommendation: localizedInfo.recommendation
                            },
                            disclaimer: typeof t === "function" ? t("result.disclaimer_text", data.disclaimer) : data.disclaimer,
                            original_image: data.original_image,
                            gradcam_image: data.gradcam_image
                        })
                    });

                    if (!response.ok) {
                        throw new Error("Failed to generate PDF report from server.");
                    }

                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = downloadUrl;
                    link.download = `PawCare_AI_Health_Report_${currentLang.toUpperCase()}_${Date.now()}.pdf`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(downloadUrl);

                } catch (pdfErr) {
                    console.error("PDF Download error:", pdfErr);
                    alert("Could not generate PDF report. Please check server logs and try again.");
                } finally {
                    newPdfBtn.disabled = false;
                    newPdfBtn.innerHTML = originalBtnContent;
                }
            });
        }

        // ---------------------------------------------------------------------
        // FEATURE 3: Find a Local Vet (Google Maps Geolocation Search)
        // ---------------------------------------------------------------------
        const findVetBtn = document.getElementById("findVetBtn");
        const findVetBtnSecondary = document.getElementById("findVetBtnSecondary");

        if (findVetBtn) {
            findVetBtn.innerHTML = `<i class="fa-solid fa-location-dot"></i> <span data-i18n="result.btn_find_vet">${typeof t === "function" ? t("result.btn_find_vet", "Find a Local Vet") : "Find a Local Vet"}</span>`;
        }
        if (findVetBtnSecondary) {
            findVetBtnSecondary.innerHTML = `<i class="fa-solid fa-location-dot"></i> <span data-i18n="result.btn_find_vet">${typeof t === "function" ? t("result.btn_find_vet", "Find a Local Vet") : "Find a Local Vet"}</span>`;
        }

        function triggerFindLocalVet(btnEl) {
            const feedbackEl = document.getElementById("vetLocatorFeedback");
            const locatingText = typeof t === "function" ? t("result.btn_locating_vet", "Locating Nearby Vets...") : "Locating Nearby Vets...";
            const originalBtnHtml = btnEl.innerHTML;

            // Reset previous feedback state
            if (feedbackEl) {
                feedbackEl.style.display = "none";
                feedbackEl.className = "vet-locator-feedback";
                feedbackEl.innerHTML = "";
            }

            function displayVetFeedback(type, message, showManualLink = true) {
                if (!feedbackEl) return;
                feedbackEl.style.display = "block";
                feedbackEl.className = `vet-locator-feedback ${type}`;

                let iconClass = "fa-circle-info";
                if (type === "success") iconClass = "fa-circle-check";
                if (type === "warning") iconClass = "fa-triangle-exclamation";
                if (type === "error") iconClass = "fa-circle-exclamation";

                const manualUrl = "https://www.google.com/maps/search/veterinary+clinic";
                const manualBtnHtml = showManualLink
                    ? `<div class="vet-manual-row">
                         <a href="${manualUrl}" target="_blank" rel="noopener noreferrer" class="btn-manual-maps">
                           <i class="fa-solid fa-arrow-up-right-from-square"></i> Search for a Vet on Google Maps
                         </a>
                       </div>`
                    : "";

                feedbackEl.innerHTML = `
                    <div class="vet-feedback-content">
                        <i class="fa-solid ${iconClass}"></i>
                        <span>${message}</span>
                    </div>
                    ${manualBtnHtml}
                `;
            }

            // Verify Geolocation API availability
            if (!navigator.geolocation) {
                displayVetFeedback(
                    "error",
                    "Geolocation is not supported by your browser. Please allow location access or search for a vet manually on Google Maps.",
                    true
                );
                return;
            }

            // Open tab synchronously on user click to prevent popup blockers
            let mapTab = null;
            try {
                mapTab = window.open("about:blank", "_blank");
                if (mapTab) {
                    mapTab.document.write(`<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Locating Nearby Vets – PawCare AI</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
      background: #f0fdf4;
      color: #1e293b;
      text-align: center;
      padding: 20px;
      box-sizing: border-box;
    }
    .card {
      background: #ffffff;
      padding: 32px 28px;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.06);
      max-width: 400px;
      border: 1px solid #dcfce7;
    }
    .spinner {
      width: 44px;
      height: 44px;
      border: 4px solid #dcfce7;
      border-top-color: #059669;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 16px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    h3 { margin: 0 0 8px; font-size: 18px; color: #065f46; font-weight: 700; }
    p { margin: 0; font-size: 14px; color: #64748b; line-height: 1.45; }
  </style>
</head>
<body>
  <div class="card">
    <div class="spinner"></div>
    <h3>Locating Nearby Veterinarians...</h3>
    <p>Requesting location permission to open Google Maps around your current coordinates.</p>
  </div>
</body>
</html>`);
                }
            } catch (e) {
                console.warn("Synchronous window.open warning:", e);
            }

            // Set button loading state
            btnEl.disabled = true;
            btnEl.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>${locatingText}</span>`;

            const geoOptions = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            };

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    btnEl.disabled = false;
                    btnEl.innerHTML = originalBtnHtml;

                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;

                    // Formulate Google Maps search URL with exact coordinates
                    const googleMapsUrl = `https://www.google.com/maps/search/veterinary+clinic/@${lat},${lng},14z`;

                    if (mapTab && !mapTab.closed) {
                        mapTab.location.href = googleMapsUrl;
                    } else {
                        window.open(googleMapsUrl, "_blank", "noopener,noreferrer");
                    }

                    displayVetFeedback(
                        "success",
                        "Opened Google Maps centered around your current location to show nearby veterinary clinics.",
                        false
                    );
                },
                (error) => {
                    btnEl.disabled = false;
                    btnEl.innerHTML = originalBtnHtml;

                    const fallbackUrl = "https://www.google.com/maps/search/veterinary+clinic";

                    if (mapTab && !mapTab.closed) {
                        mapTab.location.href = fallbackUrl;
                    }

                    let friendlyMsg = "Location access was denied. Please allow location access or search for a vet manually on Google Maps.";

                    if (error.code === error.PERMISSION_DENIED) {
                        friendlyMsg = "Location access was denied. Please allow location access or search for a vet manually on Google Maps.";
                    } else if (error.code === error.POSITION_UNAVAILABLE) {
                        friendlyMsg = "Location information is currently unavailable. Please allow location access or search for a vet manually on Google Maps.";
                    } else if (error.code === error.TIMEOUT) {
                        friendlyMsg = "Location request timed out. Please allow location access or search for a vet manually on Google Maps.";
                    } else {
                        friendlyMsg = "Unable to retrieve your location. Please allow location access or search for a vet manually on Google Maps.";
                    }

                    displayVetFeedback("warning", friendlyMsg, true);
                },
                geoOptions
            );
        }

        // Attach listeners using cloneNode to prevent duplicate bindings
        if (findVetBtn) {
            const newFindVetBtn = findVetBtn.cloneNode(true);
            findVetBtn.parentNode.replaceChild(newFindVetBtn, findVetBtn);
            newFindVetBtn.addEventListener("click", () => triggerFindLocalVet(newFindVetBtn));
        }

        if (findVetBtnSecondary) {
            const newFindVetBtnSec = findVetBtnSecondary.cloneNode(true);
            findVetBtnSecondary.parentNode.replaceChild(newFindVetBtnSec, findVetBtnSecondary);
            newFindVetBtnSec.addEventListener("click", () => triggerFindLocalVet(newFindVetBtnSec));
        }
    }
}

/* ==========================================================================
   2. TRAINING & DATASET MANAGEMENT LOGIC
   ========================================================================== */
function initTrainingPage() {
    const zipInput = document.getElementById("datasetZipInput");
    const zipDropzone = document.getElementById("zipDropzone");
    const zipName = document.getElementById("zipName");
    const zipSize = document.getElementById("zipSize");
    const zipPreview = document.getElementById("zipPreview");
    const validateBtn = document.getElementById("validateDatasetBtn");
    const summaryCard = document.getElementById("summaryCard");
    const startTrainingBtn = document.getElementById("startTrainingBtn");
    const trainingProgressCard = document.getElementById("trainingProgressCard");
    const terminalBox = document.getElementById("terminalLogs");

    if (!zipDropzone || !validateBtn) return;

    let selectedZipFile = null;
    let pollInterval = null;

    function handleZipFile(file) {
        if (!file || !file.name.toLowerCase().endsWith(".zip")) {
            alert("Invalid File: Please select a .zip dataset archive.");
            return;
        }
        selectedZipFile = file;
        zipName.textContent = file.name;
        zipSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + " MB";
        zipPreview.style.display = "block";
        validateBtn.disabled = false;
    }

    zipDropzone.addEventListener("click", () => zipInput.click());
    zipInput.addEventListener("change", () => {
        if (zipInput.files && zipInput.files.length > 0) {
            handleZipFile(zipInput.files[0]);
        }
    });

    // Validate Dataset Action
    validateBtn.addEventListener("click", async () => {
        if (!selectedZipFile) {
            alert("Please select a dataset ZIP file first.");
            return;
        }

        validateBtn.disabled = true;
        validateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Validating Archive...';

        const formData = new FormData();
        formData.append("dataset", selectedZipFile);

        try {
            const res = await fetch("/validate-dataset", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            validateBtn.disabled = false;
            validateBtn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Validate Dataset';

            if (!res.ok || !data.success) {
                alert(data.message || "Dataset validation failed.");
                return;
            }

            // Render summary metrics
            document.getElementById("countHealthy").textContent = `${data.summary.Healthy} images`;
            document.getElementById("countHypersensitivity").textContent = `${data.summary.Hypersensitivity_allergic_dermatosis} images`;
            document.getElementById("countFungal").textContent = `${data.summary.Fungal_infections} images`;
            document.getElementById("countBacterial").textContent = `${data.summary.Bacterial_dermatosis} images`;
            document.getElementById("countTotal").textContent = `${data.summary.Total} images`;

            summaryCard.style.display = "block";
            startTrainingBtn.disabled = false;
            summaryCard.scrollIntoView({ behavior: "smooth" });

        } catch (err) {
            validateBtn.disabled = false;
            validateBtn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Validate Dataset';
            console.error("Dataset validation error:", err);
            alert("An error occurred during dataset validation.");
        }
    });

    // Start Training Action
    startTrainingBtn.addEventListener("click", async () => {
        const confirmed = confirm(
            "Start training new ResNet-18 model?\n\n" +
            "• This will train on the validated dataset for 15 epochs.\n" +
            "• Checkpoint will be saved to models/dog_disease_resnet18_v2.pth.\n" +
            "• Production model best_dog_disease_resnet18.pth will NOT be overwritten."
        );
        if (!confirmed) return;

        startTrainingBtn.disabled = true;
        trainingProgressCard.style.display = "block";
        trainingProgressCard.scrollIntoView({ behavior: "smooth" });

        try {
            const res = await fetch("/start-training", { method: "POST" });
            const data = await res.json();

            if (!res.ok || !data.success) {
                alert(data.message || "Could not start training.");
                startTrainingBtn.disabled = false;
                return;
            }

            // Begin polling status
            if (pollInterval) clearInterval(pollInterval);
            pollInterval = setInterval(pollTrainingStatus, 2000);

        } catch (err) {
            console.error("Start training error:", err);
            startTrainingBtn.disabled = false;
            alert("Failed to initiate training session.");
        }
    });

    async function pollTrainingStatus() {
        try {
            const res = await fetch("/training-status");
            const data = await res.json();

            const epochText = document.getElementById("trainEpochText");
            const progressBar = document.getElementById("trainProgressBar");
            const lossVal = document.getElementById("trainLossVal");
            const trainAccVal = document.getElementById("trainAccVal");
            const valAccVal = document.getElementById("valAccVal");
            const bestValAccVal = document.getElementById("bestValAccVal");

            if (epochText) epochText.textContent = `Epoch ${data.epoch} / ${data.total_epochs}`;
            if (progressBar && data.total_epochs > 0) {
                const pct = Math.round((data.epoch / data.total_epochs) * 100);
                progressBar.style.width = `${pct}%`;
            }

            if (lossVal) lossVal.textContent = data.train_loss || "0.00";
            if (trainAccVal) trainAccVal.textContent = `${data.train_acc || "0.00"}%`;
            if (valAccVal) valAccVal.textContent = `${data.val_acc || "0.00"}%`;
            if (bestValAccVal) bestValAccVal.textContent = `${data.best_val_acc || "0.00"}%`;

            // Update terminal logs
            if (terminalBox && data.logs) {
                terminalBox.innerHTML = "";
                data.logs.forEach((log) => {
                    const div = document.createElement("div");
                    div.textContent = `> ${log}`;
                    terminalBox.appendChild(div);
                });
                terminalBox.scrollTop = terminalBox.scrollHeight;
            }

            // Check completion
            if (data.status === "completed" || data.status === "error") {
                clearInterval(pollInterval);
                startTrainingBtn.disabled = false;
                if (data.status === "completed") {
                    alert("Training Completed Successfully!\n" + data.message);
                } else {
                    alert("Training stopped with an error: " + data.message);
                }
            }

        } catch (err) {
            console.error("Poll training error:", err);
        }
    }
}
