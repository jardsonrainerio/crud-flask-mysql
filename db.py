# db.py
import mysql.connector
from mysql.connector import Error
from flask import g, current_app
import atexit

DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'mydatabase',
    'user': 'root',
    'password': 'myrootpassword'
}

def get_db():
    db = mysql.connector.connect(host="localhost",
                                 database='mydatabase',
                                 user="root",
                                 passwd='myrootpassword', use_pure=True)
    return db

def init_db():
    db = get_db()
    if db is None:
        print("Falha na conexão com o banco de dados.")
        return
    cursor = db.cursor()
    # Criação da tabela cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            telefone VARCHAR(20)
        )
    ''')
    # Criação da tabela fornecedor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornecedor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            produto VARCHAR(255),
            contato VARCHAR(255)
        )
    ''')
    # Criação da tabela usuario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    ''')
    db.commit()
    cursor.close()

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None and db.is_connected():
        db.close()

# Registro do fechamento da conexão ao final da aplicação
atexit.register(close_connection)
