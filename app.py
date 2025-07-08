from flask import Flask, render_template, request, redirect, url_for
from models import db, Receita, Usuario

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Inicializa o banco na primeira execução
with app.app_context():
    db.create_all()
    if not Usuario.query.first():
        user = Usuario(nome="Usuário Exemplo")
        db.session.add(user)
        db.session.commit()

@app.route('/')
def index():
    receitas = Receita.query.order_by(Receita.data_postagem.desc()).all()
    return render_template('index.html', receitas=receitas)

@app.route('/receita/<int:id>')
def receita_detail(id):
    receita = Receita.query.get_or_404(id)
    return render_template('recipe_detail.html', receita=receita)

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
    return render_template('new_recipe.html')

if __name__ == '__main__':
    app.run(debug=True)
