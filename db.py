# db.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    try:
        db = mysql.connector.connect(
            host= os.getenv('DB_HOST', 'localhost'),
            database= os.getenv('DB_DATABASE', 'teste'),
            user= os.getenv('DB_USER', 'flaskuser'),
            passwd= os.getenv('DB_PASSWORD', 'senha_segura'),
            use_pure=True
        )
        if db.is_connected():
            print("Conexão com o banco de dados foi estabelecida com sucesso!")
            return db
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

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
    # Criação da tabela pessoa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            data_nascimento DATE,
            foto VARCHAR(255)
        )
    ''')
    db.commit()
    cursor.close()
