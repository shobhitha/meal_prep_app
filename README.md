# AI Single Meal Suggestion

Simple Flask web app that suggests **one** meal based on user inputs using an LLM.

## Setup (local)

1. Clone or copy repository
2. Create virtualenv and activate
3. `pip install -r requirements.txt`
4. Create `.env` with `OPENAI_API_KEY=sk-...`
5. `python app.py`
6. Visit `http://127.0.0.1:5000`

## Files
- `app.py` — Flask backend and OpenAI integration
- `templates/index.html` — frontend
- `.env` — local environment (not committed)
