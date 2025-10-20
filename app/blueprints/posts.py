# app/blueprints/posts.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Community, CommunityPost

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/')
def list_posts():
    """Lista todos os posts"""
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    communities = Community.query.all()
    return render_template('posts/list.html', posts=posts, communities=communities)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Cria um novo post"""
    if request.method == 'POST':
        try:
            conteudo = (request.form.get('conteudo') or '').strip()
            community_id_raw = request.form.get('community_id')

            if not conteudo:
                flash('Conteúdo é obrigatório.', 'warning')
                return redirect(url_for('posts.create_post'))

            if not community_id_raw:
                flash('Selecione uma comunidade.', 'warning')
                return redirect(url_for('posts.create_post'))

            try:
                community_id = int(community_id_raw)
            except (TypeError, ValueError):
                flash('Comunidade inválida.', 'danger')
                return redirect(url_for('posts.create_post'))

            community = Community.query.get(community_id)
            if not community:
                flash('Comunidade não encontrada.', 'danger')
                return redirect(url_for('posts.create_post'))

            # Opcional: restringir post em comunidade bloqueada/privada
            if not community.can_user_access(current_user.id):
                flash('Você não tem acesso a esta comunidade.', 'danger')
                return redirect(url_for('posts.create_post'))

            post = CommunityPost(
                content=conteudo,
                author_id=current_user.id,
                community_id=community_id
            )
            db.session.add(post)
            db.session.commit()
            flash('Post criado com sucesso!', 'success')
            return redirect(url_for('posts.list_posts'))
        except Exception:
            db.session.rollback()
            flash('Ocorreu um erro ao criar o post.', 'danger')
            return redirect(url_for('posts.create_post'))

    communities = Community.query.order_by(Community.name.asc()).all()
    return render_template('posts/create.html', communities=communities)

@posts_bp.route('/<int:post_id>')
def view_post(post_id):
    """Visualiza um post específico"""
    post = CommunityPost.query.get_or_404(post_id)
    return render_template('posts/view.html', post=post)

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edita um post"""
    post = CommunityPost.query.get_or_404(post_id)
    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        if not conteudo:
            flash('Conteúdo é obrigatório.', 'warning')
            return redirect(url_for('posts.edit_post', post_id=post_id))
        post.content = conteudo
        db.session.commit()
        flash('Post atualizado com sucesso!', 'success')
        return redirect(url_for('posts.view_post', post_id=post_id))
    
    return render_template('posts/edit.html', post=post)

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Deleta um post"""
    post = CommunityPost.query.get_or_404(post_id)
    if post.author_id != current_user.id and not current_user.is_administrador():
        flash('Você não tem permissão para excluir este post.', 'danger')
        return redirect(url_for('posts.view_post', post_id=post_id))
    db.session.delete(post)
    db.session.commit()
    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('posts.list_posts'))