"""
PawCare AI – Professional PDF Health Report Generator
======================================================
Generates an official PawCare AI veterinary screening PDF report
using ReportLab with full multi-language support (English, Telugu, Hindi).
Incorporates prediction outcomes, 4-class probabilities, visual side-by-side
image comparison (Original + Grad-CAM heatmap), clinical signs, care guidelines,
and medical disclaimers.
"""

from __future__ import annotations

import datetime
import io
import logging
import os
from typing import Any

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus import Image as RLImage

logger = logging.getLogger("PawCareAI.PDFReport")

# Color Palette (Matching PawCare AI Web Design)
PRIMARY_GREEN = colors.HexColor("#1b4332")     # Deep forest green
ACCENT_GREEN = colors.HexColor("#2d6a4f")      # Rich emerald green
LIGHT_BG = colors.HexColor("#e8f5e9")          # Soft mint background
BORDER_GREEN = colors.HexColor("#b7e4c7")      # Light green border
DARK_TEXT = colors.HexColor("#1f2937")         # Charcoal text
MUTED_TEXT = colors.HexColor("#4b5563")        # Secondary text
ALERT_BORDER = colors.HexColor("#fbbf24")      # Disclaimer amber border
ALERT_BG = colors.HexColor("#fffbeb")          # Disclaimer soft cream

# -----------------------------------------------------------------------------
# Font Registration for Indic Script (Telugu & Devanagari/Hindi)
# -----------------------------------------------------------------------------
HAS_TELUGU_FONT = False
HAS_DEVANAGARI_FONT = False

