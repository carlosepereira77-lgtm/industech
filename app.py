from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///industech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------------------------------------
# ESTRUTURA COMPLETA DE TABELAS (12 MÓDULOS)
# ----------------------------------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

class MaterialEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Float, default=0.0)
    quantidade_minima = db.Column(db.Float, default=10.0)
    unidade = db.Column(db.String(20), default='Unidades')

    def to_dict(self):
        return {
            "id": self.id, "codigo": self.codigo, "nome": self.nome,
            "quantidade": self.quantidade, "quantidade_minima": self.quantidade_minima,
            "unidade": self.unidade,
            "status": 'Baixo' if self.quantidade <= self.quantidade_minima else 'OK'
        }

class OrdemProducao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_op = db.Column(db.String(50), unique=True, nullable=False)
    produto_nome = db.Column(db.String(100), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material_estoque.id'), nullable=True)
    quantidade_planejada = db.Column(db.Integer, nullable=False)
    quantidade_produzida = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Em Andamento')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        mat = MaterialEstoque.query.get(self.material_id) if self.material_id else None
        return {
            "id": self.id, "codigo_op": self.codigo_op, "produto_nome": self.produto_nome,
            "material_utilizado": mat.nome if mat else "N/A",
            "quantidade_planejada": self.quantidade_planejada,
            "quantidade_produzida": self.quantidade_produzida,
            "status": self.status, "criado_em": self.criado_em.strftime('%d/%m/%Y %H:%M')
        }

class Maquina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), default='Operacional')

    def to_dict(self):
        return {"id": self.id, "codigo": self.codigo, "nome": self.nome, "setor": self.setor, "status": self.status}

class InspecaoQualidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(100), nullable=False)
    aprovados = db.Column(db.Integer, default=0)
    reprovados = db.Column(db.Integer, default=0)
    defeito = db.Column(db.String(200), nullable=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "produto": self.produto, "aprovados": self.aprovados,
            "reprovados": self.reprovados, "defeito": self.defeito or "Nenhum",
            "data": self.data.strftime('%d/%m/%Y %H:%M')
        }

class RegistroDesperdicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Float, default=0.0)
    etapa = db.Column(db.String(50), nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "material": self.material, "quantidade": self.quantidade,
            "etapa": self.etapa, "motivo": self.motivo, "data": self.data.strftime('%d/%m/%Y %H:%M')
        }

class ConsumoEnergia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setor = db.Column(db.String(50), nullable=False)
    kwh = db.Column(db.Float, nullable=False)
    custo_estimado = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "setor": self.setor, "kwh": self.kwh, "custo_estimado": self.custo_estimado, "data": self.data.strftime('%d/%m/%Y')}

class PedidoLogistica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_pedido = db.Column(db.String(50), unique=True, nullable=False)
    cliente = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), default='Aguardando Envio')

    def to_dict(self):
        return {"id": self.id, "codigo_pedido": self.codigo_pedido, "cliente": self.cliente, "destino": self.destino, "status": self.status}

class LoteRastreavel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_lote = db.Column(db.String(50), unique=True, nullable=False)
    produto = db.Column(db.String(100), nullable=False)
    etapa_atual = db.Column(db.String(50), default='Usinagem')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "numero_lote": self.numero_lote, "produto": self.produto, "etapa_atual": self.etapa_atual, "data": self.data_criacao.strftime('%d/%m/%Y')}

class FuncionarioTurno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    turno = db.Column(db.String(30), default='Manhã (06h - 14h)')

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "cargo": self.cargo, "setor": self.setor, "turno": self.turno}

class OcorrenciaSeguranca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    gravidade = db.Column(db.String(20), default='Baixa')
    status = db.Column(db.String(20), default='Pendente')

    def to_dict(self):
        return {"id": self.id, "descricao": self.descricao, "setor": self.setor, "gravidade": self.gravidade, "status": self.status}

# ----------------------------------------------------
# ROTAS DA API REST
# ----------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    usr = Usuario.query.filter_by(email=dados.get('email')).first()
    if usr and check_password_hash(usr.senha_hash, dados.get('senha')):
        return jsonify({"mensagem": "Sucesso", "usuario": usr.nome}), 200
    return jsonify({"erro": "E-mail ou senha inválidos"}), 401

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify({
        "kpis": {
            "total_ops": OrdemProducao.query.count(),
            "total_pecas": db.session.query(db.func.sum(OrdemProducao.quantidade_planejada)).scalar() or 0,
            "estoque_baixo": MaterialEstoque.query.filter(MaterialEstoque.quantidade <= MaterialEstoque.quantidade_minima).count(),
            "maquinas_manut": Maquina.query.filter(Maquina.status.in_(['Atenção', 'Em Manutenção'])).count(),
            "total_reprovados": db.session.query(db.func.sum(InspecaoQualidade.reprovados)).scalar() or 0,
            "total_desperdicio": round(db.session.query(db.func.sum(RegistroDesperdicio.quantidade)).scalar() or 0, 2),
            "pedidos_pendentes": PedidoLogistica.query.filter_by(status='Aguardando Envio').count(),
            "ocorrencias_seguranca": OcorrenciaSeguranca.query.filter_by(status='Pendente').count()
        }
    }), 200

