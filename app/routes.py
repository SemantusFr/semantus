from flask import (
    render_template,
    flash, redirect,
    url_for,
    request,
    jsonify,
    Response,
    send_file
)
import requests
import json
# from datetime import date, timedelta
import sqlite3

from app import app
from app.messages import get_message_from_score
from app.figures import get_hist_image, get_stats_image

from pathlib import Path

from app.common import (
    get_puzzle_number,
    get_day_from_puzzle_number,
    connect_to_db,
    clean_word,
    get_word_from_position,
    check_word,
    _get_full_list,
    get_hash_client_ip,
    hash,
    COLORS
)

from app.clap import clap_bp
from app.link import link_bp
from app.flash import flash_bp

app.register_blueprint(clap_bp, url_prefix='/clap')
app.register_blueprint(link_bp, url_prefix='/link')
app.register_blueprint(flash_bp, url_prefix='/flash')

WORD_DB_PATH = f"{Path(__file__).parent.parent}/classique.db"
STAT_DB_PATH = f"{Path(__file__).parent.parent}/stats.db"

DB_LEM = f"{Path(__file__).parent.parent}/word2lem.db"
HINT_PENALTY = 10 # 10 point less per hint
GUESS_PENALTY = 2 # 2 point less per guess
HIST_PLACEHOLDER_PATH = 'static/images/empty_stats.png'

FLASH_NB_HINTS_START = 3
FLASH_NB_HINTS_MAX = 8


def get_history(day):
    con, cur = connect_to_db(WORD_DB_PATH)

    query = f'select * from day{day}'
    check = cur.execute(query)
    res = check.fetchall()
    return res

def get_lemma(word):
    """
    Takes a word and returns the corresping lemma
    If word not found, returns None.
    """
    cur, con = connect_to_db(DB_LEM) 
    if "'" in word:
        return None
    query = f"SELECT lemma FROM words WHERE word = '{word}'"
    res = cur.execute(query).fetchone() 
    ret = res[0] if res else None
    con.close()
    return ret

@app.route('/get_date_from_puzzle_number')   
def get_date_from_puzzle_number():
    number = int(request.args.get('number'))
    day = get_day_from_puzzle_number(number)
    return jsonify({'date': day.strftime('%d-%m-%Y')})

@app.route('/get_message')
def get_message():
    score = int(request.args.get('score'))
    word_type = request.args.get('type')
    data = {'message': get_message_from_score(score, word_type)}
    return jsonify(data)

@app.route('/stats')
def show_stats():
    return render_template(
        'stats.html', 
        colors = COLORS,
        game_mode = '',
        maxLink = 300,
        game_sub_title = '',)

@app.route('/stats_figure.png')
def get_stats_figure():
    def count_winners(mode):
        prefix =''
        if not mode == 'classique':
            prefix = mode+'_'
        con, cur = connect_to_db(STAT_DB_PATH)
        winners = []
        for day in range(get_puzzle_number()+1):
            table = f"{prefix}day{day}"
            try:
                query = f"SELECT COUNT(*) FROM {table}"
                cur.execute(query)
                res = cur.fetchall()
                winners.append(res[0][0] if res else 0)
            except:
                winners.append(0)
        con.close()
        return winners
    
    modes = ['classique','flash','link', 'clap']
    legends = ['Classique', 'Flash', 'Link', 'Clap']
    data_points = [count_winners(m) for m in modes]
    return get_stats_image(data_points, legends)

######################################
############# MASTER #################
######################################

