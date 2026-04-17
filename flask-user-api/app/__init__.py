from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app.routes import api_bp
    from app.errors import register_error_handlers
    app.register_blueprint(api_bp)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app
