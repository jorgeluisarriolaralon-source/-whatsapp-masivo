from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/whatsapp_masivo')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Register blueprints
    from app.routes import auth_bp, contactos_bp, mensajes_bp, categorias_bp, dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(contactos_bp)
    app.register_blueprint(mensajes_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(dashboard_bp)
    
    # Context processor
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return {'current_user': current_user}
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    with app.app_context():
        db.create_all()
    
    return app
