# keep root level main.py and import app.main.app, so that we can keep the `uvicorn main:app ...` start command unchanged
from app.main import app