devanagari_paths = [
    "/System/Library/Fonts/Supplemental/DevanagariMT.ttc",
    "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc",
    "/Library/Fonts/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
]
for p in devanagari_paths:
    if os.path.exists(p):
        try:
            if p.endswith(".ttc"):
                pdfmetrics.registerFont(TTFont("Devanagari", p, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont("Devanagari", p))
            HAS_DEVANAGARI_FONT = True
            break
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Could not load Devanagari font from {p}: {e}")

telugu_paths = [
    "/System/Library/Fonts/Supplemental/Telugu MN.ttc",
    "/System/Library/Fonts/Supplemental/Telugu Sangam MN.ttc",
    "/Library/Fonts/NotoSansTelugu-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf"
]
for p in telugu_paths:
    if os.path.exists(p):
        try:
            if p.endswith(".ttc"):
                pdfmetrics.registerFont(TTFont("Telugu", p, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont("Telugu", p))
            HAS_TELUGU_FONT = True
            break
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Could not load Telugu font from {p}: {e}")


# -----------------------------------------------------------------------------
# Multilingual Report String Dictionaries
# -----------------------------------------------------------------------------
REPORT_STRINGS = {
    "en": {
        "title": "PAWCARE AI",
        "subtitle": "Dog Skin Disease Analysis Report",
        "meta_prefix": "Analysis Date & Time:",
        "card_condition": "PREDICTED CONDITION",
        "card_confidence": "AI SCREENING CONFIDENCE",
        "primary_match": "Primary Match",
        "prob_title": "PROBABILITY BREAKDOWN (4 CATEGORIES)",
        "th_category": "Class Category",
        "th_metric": "Confidence Metric",
        "vis_title": "AI EXPLANATION & VISUAL INSPECTION",
        "vis_orig": "Uploaded Dog Image",
        "vis_gradcam": "AI Attention / Grad-CAM",
        "vis_cam_unavailable": "AI explanation visualization was unavailable for this analysis.",
        "vis_caption": "Highlighted regions indicate areas that contributed strongly to the model's prediction. Grad-CAM is an explanatory tool and does not prove the presence or absence of disease.",
        "edu_title": "EDUCATIONAL INFORMATION & CARE GUIDANCE",
        "signs_title": "Possible Characteristic Signs:",
        "rec_title": "Recommended Veterinary Care:",
        "disclaimer_header": "IMPORTANT VETERINARY DISCLAIMER",
        "footer_text": "PawCare AI • Educational AI Screening Tool • Healthy Pets, Happier Lives\nPowered by ResNet-18 Computer Vision & PyTorch"
    },
    "te": {
        "title": "పాకేర్ AI (PAWCARE AI)",
        "subtitle": "కుక్క చర్మ వ్యాధి విశ్లేషణ నివేదిక (Dog Skin Disease Report)",
        "meta_prefix": "విశ్లేషణ తేదీ & సమయం (Date & Time):",
        "card_condition": "గుర్తించబడిన పరిస్థితి (CONDITION)",
        "card_confidence": "AI ఖచ్చితత్వం (CONFIDENCE)",
        "primary_match": "ప్రధాన ఫలితం",
        "prob_title": "సంభావ్యత వివరాలు (4 వర్గాలు)",
        "th_category": "వ్యాధి వర్గం (Category)",
        "th_metric": "శాతం (Probability)",
        "vis_title": "AI వివరణ & దృశ్య పరిశీలన (VISUAL INSPECTION)",
        "vis_orig": "అప్‌లోడ్ చేసిన కుక్క ఫోటో",
        "vis_gradcam": "AI శ్రద్ధ / GRAD-CAM హీట్‌మ్యాప్",
        "vis_cam_unavailable": "ఈ విశ్లేషణకు AI వివరణ చిత్రం అందుబాటులో లేదు.",
        "vis_caption": "హైలైట్ చేయబడిన ప్రాంతాలు మోడల్ యొక్క నిర్ణయానికి బలంగా దోహదపడిన భాగాలను సూచిస్తాయి. Grad-CAM అనేది సహాయక వివరణ సాధనం మాత్రమే.",
        "edu_title": "విద్యా సమాచారం & పశువైద్య సంరక్షణ సలహా",
        "signs_title": "కనిపించే క్లినికల్ లక్షణాలు:",
        "rec_title": "సిఫార్సు చేయబడిన పశువైద్య సంరక్షణ:",
        "disclaimer_header": "ముఖ్యమైన పశువైద్య గమనిక (VETERINARY DISCLAIMER)",
        "footer_text": "పాకేర్ AI • విద్యా AI స్క్రీనింగ్ సాధనం • ఆరోగ్యకరమైన పెంపుడు జంతువులు\nPyTorch ResNet-18 ఆధారితం"
    },
    "hi": {
        "title": "पॉकेयर AI (PAWCARE AI)",
        "subtitle": "कुत्ता त्वचा रोग विश्लेषण रिपोर्ट (Dog Skin Disease Report)",
        "meta_prefix": "विश्लेषण तिथि एवं समय (Date & Time):",
        "card_condition": "अनुमानित स्थिति (CONDITION)",
        "card_confidence": "AI सटीकता (CONFIDENCE)",
        "primary_match": "प्राथमिक परिणाम",
        "prob_title": "संभाव्यता विवरण (4 श्रेणियां)",
        "th_category": "रोग श्रेणी (Category)",
        "th_metric": "प्रतिशत (Probability)",
        "vis_title": "AI व्याख्या एवं दृश्य निरीक्षण (VISUAL INSPECTION)",
        "vis_orig": "अपलोड की गई तस्वीर",
        "vis_gradcam": "AI ध्यान / GRAD-CAM हीटमैप",
        "vis_cam_unavailable": "इस विश्लेषण के लिए AI व्याख्या उपलब्ध नहीं थी।",
        "vis_caption": "हाइलाइट किए गए क्षेत्र उन हिस्सों को दर्शाते हैं जिन्होंने मॉडल के पूर्वानुमान में मजबूत योगदान दिया। यह कोई निश्चित निदान नहीं है।",
        "edu_title": "शैक्षिक जानकारी एवं पशु चिकित्सा देखभाल सलाह",
        "signs_title": "संभावित नैदानिक लक्षण:",
        "rec_title": "अनुशंसित पशु चिकित्सा देखभाल:",
        "disclaimer_header": "महत्वपूर्ण पशु चिकित्सा सूचना (VETERINARY DISCLAIMER)",
        "footer_text": "पॉकेयर AI • शैक्षिक AI स्क्रीनिंग साधन • स्वस्थ पालतू, खुशहाल जीवन\nPyTorch ResNet-18 द्वारा संचालित"
    }
}


def get_scaled_reportlab_image(pil_img: Image.Image, max_w: float, max_h: float) -> RLImage:
    """
    Converts a PIL Image into a ReportLab Flowable Image while strictly
    preserving the original aspect ratio within (max_w, max_h).
    """
    w, h = pil_img.size
    aspect = w / float(h)

    target_w = max_w
    target_h = target_w / aspect

    if target_h > max_h:
        target_h = max_h
        target_w = target_h * aspect

    buf = io.BytesIO()
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    pil_img.save(buf, format="JPEG", quality=92)
    buf.seek(0)

    return RLImage(buf, width=target_w, height=target_h)


def generate_health_report(
    prediction_data: dict[str, Any],
    original_pil: Image.Image | None = None,
    gradcam_pil: Image.Image | None = None,
    analysis_date: str | None = None,
    lang: str = "en"
) -> bytes:
    """
    Generates a professional PDF analysis report in bytes with multi-language support.

    Args:
        prediction_data: Dictionary containing prediction info, breakdown, signs, care, etc.
        original_pil: Optional PIL Image of the uploaded dog.
        gradcam_pil: Optional PIL Image of the Grad-CAM overlay.
        analysis_date: Optional formatted timestamp string.
        lang: Selected language code ('en', 'te', 'hi').

    Returns:
        bytes of the generated PDF file.
    """
    if lang not in ["en", "te", "hi"]:
        lang = "en"

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    usable_width = letter[0] - 72  # 540 points

    # Font Selection
    if lang == "te" and HAS_TELUGU_FONT:
        base_font = "Telugu"
        bold_font = "Telugu"
    elif lang == "hi" and HAS_DEVANAGARI_FONT:
        base_font = "Devanagari"
        bold_font = "Devanagari"
    else:
        base_font = "Helvetica"
        bold_font = "Helvetica-Bold"

    r_str = REPORT_STRINGS.get(lang, REPORT_STRINGS["en"])

    # Styles Setup
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PawCareTitle",
        parent=styles["Normal"],
        fontName=bold_font,
        fontSize=22,
        leading=26,
        textColor=PRIMARY_GREEN,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        "PawCareSubtitle",
        parent=styles["Normal"],
        fontName=bold_font,
        fontSize=12,
        leading=16,
        textColor=ACCENT_GREEN,
        alignment=1
    )

    meta_style = ParagraphStyle(
        "PawCareMeta",
        parent=styles["Normal"],
        fontName=base_font,
        fontSize=9,
        leading=13,
        textColor=MUTED_TEXT,
        alignment=1
    )

    section_heading_style = ParagraphStyle(
        "PawCareSectionHeading",
        parent=styles["Normal"],
        fontName=bold_font,
        fontSize=11.5,
        leading=15,
        textColor=PRIMARY_GREEN
    )

    card_title_style = ParagraphStyle(
        "PawCareCardTitle",
        parent=styles["Normal"],
        fontName=bold_font,
        fontSize=14,
        leading=18,
        textColor=PRIMARY_GREEN
    )

    card_label_style = ParagraphStyle(
        "PawCareCardLabel",
        parent=styles["Normal"],
        fontName=base_font,
        fontSize=8.5,
        leading=12,
        textColor=MUTED_TEXT
    )

    confidence_num_style = ParagraphStyle(
        "PawCareConfNum",
        parent=styles["Normal"],
        fontName=bold_font,
        fontSize=18,
        leading=22,
        textColor=ACCENT_GREEN,
        alignment=2
    )

    body_style = ParagraphStyle(
        "PawCareBody",
        parent=styles["Normal"],
        fontName=base_font,
        fontSize=9,
        leading=13.5,
        textColor=DARK_TEXT
    )

    bullet_style = ParagraphStyle(
        "PawCareBullet",
        parent=styles["Normal"],
        fontName=base_font,
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT
    )

    disclaimer_style = ParagraphStyle(
        "PawCareDisclaimer",
        parent=styles["Normal"],
        fontName=base_font,
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#78350f")
    )

    footer_style = ParagraphStyle(
        "PawCareFooter",
        parent=styles["Normal"],
        fontName=base_font,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6b7280"),
        alignment=1
    )

    elements = []

    # 1. HEADER BRANDING BANNER
    elements.append(Paragraph(f"<b>{r_str['title']}</b>", title_style))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph(r_str["subtitle"], subtitle_style))
    elements.append(Spacer(1, 4))

    if not analysis_date:
        analysis_date = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%B %d, %Y • %I:%M %p")
    elements.append(Paragraph(f"{r_str['meta_prefix']} <b>{analysis_date}</b>", meta_style))
    elements.append(Spacer(1, 6))

    elements.append(HRFlowable(
        width="100%", thickness=1, color=BORDER_GREEN,
        spaceBefore=2, spaceAfter=8
    ))

    # 2. SCREENING SUMMARY CARD (Condition & Confidence)
    pred_name = prediction_data.get("predicted_friendly_name", "Unknown Condition")
    conf_pct = prediction_data.get("confidence_pct", 0.0)

    condition_name_style = card_title_style
    specific_disease = prediction_data.get("specific_disease")
    summary_left = [
        Paragraph(r_str["card_condition"], card_label_style),
        Paragraph(f"<b>{pred_name}</b>", condition_name_style)
    ]
    if specific_disease:
        summary_left.append(Paragraph(f"<i>Possible Specific Condition: {specific_disease}</i>", ParagraphStyle("SpecDis", parent=body_style, fontSize=9, textColor=MUTED_TEXT)))
    summary_right = [
        Paragraph(r_str["card_confidence"], ParagraphStyle("RAlign", parent=card_label_style, alignment=2)),
        Spacer(1, 2),
        Paragraph(f"<b>{conf_pct:.2f}%</b>", confidence_num_style)
    ]

    summary_table = Table(
        [[summary_left, summary_right]],
        colWidths=[usable_width * 0.65, usable_width * 0.35]
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_GREEN),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8))

    # 3. PROBABILITY BREAKDOWN TABLE
    elements.append(Paragraph(f"<b>{r_str['prob_title']}</b>", section_heading_style))
    elements.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph(f"<b>{r_str['th_category']}</b>", ParagraphStyle("TH", parent=body_style, fontName=bold_font, textColor=PRIMARY_GREEN)),
            Paragraph(f"<b>{r_str['th_metric']}</b>", ParagraphStyle("TH2", parent=body_style, fontName=bold_font, textColor=PRIMARY_GREEN, alignment=2))
        ]
    ]

    breakdown = prediction_data.get("classes_breakdown", [])
    for item in breakdown:
        fname = item.get("friendly_name", "")
        pct = item.get("probability_pct", 0.0)
        is_winner = (fname.lower() == pred_name.lower())

        row_label = f"<b>{fname}</b> ({r_str['primary_match']})" if is_winner else fname
        row_val = f"<b>{pct:.2f}%</b>" if is_winner else f"{pct:.2f}%"

        table_data.append([
            Paragraph(row_label, body_style),
            Paragraph(row_val, ParagraphStyle("PVal", parent=body_style, alignment=2))
        ])

    prob_table = Table(table_data, colWidths=[usable_width * 0.75, usable_width * 0.25])
    prob_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
    ]))
    elements.append(prob_table)
    elements.append(Spacer(1, 8))

    # 4. VISUAL INSPECTION & GRAD-CAM EXPLAINABILITY
    elements.append(Paragraph(f"<b>{r_str['vis_title']}</b>", section_heading_style))
    elements.append(Spacer(1, 4))

    max_img_dim = 115

    # Left cell: Uploaded image
    if original_pil is not None:
        try:
            rl_orig = get_scaled_reportlab_image(original_pil, max_w=240, max_h=max_img_dim)
            orig_cell = [
                Paragraph(f"<b>{r_str['vis_orig']}</b>", ParagraphStyle("Cap", parent=card_label_style, alignment=1)),
                Spacer(1, 3),
                rl_orig
            ]
        except Exception as e:  # noqa: BLE001
            logger.debug("Failed rendering original image in PDF: %s", e)
            orig_cell = [Paragraph(r_str["vis_orig"], body_style)]
    else:
        orig_cell = [Paragraph(r_str["vis_orig"], body_style)]

    # Right cell: Grad-CAM explanation image
    if gradcam_pil is not None:
        try:
            rl_cam = get_scaled_reportlab_image(gradcam_pil, max_w=240, max_h=max_img_dim)
            cam_cell = [
                Paragraph(f"<b>{r_str['vis_gradcam']}</b>", ParagraphStyle("Cap2", parent=card_label_style, alignment=1)),
                Spacer(1, 3),
                rl_cam
            ]
        except Exception as e:  # noqa: BLE001
            logger.debug("Failed rendering Grad-CAM image in PDF: %s", e)
            cam_cell = [Paragraph(r_str["vis_cam_unavailable"], body_style)]
    else:
        cam_cell = [
            Spacer(1, 15),
            Paragraph(f"<i>{r_str['vis_cam_unavailable']}</i>", body_style)
        ]

    img_table = Table([[orig_cell, cam_cell]], colWidths=[usable_width * 0.5, usable_width * 0.5])
    img_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(img_table)
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<i>{r_str['vis_caption']}</i>", meta_style))
    elements.append(Spacer(1, 8))

    # 5. EDUCATIONAL INFORMATION & CLINICAL SIGNS
    disease_info = prediction_data.get("disease_info", {})
    signs = disease_info.get("signs", [])
    recommendation = disease_info.get("recommendation", "")

    edu_elements = []
    edu_elements.append(Paragraph(f"<b>{r_str['edu_title']}</b>", section_heading_style))
    edu_elements.append(Spacer(1, 4))

    detailed = prediction_data.get("detailed_analysis") or {}
    ai_analysis_text = detailed.get("ai_analysis") or prediction_data.get("ai_analysis")
    if ai_analysis_text:
        edu_elements.append(Paragraph("<b>AI Clinical Evaluation:</b>", body_style))
        edu_elements.append(Paragraph(ai_analysis_text, ParagraphStyle("AIAnalysisP", parent=body_style, fontSize=8.5, textColor=MUTED_TEXT)))
        edu_elements.append(Spacer(1, 3))

    if signs:
        edu_elements.append(Paragraph(f"<b>{r_str['signs_title']}</b>", body_style))
        for sign in signs:
            edu_elements.append(Paragraph(f"• {sign}", bullet_style))
        edu_elements.append(Spacer(1, 3))

    precautions = detailed.get("precautions") or prediction_data.get("precautions") or []
    if precautions:
        edu_elements.append(Paragraph("<b>Important Precautions:</b>", body_style))
        for prec in precautions:
            edu_elements.append(Paragraph(f"• {prec}", bullet_style))
        edu_elements.append(Spacer(1, 3))

    if recommendation:
        edu_elements.append(Paragraph(f"<b>{r_str['rec_title']}</b>", body_style))
        edu_elements.append(Paragraph(recommendation, bullet_style))
        edu_elements.append(Spacer(1, 3))

    when_to_see = detailed.get("when_to_see_vet") or prediction_data.get("when_to_see_vet") or []
    if when_to_see:
        edu_elements.append(Paragraph("<b>When to Consult a Veterinarian:</b>", body_style))
        for flag in when_to_see:
            edu_elements.append(Paragraph(f"• {flag}", bullet_style))
        edu_elements.append(Spacer(1, 4))

    elements.append(KeepTogether(edu_elements))

    # 6. MANDATORY MEDICAL DISCLAIMER BOX
    disclaimer_text = prediction_data.get(
        "disclaimer",
        "Important: This AI result is not a veterinary diagnosis. Consult a qualified veterinarian."
    )

    disclaimer_table = Table(
        [[Paragraph(f"<b>{r_str['disclaimer_header']}</b><br/>{disclaimer_text}", disclaimer_style)]],
        colWidths=[usable_width]
    )
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ALERT_BG),
        ("BOX", (0, 0), (-1, -1), 1, ALERT_BORDER),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(Spacer(1, 4))
    elements.append(disclaimer_table)
    elements.append(Spacer(1, 6))

    # 7. DOCUMENT FOOTER
    elements.append(Paragraph(r_str["footer_text"].replace("\n", "<br/>"), footer_style))

    # Build PDF
    doc.build(elements)
    return pdf_buffer.getvalue()
