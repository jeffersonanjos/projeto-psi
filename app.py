from flask import Flask, render_template, request, redirect, url_for
from models import db, Receita, Usuario, Favorito, Comentario, Ingrediente, ReceitaIngrediente, Notificacao
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from flask import send_file
import io

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

# Tratador de erro para o status code 404 (Not Found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Tratador de erro para o status code 403 (Forbidden)
@app.errorhandler(403)
def forbidden_error(e):
    return render_template('403.html'), 403


# Rota principal: exibe a lista de todas as receitas ou os resultados da busca
@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        # Divide a string de busca em ingredientes individuais
        ingredientes_buscados = [ing.strip().lower() for ing in query.split(',')]
        
        # Constrói a lista de IDs de receitas que contêm os ingredientes
        receita_ids = db.session.query(ReceitaIngrediente.receita_id).join(Ingrediente).filter(
            Ingrediente.nome.in_(ingredientes_buscados)
        ).group_by(ReceitaIngrediente.receita_id).having(db.func.count(Ingrediente.id) == len(ingredientes_buscados)).all()
        
        # Extrai os IDs da tupla
        receita_ids = [r[0] for r in receita_ids]
        
        # Filtra as receitas pelos IDs encontrados
        receitas = Receita.query.filter(Receita.id.in_(receita_ids)).order_by(Receita.data_postagem.desc()).all()
    else:
        receitas = Receita.query.order_by(Receita.data_postagem.desc()).all()
    
    return render_template('index.html', receitas=receitas, query=query)


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

# Rota para exibir a lista de receitas favoritas do usuário
@app.route('/favoritos/<int:usuario_id>')
def favoritos(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    favoritos = Favorito.query.filter_by(usuario_id=usuario_id).all()
    # Acessa as receitas associadas através da entidade Favorito
    receitas_favoritas = [fav.receita for fav in favoritos]
    return render_template('favoritos.html', usuario=usuario, receitas=receitas_favoritas)

# Rota para adicionar uma receita aos favoritos
@app.route('/adicionar_favorito/<int:receita_id>', methods=['POST'])
def adicionar_favorito(receita_id):
    # Por enquanto, vamos usar o usuário de ID 1, pois não há sistema de login
    usuario_id = 1
    if not Favorito.query.filter_by(usuario_id=usuario_id, receita_id=receita_id).first():
        favorito = Favorito(usuario_id=usuario_id, receita_id=receita_id)
        db.session.add(favorito)
        db.session.commit()
    return redirect(url_for('receita_detail', id=receita_id))

# Rota para remover uma receita dos favoritos
@app.route('/remover_favorito/<int:receita_id>', methods=['POST'])
def remover_favorito(receita_id):
    # Por enquanto, vamos usar o usuário de ID 1
    usuario_id = 1
    favorito = Favorito.query.filter_by(usuario_id=usuario_id, receita_id=receita_id).first()
    if favorito:
        db.session.delete(favorito)
        db.session.commit()
    return redirect(url_for('receita_detail', id=receita_id))

# Rota para gerar PDF com a lista de ingredientes
@app.route('/gerar_pdf/<int:receita_id>')
def gerar_pdf(receita_id):
    receita = Receita.query.get_or_404(receita_id)
    
    # Busca os ingredientes associados à receita
    ingredientes_receita = ReceitaIngrediente.query.filter_by(receita_id=receita.id).all()

    # Cria um objeto BytesIO para armazenar o PDF na memória
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Define o título do PDF
    c.drawString(100, 750, f"Lista de Compras para: {receita.titulo}")
    c.drawString(100, 730, "-" * 50)
    
    # Escreve a lista de ingredientes
    y_pos = 710
    for item in ingredientes_receita:
        ingrediente = item.ingrediente
        quantidade = item.quantidade
        c.drawString(100, y_pos, f"- {ingrediente.nome}: {quantidade}")
        y_pos -= 20
        if y_pos < 100:  # Quebra de página se o conteúdo for muito longo
            c.showPage()
            y_pos = 750

    c.save()
    buffer.seek(0)
    
    # Retorna o arquivo PDF para download
    return send_file(buffer, as_attachment=True, download_name=f'lista_compras_{receita.titulo}.pdf', mimetype='application/pdf')

# Rota para exibir a página de comentários de uma receita
@app.route('/receita/<int:receita_id>/comentarios')
def comentarios(receita_id):
    receita = Receita.query.get_or_404(receita_id)
    return render_template('comments.html', receita=receita)

# Rota para adicionar um novo comentário
@app.route('/receita/<int:receita_id>/adicionar_comentario', methods=['POST'])
def adicionar_comentario(receita_id):
    receita = Receita.query.get_or_404(receita_id)
    conteudo = request.form['conteudo']
    # Usando o usuário de ID 1 por padrão, já que não temos um sistema de login
    usuario_id = 1 
    
    if conteudo:
        novo_comentario = Comentario(conteudo=conteudo, usuario_id=usuario_id, receita_id=receita_id)
        db.session.add(novo_comentario)
        db.session.commit()
    
    return redirect(url_for('comentarios', receita_id=receita.id))


# Rota para perfil de usuário
@app.route('/perfil/<int:id>')
def perfil_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template('user_profile.html', usuario=usuario)

#R

if __name__ == '__main__':
    app.run(debug=True)
