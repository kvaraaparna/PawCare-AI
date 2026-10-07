
from model.skin_disease import SkinDisease


# ============================================================
# FIND DISEASE FROM USER QUESTION
# ============================================================

def find_disease(message):
    message = message.lower().strip()

    # Get disease records from PostgreSQL
    diseases = SkinDisease.query.all()

    # Fungal infection
    if any(word in message for word in [
        "fungal",
        "fungus",
        "ringworm",
        "yeast"
    ]):
        for disease in diseases:
            if "fungal" in disease.disease_name.lower():
                return disease

    # Bacterial dermatosis
    if any(word in message for word in [
        "bacterial",
        "bacteria",
        "bacterial dermatosis"
    ]):
        for disease in diseases:
            if "bacterial" in disease.disease_name.lower():
                return disease

    # Allergic / hypersensitivity
    if any(word in message for word in [
        "allergy",
        "allergic",
        "hypersensitivity",
        "hypersensitive"
    ]):
        for disease in diseases:
            name = disease.disease_name.lower()

            if (
                "allergic" in name
                or "hypersensitivity" in name
            ):
                return disease

    # Healthy
    if any(word in message for word in [
        "healthy",
        "healthy skin",
        "normal skin"
    ]):
        for disease in diseases:
            if "healthy" in disease.disease_name.lower():
                return disease

    return None


# ============================================================
# CREATE RESPONSE
# ============================================================

def create_response(disease, message):

    message = message.lower()

    disease_name = disease.disease_name

    symptoms = disease.symptoms or "Information not available."

    causes = disease.causes or "Information not available."

    suggestions = (
        disease.suggestions
        or "Please consult a veterinarian for proper advice."
    )

    prevention = (
        disease.prevention
        or "Follow proper hygiene and regular veterinary care."
    )


    # --------------------------------------------------------
    # SYMPTOMS
    # --------------------------------------------------------

    if any(word in message for word in [
        "symptom",
        "symptoms",
        "sign",
        "signs"
    ]):

        return (
            f"🐾 {disease_name}\n\n"
            f"Symptoms:\n{symptoms}"
        )


    # --------------------------------------------------------
    # CAUSES
    # --------------------------------------------------------

    if any(word in message for word in [
        "cause",
        "causes",
        "reason",
        "why"
    ]):

        return (
            f"🐾 {disease_name}\n\n"
            f"Causes:\n{causes}"
        )


    # --------------------------------------------------------
    # SUGGESTIONS / TREATMENT
    # --------------------------------------------------------

    if any(word in message for word in [
        "suggestion",
        "suggestions",
        "treatment",
        "treat",
        "help",
        "what should i do",
        "what can i do"
    ]):

        return (
            f"🐾 {disease_name}\n\n"
            f"Suggestions:\n{suggestions}"
        )


    # --------------------------------------------------------
    # PREVENTION
    # --------------------------------------------------------

    if any(word in message for word in [
        "prevent",
        "prevention",
        "avoid",
        "protect"
    ]):

        return (
            f"🐾 {disease_name}\n\n"
            f"Prevention:\n{prevention}"
        )


    # --------------------------------------------------------
    # DEFAULT: COMPLETE INFORMATION
    # --------------------------------------------------------

    return (
        f"🐾 {disease_name}\n\n"

        f"Symptoms:\n"
        f"{symptoms}\n\n"

        f"Causes:\n"
        f"{causes}\n\n"

        f"Suggestions:\n"
        f"{suggestions}\n\n"

        f"Prevention:\n"
        f"{prevention}"
    )


# ============================================================
# MAIN CHATBOT FUNCTION
# ============================================================

def get_chatbot_response(user_message):

    if not user_message:

        return "Please enter your question."


    message = user_message.strip().lower()


    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if message in [
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii"
    ]:

        return (
            "🐾 Hello! Welcome to PawCare AI.\n\n"

            "I can help you with information about "
            "dog skin diseases.\n\n"

            "Available conditions:\n"
            "• Bacterial Dermatosis\n"
            "• Fungal Infection\n"
            "• Hypersensitivity / Allergic Dermatosis\n"
            "• Healthy\n\n"

            "You can ask about symptoms, causes, "
            "suggestions or prevention."
        )


    # --------------------------------------------------------
    # DATABASE SEARCH
    # --------------------------------------------------------

    try:

        disease = find_disease(message)

    except Exception as e:

        import traceback

        print("\n========== CHATBOT DATABASE ERROR ==========")
        print("ERROR:", repr(e))
        traceback.print_exc()
        print("============================================\n")

        return (
            "Sorry, I could not access the disease database."
        )


    # --------------------------------------------------------
    # DISEASE FOUND
    # --------------------------------------------------------

    if disease:

        print(
            "Disease found:",
            disease.disease_name
        )

        return create_response(
            disease,
            message
        )


    # --------------------------------------------------------
    # DISEASE NOT FOUND
    # --------------------------------------------------------

    return (
        "🐾 I can answer questions about these dog skin "
        "conditions:\n\n"

        "1. Bacterial Dermatosis\n"
        "2. Fungal Infection\n"
        "3. Hypersensitivity / Allergic Dermatosis\n"
        "4. Healthy\n\n"

        "Examples:\n"
        "• What are the symptoms of fungal infection?\n"
        "• What causes bacterial dermatosis?\n"
        "• How can allergic dermatosis be prevented?\n"
        "• What should I do for fungal infection?"
    )