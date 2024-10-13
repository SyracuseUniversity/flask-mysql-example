from flask import Flask, render_template_string, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from settings import *
from database import db, Logbook

# Create the Flask application
app = Flask(__name__)
# set secret
app.secret_key = APP_SECRET
# config database
app.config[SQLALCHEMY_DATABASE_URI] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
db.init_app(app)
# init db if not created
db.create_all()

# create logger
logger = logging.getLogger(__name__)

# configure logger to output to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# set log level
match LOGGING_LEVEL:
    case "DEBUG":
        logger.setLevel(logging.DEBUG)
    case "WARN":
        logger.setLevel(logging.WARN)
    case "ERROR":
        logger.setLevel(logging.ERROR)
    case _:
        logger.setLevel(logging.INFO)

def debug_inputs():
    # print app version
    logger.info(f"{APP_NAME} {APP_VERSION}")

    # print environment variables
    logger.debug("Environment Variables")
    logger.debug(f"APP_NAME:        {APP_NAME}")
    logger.debug(f"APP_VERSION:     {APP_VERSION}")
    logger.debug(f"LOGGING_LEVEL:   {LOGGING_LEVEL}")
    logger.debug(f"APP_SECRET:      [redacted]")
    logger.debug(f"DB_HOST:         {DB_HOST}")
    logger.debug(f"DB_PORT:         {DB_PORT}")
    logger.debug(f"DB_NAME:         {DB_NAME}")
    logger.debug(f"DB_USER:         {DB_USER}")
    logger.debug(f"DB_PASS:         [redacted]")

@app.route('/', methods=['GET'])
def index():
    entries = db.query(Logbook).scalars().all()
    
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Guest Book</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='css/index.css') }}">
        </head>
        <body>
            <div class="container">
	            <form action="{{ url_for('add_entry') }}" method="post">
		            <h3>Guest book entry</h3>

		            <div class="form-group">
			            <label for="name">Name: *</label>
			            <input type="text" id="name" class="form-control">
		            </div>

		            <button type="submit" class="btn btn-default">Add</button>
	            </form>
	
	            <ul class="entries">
                    {% for entry in entries -%}
		            <li>
			            <h4>{{ entry.timestamp }} - {{ entry.name }}</h4>
		            </li>
                    {%- endfor %}
                </ul>
            </div>
        </body>
        </html>
    """, entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    name = request.form.get('name',None)
    logger.info(f"Adding {name} to guestbook.")
    
    if name != None:
        entry = Logbook(name)
        db.add(entry)
        db.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    debug_inputs()
    app.run()