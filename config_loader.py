import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SECRETS_DIR = BASE_DIR / "passwords"


def load_json_secret(filename):
    secret_path = SECRETS_DIR / filename

    if not secret_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de credenciales: {secret_path}")

    with secret_path.open("r", encoding="utf-8") as secret_file:
        return json.load(secret_file)