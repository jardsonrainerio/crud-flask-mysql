# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql.connector
import sys

# Criação do Blueprint de autenticação
auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

def login_required(f):
    """
    Decorador para proteger rotas que requerem autenticação.
    Redireciona para a página de login se o usuário não estiver autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota para registro de novos usuários.
    GET: Exibe o formulário de registro.
    POST: Processa os dados do formulário e cria um novo usuário.
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Por favor, preencha todos os campos.')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                'INSERT INTO usuario (username, password) VALUES (%s, %s)',
                (username, hashed_password)
            )
            db.commit()
            flash('Usuário cadastrado com sucesso! Faça login.')
            return redirect(url_for('auth.login'))
        except mysql.connector.IntegrityError:
            flash('Nome de usuário já existe. Por favor, escolha outro.')
            return redirect(url_for('auth.register'))
        except Exception as e:
            db.rollback()
            print(f"Erro ao registrar usuário: {e}", file=sys.stderr)
            flash('Ocorreu um erro ao registrar o usuário. Tente novamente.')
            return redirect(url_for('auth.register'))
        finally:
            cursor.close()

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para login de usuários.
    GET: Exibe o formulário de login.
    POST: Processa os dados do formulário e autentica o usuário.
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                'SELECT * FROM usuario WHERE username = %s',
                (username,)
            )
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login realizado com sucesso!')
                return redirect(url_for('index'))
            else:
                flash('Nome de usuário ou senha incorretos.')
                return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Erro ao fazer login: {e}", file=sys.stderr)
            flash('Ocorreu um erro ao processar o login. Tente novamente.')
            return redirect(url_for('auth.login'))
        finally:
            cursor.close()

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Rota para logout de usuários.
    Remove as informações de sessão e redireciona para a página de login.
    """
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logout realizado com sucesso!')
    return redirect(url_for('auth.login'))
