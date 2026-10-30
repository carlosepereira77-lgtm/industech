import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///industech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da tabela de Usuários
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Função para garantir que o usuário admin existe
def init_db():
    db.create_all()
    admin_email = 'admin@industech.com'
    admin_pass = 'admin123'
    
    user = User.query.filter_by(email=admin_email).first()
    if not user:
        user = User(email=admin_email, password=admin_pass)
        db.session.add(user)
        db.session.commit()
    else:
        user.password = admin_pass
        db.session.commit()

# Rota de Status
@app.route('/api/status', methods=['GET'])
def status():
    init_db()
    return jsonify({"status": "online", "message": "API IndusTech operando!"}), 200

# Rota de Login sem complicações de Hash
@app.route('/api/login', methods=['POST'])
def login():
    init_db()  # Garante que o banco e o admin existem antes de validar
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({"message": "E-mail e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        return jsonify({"message": "Login realizado com sucesso!", "user": {"email": user.email}}), 200
    
    return jsonify({"message": "E-mail ou senha incorretos!"}), 401

if __name__ == '__main__':
    with app.app_context():
        init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)