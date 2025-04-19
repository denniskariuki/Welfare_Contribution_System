import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chuka_welfare_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://root:@localhost/chuka_welfare_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False