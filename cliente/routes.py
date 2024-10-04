# cliente/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db
import mysql.connector

cliente_bp = Blueprint('cliente', __name__, template_folder='templates/cliente')


@cliente_bp.route('/')
def listar():
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('index'))

    # Paginação
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = 5  # Itens por página
    offset = (page - 1) * per_page

    cursor = db.cursor(dictionary=True)
    try:
        # Total de clientes
        cursor.execute('SELECT COUNT(*) as total FROM cliente')
        total_items = cursor.fetchone()['total']
        total_pages = (total_items + per_page - 1) // per_page

        # Clientes da página atual
        cursor.execute('SELECT * FROM cliente ORDER BY id LIMIT %s OFFSET %s', (per_page, offset))
        clientes = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar clientes: {e}')
        clientes = []
        total_pages = 1
    finally:
        cursor.close()

    return render_template('cliente_listar.html', clientes=clientes, page=page, total_pages=total_pages)


@cliente_bp.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        db = get_db()
        if db is None:
            flash('Erro de conexão com o banco de dados.')
            return redirect(url_for('cliente.criar'))
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO cliente (nome, email, telefone) VALUES (%s, %s, %s)', (nome, email, telefone))
            db.commit()
            flash('Cliente criado com sucesso!')
            return redirect(url_for('cliente.listar'))
        except mysql.connector.IntegrityError:
            flash('Erro: Email já existe.')
        except mysql.connector.Error as e:
            flash(f'Erro ao criar cliente: {e}')
        finally:
            cursor.close()
    return render_template('cliente_criar.html')


@cliente_bp.route('/<int:id>')
def detalhes(id):
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('cliente.listar'))
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cursor.fetchone()
        if cliente is None:
            flash('Cliente não encontrado.')
            return redirect(url_for('cliente.listar'))
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar cliente: {e}')
        cliente = None
    finally:
        cursor.close()
    return render_template('cliente_detalhes.html', cliente=cliente)


@cliente_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('cliente.listar'))
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cursor.fetchone()
        if cliente is None:
            flash('Cliente não encontrado.')
            return redirect(url_for('cliente.listar'))
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar cliente: {e}')
        cliente = None
    finally:
        cursor.close()

    if request.method == 'POST' and cliente:
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cursor = db.cursor()
        try:
            cursor.execute('UPDATE cliente SET nome = %s, email = %s, telefone = %s WHERE id = %s',
                           (nome, email, telefone, id))
            db.commit()
            flash('Cliente atualizado com sucesso!')
            return redirect(url_for('cliente.detalhes', id=id))
        except mysql.connector.IntegrityError:
            flash('Erro: Email já existe.')
        except mysql.connector.Error as e:
            flash(f'Erro ao atualizar cliente: {e}')
        finally:
            cursor.close()

    return render_template('cliente_editar.html', cliente=cliente)


@cliente_bp.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('cliente.listar'))
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM cliente WHERE id = %s', (id,))
        db.commit()
        flash('Cliente deletado com sucesso!')
    except mysql.connector.Error as e:
        flash(f'Erro ao deletar cliente: {e}')
    finally:
        cursor.close()
    return redirect(url_for('cliente.listar'))
