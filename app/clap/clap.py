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
from pathlib import Path

from app.common import (
    get_puzzle_number,
    get_day_from_puzzle_number,
    connect_to_db,
    clean_word,
    hash,
    COLORS
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
    title, overview = get_movie_info(puzzleNumber)
    return render_template(
        'clap.html', 
        puzzleNumber = puzzleNumber,
        movie_title = title,
        movie_overview = get_redacted_html(overview),
        # yesterday_word = get_yesterday_word(),
        # winners_yesterday = get_flash_winners(puzzleNumber-1),
        # winners_today = winners_today,
        game_mode = 'Clap',
        # game_sub_title = game_catch_phrase,
        colors = COLORS,
    )

@clap_bp.route('/get_hints')   
def get_hints():
    word = int(request.args.get('word'))
    jsonify({'date': day.strftime('%d-%m-%Y')})

def get_movie_info(day):
    print('*'*100)
    print(CLAP_DB_PATH)

    cur, con = connect_to_db(CLAP_DB_PATH)
    query = f"SELECT * FROM day{day} LIMIT 1"
    check = cur.execute(query)
    [title, overview] = check.fetchall()[0]
    return title, overview

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