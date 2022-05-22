from flask import (
    Blueprint,
    # Response,
    render_template, 
    # flash, 
    # redirect,
    # session, 
    request,
    # url_for,
    # render_template_string,
    jsonify
)
import re
import json
from pathlib import Path

from app.common import (
    get_puzzle_number,
    get_day_from_puzzle_number,
    connect_to_db,
    clean_word,
    get_hash_client_ip,
    get_word_from_position,
    check_word,
    _get_full_list,
    COLORS,
    STAT_DB_PATH
)

FLASH_DB_PATH = f"{Path(__file__).parent.parent.parent}/flash.db"

flash_bp = Blueprint('flash', __name__, template_folder='templates', static_folder='static')

@flash_bp.route('/')
def flash():
    puzzleNumber = get_puzzle_number()
    # yesterday_list = get_history(puzzleNumber-1)
    # yesterday_list = [[w,s] for w,_,_,s in yesterday_list]
    winners_today = get_flash_winners_today()
    game_mode = "Flash"
    game_catch_phrase = "Trouve plus de mots que Martine de la compta."

    return render_template(
        'flash.html', 
        puzzleNumber = get_puzzle_number(),
        # yesterday_word = get_yesterday_word(),
        winners_yesterday = get_flash_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

@flash_bp.route('/get_word')
def get_flash_word():
    # JUST FOR TESTS
    data = {'word': get_word_from_position(FLASH_DB_PATH, get_puzzle_number(), 1000)}
    return jsonify(data)

@flash_bp.route('/get_score')
def get_flash_score():
    word = request.args.get('word')
    word, score = check_word(FLASH_DB_PATH, get_puzzle_number(), word)
    data = {'score': score, 'word': word}
    return jsonify(data)

def get_flash_winners(day):
    con, cur = connect_to_db(STAT_DB_PATH)
    table = f'flash_day{day}'
    query = f"create table if not exists {table}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guesses INT, points INT)"
    cur.execute(query)
    con.commit()
    total_winners = -1
    with con:
        query = f"SELECT COUNT(*) FROM {table}"
        cur.execute(query)
        res = cur.fetchall()
        total_winners = res[0][0] 
    return total_winners

@flash_bp.route('/win')
def flash_win():
    '''
    Update the database to add the win.
    Give the win to check it is not a hack.
    '''
    score = request.args.get('score')
    guesses = int(request.args.get('guesses'))
    user_id = request.args.get('user_id')
    puzzleNumber = get_puzzle_number()
   
    ip_hash = get_hash_client_ip()
    user_hash = hash(user_id)
    unique_hash = ip_hash+user_hash
    con, cur = connect_to_db(STAT_DB_PATH)
    con.commit()
    query = f"create table if not exists flash_day{puzzleNumber}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guesses INT, points INT)"
    cur.execute(query)
    con.commit()

    already_won = False
    # check if the same user alread won
    with con:
        query = f'SELECT * FROM flash_day{puzzleNumber} WHERE unique_hash = "{unique_hash}"'
        cur.execute(query)
        res = cur.fetchall()
        if len(res) > 0:
            already_won = True
        else:
            with con:
                query = f"insert into flash_day{puzzleNumber} (unique_hash, ip_hash, user_hash, guesses, points)"
                query += f"values (\"{unique_hash}\", \"{ip_hash}\", \"{user_hash}\", {guesses}, {score})"""
                cur.execute(query)
                con.commit()
        query = f"SELECT * FROM flash_day{puzzleNumber}"
        cur.execute(query)
        res = cur.fetchall()
        
        data = {
            'already_won':already_won,
            'winners':get_flash_winners_today(),
        }
        return jsonify(data)

@flash_bp.route('/get_stat_hist.png')
def get_flash_stat_hist():
    return _get_flash_stat_hist(None)

@flash_bp.route('/get_stat_hist_<int:user_points>.png')
def get_flash_stat_hist_user(user_points):
    return _get_flash_stat_hist(user_points)

def _get_flash_stat_hist(user_points):
    con, cur = connect_to_db(STAT_DB_PATH)
    query = f"SELECT * FROM flash_day{get_puzzle_number()}"
    cur.execute(query)
    res = cur.fetchall()
    con.close()
    if res:
        data_points = list(zip(*res))[-1]
        return get_hist_image(data_points, user_points)
    else:
        return send_file(HIST_PLACEHOLDER_PATH, mimetype='image/png')

@flash_bp.route('/get_winners')
def get_flash_winners_today():
    puzzleNumber = get_puzzle_number()
    return get_flash_winners(puzzleNumber)

@flash_bp.route('/get_full_list')
def get_flash_full_list():
    day = request.args.get('day')
    puzzleNumber = get_puzzle_number()
    day = day if day else puzzleNumber
    res = _get_full_list(FLASH_DB_PATH, day)
    data = {'word_list':res}
    return jsonify(data) 

