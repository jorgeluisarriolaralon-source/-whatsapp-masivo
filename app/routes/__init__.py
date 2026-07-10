from flask import Blueprint

# Crear blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')
contactos_bp = Blueprint('contactos', __name__, url_prefix='/contactos')
mensajes_bp = Blueprint('mensajes', __name__, url_prefix='/mensajes')
categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

from app.routes import auth, dashboard, contactos, mensajes, categorias
