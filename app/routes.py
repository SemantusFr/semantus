from flask import (
    render_template,
    flash, redirect,
    url_for,
    request,
    jsonify,
    Response
)
import requests
from datetime import date, timedelta
import sqlite3

# from flask_login import current_user, login_user, logout_user, login_required

from app import app
# from app.forms import SumbitForm
from app.messages import get_message_from_score
from app.figures import get_hist_image

from pathlib import Path
WORD_DB_PATH = f"{Path(__file__).parent.parent}/word2vec.db"
STAT_DB_PATH = f"{Path(__file__).parent.parent}/stats.db"
HINT_PENALTY = 5 # 5 point less per hint


from hashlib import sha1

puzzleNumber = 0

def hash(s):
    h = sha1()
    h.update(s.encode("ascii"))
    hash = h.hexdigest()
    return hash


def get_puzzle_number():
    today = date.today()
    day0 = date(*app.config['DAY0'])
    delta_days = (today-day0).days
    assert(delta_days > 0)
    return delta_days

@app.route('/get_date_from_puzzle_number')   
def get_date_from_puzzle_number():
    number = int(request.args.get('number'))
    day0 = date(*app.config['DAY0'])
    day = day0+ timedelta(days=number)
    return jsonify({'date': day.strftime('%d-%m-%Y')})
    




@app.route('/get_message')
def get_message():
    score = int(request.args.get('score'))
    word_type = request.args.get('type')
    data = {'message': get_message_from_score(score, word_type)}
    return jsonify(data)

@app.route('/')
def index():
    global puzzleNumber
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
    winners_today = get_winners_today()
    game_mode = "Classique"

    return render_template(
        'base.html', 
        puzzleNumber = puzzleNumber,
        yesterday_word = get_yesterday_word(),
        yesterday_list = yesterday_list,
        winners_yesterday = get_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
    )

def compute_points(guesses, hints):
    return 1000 - (guesses-1) - HINT_PENALTY*(hints-1)


@app.route('/get_stat_hist.png')
def get_stat_hist():
    return _get_stat_hist(None)


@app.route('/get_stat_hist_<int:user_points>.png')
def get_stat_hist_user(user_points):
    return _get_stat_hist(user_points)

def _get_stat_hist(user_points):
    # user_points = request.args.get('user_points')
    # user_points = 0 if user_points == None else user_points
    con = sqlite3.connect(STAT_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()
    query = f"SELECT * FROM day{get_puzzle_number()}"
    cur.execute(query)
    res = cur.fetchall()

    data_points = list(zip(*res))[-1]
    return get_hist_image(data_points, user_points)


@app.route('/get_score')
def get_score():
    word = request.args.get('word')

    data = {'score': check_word(1, word)}
    return jsonify(data)

def get_hash_client_ip():
    '''
    Get the hash of the client IP address to count the number of wins.
    Hash to preserve privacy.
    '''
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    return hash(ip_addr)

@app.route('/win')
def win():
    '''
    Update the database to add the win.
    Give the win to check it is not a hack.
    '''

    word = request.args.get('word')
    guesses = int(request.args.get('guesses'))
    hints = int(request.args.get('hints'))
    user_id = request.args.get('user_id')

    # check if really a win 
    if (word == get_today_word()):     
        ip_hash = get_hash_client_ip()
        user_hash = hash(user_id)
        unique_hash = ip_hash+user_hash
        con = sqlite3.connect(STAT_DB_PATH)
        con.execute("PRAGMA journal_mode=WAL")
        cur = con.cursor()
        con.commit()
        query = f"create table if not exists day{puzzleNumber}"
        query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guesses INT, hints INT, points INT)"
        cur.execute(query)
        con.commit()

        nb_points = compute_points(guesses, hints) 

        already_won = False
        # check if the same user alread won
        with con:
            query = f'SELECT * FROM day{puzzleNumber} WHERE unique_hash = "{unique_hash}"'
            cur.execute(query)
            res = cur.fetchall()
            if len(res) > 0:
                already_won = True
            else:
                with con:
                    query = f"insert into day{puzzleNumber} (unique_hash, ip_hash, user_hash, guesses, hints, points)"
                    query += f"values (\"{unique_hash}\", \"{ip_hash}\", \"{user_hash}\", {guesses}, {hints}, {nb_points})"""
                    cur.execute(query)
                    con.commit()
                    


            query = f"SELECT * FROM day{puzzleNumber}"
            cur.execute(query)
            res = cur.fetchall()
            
            data = {
                'already_won':already_won,
                'winners':get_winners_today(),
                'nb_points':nb_points
            }
            


            return jsonify(data)
    else:
        return jsonify({})


@app.route('/get_hint')
def get_hint():
    best_user_score = int(request.args.get('score'))
    if best_user_score < 1000:
        data = {'hint_word': get_word_from_position(puzzleNumber, best_user_score)}
    else:
        data = {}
    return jsonify(data)  

@app.route('/get_winners')
def get_winners_today():
    return get_winners(puzzleNumber)

def get_winners(day):
    con = sqlite3.connect(STAT_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()
    cur.execute(f"create table if not exists day{day} (ip_hash INT PRIMARY KEY, guesses INT, hints INT)")
    con.commit()
    total_winners = -1
    with con:
        query = f"SELECT COUNT(*) FROM day{day}"
        cur.execute(query)
        res = cur.fetchall()
        total_winners = res[0][0] 
    return total_winners

def get_today_word():
    return get_word_from_position(puzzleNumber, 1000)

def get_word_from_position(day, score):
    con = sqlite3.connect(WORD_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()

    query = f'select * from day{day} where score={score}'
    check = cur.execute(query)

    return check.fetchone()[0]

# @app.route('/get_yesterday_word')
def get_yesterday_word():
    # data = {'hint_word': get_word_from_position(puzzleNumber-1, score = 1000)}
    # return jsonify(data)
    return get_word_from_position(puzzleNumber-1, score = 1000)

def get_history(day):
    con = sqlite3.connect(WORD_DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()

    query = f'select * from day{day}'
    check = cur.execute(query)
    return check.fetchall()

@app.route('/get_yesterday_list')
def get_yesterday_list():
    data = {'history': get_history(puzzleNumber-1)}
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
        print('--'*10)
        print(f"{puzzleNumber=}")
        with con:
            query = f'select * from day{puzzleNumber} where word="{word}" collate nocase'
            check = cur.execute(query)
            found = check.fetchone()
            if found:
                return found[2]
            else:
                return 0

    word_exists = does_word_exist(word)
    if not (word_exists):
        return -1

    score = get_score(word)
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