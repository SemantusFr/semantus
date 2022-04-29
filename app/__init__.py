from flask import Flask


from config import Config

## Create the app
app = Flask(__name__)

app.config.from_object(Config)

from datetime import date



from app import routes





