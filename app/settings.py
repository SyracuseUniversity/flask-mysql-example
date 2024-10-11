from os import environ, urandom
from pathlib import Path

# App settings
APP_NAME      = environ.get("APP_NAME", "flask-mysql-example")
APP_VERISON   = Path('version.txt').read_text().reaplace('\n','')
LOGGING_LEVEL = environ.get("LOGGING_LEVEL","INFO")

# Flask settings
APP_SECRET = environ.get("APP_SECRET") or urandom(24)

# Database Info
DB_HOST = environ.get("DB_HOST", "mysql")
DB_PORT = environ.get("DB_PORT", 3306)
DB_NAME = environ.get("DB_NAME", "logbook")
DB_USER = environ.get("DB_USER", "root")
DB_PASS = environ.get("DB_PASS")