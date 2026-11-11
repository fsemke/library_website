from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIRECTORY = BASE_DIR / "uploads"
DB_DIRECTORY = BASE_DIR / "instance"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

DB_DIRECTORY.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_PATH = DB_DIRECTORY / "db.db"
