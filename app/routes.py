from flask import (
    render_template,
    flash, redirect,
    url_for,
    request,
    jsonify,
    Response
)
import requests
from datetime import date
import sqlite3
# from flask_login import current_user, login_user, logout_user, login_required

from app import app
# from app.forms import SumbitForm
from app import puzzleNmber


from pathlib import Path
WORD_DB_PATH = f"{Path(__file__).parent.parent}/word2vec.db"

print('*'*50)
print(WORD_DB_PATH)


@app.route('/')
def hello_world():
    # form = SumbitForm()
    # print('*'*100)

    yesterday_list = get_history(puzzleNmber-1)

    return render_template(
        'base.html', 
        puzzleNumber = puzzleNmber,
        yesterday_word = get_yesterday_word(),
        yesterday_list = yesterday_list,
        message = 'Hello, World!')

@app.route('/get_score')
def test():
    word = request.args.get('test')
    print(f'Testing word {word}')

    data = {'score': check_word(1, word)}
    print('*'*25)
    # print(data["error"])
    return jsonify(data)

@app.route('/get_hint/<int:score>')
def get_hint(score):
    # con = sqlite3.connect("word2vec.db")
    # con.execute("PRAGMA journal_mode=WAL")
    # cur = con.cursor()

    # query = f'select * from day{puzzleNmber} where score={score}'
    # check = cur.execute(query)


    data = {'hint_word': get_word_from_position(puzzleNmber, score)}

    return jsonify(data)

def get_word_from_position(day, score):
    con = sqlite3.connect(WORD_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()

    query = f'select * from day{day} where score={score}'
    check = cur.execute(query)

    return check.fetchone()[0]

# @app.route('/get_yesterday_word')
def get_yesterday_word():
    # data = {'hint_word': get_word_from_position(puzzleNmber-1, score = 1000)}
    # return jsonify(data)
    return get_word_from_position(puzzleNmber-1, score = 1000)

def get_history(day):
    con = sqlite3.connect(WORD_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()

    query = f'select * from day{day}'
    check = cur.execute(query)
    return check.fetchall()

@app.route('/get_yesterday_list')
def get_yesterday_list():
    data = {'history': get_history(puzzleNmber-1)}
    return data

def check_word(day, word):
    con = sqlite3.connect(WORD_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()

    def does_word_exist(word):
        with con:
            query=f'select exists(select 1 from all_words_fr where word="{word}" collate nocase) limit 1'
            check = cur.execute(query) 
            found = check.fetchone()[0]
            if found:
                return 1
            else:
                return 0

    def get_score(word):
        with con:
            query = f'select * from day{puzzleNmber} where word="{word}" collate nocase'
            check = cur.execute(query)
            found = check.fetchone()
            if found:
                return found[2]
            else:
                return 0

    print('Checking if word exist')
    word_exists = does_word_exist(word)
    if not (word_exists):
        return -1

    print('Getting score')
    score = get_score(word)
    print(score)
    return score


# def get_score(word):
#     url = 'https://cemantix.herokuapp.com/score'
#     headers = { "Content-Type": "application/x-www-form-urlencoded" }
#     payload = {'word': word}

#     r = requests.post(url, data=payload, headers = headers)

#     if r.json().get("error"):
#         return -1

#     try:
#         score = int(r.json().get('percentile', 0))
#     except:
#         return -1

#     return score