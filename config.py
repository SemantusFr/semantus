import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't@mereen$tring48201dfa4dfgsdasaf4724]['
    DAY0 = (2022, 4, 24)