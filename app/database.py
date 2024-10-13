from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

# create logger
logger = logging.getLogger(__name__)

# init db
db = SQLAlchemy()

class Logbook(db.Model):
    __tablename__ = 'logbook'
    id        = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    name      = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        logger.debug(f"db object name: {name}")
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.name = name

