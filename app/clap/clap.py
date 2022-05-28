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
    hash,
    get_hash_client_ip,
    COLORS,
    STAT_DB_PATH
)

CLAP_DB_PATH = f"{Path(__file__).parent.parent.parent}/clap.db"
PONCTUATION = [',',':',';','.','?',"'",'!',' ']
STOP_WORDS = ['à', 'le', 'la', 'les', 'l','d', 'de', 'des', 'du', 'une','en','un','alors', 'donc', 'au', 
              'avec','car','ce','cet','cette','ces', 'ceux', 'son', 'sa', 'se', 'leur', 'leurs', 
              'ceci', 'cela', 'ça', 'là', 'chaque', 'tous', 'tout','pas', 'aux', 'or', 'mais', 'ni', 'ne',
              'il', 'ils', 'elle', 'elles', 'je', 'tu', 'nous', 'vous', 'et', 'y', 'aussi', 'aucun', 
              'es', 'est', 'sont', 'a', 'être', 'avoir', 'plus', 'moins', 'dès', 'toi', 
              'quel', 'quelle', 'quelles', 'quels', 'trop', 'très', 'ou', 'ci'
               'étaient', 'étais', 'était', 'étant', 'étiez', 'étions', 'étés', 'êtes', 'être', 'voilà'
              ]

clap_bp = Blueprint('clap', __name__, template_folder='templates', static_folder='static')

@clap_bp.route('/')
def clap():
    '''
    set all publications to visible.
    '''
    puzzleNumber = get_puzzle_number()
    winners_today = get_clap_winners_today()
    yesterday_title, yesterday_overview, _, _, yesterday_image_url  = get_movie_info(puzzleNumber-1)
    title, _, overview_redacted, max_score, _ = get_movie_info(puzzleNumber)
    return render_template(
        'clap.html', 
        puzzleNumber = puzzleNumber,
        movie_title = title,
        movie_overview = overview_redacted,
        yesterday_title = yesterday_title,
        winners_yesterday = get_clap_winners(puzzleNumber-1),
        yesterday_overview = yesterday_overview,
        yesterday_image_url = yesterday_image_url,
        winners_today = winners_today,
        max_score = max_score,
        game_mode = 'Clap',
        # game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

def get_score(nb_guesses, nb_title_guesses):
    score = 1000-3*nb_guesses-15*(nb_title_guesses-1)
    return score if score > 0 else 0

@clap_bp.route('/win')
def clap_win():
    '''
    Update the database to add the win.
    '''
    title = request.args.get('title')
    nb_guesses = int(request.args.get('nb_guesses'))
    nb_title_guesses = int(request.args.get('nb_title_guesses'))
    user_id = request.args.get('user_id')
    score = get_score(nb_guesses, nb_title_guesses)
    puzzleNumber = get_puzzle_number()
    real_title, overview,_, _, _ = get_movie_info(puzzleNumber)
    already_won = False
    if not (real_title.lower().strip() == title.lower().strip()):
        return jsonify({})
    ip_hash = get_hash_client_ip()
    user_hash = hash(user_id)
    unique_hash = ip_hash+user_hash
    table_name = f"clap_day{puzzleNumber}"
    con, cur = connect_to_db(STAT_DB_PATH)
    con.commit()
    query = f"create table if not exists {table_name}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, nb_guesses INT, nb_title_guesses INT, points INT)"
    cur.execute(query)
    con.commit()
    with con:
        query = f'SELECT * FROM clap_day{puzzleNumber} WHERE unique_hash = "{unique_hash}"'
        cur.execute(query)
        res = cur.fetchall()
        if len(res) > 0:
            already_won = True
        else:
            with con:
                query = f"insert into clap_day{puzzleNumber} (unique_hash, ip_hash, user_hash, nb_guesses, nb_title_guesses, points)"
                query += f"values (\"{unique_hash}\", \"{ip_hash}\", \"{user_hash}\", {nb_guesses}, {nb_title_guesses}, {score})"""
                cur.execute(query)
                con.commit()
        query = f"SELECT * FROM clap_day{puzzleNumber}"
        cur.execute(query)
        res = cur.fetchall()
    data = {
        'already_won': already_won,
        'winners': get_clap_winners_today(),
        'overview': overview,
        'title': real_title,
        'score': score,
    }
    return jsonify(data)

def get_clap_winners_today():
    puzzleNumber = get_puzzle_number()
    return get_clap_winners(puzzleNumber)

def get_clap_winners(day):
    con, cur = connect_to_db(STAT_DB_PATH)
    table_name = f'clap_day{day}'
    query = f"create table if not exists {table_name}"
    query += "(unique_hash TEXT PRIMARY KEY, ip_hash TEXT, user_hash TEXT, nb_guesses INT, nb_title_guesses INT, points INT)"
    cur.execute(query)
    con.commit()
    total_winners = -1
    with con:
        query = f"SELECT COUNT(*) FROM {table_name}"
        cur.execute(query)
        res = cur.fetchall()
        total_winners = res[0][0] 
    return total_winners


@clap_bp.route('/check_title')   
def check_title():
    guess = request.args.get('title')
    puzzleNumber = get_puzzle_number()
    title, overview, overview_redacted, max_score, image_url = get_movie_info(puzzleNumber)
    if (guess.lower().strip() == title.lower().strip()):
        data = {
            'overview':overview,
            'title':title,
            'image_url': image_url,
            'win': True}
    else:
        data = {'win': False}
    return jsonify(data)

@clap_bp.route('/check_word')   
def check_word():
    puzzleNumber = get_puzzle_number()
    _, _,_, max_score, _ = get_movie_info(puzzleNumber)
    word = request.args.get('word')
    cur, con = connect_to_db(CLAP_DB_PATH)
    query = f"SELECT word,json FROM day{puzzleNumber}_words WHERE LOWER(word)=\"{word}\" LIMIT 1"
    check = cur.execute(query)
    ret = check.fetchall()
    def check_evaluation(data):
        best = 0
        for e in data:
            if e[-1] > best:
                best = e[-1]
            if e[-1] == max_score:
                return 'great'
        else:
            return 'good'
    if ret:
        word, word_data = ret[0]
        words_data = json.loads(word_data)
        evaluation = check_evaluation(words_data)
        return jsonify({'word': word, 'words':words_data, 'evaluation':evaluation})
    else:
        return jsonify({'word': None, 'words':None,'evaluation':'poop'})

def get_movie_info(day):
    cur, con = connect_to_db(CLAP_DB_PATH)
    query = f"SELECT * FROM day{day} LIMIT 1"
    check = cur.execute(query)
    [title, overview, overview_redacted, max_score, image_url] = check.fetchall()[0]
    return title, overview, overview_redacted, max_score, image_url

def get_redacted_html(text):
    pattern = re.compile(r"[\w]+|[.,!?; '\"]")
    split_text = pattern.findall(text)
    html_text = ''
    keyword = []
    id = 0
    for w in split_text:
        if not w.lower() in PONCTUATION+STOP_WORDS:
            html_text+=f'<span id={id} style="background-color:red;">{"&nbsp;"*len(w)}</span>'
            keyword.append(clean_word(w))
            id+=1
        else:
            html_text+=w
    return html_text