from app import app
from flask import (
    request,
)

from pathlib import Path
import sqlite3
from datetime import date, timedelta
from hashlib import sha1

STAT_DB_PATH = f"{Path(__file__).parent.parent.parent}/stats.db"

COLORS = {
    'classique' : '#5cb85c',
    'flash' : '#d25e00',
    'master' : '#dc3545',
    'clap': '#0275d8'
}

def hash(s):
    h = sha1()
    h.update(s.encode("ascii"))
    hash = h.hexdigest()
    return hash

def get_word_from_position(db, day, score):
    con, cur = connect_to_db(db)
    query = f'select * from day{day} where score={score}'
    check = cur.execute(query)
    return check.fetchone()[0]

def get_puzzle_number():
    today = date.today()
    day0 = date(*app.config['DAY0'])
    delta_days = (today-day0).days
    assert(delta_days > 0)
    return delta_days

def get_day_from_puzzle_number():
    number = int(request.args.get('number'))
    day0 = date(*app.config['DAY0'])
    day = day0+ timedelta(days=number)
    return day

def connect_to_db(db_path):
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL")
    cur = con.cursor()
    return con, cur

def clean_word(word):
    return word.replace('œ', 'oe').replace('æ', 'ae')

def get_hash_client_ip():
    '''
    Get the hash of the client IP address to count the number of wins.
    Hash to preserve privacy.
    '''
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    return hash(ip_addr)

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

def _get_full_list(db, day):
    con, cur = connect_to_db(db)
    query = f'select * from day{day}'
    check = cur.execute(query)
    res = [[w,s] for w,_,_,s in check.fetchall()]
    return  res