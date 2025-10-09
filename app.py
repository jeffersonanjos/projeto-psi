from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from models import db, Receita, Usuario, Favorito, Comentario, Ingrediente, ReceitaIngrediente, Notificacao, Avaliacao
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from flask import send_file
import io
import textwrap
from werkzeug.security import generate_password_hash, check_password_hash
from email_utils import send_email
from sqlalchemy import text as sa_text, or_

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desabilita o rastreamento de modificações para otimização
db.init_app(app)

# Inicialização do banco de dados e criação de um usuário padrão
with app.app_context():
    db.create_all()
    # Garante coluna 'tipo' na tabela receita (migração simples para SQLite)
    try:
        with db.engine.connect() as conn:
            result = conn.execute(sa_text("PRAGMA table_info('receita')"))
            col_names = [row[1] for row in result]
            if 'tipo' not in col_names:
                conn.execute(sa_text("ALTER TABLE receita ADD COLUMN tipo VARCHAR(50) DEFAULT 'Outros'"))
    except Exception:
        # Em ambientes diferentes pode não ser necessário; seguir sem interromper
        pass
    if not Usuario.query.first():
        user = Usuario(
            nome="Usuário Exemplo",
            email="exemplo@teste.com",
            senha=generate_password_hash("123456")
        )
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
    current_user_id = session.get('user_id')
    # Parâmetros de busca: 'query' (ingredientes), 'q' (título/descrição) e 'tipo' (categoria)
    query_ingredientes = request.args.get('query')
    q = request.args.get('q')
    tipo = request.args.get('tipo')

    categorias = [
        'Canais Especiais', 'Notícias', 'Bolos e Tortas', 'Carnes', 'Aves',
        'Peixes e Frutos do Mar', 'Saladas e Molhos', 'Sopas', 'Massas', 'Bebidas',
        'Doces e Sobremesas', 'Lanches', 'Alimentação Saudável', 'Outros'
    ]

    base_query = Receita.query

    if query_ingredientes:
        ingredientes_buscados = [ing.strip().lower() for ing in query_ingredientes.split(',') if ing.strip()]
        if ingredientes_buscados:
            receita_ids = (
                db.session.query(ReceitaIngrediente.receita_id)
                .join(Ingrediente)
                .filter(Ingrediente.nome.in_(ingredientes_buscados))
                .group_by(ReceitaIngrediente.receita_id)
                .having(db.func.count(Ingrediente.id) == len(ingredientes_buscados))
                .all()
            )
            receita_ids = [r[0] for r in receita_ids]
            base_query = base_query.filter(Receita.id.in_(receita_ids))

    if q:
        like = f"%{q}%"
        base_query = base_query.filter(or_(Receita.titulo.ilike(like), Receita.descricao.ilike(like)))

    if tipo and tipo != 'Todos':
        base_query = base_query.filter(Receita.tipo == tipo)

    receitas = base_query.order_by(Receita.data_postagem.desc()).all()

    return render_template(
        'index.html',
        receitas=receitas,
        query=query_ingredientes,
        q=q,
        tipo=tipo,
        categorias=categorias,
        current_user_id=current_user_id,
    )


# Rota para detalhes da receita: exibe informações de uma receita específica por ID
@app.route('/receita/<int:id>')
def receita_detail(id):
    receita = Receita.query.get_or_404(id)
    current_user_id = session.get('user_id')
    is_owner = current_user_id == receita.usuario_id if current_user_id else False
    # Média e minha avaliação
    media = db.session.query(db.func.avg(Avaliacao.nota)).filter_by(receita_id=id).scalar() or 0
    media = round(float(media), 1) if media else 0
    total = db.session.query(db.func.count(Avaliacao.id)).filter_by(receita_id=id).scalar() or 0
    minha = None
    if current_user_id:
        av = Avaliacao.query.filter_by(usuario_id=current_user_id, receita_id=id).first()
        if av:
            minha = av.nota
    return render_template(
        'recipe_detail.html',
        receita=receita,
        current_user_id=current_user_id,
        is_owner=is_owner,
        media_avaliacao=media,
        total_avaliacoes=total,
        minha_avaliacao=minha,
    )

