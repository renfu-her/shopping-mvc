from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.controllers.home import home_bp
    from app.controllers.cart import cart_bp
    from app.controllers.auth import auth_bp
    from app.controllers.admin import backend_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(backend_bp, url_prefix='/backend')
    
    return app
