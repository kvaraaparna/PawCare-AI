/**
 * PawCare AI – Comprehensive Multilingual Translations
 * ====================================================
 * Supported Languages:
 *   - en: English (Default)
 *   - te: తెలుగు (Telugu)
 *   - hi: हिन्दी (Hindi)
 *
 * Provides accurate, self-contained translations for UI, clinical insights,
 * disease names, recommendations, error alerts, and disclaimers without external APIs.
 */

const PAWCARE_TRANSLATIONS = {
    en: {
        // Brand & Navigation
        "brand.name": "PawCare",
        "brand.ai": "AI",
        "brand.tagline": "Healthy Pets, Happier Lives",
        "nav.home": "Home",
        "nav.about": "About",
        "nav.detect": "Detect Disease",
        "nav.how_it_works": "How It Works",
        "nav.training": "Training",
        "nav.contact": "Contact",
        "nav.detect_now": "Detect Now",
        "nav.get_started": "Get Started",
        "nav.language": "Language",

        // Hero Section
        "hero.badge": "AI Powered • Faster Detection • Healthier Pets",
        "hero.title_p1": "Detect Dog",
        "hero.title_highlight": "Skin Diseases",
        "hero.title_p2": "Early",
        "hero.description": "Use AI-powered image analysis to screen dog skin images for possible conditions and support earlier veterinary attention. Because every pet deserves a healthier and happier life.",
        "hero.btn_upload": "Upload Image",
        "hero.btn_learn": "Learn More",
        "hero.security": "Your data is safe and secure",
        "hero.card_text": "A Healthier<br>Tomorrow<br>for Every<br>Pet",

        // Features Section
        "features.badge": "Why PawCare AI",
        "features.title": "Fast, Accurate & Accessible Canine Dermatological Screening",
        "features.card1_title": "Instant AI Analysis",
        "features.card1_desc": "State-of-the-art ResNet-18 deep learning model processes photographs within milliseconds.",
        "features.card2_title": "Explainable AI (Grad-CAM)",
        "features.card2_desc": "Transparent heatmaps reveal precisely which visual regions contributed to the model's prediction.",
        "features.card3_title": "Canine Presence Validator",
        "features.card3_desc": "Smart gatekeeper ensures only legitimate dog photographs and skin close-ups are evaluated.",
        "features.card4_title": "PDF Health Reports",
        "features.card4_desc": "Downloadable clinical screening summaries ready to share with your licensed veterinary doctor.",

        // How It Works
        "steps.badge": "Easy 4-Step Process",
        "steps.title": "How PawCare AI Works",
        "steps.step1_title": "Upload Photograph",
        "steps.step1_desc": "Take or select a clear photograph of your dog's affected skin area.",
        "steps.step2_title": "Canine Verification",
        "steps.step2_desc": "ImageNet validator verifies that the image depicts a canine or dermatological tissue.",
        "steps.step3_title": "ResNet-18 Inference",
        "steps.step3_desc": "Deep neural network evaluates visual patterns across 4 dermatological categories.",
        "steps.step4_title": "Results & Advice",
        "steps.step4_desc": "Receive instant probabilities, Grad-CAM explanations, and veterinary guidance.",

        // Detection Page Upload
        "detect.badge": "AI Screening Aid • ResNet-18",
        "detect.heading": "Dog Skin Disease Detection",
        "detect.subtitle": "Upload a clear photograph of your dog or affected skin area to analyze possible dermatological patterns.",
        "detect.upload_card_title": "Upload Dog Image",
        "detect.dropzone_text": "Drag & drop your dog photograph here",
        "detect.dropzone_subtext": "Supports JPG, JPEG, PNG, WEBP (Max 16MB)",
        "detect.browse_btn": "Choose Image",
        "detect.btn_remove": "Remove",
        "detect.btn_analyze": "Analyze Image",
        "detect.loading_text": "Analyzing your dog's image...",
        "detect.loading_subtext": "Canine validation & ResNet-18 disease inference in progress",
        "detect.demo_title": "Quick Demo Test Samples",
        "detect.sample_healthy": "Healthy Dog",
        "detect.sample_bacterial": "Bacterial Lesion",
        "detect.sample_fungal": "Fungal Infection",
        "detect.sample_allergic": "Allergic Dermatosis",
        "detect.sample_nondog": "Non-Dog Reject Test",

        "detect.tab_upload": "Upload Image",
        "detect.tab_camera": "Scan Using Camera",
        "detect.btn_capture": "Capture Photo",
        "detect.btn_retake": "Retake Photo",
        "detect.btn_flip_camera": "Switch Camera",
        "detect.btn_cancel_camera": "Cancel Camera",
        "detect.dog_verified": "Dog detected ✓",
        "detect.camera_live": "Live Camera Feed",
        "detect.camera_hint": "Center your dog or skin lesion within the frame",

        // Initial & Rejection States
        "detect.awaiting_title": "Awaiting Image Upload",
        "detect.awaiting_desc": "Select an image above or click any of the Quick Demo Samples to run real AI screening.",
        "detect.rejection_title": "No Dog Detected",
        "detect.rejection_desc": "No dog detected. Please upload or capture a clear image of a dog.",
        "detect.btn_retry": "Try Another Image",

        // Prediction Results Card
        "result.badge_condition": "Condition",
        "result.confidence_label": "AI Confidence",
        "result.probabilities_title": "Class Probabilities (4 Categories)",
        "result.primary_match": "Primary Match",
        "result.btn_find_vet": "Find a Local Vet",
        "result.btn_locating_vet": "Locating Nearby Vets...",
        "result.btn_download_pdf": "Download PDF Report",
        "result.btn_download_pdf_loading": "Generating PDF Report...",
        "result.btn_view_explanation": "View AI Explanation",
        "result.btn_hide_explanation": "Hide AI Explanation",
        "result.visible_signs_title": "Visible Clinical Signs",
        "result.vet_care_title": "Recommended Veterinary Care",
        "result.disclaimer_title": "Important Notice:",
        "result.disclaimer_text": "This AI screening result is an educational assistive tool and does not constitute a clinical veterinary diagnosis. If your dog exhibits signs of pain, pruritus, or worsening lesions, please consult a certified veterinary professional.",

        // AI Explanation (Grad-CAM)
        "explanation.heading": "AI Explanation",
        "explanation.subtitle": "See which regions of the image contributed most strongly to the AI prediction.",
        "explanation.card_original": "ORIGINAL IMAGE",
        "explanation.card_gradcam": "AI ATTENTION / GRAD-CAM",
        "explanation.notice": "Highlighted regions show areas that contributed strongly to the model's prediction.",
        "explanation.legend_low": "Low contribution",
        "explanation.legend_high": "High contribution",
        "explanation.btn_download": "Download Explanation Image",
        "explanation.fallback_msg": "AI explanation is temporarily unavailable, but the prediction result is still available.",

        // Training Page
        "training.badge": "Model Administration",
        "training.title": "Model Training & Dataset Management",
        "training.subtitle": "Upload curated ZIP archives containing 4 canonical classes to validate and retrain the ResNet-18 model.",
        "training.dropzone_text": "Drag & drop your dataset ZIP file here",
        "training.dropzone_subtext": "Must contain subfolders: Bacterial_dermatosis, Fungal_infections, Healthy, Hypersensitivity_allergic_dermatosis",
        "training.btn_validate": "Validate Dataset Archive",
        "training.btn_start": "START TRAINING (15 EPOCHS)",

        // Footer
        "footer.tagline": "Dog Skin Disease Detection System. Powered by PyTorch ResNet-18 Transfer Learning.",
        "footer.copyright": "© 2026 PawCare AI. All rights reserved.",

        // Disease Names & Details
        "disease.Bacterial_dermatosis.name": "Bacterial Dermatosis",
        "disease.Bacterial_dermatosis.signs": [
            "Redness, erythema, and cutaneous inflammation",
            "Crusting, scaling, or epidermal collarettes",
            "Pustules, papules, or active skin lesions",
            "Localized irritation and follicular swelling"
        ],
        "disease.Bacterial_dermatosis.recommendation": "Consult a qualified veterinarian for cytology, bacterial culture, and appropriate targeted antimicrobial or topical therapy.",

        "disease.Fungal_infections.name": "Fungal Infection",
        "disease.Fungal_infections.signs": [
            "Circular patches of hair loss (alopecia rings)",
            "Scaly, crusty, or flaky epidermal patches",
            "Redness, hyperpigmentation, or mild lichenification",
            "Moderate to severe pruritus (itching) and irritation"
        ],
        "disease.Fungal_infections.recommendation": "A clinical examination with fungal culture or Wood's lamp evaluation is recommended to identify dermatophytes and administer antifungal treatments.",

        "disease.Healthy.name": "Healthy",
        "disease.Healthy.signs": [
            "Intact epidermal barrier without pustules or active lesions",
            "Even and consistent hair coat density",
            "Absence of evident erythema or active inflammation"
        ],
        "disease.Healthy.recommendation": "Maintain regular preventative grooming, parasite control, and routine veterinary wellness check-ups. Monitor for any future skin changes.",

        "disease.Hypersensitivity_allergic_dermatosis.name": "Allergic Dermatosis (Hypersensitivity)",
        "disease.Hypersensitivity_allergic_dermatosis.signs": [
            "Intense itching, scratching, paw-licking, or rubbing",
            "Redness, inflamed ear flaps, or facial irritation",
            "Secondary alopecia (hair loss) from persistent trauma",
            "Recurrent secondary infections or skin irritation"
        ],
        "disease.Hypersensitivity_allergic_dermatosis.recommendation": "Consult a veterinarian to identify underlying allergens (flea, food, or environmental) and discuss effective allergy management plans."
    },

    te: {
        // బ్రాండ్ & నావిగేషన్ (Brand & Navigation)
        "brand.name": "పాకేర్",
        "brand.ai": "AI",
        "brand.tagline": "ఆరోగ్యకరమైన పెంపుడు జంతువులు, ఆనందకరమైన జీవితాలు",
        "nav.home": "హోమ్",
        "nav.about": "గురించి",
        "nav.detect": "వ్యాధి గుర్తింపు",
        "nav.how_it_works": "ఇది ఎలా పనిచేస్తుంది",
        "nav.training": "ట్రైనింగ్",
        "nav.contact": "సంప్రదించండి",
        "nav.detect_now": "ఇప్పుడే పరీక్షించండి",
        "nav.get_started": "ప్రారంభించండి",
        "nav.language": "భాష (Language)",

        // హీరో విభాగం (Hero Section)
        "hero.badge": "AI ఆధారిత • వేగవంతమైన గుర్తింపు • ఆరోగ్యకరమైన పెంపుడు జంతువులు",
        "hero.title_p1": "కుక్కల",
        "hero.title_highlight": "చర్మ వ్యాధులను",
        "hero.title_p2": "ముందే గుర్తించండి",
        "hero.description": "AI ఇమేజ్ విశ్లేషణ ద్వారా మీ కుక్క చర్మ సమస్యలను ముందస్తుగా గుర్తించి సరైన పశువైద్య సహాయం పొందండి. ప్రతి పెంపుడు జంతువు ఆరోగ్యంగా ఉండటానికి ఇది తోడ్పడుతుంది.",
        "hero.btn_upload": "ఫోటో అప్‌లోడ్ చేయండి",
        "hero.btn_learn": "మరింత తెలుసుకోండి",
        "hero.security": "మీ డేటా సురక్షితమైనది మరియు గోప్యమైనది",
        "hero.card_text": "ప్రతి పెంపుడు జంతువుకు<br>ఆరోగ్యకరమైన<br>రేపటి దినం",

        // ఫీచర్లు (Features)
        "features.badge": "పాకేర్ AI ఎందుకు?",
        "features.title": "వేగవంతమైన, ఖచ్చితమైన మరియు సులభమైన కుక్కల చర్మ వ్యాధి పరీక్ష",
        "features.card1_title": "తక్షణ AI విశ్లేషణ",
        "features.card1_desc": "అత్యాధునిక ResNet-18 డీప్ లెర్నింగ్ మోడల్ కొన్ని సెకన్లలోనే ఫోటోను విశ్లేషిస్తుంది.",
        "features.card2_title": "వివరణాత్మక AI (Grad-CAM)",
        "features.card2_desc": "మోడల్ ఏయే భాగాలను ఆధారంగా చేసుకుని ఫలితాన్ని ఇచ్చిందో స్పష్టమైన హీట్‌మ్యాప్ చూపిస్తుంది.",
        "features.card3_title": "కుక్కల గుర్తింపు ధృవీకరణ",
        "features.card3_desc": "అప్‌లోడ్ చేసిన చిత్రం నిజంగా కుక్క లేదా చర్మానికి సంబంధించిందా కాదా అని స్వయంచాలకంగా పరీక్షిస్తుంది.",
        "features.card4_title": "PDF హెల్త్ రిపోర్టులు",
        "features.card4_desc": "మీ పశువైద్యుడితో పంచుకోవడానికి సమగ్రమైన డిజిటల్ రిపోర్టును డౌన్‌లోడ్ చేసుకోండి.",

        // ఇది ఎలా పనిచేస్తుంది (How It Works)
        "steps.badge": "సులభమైన 4 దశలు",
        "steps.title": "పాకేర్ AI ఎలా పనిచేస్తుంది",
        "steps.step1_title": "ఫోటో అప్‌లోడ్ చేయండి",
        "steps.step1_desc": "మీ కుక్క ప్రభావిత చర్మ ప్రాంతం యొక్క స్పష్టమైన ఫోటోను తీయండి లేదా ఎంచుకోండి.",
        "steps.step2_title": "కుక్కల ధృవీకరణ",
        "steps.step2_desc": "ఇది కుక్క చిత్రమేనని ImageNet వాలిడేటర్ స్వయంచాలకంగా నిర్ధారిస్తుంది.",
        "steps.step3_title": "ResNet-18 విశ్లేషణ",
        "steps.step3_desc": "న్యూరల్ నెట్‌వర్క్ 4 రకాల చర్మ వ్యాధి వర్గాలను పరిశీలిస్తుంది.",
        "steps.step4_title": "ఫలితాలు & సలహాలు",
        "steps.step4_desc": "తక్షణ ఫలితాలు, Grad-CAM వివరణలు మరియు వెటర్నరీ సంరక్షణ సలహాలు పొందండి.",

        // వ్యాధి గుర్తింపు పేజీ (Detection Page)
        "detect.badge": "AI స్క్రీనింగ్ సహాయం • ResNet-18",
        "detect.heading": "కుక్కల చర్మ వ్యాధి గుర్తింపు",
        "detect.subtitle": "సాధ్యమయ్యే చర్మ వ్యాధి లక్షణాలను విశ్లేషించడానికి మీ కుక్క లేదా చర్మ ప్రాంతం యొక్క స్పష్టమైన ఫోటోను అప్‌లోడ్ చేయండి.",
        "detect.upload_card_title": "కుక్క ఫోటోను అప్‌లోడ్ చేయండి",
        "detect.dropzone_text": "మీ కుక్క ఫోటోను ఇక్కడ డ్రాగ్ & డ్రాప్ చేయండి",
        "detect.dropzone_subtext": "JPG, JPEG, PNG, WEBP ఫార్మాట్‌లు (గరిష్టంగా 16MB)",
        "detect.browse_btn": "ఫోటో ఎంచుకోండి",
        "detect.btn_remove": "తొలగించు",
        "detect.btn_analyze": "ఫోటో విశ్లేషించండి",
        "detect.loading_text": "మీ కుక్క ఫోటో విశ్లేషించబడుతోంది...",
        "detect.loading_subtext": "కుక్క ధృవీకరణ మరియు ResNet-18 వ్యాధి గుర్తింపు ప్రక్రియ కొనసాగుతోంది",
        "detect.demo_title": "త్వరిత డెమో నమూనాలు",
        "detect.sample_healthy": "ఆరోగ్యకరమైన కుక్క",
        "detect.sample_bacterial": "బాక్టీరియల్ గాయం",
        "detect.sample_fungal": "ఫంగల్ ఇన్ఫెక్షన్",
        "detect.sample_allergic": "అలెర్జిక్ డెర్మటోసిస్",
        "detect.sample_nondog": "కుక్క-కాని తిరస్కరణ పరీక్ష",

        "detect.tab_upload": "చిత్రాన్ని అప్‌లోడ్ చేయండి",
        "detect.tab_camera": "కెమెరాతో స్కాన్ చేయండి",
        "detect.btn_capture": "ఫోటో తీయండి",
        "detect.btn_retake": "మరొక ఫోటో తీయండి",
        "detect.btn_flip_camera": "కెమెరా మార్చండి",
        "detect.btn_cancel_camera": "రద్దు చేయండి",
        "detect.dog_verified": "కుక్క గుర్తించబడింది ✓",
        "detect.camera_live": "లైవ్ కెమెరా ఫీడ్",
        "detect.camera_hint": "మీ కుక్కను లేదా చర్మ ప్రాంతాన్ని ఫ్రేమ్‌లో ఉంచండి",

        // ప్రారంభ & తిరస్కరణ స్థితి (States)
        "detect.awaiting_title": "చిత్రం అప్‌లోడ్ కోసం వేచి ఉంది",
        "detect.awaiting_desc": "పైనున్న చిత్రాన్ని ఎంచుకోండి లేదా నిజమైన AI స్క్రీనింగ్ కోసం డెమో నమూనాలను క్లిక్ చేయండి.",
        "detect.rejection_title": "కుక్క గుర్తించబడలేదు",
        "detect.rejection_desc": "కుక్క గుర్తించబడలేదు. దయచేసి కుక్క యొక్క స్పష్టమైన చిత్రాన్ని అప్‌లోడ్ చేయండి లేదా ఫోటో తీయండి.",
        "detect.btn_retry": "మరొక ఫోటో ప్రయత్నించండి",

        // ఫలితాల కార్డ్ (Results Card)
        "result.badge_condition": "పరిస్థితి",
        "result.confidence_label": "AI ఖచ్చితత్వం / విశ్వాసం",
        "result.probabilities_title": "తరగతి సంభావ్యతలు (4 వర్గాలు)",
        "result.primary_match": "ప్రధాన ఫలితం",
        "result.btn_find_vet": "సమీపంలోని వెటర్నరీ వైద్యుడిని కనుగొనండి",
        "result.btn_locating_vet": "సమీప క్లినిక్‌లను వెతుకుతోంది...",
        "result.btn_download_pdf": "PDF రిపోర్ట్ డౌన్‌లోడ్ చేయండి",
        "result.btn_download_pdf_loading": "PDF రిపోర్ట్ రూపొందించబడుతోంది...",
        "result.btn_view_explanation": "AI వివరణ చూడండి",
        "result.btn_hide_explanation": "AI వివరణను దాచండి",
        "result.visible_signs_title": "కనిపించే క్లినికల్ లక్షణాలు",
        "result.vet_care_title": "సిఫార్సు చేయబడిన పశువైద్య సంరక్షణ",
        "result.disclaimer_title": "ముఖ్య గమనిక:",
        "result.disclaimer_text": "ఈ AI స్క్రీనింగ్ ఫలితం విద్యా మరియు సహాయక సాధనం మాత్రమే. ఇది తుది క్లినికల్ వెటర్నరీ నిర్ధారణ కాదు. మీ కుక్కకు నొప్పి, దురద లేదా చర్మ సమస్యలు ఉంటే వెంటనే లైసెన్స్ పొందిన పశువైద్యుడిని సంప్రదించండి.",

        // AI వివరణ (Grad-CAM)
        "explanation.heading": "AI వివరణ",
        "explanation.subtitle": "AI అంచనాకు చిత్రం యొక్క ఏయే భాగాలు ఎక్కువగా దోహదపడ్డాయో చూడండి.",
        "explanation.card_original": "అసలు చిత్రం",
        "explanation.card_gradcam": "AI శ్రద్ధ / GRAD-CAM",
        "explanation.notice": "హైలైట్ చేయబడిన ప్రాంతాలు మోడల్ యొక్క నిర్ణయానికి బలంగా దోహదపడిన భాగాలను సూచిస్తాయి.",
        "explanation.legend_low": "తక్కువ ప్రభావం",
        "explanation.legend_high": "ఎక్కువ ప్రభావం",
        "explanation.btn_download": "వివరణ చిత్రాన్ని డౌన్‌లోడ్ చేయండి",
        "explanation.fallback_msg": "AI వివరణ ప్రస్తుతం అందుబాటులో లేదు, కానీ వ్యాధి అంచనా ఫలితం సిద్ధంగా ఉంది.",

        // ట్రైనింగ్ పేజీ (Training Page)
        "training.badge": "మోడల్ నిర్వహణ",
        "training.title": "మోడల్ ట్రైనింగ్ & డేటాసెట్ నిర్వహణ",
        "training.subtitle": "ResNet-18 మోడల్‌ను రీట్రైన్ చేయడానికి 4 వ్యాధి వర్గాలను కలిగి ఉన్న ZIP ఫైల్‌ను అప్‌లోడ్ చేయండి.",
        "training.dropzone_text": "మీ డేటాసెట్ ZIP ఫైల్‌ను ఇక్కడ డ్రాప్ చేయండి",
        "training.dropzone_subtext": "ఇందులో Bacterial_dermatosis, Fungal_infections, Healthy, Hypersensitivity_allergic_dermatosis ఫోల్డర్లు ఉండాలి",
        "training.btn_validate": "డేటాసెట్‌ను ధృవీకరించండి",
        "training.btn_start": "ట్రైనింగ్ ప్రారంభించండి (15 ఎపోచ్‌లు)",

        // ఫుటర్ (Footer)
        "footer.tagline": "కుక్కల చర్మ వ్యాధి గుర్తింపు వ్యవస్థ. PyTorch ResNet-18 ట్రాన్స్‌ఫర్ లెర్నింగ్ ద్వారా ఆధారితం.",
        "footer.copyright": "© 2026 పాకేర్ AI. సర్వహక్కులు ప్రత్యేకించబడ్డాయి.",

        // వ్యాధి వివరాలు (Disease Clinical Data)
        "disease.Bacterial_dermatosis.name": "బాక్టీరియల్ డెర్మటోసిస్ (బాక్టీరియా చర్మ వ్యాధి)",
        "disease.Bacterial_dermatosis.signs": [
            "చర్మం ఎర్రబడటం, దద్దుర్లు మరియు వాపు",
            "పొక్కులు, పొలుసులు లేదా చర్మం పైపొర ఊడటం",
            "చీము బొబ్బలు లేదా చురుకైన చర్మ గాయాలు",
            "తీవ్రమైన దురద మరియు వెంట్రుకల కుదుళ్ల వాపు"
        ],
        "disease.Bacterial_dermatosis.recommendation": "సరైన యాంటీబయాటిక్స్ లేదా ఆయింట్‌మెంట్ల కోసం సైటాలజీ మరియు బ్యాక్టీరియల్ కల్చర్ పరీక్ష కొరకు పశువైద్యుడిని సంప్రదించండి.",

        "disease.Fungal_infections.name": "ఫంగల్ ఇన్ఫెక్షన్ (శిలీంధ్రాల సంక్రమణ)",
        "disease.Fungal_infections.signs": [
            "గుండ్రంగా వెంట్రుకలు రాలిపోవడం (రింగ్‌వార్మ్ వలయాలు)",
            "పొడిబారిన, పొలుసుల మాదిరిగా ఉన్న చర్మ మచ్చలు",
            "చర్మం ఎరుపు లేదా నలుపు రంగులోకి మారడం",
            "నిరంతర దురద మరియు అసౌకర్యం"
        ],
        "disease.Fungal_infections.recommendation": "శిలీంధ్ర రకాన్ని నిర్ధారించడానికి మరియు సరైన యాంటీఫంగల్ చికిత్స కోసం పశువైద్య పరీక్ష అవసరం.",

        "disease.Healthy.name": "ఆరోగ్యకరమైనది (హెల్తీ)",
        "disease.Healthy.signs": [
            "ఎలాంటి పొక్కులు లేదా గాయాలు లేని స్పష్టమైన చర్మం",
            "సమానమైన మరియు మెరిసే వెంట్రుకల సాంద్రత",
            "ఎర్రబడటం లేదా వాపు లేకపోవడం"
        ],
        "disease.Healthy.recommendation": "సాధారణ గ్రూమింగ్, పరాన్నజీవుల నివారణ మరియు రెగ్యులర్ చెకప్‌లను కొనసాగించండి.",

        "disease.Hypersensitivity_allergic_dermatosis.name": "అలెర్జిక్ డెర్మటోసిస్ (హైపర్‌సెన్సిటివిటీ)",
        "disease.Hypersensitivity_allergic_dermatosis.signs": [
            "తీవ్రమైన దురద, గోకడం, పాదాలు నాకడం లేదా రుద్దడం",
            "చెవుల లోపలి భాగం లేదా ముఖం ఎర్రబడటం",
            "నిరంతరం గోకడం వల్ల వెంట్రుకలు రాలిపోవడం",
            "తరచుగా తిరగబెట్టే చర్మపు చికాకు"
        ],
        "disease.Hypersensitivity_allergic_dermatosis.recommendation": "ఆహారపు లేదా పర్యావరణ అలెర్జీలను గుర్తించి తగిన అలెర్జీ నిర్వహణ కొరకు పశువైద్యుడిని సంప్రదించండి."
    },

    hi: {
        // ब्रांड एवं नेविगेशन (Brand & Navigation)
        "brand.name": "पॉकेयर",
        "brand.ai": "AI",
        "brand.tagline": "स्वस्थ पालतू, खुशहाल जीवन",
        "nav.home": "होम",
        "nav.about": "परिचय",
        "nav.detect": "रोग पहचान",
        "nav.how_it_works": "यह कैसे काम करता है",
        "nav.training": "ट्रेनिंग",
        "nav.contact": "संपर्क करें",
        "nav.detect_now": "अभी जांचें",
        "nav.get_started": "शुरू करें",
        "nav.language": "भाषा (Language)",

        // मुख्य अनुभाग (Hero Section)
        "hero.badge": "AI संचालित • त्वरित पहचान • स्वस्थ पालतू जानवर",
        "hero.title_p1": "कुत्तों के",
        "hero.title_highlight": "त्वचा रोगों की",
        "hero.title_p2": "जल्दी पहचान करें",
        "hero.description": "AI-संचालित इमेज विश्लेषण से अपने कुत्ते की त्वचा की समस्याओं की समय रहते जांच करें और उचित पशु चिकित्सा सहायता प्राप्त करें। क्योंकि हर पालतू स्वस्थ जीवन का हकदार है।",
        "hero.btn_upload": "तस्वीर अपलोड करें",
        "hero.btn_learn": "अधिक जानें",
        "hero.security": "आपका डेटा सुरक्षित और गोपनीय है",
        "hero.card_text": "हर पालतू के लिए<br>एक स्वस्थ<br>और बेहतर<br>कल",

        // विशेषताएं (Features)
        "features.badge": "पॉकेयर AI क्यों?",
        "features.title": "कुत्तों के त्वचा रोगों की त्वरित, सटीक और सुलभ जांच",
        "features.card1_title": "त्वरित AI विश्लेषण",
        "features.card1_desc": "उन्नत ResNet-18 डीप लर्निंग मॉडल सेकंडों में तस्वीर का विश्लेषण करता है।",
        "features.card2_title": "व्याख्यात्मक AI (Grad-CAM)",
        "features.card2_desc": "सटीक हीटमैप से देखें कि तस्वीर के किन हिस्सों के आधार पर AI ने परिणाम दिया।",
        "features.card3_title": "कुत्ता पहचान सत्यापन",
        "features.card3_desc": "स्मार्ट गेटकीपर सुनिश्चित करता है कि केवल वैध कुत्तों की तस्वीरें ही जांची जाएं।",
        "features.card4_title": "PDF स्वास्थ्य रिपोर्ट",
        "features.card4_desc": "अपने पशु चिकित्सक (वेटनरी डॉक्टर) को दिखाने के लिए डिजिटल रिपोर्ट डाउनलोड करें।",

        // कार्यप्रणाली (How It Works)
        "steps.badge": "आसान 4 चरण",
        "steps.title": "पॉकेयर AI कैसे काम करता है",
        "steps.step1_title": "तस्वीर अपलोड करें",
        "steps.step1_desc": "कुत्ते के प्रभावित त्वचा क्षेत्र की स्पष्ट तस्वीर लें या चुनें।",
        "steps.step2_title": "कुत्ता सत्यापन",
        "steps.step2_desc": "ImageNet सत्यापनकर्ता पुष्टि करता है कि छवि कुत्ते की ही है।",
        "steps.step3_title": "ResNet-18 विश्लेषण",
        "steps.step3_desc": "डीप न्यूरल नेटवर्क 4 त्वचा रोग श्रेणियों में विश्लेषण करता है।",
        "steps.step4_title": "परिणाम एवं सुझाव",
        "steps.step4_desc": "सटीक संभावनाएं, Grad-CAM हीटमैप और डॉक्टर की सलाह प्राप्त करें।",

        // रोग जांच पृष्ठ (Detection Page)
        "detect.badge": "AI स्क्रीनिंग सहायक • ResNet-18",
        "detect.heading": "कुत्तों के त्वचा रोग की जांच",
        "detect.subtitle": "संभावित त्वचा रोग पैटर्न का विश्लेषण करने के लिए अपने कुत्ते या प्रभावित त्वचा की स्पष्ट तस्वीर अपलोड करें।",
        "detect.upload_card_title": "कुत्ते की तस्वीर अपलोड करें",
        "detect.dropzone_text": "कुत्ते की तस्वीर यहाँ ड्रैग और ड्रॉप करें",
        "detect.dropzone_subtext": "JPG, JPEG, PNG, WEBP फॉर्मेट समर्थित (अधिकतम 16MB)",
        "detect.browse_btn": "तस्वीर चुनें",
        "detect.btn_remove": "हटाएं",
        "detect.btn_analyze": "तस्वीर का विश्लेषण करें",
        "detect.loading_text": "तस्वीर का विश्लेषण किया जा रहा है...",
        "detect.loading_subtext": "कुत्ता सत्यापन एवं ResNet-18 रोग विश्लेषण प्रगति पर है",
        "detect.demo_title": "त्वरित डेमो नमूने",
        "detect.sample_healthy": "स्वस्थ कुत्ता",
        "detect.sample_bacterial": "बैक्टीरियल संक्रमण",
        "detect.sample_fungal": "फंगल इन्फेक्शन",
        "detect.sample_allergic": "एलर्जिक डर्मेटोसिस",
        "detect.sample_nondog": "गैर-कुत्ता अस्वीकृति टेस्ट",

        "detect.tab_upload": "तस्वीर अपलोड करें",
        "detect.tab_camera": "कैमरे से स्कैन करें",
        "detect.btn_capture": "तस्वीर लें",
        "detect.btn_retake": "फिर से तस्वीर लें",
        "detect.btn_flip_camera": "कैमरा बदलें",
        "detect.btn_cancel_camera": "रद्द करें",
        "detect.dog_verified": "कुत्ता पहचाना गया ✓",
        "detect.camera_live": "लाइव कैमरा फीड",
        "detect.camera_hint": "कुत्ते या त्वचा के प्रभावित हिस्से को फ्रेम के बीच में रखें",

        // स्थितियां (States)
        "detect.awaiting_title": "तस्वीर अपलोड की प्रतीक्षा है",
        "detect.awaiting_desc": "ऊपर दी गई तस्वीर चुनें या वास्तविक AI परीक्षण देखने के लिए डेमो नमूनों पर क्लिक करें।",
        "detect.rejection_title": "कुत्ता नहीं पहचाना गया",
        "detect.rejection_desc": "कुत्ता नहीं पहचाना गया। कृपया कुत्ते की एक स्पष्ट तस्वीर अपलोड करें या कैमरे से लें।",
        "detect.btn_retry": "दूसरी तस्वीर आज़माएं",

        // परिणाम कार्ड (Results Card)
        "result.badge_condition": "स्थिति",
        "result.confidence_label": "AI सटीकता / आत्मविश्वास",
        "result.probabilities_title": "श्रेणी संभावनाएं (4 श्रेणियां)",
        "result.primary_match": "प्राथमिक परिणाम",
        "result.btn_find_vet": "नज़दीकी पशु चिकित्सक (Vet) खोजें",
        "result.btn_locating_vet": "नज़दीकी क्लिनिक खोज रहे हैं...",
        "result.btn_download_pdf": "PDF रिपोर्ट डाउनलोड करें",
        "result.btn_download_pdf_loading": "PDF रिपोर्ट तैयार हो रही है...",
        "result.btn_view_explanation": "AI व्याख्या देखें",
        "result.btn_hide_explanation": "AI व्याख्या छुपाएं",
        "result.visible_signs_title": "दृश्य नैदानिक लक्षण",
        "result.vet_care_title": "अनुशंसित पशु चिकित्सा देखभाल",
        "result.disclaimer_title": "महत्वपूर्ण सूचना:",
        "result.disclaimer_text": "यह AI स्क्रीनिंग परिणाम केवल एक शैक्षिक और सहायक साधन है। यह कोई अंतिम नैदानिक पशु चिकित्सा निदान नहीं है। यदि आपके कुत्ते को दर्द, खुजली या त्वचा संबंधी समस्या है, तो कृपया प्रमाणित पशु चिकित्सक से परामर्श लें।",

        // AI व्याख्या (Grad-CAM)
        "explanation.heading": "AI व्याख्या",
        "explanation.subtitle": "देखें कि तस्वीर के किन क्षेत्रों ने AI पूर्वानुमान में सबसे अधिक योगदान दिया।",
        "explanation.card_original": "मूल तस्वीर",
        "explanation.card_gradcam": "AI ध्यान / GRAD-CAM",
        "explanation.notice": "हाइलाइट किए गए क्षेत्र उन हिस्सों को दर्शाते हैं जिन्होंने मॉडल के पूर्वानुमान में मजबूत योगदान दिया।",
        "explanation.legend_low": "कम प्रभाव",
        "explanation.legend_high": "अधिक प्रभाव",
        "explanation.btn_download": "व्याख्या तस्वीर डाउनलोड करें",
        "explanation.fallback_msg": "AI व्याख्या वर्तमान में अनुपलब्ध है, लेकिन रोग जांच परिणाम उपलब्ध है।",

        // ट्रेनिंग पृष्ठ (Training Page)
        "training.badge": "मॉडल प्रशासन",
        "training.title": "मॉडल ट्रेनिंग और डेटासेट प्रबंधन",
        "training.subtitle": "ResNet-18 मॉडल को पुनः प्रशिक्षित करने के लिए 4 श्रेणियों वाली ZIP फ़ाइल अपलोड करें।",
        "training.dropzone_text": "डेटासेट ZIP फ़ाइल यहाँ ड्रॉप करें",
        "training.dropzone_subtext": "इसमें Bacterial_dermatosis, Fungal_infections, Healthy, Hypersensitivity_allergic_dermatosis फ़ोल्डर होने चाहिए",
        "training.btn_validate": "डेटासेट सत्यापित करें",
        "training.btn_start": "ट्रेनिंग शुरू करें (15 एपोक्स)",

        // पादलेख (Footer)
        "footer.tagline": "कुत्ता त्वचा रोग पहचान प्रणाली। PyTorch ResNet-18 ट्रांसफर लर्निंग द्वारा संचालित।",
        "footer.copyright": "© 2026 पॉकेयर AI. सर्वाधिकार सुरक्षित।",

        // रोग विवरण (Disease Clinical Data)
        "disease.Bacterial_dermatosis.name": "बैक्टीरियल डर्मेटोसिस (जीवाणु त्वचा संक्रमण)",
        "disease.Bacterial_dermatosis.signs": [
            "त्वचा पर लालिमा, चकत्ते और सूजन",
            "पपड़ी जमना, छिलके उतरना या घाव बनना",
            "मवाद वाले दाने या सक्रिय त्वचा संक्रमण",
            "गंभीर खुजली और बालों की जड़ों में सूजन"
        ],
        "disease.Bacterial_dermatosis.recommendation": "सटीक एंटीबायोटिक या सामयिक उपचार के लिए साइटोलॉजी और जीवाणु संवर्धन हेतु पशु चिकित्सक से परामर्श करें।",

        "disease.Fungal_infections.name": "फंगल इन्फेक्शन (फफूंद संक्रमण)",
        "disease.Fungal_infections.signs": [
            "गोल घेरों में बालों का झड़ना (रिंगवर्म)",
            "रूखी, पपड़ीदार या परतदार त्वचा के धब्बे",
            "त्वचा का लाल या गहरा रंग होना",
            "लगातार खुजली और त्वचा में जलन"
        ],
        "disease.Fungal_infections.recommendation": "फफूंद के प्रकार की पुष्टि और एंटीफंगल दवाइयों के लिए पशु चिकित्सक द्वारा जांच आवश्यक है।",

        "disease.Healthy.name": "स्वस्थ (हेल्दी)",
        "disease.Healthy.signs": [
            "घाव या दानों से रहित साफ और स्वस्थ त्वचा",
            "समान और घने बालों की परत",
            "लालिमा या सूजन का अभाव"
        ],
        "disease.Healthy.recommendation": "नियमित ग्रूमिंग, परजीवी नियंत्रण और नियमित स्वास्थ्य जांच बनाए रखें।",

        "disease.Hypersensitivity_allergic_dermatosis.name": "एलर्जिक डर्मेटोसिस (अतिसंवेदनशीलता)",
        "disease.Hypersensitivity_allergic_dermatosis.signs": [
            "अत्यधिक खुजली, खरोंचना, पंजे चाटना या रगड़ना",
            "कानों के भीतरी भाग या चेहरे पर लालिमा",
            "बार-बार खरोंचने के कारण बालों का गिरना",
            "त्वचा में बार-बार होने वाली जलन और एलर्जी"
        ],
        "disease.Hypersensitivity_allergic_dermatosis.recommendation": "एलर्जी के कारणों (भोजन, पिस्सू या वातावरण) की पहचान और प्रबंधन के लिए पशु चिकित्सक से संपर्क करें।"
    }
};

