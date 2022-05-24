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
    hash,
    COLORS,
    STAT_DB_PATH
)

LINK_DB_PATH = f"{Path(__file__).parent.parent.parent}/link.db"

link_bp = Blueprint('link', __name__, template_folder='templates', static_folder='static')

@link_bp.route('/')
def link():
    puzzleNumber = get_puzzle_number()
    yesterday_solutions = get_link_solutions(puzzleNumber-1)
    yesterday_solutions = [[w1+'-'+w2,s] for _,w1,w2,s in yesterday_solutions]
    yesterday_words = _get_link_words(puzzleNumber-1)
    winners_today = get_link_winners_today()
    game_mode = "Link"
    game_catch_phrase = "Trouve le lien le plus fort entre deux mots qui n'ont rien à voir !"
    # best_yesterday_combination = get

    return render_template(
        'link.html', 
        puzzleNumber = puzzleNumber,
        yesterday_words = yesterday_words,
        yesterday_list = yesterday_solutions,
        winners_today = winners_today,
        game_mode = game_mode,
        maxLink = 300,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

def get_link_solutions(day, all = False):
    cur, con = connect_to_db(LINK_DB_PATH)
    query = f"SELECT * FROM day{day}_solutions"
    if all:
       query += " LIMIT 1" 
    check = cur.execute(query)
    solutions = check.fetchall()
    return solutions

@link_bp.route('/get_words')
def get_link_words():
    puzzleNumber = get_puzzle_number()
    words = _get_link_words(puzzleNumber)
    data = {'words':words}
    return jsonify(data)

def _get_link_words(day):
    cur, con = connect_to_db(LINK_DB_PATH)
    query = f"SELECT * FROM day{day}"
    check = cur.execute(query)
    words = check.fetchall()
    words = list(zip(*words))[0]
    return words

@link_bp.route('/get_best_score')
def get_link_best_score():
    puzzleNumber = get_puzzle_number()
    cur, con = connect_to_db(LINK_DB_PATH)
    query = f"SELECT score FROM day{puzzleNumber}_solutions LIMIT 1"
    check = cur.execute(query)
    best_score = check.fetchone()[0]
    data = {'best_score': best_score}
    return jsonify(data)

@link_bp.route('/get_score')
def get_link_score():
    puzzleNumber = get_puzzle_number()
    guess_1 = request.args.get('guess_1')
    guess_2 = request.args.get('guess_2')
    link_1, link_2, link_3, score = get_link_scores(
        puzzleNumber, 
        guess_1, 
        guess_2
        )
    data = {'link_1': link_1,
            'link_2': link_2,
            'link_3': link_3,
            'score': score}
    return jsonify(data)

@link_bp.route('/win')
def link_win():
    '''
    Update the database to add the win.
    '''
    guess_1 = request.args.get('guess_1')
    guess_2 = request.args.get('guess_2')
    user_id = request.args.get('user_id')
    puzzleNumber = get_puzzle_number()
    score = get_link_scores(puzzleNumber, guess_1, guess_2)[-1]
    if score <= 0:
        return jsonify({})
    ip_hash = get_hash_client_ip()
    user_hash = hash(user_id)
    unique_hash = ip_hash+user_hash
    table_name = f"link_day{puzzleNumber}"
    con, cur = connect_to_db(STAT_DB_PATH)
    con.commit()
    query = f"create table if not exists {table_name}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guess_1 INT, guess_2 INT, points INT)"
    cur.execute(query)
    con.commit()
    # check if the same user has already win with a better score
    with con:
        query = f'SELECT points FROM {table_name} WHERE unique_hash = "{unique_hash}"'
        cur.execute(query)
        res = cur.fetchall()
        if res and res[0][0] >= score:
            # do nothing, only keep the best score
            ret = jsonify({})
            return ret
        else:
            with con:
                query = f"REPLACE into {table_name} (unique_hash, ip_hash, user_hash, guess_1, guess_2, points)"
                query += f"values (\"{unique_hash}\", \"{ip_hash}\", \"{user_hash}\", \"{guess_1}\", \"{guess_2}\", {score})"""
                cur.execute(query)
                con.commit()
    data = {}
    return jsonify(data)

def get_link_winners(day):
    con, cur = connect_to_db(STAT_DB_PATH)
    table = f"link_day{day}"
    query = f"create table if not exists {table}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, guess_1 INT, guess_2 INT, points INT)"
    cur.execute(query)
    con.commit()
    total_winners = -1
    with con:
        query = f"SELECT COUNT(*) FROM {table}"
        cur.execute(query)
        res = cur.fetchall()
        total_winners = res[0][0] 
    return total_winners

# @app.route('/link/get_winners')
def get_link_winners_today():
    puzzleNumber = get_puzzle_number()
    return get_link_winners(puzzleNumber)

def get_link_scores(day, guess_1, guess_2):
    def does_word_exist(word):
        query=f'select exists(select 1 from all_words_fr where word="{word}" collate nocase) limit 1'
        check = cur.execute(query) 
        found = check.fetchone()[0]
        if found:
            return True
        else:
            return False

    def check_top_to_guess1(word):
        word.replace("'","''")
        query = f"SELECT score FROM day{day}_link1 where word='{word}'"
        check = cur.execute(query)
        ret = check.fetchone()
        return ret[0] if ret else 0

    def check_botom_to_guess2(word):
        word.replace("'","''")
        query = f"SELECT score FROM day{day}_linka where word='{word}'"
        check = cur.execute(query)
        ret = check.fetchone()
        return ret[0] if ret else 0


    def check_guess1_to_guess2(word1, word2):
        query = f"SELECT json FROM day{day}_link2 where word='{word1}'"
        check = cur.execute(query)
        ret = check.fetchone()
        if not ret:
            return -1
        dic = json.loads(ret[0])
        ret = dic.get(word2)
        if not ret:
            return 0
        return ret[-1]

    def check_guess2_to_guess1(word1, word2):
        query = f"SELECT json FROM day{day}_linkb where word='{word1}'"
        check = cur.execute(query)
        ret = check.fetchone()
        if not ret:
            return -1
        dic = json.loads(ret[0])
        ret = dic.get(word2)
        if not ret:
            return 0
        return ret[-1]
    
    link_1 = link_2 = link_3 = 0

    cur, con = connect_to_db(LINK_DB_PATH)

    if guess_1 and does_word_exist(guess_1):
        link_1 = check_top_to_guess1(guess_1)
    else:
        link_1 = -1

    if guess_2 and does_word_exist(guess_2):
        link_3 = check_botom_to_guess2(guess_2)
    else:
        link_3 = -1    
        

    if link_1 > 0 and link_3 > 0:
        link_2 = check_guess1_to_guess2(guess_1, guess_2)
        temp = check_guess2_to_guess1(guess_1, guess_2)
        link_2 = temp if temp > link_2 else link_2
        
    con.close()
    
    if link_1 and link_2 and link_3:
        score = link_1+link_2+link_3
    else:
        score = None
    
    return link_1, link_2, link_3, score 

