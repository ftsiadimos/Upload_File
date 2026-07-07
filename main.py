from app import create_app
from dotenv import load_dotenv
from pathlib import Path

# Load .flaskenv first, then .env (both override previous values)
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".flaskenv", override=True)
load_dotenv(base_dir / ".env", override=True)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
