from flask import Flask, render_template, request, redirect, url_for
from models import db, Receita, Usuario

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desabilita o rastreamento de modificações para otimização
db.init_app(app)

# Inicialização do banco de dados e criação de um usuário padrão
with app.app_context():
    db.create_all()
    if not Usuario.query.first():
        user = Usuario(nome="Usuário Exemplo")
        db.session.add(user)
        db.session.commit()

# Rota principal: exibe a lista de todas as receitas
@app.route('/')
def index():
    receitas = Receita.query.order_by(Receita.data_postagem.desc()).all()
    return render_template('index.html', receitas=receitas)

# Rota para detalhes da receita: exibe informações de uma receita específica por ID
@app.route('/receita/<int:id>')
def receita_detail(id):
    receita = Receita.query.get_or_404(id)
    return render_template('recipe_detail.html', receita=receita)

# Rota para adicionar nova receita: lida com a exibição do formulário e o processamento dos dados
# Esta rota agora usa o template 'edit_recipe.html' para adicionar novas receitas
@app.route('/nova', methods=['GET', 'POST'])
def nova_receita():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        modo_preparo = request.form['modo_preparo']
        nova = Receita(titulo=titulo, descricao=descricao, modo_preparo=modo_preparo, usuario_id=1)
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for('index')) 
    # Passa uma receita vazia para o formulário de nova receita
    return render_template('edit_recipe.html', receita=None)

# Rota para editar uma receita existente
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    receita = Receita.query.get_or_404(id)
    if request.method == 'POST':
        receita.titulo = request.form['titulo']
        receita.descricao = request.form['descricao']
        receita.modo_preparo = request.form['modo_preparo']
        db.session.commit()
        return redirect(url_for('receita_detail', id=receita.id))
    return render_template('edit_recipe.html', receita=receita)

# Rota para excluir uma receita
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)
    db.session.delete(receita)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
