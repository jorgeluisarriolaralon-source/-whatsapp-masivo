from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Categoria
from app.routes import categorias_bp

@categorias_bp.route('/')
@login_required
def listar():
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    return render_template('categorias/listar.html', categorias=categorias)

@categorias_bp.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre es requerido', 'error')
            return redirect(url_for('categorias.agregar'))
        
        nueva_categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion,
            usuario_id=current_user.id
        )
        db.session.add(nueva_categoria)
        db.session.commit()
        
        flash('Categoría creada exitosamente', 'success')
        return redirect(url_for('categorias.listar'))
    
    return render_template('categorias/agregar.html')

@categorias_bp.route('/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    
    if categoria.usuario_id != current_user.id:
        flash('No tienes permiso', 'error')
        return redirect(url_for('categorias.listar'))
    
    if request.method == 'POST':
        categoria.nombre = request.form.get('nombre')
        categoria.descripcion = request.form.get('descripcion')
        db.session.commit()
        
        flash('Categoría actualizada', 'success')
        return redirect(url_for('categorias.listar'))
    
    return render_template('categorias/editar.html', categoria=categoria)

@categorias_bp.route('/<int:categoria_id>/eliminar', methods=['POST'])
@login_required
def eliminar(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    
    if categoria.usuario_id != current_user.id:
        return jsonify({'exito': False}), 403
    
    db.session.delete(categoria)
    db.session.commit()
    
    flash('Categoría eliminada', 'success')
    return redirect(url_for('categorias.listar'))
