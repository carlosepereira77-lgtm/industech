import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados SQLite local na nuvem
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///industech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da tabela de Usuários
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Rota de Status para testar se o servidor está online
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "API IndusTech operando perfeitamente!"}), 200

# Rota de Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "E-mail e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login realizado com sucesso!", "user": {"email": user.email}}), 200
    
    return jsonify({"message": "E-mail ou senha incorretos!"}), 401

# Criação automática do Banco de Dados e do Usuário Admin ao iniciar
with app.app_context():
    db.create_all()
    
    # CREDENCIAIS DO USUÁRIO PADRÃO
    ADMIN_EMAIL = 'admin@industech.com'
    ADMIN_PASSWORD = 'admin123'

    # Cria o usuário admin se ele ainda não existir no banco
    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        hashed_pw = generate_password_hash(ADMIN_PASSWORD)
        new_admin = User(email=ADMIN_EMAIL, password=hashed_pw)
        db.session.add(new_admin)
        db.session.commit()
        print(f"Usuário administrador criado: {ADMIN_EMAIL}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)