# Pravav AI Portfolio - Final Ready Version

Professional Flask portfolio website with animations, dashboard demos, testimonials, case studies, resume route, and a real OpenAI-powered chatbot.

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your real OpenAI key in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Start the app:

```bash
python app.py
```

Open: http://127.0.0.1:5000

## Render deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```

Add Environment Variables in Render:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## Important files

- `app.py` - Full Flask app, UI, chatbot, routes
- `requirements.txt` - Python dependencies
- `Procfile` - Deployment start command
- `.env.example` - Environment variable example
- `static/resume.pdf` - Add your resume here
- `static/profile.jpg` - Add your profile image here
