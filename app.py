from flask import Flask, render_template, request, jsonify
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Put your OPENAI_API_KEY in a .env file")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__, static_folder="static", template_folder="templates")

def extract_json_object(text):
    """Try to extract a JSON object from the model output."""
    m = re.search(r"\{(?:.|\n)*\}", text)
    return m.group(0) if m else text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/suggest", methods=["POST"])
def suggest():
    data = request.json or {}
    # Expected fields from frontend
    cuisine = data.get("cuisine", "").strip()
    meal_type = data.get("meal_type", "").strip()
    dietary = data.get("dietary", "").strip()
    allergies = data.get("allergies", "").strip()
    ingredients_on_hand = data.get("ingredients_on_hand", "").strip()
    calories_target = data.get("calories_target", "").strip()

    # Build user prompt
    user_prompt = f"""
You are a helpful cooking assistant. Produce exactly ONE meal suggestion (single meal).
Return only a JSON object (no explanatory text) with the following keys:
- name: short name of the meal (string)
- description: one-sentence description (string)
- ingredients: list of strings (each ingredient with approximate quantity)
- steps: list of strings (short numbered steps)
- calories_estimate: string or number (approximate calories)
- tags: list of strings (e.g., vegetarian, gluten-free)
- shopping_list: list of strings (extra items to buy, if any)

User constraints:
cuisine: {cuisine or 'any'}
meal_type: {meal_type or 'any'}
dietary: {dietary or 'none'}
allergies: {allergies or 'none'}
ingredients_on_hand: {ingredients_on_hand or 'none'}
calories_target: {calories_target or 'none'}

Make the meal practical, use common pantry items, and if ingredients_on_hand is provided, prioritize those.
Keep ingredient quantities simple (e.g., "1 cup rice", "2 eggs").
Return well-formed JSON only.
"""

    try:
        # Call OpenAI with the new client style
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for generating recipes."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        text = response.choices[0].message.content.strip()
        json_text = extract_json_object(text)

        try:
            result = json.loads(json_text)
        except json.JSONDecodeError:
            # fallback if JSON parsing fails
            result = {"raw_output": text}

        return jsonify({"ok": True, "meal": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