/**
 * Gets the current active language (stored in localStorage or defaults to 'en').
 */
function getCurrentLanguage() {
    const saved = localStorage.getItem("pawcare_lang");
    if (saved && (saved === "en" || saved === "te" || saved === "hi")) {
        return saved;
    }
    return "en";
}

/**
 * Returns translation for a specific key, falling back to English or fallback string.
 */
function t(key, fallback = "") {
    const lang = getCurrentLanguage();
    if (PAWCARE_TRANSLATIONS[lang] && PAWCARE_TRANSLATIONS[lang][key] !== undefined) {
        return PAWCARE_TRANSLATIONS[lang][key];
    }
    if (PAWCARE_TRANSLATIONS.en && PAWCARE_TRANSLATIONS.en[key] !== undefined) {
        return PAWCARE_TRANSLATIONS.en[key];
    }
    return fallback || key;
}

/**
 * Retrieves localized clinical disease information for a canonical disease class key.
 */
function getLocalizedDiseaseInfo(classKey, lang = null) {
    if (!lang) lang = getCurrentLanguage();
    const dict = PAWCARE_TRANSLATIONS[lang] || PAWCARE_TRANSLATIONS.en;
    const name = dict[`disease.${classKey}.name`] || classKey;
    const signs = dict[`disease.${classKey}.signs`] || [];
    const recommendation = dict[`disease.${classKey}.recommendation`] || "";

    return {
        name,
        signs,
        recommendation
    };
}

