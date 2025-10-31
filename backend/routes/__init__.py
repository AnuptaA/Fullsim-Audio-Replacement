from .responses import responses_bp
from .participants import participants_bp
from .videos import videos_bp
from .admin import admin_bp
from .auth import auth_bp
from .calibration import calibration_bp

def register_routes(app):
    app.register_blueprint(participants_bp, url_prefix='/api/participants')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(responses_bp, url_prefix='/api/responses')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(calibration_bp, url_prefix='/api/calibration')
