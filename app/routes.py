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
from app.messages import get_message_from_score

from pathlib import Path
WORD_DB_PATH = f"{Path(__file__).parent.parent}/word2vec.db"
STAT_DB_PATH = f"{Path(__file__).parent.parent}/stats.db"


from hashlib import sha1

def hash(s):
    h = sha1()
    h.update(s.encode("ascii"))
    hash = h.hexdigest()
    return hash


@app.route('/get_message')
def get_message():
    score = int(request.args.get('score'))
    data = {'message': get_message_from_score(score)}
    return jsonify(data)

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
    )

@app.route('/get_score')
def get_score():
    word = request.args.get('word')

    data = {'score': check_word(1, word)}
    # print(data["error"])
    return jsonify(data)

def get_hash_client_ip():
    '''
    Get the hash of the client IP address to count the number of wins.
    Hash to preserve privacy.
    '''
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    print('-'*100)
    print(hash(ip_addr))
    print(hash(ip_addr))
    return hash(ip_addr)

@app.route('/win')
def win():
    '''
    Update the database to add the win.
    Give the win to check it is not a hack.
    '''
    print('*'*100)
    word = request.args.get('word')
    guesses = int(request.args.get('guesses'))
    hints = int(request.args.get('hints'))

    # check if really a win 
    if (word == get_today_word()):     
        ip_hash = get_hash_client_ip()
        con = sqlite3.connect(STAT_DB_PATH)
        con.execute("PRAGMA journal_mode=WAL")
        cur = con.cursor()
        con.commit()
        cur.execute(f"create table if not exists day{puzzleNmber} (hash_user_ip TEXT PRIMARY KEY, guesses INT, hints INT)")
        con.commit()

        
        already_won = False
        # check if the same user alread won
        with con:
            query = f'SELECT * FROM day{puzzleNmber} WHERE hash_user_ip = "{ip_hash}"'
            cur.execute(query)
            res = cur.fetchall()
            if len(res) > 0:
                already_won = True
            else:
                with con:
                    query = f"""insert into day{puzzleNmber} (hash_user_ip, guesses, hints)
                             values (\"{ip_hash}\", {guesses}, {hints})"""
                    cur.execute(query)
                    con.commit()


            query = f"SELECT * FROM day{puzzleNmber}"
            print(query)
            cur.execute(query)
            res = cur.fetchall()
            print(res)
            data = {
                'already_won':already_won,
                'winners':get_winners_today()
            }
            return jsonify(data)
    else:
        return jsonify({})


@app.route('/get_hint')
def get_hint():
    best_user_score = int(request.args.get('score'))
    if best_user_score < 999:
        data = {'hint_word': get_word_from_position(puzzleNmber, best_user_score+1)}
    else:
        data = {}
    return jsonify(data)  

@app.route('/get_winners')
def get_winners_today():
    con = sqlite3.connect(STAT_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()
    cur.execute(f"create table if not exists day{puzzleNmber} (hash_user_ip INT PRIMARY KEY, guesses INT, hints INT)")
    con.commit()
    total_winners = -1
    with con:
        query = f"SELECT COUNT(*) FROM day{puzzleNmber}"
        print(query)
        cur.execute(query)
        res = cur.fetchall()
        total_winners = res[0][0] 
    return total_winners
    # data = {'total_winners': total_winners}

    # return jsonify(data)

def get_today_word():
    return get_word_from_position(puzzleNmber, 1000)

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