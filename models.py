from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instância do SQLAlchemy para interagir com o banco de dados
db = SQLAlchemy()

# Modelo de dados para a tabela 'Usuario'
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) # Adicionei email para consistência
    senha = db.Column(db.String(255), nullable=True) # Armazena hash de senha
    foto_perfil = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)

# Modelo de dados para a tabela 'Receita'
class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    modo_preparo = db.Column(db.Text)
    imagem = db.Column(db.String(255), nullable=True) # Campo para a imagem
    data_postagem = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('receitas', lazy=True))

# Modelo de dados para a tabela 'Ingrediente'
class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

# Modelo de dados para a tabela 'ReceitaIngrediente' (entidade associativa)
class ReceitaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable=False)
    quantidade = db.Column(db.String(50), nullable=False)

    receita = db.relationship('Receita', backref=db.backref('ingredientes_associados', lazy=True))
    ingrediente = db.relationship('Ingrediente', backref=db.backref('receitas_associadas', lazy=True))

# Modelo de dados para a tabela 'Favorito'
class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('favoritos', lazy=True))
    receita = db.relationship('Receita', backref=db.backref('favoritado_por', lazy=True))

# Modelo de dados para a tabela 'Comentario'
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_comentario = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('comentarios', lazy=True))
    receita = db.relationship('Receita', backref=db.backref('comentarios', lazy=True))

# Modelo de dados para a tabela 'Notificacao'
class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visualizado = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    comentario_id = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('notificacoes', lazy=True))
    comentario = db.relationship('Comentario', backref=db.backref('notificacao', lazy=True, uselist=False))