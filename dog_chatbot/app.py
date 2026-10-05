import os
import json
from pathlib import Path

from flask import (
    Flask,
    request,
    jsonify,
    render_template
)

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / "chatbot sample.env"

VECTOR_STORE_FILE = BASE_DIR / "vector_store_id.txt"

MODEL = "gpt-5"


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    dotenv_path=ENV_FILE
)


API_KEY = os.getenv(
    "OPENAI_API_KEY"
)


if not API_KEY:

    raise ValueError(

        "\nOPENAI_API_KEY was not found.\n\n"

        f"Expected file:\n{ENV_FILE}\n\n"

        "Make sure your file contains:\n"

        "OPENAI_API_KEY=your_actual_api_key\n"

    )


print(
    "========================================"
)

print(
    "OpenAI API key loaded successfully."
)

print(
    "========================================"
)


# ============================================================
# 3. CREATE OPENAI CLIENT
# ============================================================

client = OpenAI(
    api_key=API_KEY
)


# ============================================================
# 4. CREATE FLASK APPLICATION
# ============================================================

app = Flask(
    __name__
)
@app.route("/api/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json()

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "reply": "Please enter a message."
            }), 400

        response = client.responses.create(
            model="gpt-5-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are PawCare AI, an educational dog health "
                        "assistant. Provide general information about dog "
                        "health and skin conditions. Do not claim to provide "
                        "a confirmed veterinary diagnosis. Encourage the "
                        "user to consult a veterinarian for serious or "
                        "persistent symptoms."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        reply = response.output_text

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        print("CHATBOT ERROR:", e)

        return jsonify({
            "reply": "Sorry, I could not process your request right now."
        }), 500


# ============================================================
# 5. LOAD VECTOR STORE ID
# ============================================================

if not VECTOR_STORE_FILE.exists():

    raise ValueError(

        "\nvector_store_id.txt was not found.\n\n"

        "Please run:\n"

        "python ingest.py\n\n"

        "first."

    )


VECTOR_STORE_ID = (

    VECTOR_STORE_FILE

    .read_text(
        encoding="utf-8"
    )

    .strip()

)


if not VECTOR_STORE_ID:

    raise ValueError(

        "\nvector_store_id.txt is empty.\n\n"

        "Please run:\n"

        "python ingest.py"

    )


print(
    "\nVector Store:"
)

print(
    VECTOR_STORE_ID
)


# ============================================================
# 6. SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are a veterinary information assistant for a
dog skin disease detection website.

Your purpose is to provide educational information
about canine skin diseases.

IMPORTANT RULES:

1. Use information retrieved from the veterinary
knowledge base as the primary source.

2. Do not invent veterinary facts that are not
supported by the retrieved knowledge.

3. If the knowledge base does not provide enough
information to answer a question, clearly say that
the available knowledge base does not provide enough
information.

4. The detected disease comes from a machine-learning
image classification model.

5. The predicted disease is NOT a confirmed veterinary
diagnosis.

6. Never present an image-model prediction as a
confirmed diagnosis.

7. Do not guarantee that a dog has a particular disease.

8. Do not prescribe medication.

9. Do not provide unsafe medication dosages.

10. If the user asks whether a particular medicine is
appropriate, explain that medication decisions should
be made by a veterinarian.

11. Provide educational information only.

12. Use simple language suitable for a dog owner.

13. When appropriate, organize answers using:

- What it means
- Common signs
- Possible causes
- General care
- Prevention
- When to see a veterinarian

14. Encourage veterinary consultation when symptoms are
severe, persistent, rapidly worsening, painful, associated
with fever, lethargy, extensive lesions, or other concerning
signs.

15. Never tell a user to ignore serious symptoms.

16. Do not claim certainty based only on an image.

17. If the user asks something unrelated to dog skin
diseases, politely explain that your main purpose is to
provide information about canine skin conditions.

"""


# ============================================================
# 7. GENERATE RAG ANSWER
# ============================================================

def generate_answer(

    user_message,

    detected_disease=None,

    confidence=None,

    conversation=None

):

    if conversation is None:

        conversation = []


    # --------------------------------------------------------
    # Disease context
    # --------------------------------------------------------

    disease_context = (

        "No disease prediction was provided."

    )


    if detected_disease:

        disease_context = (

            f"Predicted disease from the website's "
            f"machine-learning model: {detected_disease}"

        )


    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence_text = ""


    if confidence is not None:

        try:

            confidence_value = float(
                confidence
            )


            if confidence_value <= 1:

                confidence_value *= 100


            confidence_text = (

                f"\nModel confidence: "
                f"{confidence_value:.2f}%"

            )


        except (
            ValueError,
            TypeError
        ):

            confidence_text = ""


    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    history = json.dumps(

        conversation[-10:],

        ensure_ascii=False

    )


    # --------------------------------------------------------
    # RAG prompt
    # --------------------------------------------------------

    prompt = f"""

DETECTED DISEASE INFORMATION

{disease_context}

{confidence_text}


USER QUESTION

{user_message}


PREVIOUS CONVERSATION

{history}


TASK

Answer the user's question using information retrieved
from the veterinary knowledge base.

The veterinary knowledge base is the primary source.

If the knowledge base does not support a statement,
do not present that statement as a fact.

Remember that the detected disease is only a prediction
from the website's machine-learning model and is not a
confirmed veterinary diagnosis.

"""


    # ========================================================
    # RESPONSES API + FILE SEARCH
    # ========================================================

    response = client.responses.create(

        model=MODEL,

        instructions=SYSTEM_PROMPT,

        tools=[

            {

                "type": "file_search",

                "vector_store_ids": [

                    VECTOR_STORE_ID

                ],

                "max_num_results": 6

            }

        ],

        input=prompt

    )


    return response.output_text


# ============================================================
# 8. CHAT API
# ============================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({

                "error":
                "Request body is empty."

            }), 400


        # ----------------------------------------------------
        # User message
        # ----------------------------------------------------

        message = (

            data.get(
                "message",
                ""
            )

            .strip()

        )


        if not message:

            return jsonify({

                "error":
                "Please enter a question."

            }), 400


        # ----------------------------------------------------
        # Disease
        # ----------------------------------------------------

        detected_disease = data.get(

            "detected_disease"

        )


        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = data.get(

            "confidence"

        )


        # ----------------------------------------------------
        # Conversation
        # ----------------------------------------------------

        conversation = data.get(

            "conversation",
            []

        )


        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        answer = generate_answer(

            user_message=
            message,

            detected_disease=
            detected_disease,

            confidence=
            confidence,

            conversation=
            conversation

        )


        return jsonify({

            "answer":
            answer,

            "detected_disease":
            detected_disease,

            "confidence":
            confidence

        })


    except Exception as e:

        print(
            "\nERROR:"
        )

        print(
            str(e)
        )


        return jsonify({

            "error":
            "An error occurred while generating the answer.",

            "details":
            str(e)

        }), 500


# ============================================================
# 9. HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "frontend.html"
    )


# ============================================================
# 10. HEALTH CHECK
# ============================================================

@app.route(
    "/health"
)
def health():

    return jsonify({

        "status":
        "running",

        "vector_store":
        VECTOR_STORE_ID

    })


# ============================================================
# 11. RUN SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "DOG SKIN DISEASE RAG CHATBOT"
    )

    print(
        "========================================"
    )

    print(
        "\nOpen this URL:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "\n========================================"
    )


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
