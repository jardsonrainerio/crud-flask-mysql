# fornecedor/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db
import mysql.connector

fornecedor_bp = Blueprint('fornecedor', __name__, template_folder='templates/fornecedor')


@fornecedor_bp.route('/')
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
        # Total de fornecedores
        cursor.execute('SELECT COUNT(*) as total FROM fornecedor')
        total_items = cursor.fetchone()['total']
        total_pages = (total_items + per_page - 1) // per_page

        # Fornecedores da página atual
        cursor.execute('SELECT * FROM fornecedor ORDER BY id LIMIT %s OFFSET %s', (per_page, offset))
        fornecedores = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar fornecedores: {e}')
        fornecedores = []
        total_pages = 1
    finally:
        cursor.close()

    return render_template('fornecedor_listar.html', fornecedores=fornecedores, page=page, total_pages=total_pages)


@fornecedor_bp.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        nome = request.form['nome']
        produto = request.form['produto']
        contato = request.form['contato']
        db = get_db()
        if db is None:
            flash('Erro de conexão com o banco de dados.')
            return redirect(url_for('fornecedor.criar'))
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO fornecedor (nome, produto, contato) VALUES (%s, %s, %s)',
                           (nome, produto, contato))
            db.commit()
            flash('Fornecedor criado com sucesso!')
            return redirect(url_for('fornecedor.listar'))
        except mysql.connector.IntegrityError:
            flash('Erro: Nome do fornecedor já existe.')
        except mysql.connector.Error as e:
            flash(f'Erro ao criar fornecedor: {e}')
        finally:
            cursor.close()
    return render_template('fornecedor_criar.html')


@fornecedor_bp.route('/<int:id>')
def detalhes(id):
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('fornecedor.listar'))
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM fornecedor WHERE id = %s', (id,))
        fornecedor = cursor.fetchone()
        if fornecedor is None:
            flash('Fornecedor não encontrado.')
            return redirect(url_for('fornecedor.listar'))
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar fornecedor: {e}')
        fornecedor = None
    finally:
        cursor.close()
    return render_template('fornecedor_detalhes.html', fornecedor=fornecedor)


@fornecedor_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('fornecedor.listar'))
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM fornecedor WHERE id = %s', (id,))
        fornecedor = cursor.fetchone()
        if fornecedor is None:
            flash('Fornecedor não encontrado.')
            return redirect(url_for('fornecedor.listar'))
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar fornecedor: {e}')
        fornecedor = None
    finally:
        cursor.close()

    if request.method == 'POST' and fornecedor:
        nome = request.form['nome']
        produto = request.form['produto']
        contato = request.form['contato']
        cursor = db.cursor()
        try:
            cursor.execute('UPDATE fornecedor SET nome = %s, produto = %s, contato = %s WHERE id = %s',
                           (nome, produto, contato, id))
            db.commit()
            flash('Fornecedor atualizado com sucesso!')
            return redirect(url_for('fornecedor.detalhes', id=id))
        except mysql.connector.IntegrityError:
            flash('Erro: Nome do fornecedor já existe.')
        except mysql.connector.Error as e:
            flash(f'Erro ao atualizar fornecedor: {e}')
        finally:
            cursor.close()

    return render_template('fornecedor_editar.html', fornecedor=fornecedor)


@fornecedor_bp.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    db = get_db()
    if db is None:
        flash('Erro de conexão com o banco de dados.')
        return redirect(url_for('fornecedor.listar'))
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM fornecedor WHERE id = %s', (id,))
        db.commit()
        flash('Fornecedor deletado com sucesso!')
    except mysql.connector.Error as e:
        flash(f'Erro ao deletar fornecedor: {e}')
    finally:
        cursor.close()
    return redirect(url_for('fornecedor.listar'))
