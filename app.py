# app.py
from flask import Flask, render_template
from db import init_db
from cliente import cliente_bp
from fornecedor import fornecedor_bp
from auth import auth_bp  # Importa o Blueprint de autenticação
from pessoa import pessoa_bp
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar flash messages e sessões

# Configurações de upload
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Garantir que o diretório de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializa o banco de dados
init_db()

# Registra os Blueprints
app.register_blueprint(cliente_bp, url_prefix='/cliente')
app.register_blueprint(fornecedor_bp, url_prefix='/fornecedor')
app.register_blueprint(auth_bp)  # Registra o Blueprint de autenticação
app.register_blueprint(pessoa_bp, url_prefix='/pessoa')

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')  # Renderiza o template index.html

if __name__ == '__main__':
    app.run(debug=True)