/**
 * Applies the selected language across all DOM elements tagged with [data-i18n].
 */
function applyLanguage(lang) {
    if (!lang || (lang !== "en" && lang !== "te" && lang !== "hi")) {
        lang = "en";
    }
    localStorage.setItem("pawcare_lang", lang);

    // Update Language Selector Active State
    const langButtons = document.querySelectorAll(".lang-btn, .lang-option-btn");
    langButtons.forEach(btn => {
        if (btn.getAttribute("data-lang") === lang) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    // Translate DOM nodes with data-i18n
    const translatableNodes = document.querySelectorAll("[data-i18n]");
    translatableNodes.forEach(node => {
        const key = node.getAttribute("data-i18n");
        const translation = t(key);
        if (translation) {
            // Check if translation contains HTML (like <br>)
            if (translation.includes("<") && translation.includes(">")) {
                node.innerHTML = translation;
            } else {
                node.textContent = translation;
            }
        }
    });

    // Dispatch custom event for dynamic components (like live prediction results)
    window.dispatchEvent(new CustomEvent("pawcare_language_changed", { detail: { language: lang } }));
}

// Global initialization helper
function initLanguageSelector() {
    const currentLang = getCurrentLanguage();
    applyLanguage(currentLang);

    // Dropdown toggle logic
    const dropdownBtn = document.getElementById("langDropdownBtn");
    const dropdownWrapper = document.getElementById("langDropdownWrapper");

    if (dropdownBtn && dropdownWrapper) {
        dropdownBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            const isOpen = dropdownWrapper.classList.toggle("open");
            dropdownBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });

        // Close dropdown when clicking anywhere outside
        document.addEventListener("click", (e) => {
            if (!dropdownWrapper.contains(e.target)) {
                dropdownWrapper.classList.remove("open");
                dropdownBtn.setAttribute("aria-expanded", "false");
            }
        });

        // Close on Escape key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && dropdownWrapper.classList.contains("open")) {
                dropdownWrapper.classList.remove("open");
                dropdownBtn.setAttribute("aria-expanded", "false");
                dropdownBtn.focus();
            }
        });
    }

    // Bind option click handlers
    const langButtons = document.querySelectorAll(".lang-option-btn, .lang-btn");
    langButtons.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            const targetLang = btn.getAttribute("data-lang");
            if (targetLang) {
                applyLanguage(targetLang);
                if (dropdownWrapper) {
                    dropdownWrapper.classList.remove("open");
                }
                if (dropdownBtn) {
                    dropdownBtn.setAttribute("aria-expanded", "false");
                }
            }
        });
    });
}
