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
from datetime import date, timedelta
import sqlite3
from hashlib import sha1

from app import app
from app.messages import get_message_from_score
from app.figures import get_hist_image

from pathlib import Path
WORD_DB_PATH = f"{Path(__file__).parent.parent}/classique.db"
STAT_DB_PATH = f"{Path(__file__).parent.parent}/stats.db"
FLASH_DB_PATH = f"{Path(__file__).parent.parent}/flash.db"
# MASTER_DB_PATH = f"{Path(__file__).parent.parent}/master.db"
LINK_DB_PATH = f"{Path(__file__).parent.parent}/link.db"
DB_LEM = f"{Path(__file__).parent.parent}/word2lem.db"
HINT_PENALTY = 10 # 10 point less per hint
GUESS_PENALTY = 2 # 2 point less per guess
HIST_PLACEHOLDER_PATH = 'static/images/empty_stats.png'

FLASH_NB_HINTS_START = 3
FLASH_NB_HINTS_MAX = 8
COLORS = {
    'classique' : '#5cb85c',
    'flash' : '#d25e00',
    'master' : '#dc3545',
}

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
    day0 = date(*app.config['DAY0'])
    day = day0+ timedelta(days=number)
    return jsonify({'date': day.strftime('%d-%m-%Y')})

@app.route('/get_message')
def get_message():
    score = int(request.args.get('score'))
    word_type = request.args.get('type')
    data = {'message': get_message_from_score(score, word_type)}
    return jsonify(data)

def get_hash_client_ip():
    '''
    Get the hash of the client IP address to count the number of wins.
    Hash to preserve privacy.
    '''
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    return hash(ip_addr)

######################################
############## LINK ##################
######################################

@app.route('/link')
def link():
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
    winners_today = get_flash_winners_today()
    game_mode = "Link"
    game_catch_phrase = "Trouve le lien le plus fort entre deux mot qui n'ont rien à voir !"

    return render_template(
        'link.html', 
        puzzleNumber = puzzleNumber,
        minWords = FLASH_NB_HINTS_START,
        maxWords = FLASH_NB_HINTS_MAX,
        yesterday_word = get_yesterday_word(),
        yesterday_list = yesterday_list,
        winners_yesterday = get_flash_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
        maxLink = 300,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

@app.route('/link/get_words')
def get_link_words():
    puzzleNumber = get_puzzle_number()
    cur, con = connect_to_db(LINK_DB_PATH)
    query = f"SELECT * FROM day{puzzleNumber}"
    check = cur.execute(query)
    words = check.fetchall()
    words = list(zip(*words))[0]
    print(words)
    data = {'words':words}
    return jsonify(data)

@app.route('/link/get_best_score')
def get_link_best_score():
    puzzleNumber = get_puzzle_number()
    cur, con = connect_to_db(LINK_DB_PATH)
    query = f"SELECT score FROM day{puzzleNumber}_solutions LIMIT 1"
    check = cur.execute(query)
    best_score = check.fetchone()[0]
    data = {'best_score': best_score}
    return jsonify(data)


@app.route('/link/get_score')
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

@app.route('/link/win')
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
    data = {
        # 'winners':get_flash_winners_today(),
    }
    return jsonify(data)

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




####################################
############ FLASH #################
####################################

@app.route('/flash')
def flash():
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
    winners_today = get_flash_winners_today()
    game_mode = "Flash"
    game_catch_phrase = "Trouve plus de mots que Martine de la compta."

    return render_template(
        'flash.html', 
        puzzleNumber = get_puzzle_number(),
        yesterday_word = get_yesterday_word(),
        winners_yesterday = get_flash_winners(puzzleNumber-1),
        winners_today = winners_today,
        game_mode = game_mode,
        game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

@app.route('/flash/get_word')
def get_flash_word():
    # JUST FOR TESTS
    data = {'word': get_word_from_position(FLASH_DB_PATH, get_puzzle_number(), 1000)}
    return jsonify(data)

@app.route('/flash/get_score')
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

@app.route('/flash/win')
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
        query = f"SELECT * FROM day{puzzleNumber}"
        cur.execute(query)
        res = cur.fetchall()
        con.close()
        data = {
            'already_won':already_won,
            'winners':get_flash_winners_today(),
        }
        return jsonify(data)

@app.route('/flash/get_stat_hist.png')
def get_flash_stat_hist():
    return _get_flash_stat_hist(None)

@app.route('/flash/get_stat_hist_<int:user_points>.png')
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

@app.route('/flash/get_winners')
def get_flash_winners_today():
    puzzleNumber = get_puzzle_number()
    return get_flash_winners(puzzleNumber)

@app.route('/flash/get_full_list')
def get_flash_full_list():
    day = request.args.get('day')
    puzzleNumber = get_puzzle_number()
    day = day if day else puzzleNumber
    res = _get_full_list(FLASH_DB_PATH, day)
    data = {'word_list':res}
    return jsonify(data) 

############################################
################ CLASSIQUE #################
############################################

@app.route('/')
def index():
    puzzleNumber = get_puzzle_number()
    yesterday_list = get_history(puzzleNumber-1)
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
    con, cur = connect_to_db(STAT_DB_PATH)
    query = f"SELECT * FROM day{get_puzzle_number()}"
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

def _get_full_list(db, day):
    con, cur = connect_to_db(db)
    query = f'select * from day{day}'
    check = cur.execute(query)
    res = [[w,s] for w,_,_,s in check.fetchall()]
    return  res

     

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

def get_word_from_position(db, day, score):
    con, cur = connect_to_db(db)
    query = f'select * from day{day} where score={score}'
    check = cur.execute(query)
    return check.fetchone()[0]

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

def connect_to_db(db_path):
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()
    return con, cur

def clean_word(word):
    return word.replace('œ', 'oe').replace('æ', 'ae')

def check_word(db, day, word):
    word = clean_word(word)
    # lemma = get_lemma(word)
    # if not lemma:
    #     return '',-1
    con, cur = connect_to_db(db)
    def get_score_from_lemma(lemma):
        with con:
            query = f'select * from day{day} where lemma="{lemma}" collate nocase'
            check = cur.execute(query)
            found = check.fetchone()
            if found:
                return found[0], found[3]
            else:
                return '',0
    def get_score_from_word(word):
        with con:
            query = f'select score from day{day} where word="{word}" collate nocase'
            check = cur.execute(query)
            found = check.fetchone()
            if found:
                return found[0]
            else:
                return 0
    def does_word_exist(word):
        with con:
            query=f'select exists(select 1 from all_words_fr where word="{word}" collate nocase) limit 1'
            check = cur.execute(query) 
            found = check.fetchone()[0]
            if found:
                return 1
            else:
                return 0
    # lemma = get_lemma(word)

    word_exists = does_word_exist(word)
    if not (word_exists):
        con.close()
        return '',-1

    score = get_score_from_word(word)
    # if not word:
    #     word = lemma
    con.close()
    return word, score