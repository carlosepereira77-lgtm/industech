import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Rota para verificar se a API está online
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "API IndusTech liberada!"}), 200

# Rota de Login sem restrições (Libera qualquer tentativa)
@app.route('/api/login', methods=['POST'])
def login():
    return jsonify({
        "message": "Login realizado com sucesso!",
        "user": {
            "email": "admin@industech.com"
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)