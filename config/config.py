import pathlib
from dotenv import dotenv_values

BASE_DIR = pathlib.Path(__file__).parent.parent
config = dotenv_values('.env')
PAGINATOR_NUMBER = 3  # кількість записів для представлення
STRING_WIDTH = 80


class Config:
    SQLALCHEMY_DATABASE_URI = 'mariadb+mariadbconnector://root:456852@127.0.0.1:3306/assistant_mariadb'
    SECRET_KEY = config['SECRET_KEY']
