from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app.routes import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña inválidos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validaciones
        if Usuario.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
            return redirect(url_for('auth.register'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('auth.register'))
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(username=username, email=email)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso, inicia sesión', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
