import os
from flask import Flask, session
from datetime import timedelta
import atexit

from app.config import config
from app import db

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize database configuration
    db.init_db(app)
    
    # Set session timeout
    app.permanent_session_lifetime = timedelta(hours=2)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.citizen import citizen_bp
    from app.routes.employee import employee_bp
    from app.routes.monitor import monitor_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(monitor_bp, url_prefix='/monitor')
    
    # Clean up database connection when the app shuts down
    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db.close_connection()

    atexit.register(db.close_connection)
    
    return app