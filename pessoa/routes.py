# pessoa/routes.py
from flask import  Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from db import get_db
from auth import login_required
import os

pessoa_bp = Blueprint('pessoa', __name__, template_folder='templates/pessoa')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    if filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return True


@pessoa_bp.route('/')
def listar():
    """
    Rota pública para listar pessoas com paginação.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Obtém o número da página a partir dos parâmetros da URL, padrão 1
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = 5  # Itens por página
    offset = (page - 1) * per_page

    # Consulta para obter o total de pessoas
    cursor.execute('SELECT COUNT(*) AS total FROM pessoa')
    total_items = cursor.fetchone()['total']
    total_pages = (total_items + per_page - 1) // per_page

    # Consulta para obter as pessoas da página atual
    cursor.execute('SELECT * FROM pessoa ORDER BY id LIMIT %s OFFSET %s', (per_page, offset))
    pessoas = cursor.fetchall()

    cursor.close()
    return render_template('pessoa_listar.html', pessoas=pessoas, page=page, total_pages=total_pages)


@pessoa_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """
    Rota protegida para criar uma nova pessoa.
    """
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        data_nascimento = request.form['data_nascimento'].strip()
        foto = request.files.get('foto')

        if not nome or not data_nascimento:
            flash('Nome e Data de Nascimento são obrigatórios.')
            return redirect(url_for('pessoa.criar'))

        db = get_db()
        cursor = db.cursor()

        try:
            # Inserir a pessoa sem a foto inicialmente
            cursor.execute(
                'INSERT INTO pessoa (nome, data_nascimento) VALUES (%s, %s)',
                (nome, data_nascimento)
            )
            pessoa_id = cursor.lastrowid
            # Processar a foto
            if foto and allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{pessoa_id}.{ext}"
                foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                foto.save(foto_path)

                # Atualizar o registro com o caminho da foto
                cursor.execute(
                    'UPDATE pessoa SET foto = %s WHERE id = %s',
                    (f'uploads/{new_filename}', pessoa_id)
                )
            elif foto:
                flash('Tipo de arquivo de foto não permitido.')
                return redirect(url_for('pessoa.criar'))

            db.commit()
            flash('Pessoa criada com sucesso!')
            return redirect(url_for('pessoa.listar'))
        except Exception as e:
            db.rollback()
            flash('Ocorreu um erro ao criar a pessoa.')
            return redirect(url_for('pessoa.criar'))
        finally:
            cursor.close()

    return render_template('pessoa_criar.html')


@pessoa_bp.route('/detalhes/<int:id>')
def detalhes(id):
    """
    Rota pública para visualizar detalhes de uma pessoa específica.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM pessoa WHERE id = %s', (id,))
    pessoa = cursor.fetchone()
    cursor.close()

    if pessoa is None:
        flash('Pessoa não encontrada.')
        return redirect(url_for('pessoa.listar'))

    return render_template('pessoa_detalhes.html', pessoa=pessoa)


@pessoa_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """
    Rota protegida para editar uma pessoa existente.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM pessoa WHERE id = %s', (id,))
    pessoa = cursor.fetchone()

    if pessoa is None:
        cursor.close()
        flash('Pessoa não encontrada.')
        return redirect(url_for('pessoa.listar'))

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        data_nascimento = request.form['data_nascimento'].strip()
        foto = request.files.get('foto')

        if not nome or not data_nascimento:
            flash('Nome e Data de Nascimento são obrigatórios.')
            return redirect(url_for('pessoa.editar', id=id))

        try:
            # Atualizar nome e data de nascimento
            cursor.execute(
                'UPDATE pessoa SET nome = %s, data_nascimento = %s WHERE id = %s',
                (nome, data_nascimento, id)
            )

            # Processar a foto, se fornecida
            if foto and allowed_file(foto.filename):
                filename = secure_filename(foto.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{id}.{ext}"
                foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                foto.save(foto_path)

                # Atualizar o registro com o novo caminho da foto
                cursor.execute(
                    'UPDATE pessoa SET foto = %s WHERE id = %s',
                    (f'uploads/{new_filename}', id)
                )
            elif foto:
                flash('Tipo de arquivo de foto não permitido.')
                return redirect(url_for('pessoa.editar', id=id))

            db.commit()
            flash('Pessoa atualizada com sucesso!')
            return redirect(url_for('pessoa.detalhes', id=id))
        except Exception as e:
            db.rollback()
            flash('Ocorreu um erro ao atualizar a pessoa.')
            return redirect(url_for('pessoa.editar', id=id))
        finally:
            cursor.close()

    cursor.close()
    return render_template('pessoa_editar.html', pessoa=pessoa)


@pessoa_bp.route('/deletar/<int:id>', methods=['POST'])
@login_required
def deletar(id):
    """
    Rota protegida para deletar uma pessoa existente.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        # Obter a foto antes de deletar
        cursor.execute('SELECT foto FROM pessoa WHERE id = %s', (id,))
        pessoa = cursor.fetchone()
        if pessoa and pessoa[0]:
            foto_path = os.path.join(current_app.root_path, 'static', pessoa[0])
            if os.path.exists(foto_path):
                os.remove(foto_path)

        # Deletar a pessoa
        cursor.execute('DELETE FROM pessoa WHERE id = %s', (id,))
        db.commit()
        flash('Pessoa deletada com sucesso!')
    except Exception as e:
        db.rollback()
        flash('Ocorreu um erro ao deletar a pessoa.')
    finally:
        cursor.close()

    return redirect(url_for('pessoa.listar'))
