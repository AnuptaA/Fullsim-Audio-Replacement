from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from models import db
import os
from routes import participants_bp, videos_bp, interactions_bp

migrate = Migrate()

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # check environment and setup db
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # handle CORS for development vs prod
    if app.config['FLASK_ENV'] == 'development':
        CORS(app, origins=app.config['CORS_ORIGINS'])
    else:
        CORS(app)

    # blueprints for API routes
    app.register_blueprint(participants_bp, url_prefix='/api/participants')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(interactions_bp, url_prefix='/api/interactions')

    # health check test route
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'environment': app.config['FLASK_ENV']})
    
    # serve video files
    @app.route('/videos/<path:filepath>')
    def serve_video(filepath):
        """Serve video files from videos directory"""
        videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'videos')

        # check existence
        full_path = os.path.join(videos_dir, filepath)
        if not os.path.exists(full_path):
            return jsonify({
                'error': 'Video not found',
                'message': f'Please upload {filepath} to the videos directory'
            }), 404
        
        return send_from_directory(videos_dir, filepath)
    
    # serve static React app files
    if os.path.exists(app.static_folder):
        @app.route('/')
        def serve_react():
            return send_from_directory(app.static_folder, 'index.html')
        
        @app.route('/<path:path>')
        def serve_static(path):
            if os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                # need to add better fallback here
                return send_from_directory(app.static_folder, 'index.html')
    
    return app

# obligatory comment
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=3000)