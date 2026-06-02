from flask import Flask

from .config import Config
from .routes import register_error_handlers, upload_bp


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    app.register_blueprint(upload_bp)
    register_error_handlers(app)
    return app
