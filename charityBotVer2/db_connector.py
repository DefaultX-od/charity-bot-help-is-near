import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def connect():
    dataBaseName = os.getenv('dataBaseName')
    userName = os.getenv('userName')
    userPassword = os.getenv('userPassword')
    hostName = os.getenv('hostName')
    try:
        conn = psycopg2.connect(dbname=dataBaseName, user=userName, password=userPassword, host=hostName)
        return conn
    except:
        print('Can`t establish connection to database')
