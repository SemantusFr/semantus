from flask import Flask


from config import Config

## Create the app
app = Flask(__name__)

app.config.from_object(Config)

from datetime import date

def get_puzzle_number():
    today = date.today()
    day0 = date(*app.config['DAY0'])
    delta_days = (today-day0).days
    assert(delta_days > 0)
    return delta_days
    
puzzleNmber = get_puzzle_number()

from app import routes