# Rota para adicionar nova receita: lida com a exibição do formulário e o processamento dos dados
# Esta rota agora usa o template 'edit_recipe.html' para adicionar novas receitas
@app.route('/nova', methods=['GET', 'POST'])
def nova_receita():
    if not session.get('user_id'):
        flash('Faça login para adicionar receitas.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        modo_preparo = request.form['modo_preparo']
        tipo = request.form.get('tipo') or 'Outros'
        nova = Receita(titulo=titulo, descricao=descricao, modo_preparo=modo_preparo, tipo=tipo, usuario_id=session['user_id'])
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for('index')) 
    # Passa uma receita vazia para o formulário de nova receita
    return render_template('edit_recipe.html', receita=None)

# Rota para editar uma receita existente
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    receita = Receita.query.get_or_404(id)
    if not session.get('user_id'):
        flash('Faça login para editar receitas.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        receita.titulo = request.form['titulo']
        receita.descricao = request.form['descricao']
        receita.modo_preparo = request.form['modo_preparo']
        receita.tipo = request.form.get('tipo') or receita.tipo
        db.session.commit()
        return redirect(url_for('receita_detail', id=receita.id))
    return render_template('edit_recipe.html', receita=receita)

# Rota para excluir uma receita
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)
    if not session.get('user_id'):
        flash('Faça login para excluir receitas.')
        return redirect(url_for('login'))
    if receita.usuario_id != session['user_id']:
        abort(403)
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

# Favoritos do usuário logado
@app.route('/meus_favoritos')
def meus_favoritos():
    if not session.get('user_id'):
        flash('Faça login para ver seus favoritos.')
        return redirect(url_for('login'))
    usuario_id = session['user_id']
    usuario = Usuario.query.get_or_404(usuario_id)
    favoritos = Favorito.query.filter_by(usuario_id=usuario_id).all()
    receitas_favoritas = [fav.receita for fav in favoritos]
    return render_template('favoritos.html', usuario=usuario, receitas=receitas_favoritas)

# Rota para adicionar uma receita aos favoritos
@app.route('/adicionar_favorito/<int:receita_id>', methods=['POST'])
def adicionar_favorito(receita_id):
    if not session.get('user_id'):
        flash('Faça login para favoritar receitas.')
        return redirect(url_for('login'))
    usuario_id = session['user_id']
    if not Favorito.query.filter_by(usuario_id=usuario_id, receita_id=receita_id).first():
        favorito = Favorito(usuario_id=usuario_id, receita_id=receita_id)
        db.session.add(favorito)
        db.session.commit()
    return redirect(url_for('receita_detail', id=receita_id))

# Rota para remover uma receita dos favoritos
@app.route('/remover_favorito/<int:receita_id>', methods=['POST'])
def remover_favorito(receita_id):
    if not session.get('user_id'):
        flash('Faça login para gerenciar favoritos.')
        return redirect(url_for('login'))
    usuario_id = session['user_id']
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
    c.drawString(72, 770, f"Receita: {receita.titulo}")
    c.drawString(72, 754, f"Tipo: {receita.tipo or 'Outros'}")
    c.drawString(72, 740, "-" * 80)
    
    # Descrição
    y_pos = 720
    if receita.descricao:
        for line in textwrap.wrap(receita.descricao, width=90):
            c.drawString(72, y_pos, line)
            y_pos -= 14
    y_pos -= 10
    c.drawString(72, y_pos, "Ingredientes:")
    y_pos -= 16
    for item in ingredientes_receita:
        ingrediente = item.ingrediente
        quantidade = item.quantidade
        c.drawString(90, y_pos, f"- {ingrediente.nome}: {quantidade}")
        y_pos -= 16
        if y_pos < 100:  # Quebra de página se o conteúdo for muito longo
            c.showPage()
            y_pos = 770

    y_pos -= 10
    c.drawString(72, y_pos, "Modo de Preparo:")
    y_pos -= 16
    if receita.modo_preparo:
        for line in textwrap.wrap(receita.modo_preparo, width=95):
            c.drawString(72, y_pos, line)
            y_pos -= 14
            if y_pos < 100:
                c.showPage()
                y_pos = 770

    c.save()
    buffer.seek(0)
    
    # Retorna o arquivo PDF para download
    return send_file(buffer, as_attachment=True, download_name=f'lista_compras_{receita.titulo}.pdf', mimetype='application/pdf')