@app.route('/master')
def master():
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
    winners_today = get_flash_winners_today()
    game_mode = "Master"
    game_catch_phrase = "Fais le plus de points avant de tirer la chasse."

    return render_template(
        'master.html', 
        puzzleNumber = get_puzzle_number(),
        minWords = FLASH_NB_HINTS_START,
        maxWords = FLASH_NB_HINTS_MAX,
        yesterday_word = get_yesterday_word(),
        yesterday_list = yesterday_list,
        winners_yesterday = get_flash_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

@app.route('/master/get_list')
def get_master_word_lists():
    con, cur = connect_to_db(MASTER_DB_PATH)
    query = f"SELECT * FROM day{get_puzzle_number()}"
    cur.execute(query)
    res = cur.fetchall()
    only_hints = list(zip(*list(zip(*res))[1:]))
    data = {'hints': only_hints}
    return jsonify(data)

############################################
################ CLASSIQUE #################
############################################

@app.route('/stats/bare')
def bare_stats():
    return render_template(
        'stats_bare.html', 
        puzzleNumber = get_puzzle_number(),
        colors = COLORS,
    )

@app.route('/info/bare')
def bare_info():
    return render_template(
        'info_bare.html',
        colors = COLORS,
    )

@app.route('/classic/bare')
def bare_classic():
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
    yesterday_list = [[w,s] for w,_,_,s in yesterday_list]
    winners_today = get_winners_today()
    game_mode = "Classique"
    game_catch_phrase = "Trouve le mot caché plus rapidement que ton beau-frère."

    return render_template(
        'classic_bare.html', 
        puzzleNumber = get_puzzle_number(),
        yesterday_word = get_yesterday_word(),
        yesterday_list = yesterday_list,
        winners_yesterday = get_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

@app.route('/')
def index():
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
    yesterday_list = [[w,s] for w,_,_,s in yesterday_list]
    winners_today = get_winners_today()
    game_mode = "Classique"
    game_catch_phrase = "Trouve le mot caché plus rapidement que ton beau-frère."

    return render_template(
        'classic.html', 
        puzzleNumber = get_puzzle_number(),
        yesterday_word = get_yesterday_word(),
        yesterday_list = yesterday_list,
        winners_yesterday = get_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

def compute_points(guesses, hints):
    return 1000 - GUESS_PENALTY*(guesses-1) - HINT_PENALTY*(hints-1)

@app.route('/get_stat_hist.png')
def get_stat_hist():
    return _get_stat_hist(None)

@app.route('/get_stat_hist_<int:user_points>.png')
def get_stat_hist_user(user_points):
    return _get_stat_hist(user_points)

def _get_stat_hist(user_points):
    puzzleNumber = get_puzzle_number()
    con, cur = connect_to_db(STAT_DB_PATH)
    query = f"create table if not exists day{puzzleNumber}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guesses INT, hints INT, points INT)"
    cur.execute(query)
    con.commit()
    query = f"SELECT * FROM day{puzzleNumber}"
    cur.execute(query)
    res = cur.fetchall()
    con.close()
    if res:
        data_points = list(zip(*res))[-1]
        return get_hist_image(data_points, user_points)
    else:
        return send_file(HIST_PLACEHOLDER_PATH, mimetype='image/png')

@app.route('/get_score')
def get_score():
    word = request.args.get('word')
    word, score = check_word(WORD_DB_PATH, get_puzzle_number(), word)
    data = {'score': score, 'word': word}
    return jsonify(data)



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
    puzzleNumber = get_puzzle_number()

    # check if really a win 
    if (word == get_today_word()):     
        ip_hash = get_hash_client_ip()
        
        user_hash = hash(user_id)
        unique_hash = ip_hash+user_hash
        con, cur = connect_to_db(STAT_DB_PATH)
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
                    query += f"values (\"{unique_hash}\", \"{ip_hash}\", \"{user_hash}\", {guesses}, {hints}, {nb_points})"
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

@app.route('/get_full_list')
def get_full_list():
    secret_word = request.args.get('secret_word')
    day = request.args.get('day')
    puzzleNumber = get_puzzle_number()
    day = day if day else puzzleNumber
    res = _get_full_list(WORD_DB_PATH, day)
    # if it is the running day and that the secret word
    # is not provided, we return nothing
    if day == puzzleNumber and not res[0][0] == secret_word:
        return jsonify({}) 
    data = {'word_list':res}
    return jsonify(data) 



     

@app.route('/get_hint')
def get_hint():
    best_user_score = int(request.args.get('score'))
    puzzleNumber = get_puzzle_number()
    if best_user_score < 1000:
        data = {'hint_word': get_word_from_position(WORD_DB_PATH, puzzleNumber, best_user_score)}
    else:
        data = {}
    return jsonify(data)  

@app.route('/get_winners')
def get_winners_today():
    puzzleNumber = get_puzzle_number()
    return get_winners(puzzleNumber)

def get_winners(day, mode = 'classique'):
    con, cur = connect_to_db(STAT_DB_PATH)
    table = f'day{day}'
    query = f"create table if not exists {table} "
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guesses INT, hints INT, points INT)"
    cur.execute(query)
    con.commit()
    total_winners = -1
    with con:
        query = f"SELECT COUNT(*) FROM {table}"
        cur.execute(query)
        res = cur.fetchall()
        total_winners = res[0][0] 
    return total_winners

def get_today_word():
    puzzleNumber = get_puzzle_number()
    return get_word_from_position(WORD_DB_PATH, puzzleNumber, 1000)

def get_yesterday_word():
    puzzleNumber = get_puzzle_number()
    return get_word_from_position(WORD_DB_PATH, puzzleNumber-1, score = 1000)

def get_history(day):
    con, cur = connect_to_db(WORD_DB_PATH)

    query = f'select * from day{day}'
    check = cur.execute(query)
    res = check.fetchall()
    return res

@app.route('/get_yesterday_list')
def get_yesterday_list():
    puzzleNumber = get_puzzle_number()
    data = {'history': get_history(puzzleNumber-1)}
    return data




