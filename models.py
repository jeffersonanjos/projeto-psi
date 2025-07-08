from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instância do SQLAlchemy para interagir com o banco de dados
db = SQLAlchemy()

# Modelo de dados para a tabela 'Usuario'
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Chave primária auto-incrementável
    nome = db.Column(db.String(100), nullable=False) # Nome do usuário, campo obrigatório

# Modelo de dados para a tabela 'Receita'
class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text) 
    modo_preparo = db.Column(db.Text)
    data_postagem = db.Column(db.DateTime, default=datetime.utcnow) # Data e hora da criação da receita, com valor padrão
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Relacionamento com o modelo Usuario: permite acessar o objeto Usuario associado a uma receita # e, inversamente, acessar todas as receitas de um Usuario (via 'backref').
    usuario = db.relationship('Usuario', backref=db.backref('receitas', lazy=True))