# Rota para avaliar receita (1-5 estrelas)
@app.route('/receita/<int:receita_id>/avaliar', methods=['POST'])
def avaliar_receita(receita_id):
    if not session.get('user_id'):
        flash('Faça login para avaliar receitas.')
        return redirect(url_for('login'))
    receita = Receita.query.get_or_404(receita_id)
    usuario_id = session['user_id']
    try:
        nota = int(request.form.get('nota', 0))
    except ValueError:
        nota = 0
    if nota < 1 or nota > 5:
        flash('Avaliação inválida.')
        return redirect(url_for('receita_detail', id=receita.id))

    avaliacao = Avaliacao.query.filter_by(usuario_id=usuario_id, receita_id=receita_id).first()
    if avaliacao:
        avaliacao.nota = nota
    else:
        db.session.add(Avaliacao(nota=nota, usuario_id=usuario_id, receita_id=receita_id))
    db.session.commit()
    flash('Avaliação registrada!')
    return redirect(url_for('receita_detail', id=receita.id))

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
    if not session.get('user_id'):
        flash('Faça login para comentar.')
        return redirect(url_for('login'))
    usuario_id = session['user_id'] 
    
    if conteudo:
        novo_comentario = Comentario(conteudo=conteudo, usuario_id=usuario_id, receita_id=receita_id)
        db.session.add(novo_comentario)
        db.session.commit()

        # Cria notificação para o dono da receita e envia e-mail
        if receita.usuario_id != usuario_id:
            notificacao = Notificacao(visualizado=False, usuario_id=receita.usuario_id, comentario_id=novo_comentario.id)
            db.session.add(notificacao)
            db.session.commit()
            try:
                destinatario = receita.usuario.email
                if destinatario:
                    assunto = f"Novo comentário na sua receita: {receita.titulo}"
                    corpo = (
                        f"Olá, {receita.usuario.nome}!\n\n"
                        f"Você recebeu um novo comentário na sua receita '{receita.titulo}'.\n\n"
                        f"Comentário: {conteudo}\n\n"
                        "Acesse o site para responder."
                    )
                    send_email(assunto, corpo, destinatario)
            except Exception:
                # Entrega de e-mail é melhor esforço; não falhar o fluxo
                pass
    
    return redirect(url_for('comentarios', receita_id=receita.id))


# Rota para perfil de usuário
@app.route('/perfil/<int:id>')
def perfil_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template('user_profile.html', usuario=usuario)

# Autenticação: registrar, login, logout
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        if not nome or not email or not senha:
            flash('Preencha todos os campos.')
            return redirect(url_for('registrar'))
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.')
            return redirect(url_for('registrar'))
        novo = Usuario(nome=nome, email=email, senha=generate_password_hash(senha))
        db.session.add(novo)
        db.session.commit()
        # E-mail de boas-vindas (não bloqueante)
        try:
            send_email(
                'Bem-vindo ao Receitas App',
                f'Olá, {nome}! Seu cadastro foi realizado com sucesso. Boas receitas!',
                email,
            )
        except Exception:
            pass
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = Usuario.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.senha, senha):
            flash('Credenciais inválidas.')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        flash('Login efetuado com sucesso.')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da conta.')
    return redirect(url_for('index'))


# Notificações do usuário logado
@app.route('/notificacoes')
def notificacoes():
    if not session.get('user_id'):
        flash('Faça login para ver suas notificações.')
        return redirect(url_for('login'))
    usuario_id = session['user_id']
    notificacoes = Notificacao.query.filter_by(usuario_id=usuario_id).all()
    # Marca como visualizadas após carregar
    for n in notificacoes:
        if not n.visualizado:
            n.visualizado = True
    db.session.commit()
    return render_template('notifications.html', notificacoes=notificacoes)

if __name__ == '__main__':
    app.run(debug=True)