# ROTAS CRUD GENÉRICAS PARA TODOS OS MÓDULOS
@app.route('/api/producao', methods=['GET', 'POST'])
def api_producao():
    if request.method == 'POST':
        d = request.get_json()
        if d.get('material_id'):
            m = MaterialEstoque.query.get(d['material_id'])
            if m: m.quantidade = max(0.0, m.quantidade - float(d.get('quantidade_planejada', 0)))
        nova = OrdemProducao(codigo_op=f"OP-{int(datetime.utcnow().timestamp())}", produto_nome=d['produto_nome'], material_id=d.get('material_id'), quantidade_planejada=int(d['quantidade_planejada']))
        db.session.add(nova); db.session.commit()
        return jsonify(nova.to_dict()), 201
    return jsonify([x.to_dict() for x in OrdemProducao.query.order_by(OrdemProducao.id.desc()).all()])

@app.route('/api/estoque', methods=['GET', 'POST'])
def api_estoque():
    if request.method == 'POST':
        d = request.get_json()
        novo = MaterialEstoque(codigo=f"MAT-{int(datetime.utcnow().timestamp())%10000}", nome=d['nome'], quantidade=float(d['quantidade']), quantidade_minima=float(d['quantidade_minima']), unidade=d['unidade'])
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in MaterialEstoque.query.order_by(MaterialEstoque.id.desc()).all()])

@app.route('/api/manutencao', methods=['GET', 'POST'])
def api_manutencao():
    if request.method == 'POST':
        d = request.get_json()
        novo = Maquina(codigo=f"MAQ-{int(datetime.utcnow().timestamp())%10000}", nome=d['nome'], setor=d['setor'], status=d['status'])
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in Maquina.query.order_by(Maquina.id.desc()).all()])

@app.route('/api/qualidade', methods=['GET', 'POST'])
def api_qualidade():
    if request.method == 'POST':
        d = request.get_json()
        novo = InspecaoQualidade(produto=d['produto'], aprovados=int(d['aprovados']), reprovados=int(d['reprovados']), defeito=d.get('defeito'))
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in InspecaoQualidade.query.order_by(InspecaoQualidade.id.desc()).all()])

@app.route('/api/desperdicios', methods=['GET', 'POST'])
def api_desperdicios():
    if request.method == 'POST':
        d = request.get_json()
        novo = RegistroDesperdicio(material=d['material'], quantidade=float(d['quantidade']), etapa=d['etapa'], motivo=d['motivo'])
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in RegistroDesperdicio.query.order_by(RegistroDesperdicio.id.desc()).all()])

@app.route('/api/energia', methods=['GET', 'POST'])
def api_energia():
    if request.method == 'POST':
        d = request.get_json()
        novo = ConsumoEnergia(setor=d['setor'], kwh=float(d['kwh']), custo_estimado=float(d['kwh']) * 0.75)
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in ConsumoEnergia.query.order_by(ConsumoEnergia.id.desc()).all()])

@app.route('/api/logistica', methods=['GET', 'POST'])
def api_logistica():
    if request.method == 'POST':
        d = request.get_json()
        novo = PedidoLogistica(codigo_pedido=f"PED-{int(datetime.utcnow().timestamp())%10000}", cliente=d['cliente'], destino=d['destino'], status=d.get('status', 'Aguardando Envio'))
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in PedidoLogistica.query.order_by(PedidoLogistica.id.desc()).all()])

@app.route('/api/rastreabilidade', methods=['GET', 'POST'])
def api_rastreabilidade():
    if request.method == 'POST':
        d = request.get_json()
        novo = LoteRastreavel(numero_lote=f"LOT-{int(datetime.utcnow().timestamp())%100000}", produto=d['produto'], etapa_atual=d['etapa_atual'])
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in LoteRastreavel.query.order_by(LoteRastreavel.id.desc()).all()])

@app.route('/api/funcionarios', methods=['GET', 'POST'])
def api_funcionarios():
    if request.method == 'POST':
        d = request.get_json()
        novo = FuncionarioTurno(nome=d['nome'], cargo=d['cargo'], setor=d['setor'], turno=d['turno'])
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in FuncionarioTurno.query.order_by(FuncionarioTurno.id.desc()).all()])

@app.route('/api/seguranca', methods=['GET', 'POST'])
def api_seguranca():
    if request.method == 'POST':
        d = request.get_json()
        novo = OcorrenciaSeguranca(descricao=d['descricao'], setor=d['setor'], gravidade=d['gravidade'])
        db.session.add(novo); db.session.commit()
        return jsonify(novo.to_dict()), 201
    return jsonify([x.to_dict() for x in OcorrenciaSeguranca.query.order_by(OcorrenciaSeguranca.id.desc()).all()])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(email='admin@industech.com').first():
            db.session.add(Usuario(nome='Administrador', email='admin@industech.com', senha_hash=generate_password_hash('admin123')))
            db.session.commit()
    print("--------------------------------------------------")
    print("🚀 SERVIDOR INDUSTECH (12 MÓDULOS) RODANDO EM http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(debug=True, port=5000)