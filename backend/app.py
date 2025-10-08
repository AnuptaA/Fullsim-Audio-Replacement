from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import config
from models import db
from werkzeug.utils import secure_filename
from middleware.auth import require_client_secret
from routes import participants_bp, videos_bp, responses_bp
from routes.admin import admin_bp
import os
import re

#---------------------------------------------------------------------#

migrate = Migrate()
jwt = JWTManager()

#---------------------------------------------------------------------#

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    if app.config['FLASK_ENV'] == 'development':
        CORS(app, origins=app.config['CORS_ORIGINS'])
    else:
        CORS(app)
    
    app.register_blueprint(participants_bp, url_prefix='/api/participants')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(responses_bp, url_prefix='/api/responses')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok', 'environment': app.config['FLASK_ENV']})
    
    # serve video files
    @app.route('/videos/<path:filepath>')
    def serve_video(filepath):
        videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
        full_path = os.path.join(videos_dir, filepath)
        
        print(f"Video request: {filepath}")
        print(f"Videos dir: {videos_dir}")
        print(f"Full path: {full_path}")
        print(f"File exists: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'Video not found', 'path': full_path}), 404
        return send_from_directory(videos_dir, filepath)
    
    # serve audio recordings
    @app.route('/recordings/<path:filepath>')
    def serve_recording(filepath):
        recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings')
        full_path = os.path.join(recordings_dir, filepath)
        if not os.path.exists(full_path):
            return jsonify({'error': 'Recording not found'}), 404
        return send_from_directory(recordings_dir, filepath)
    
    # upload audio recording
    @app.route('/api/upload-recording', methods=['POST'])
    @require_client_secret
    def upload_recording():
        print("=== Upload Recording Request ===")
        print(f"Files: {request.files}")
        print(f"Form data: {request.form}")
        
        if 'audio' not in request.files:
            print("ERROR: No audio file in request")
            return jsonify({'error': 'No audio file'}), 400
        
        audio_file = request.files['audio']
        participant_id = request.form.get('participant_id')
        video_id = request.form.get('video_id')
        snippet_index = request.form.get('snippet_index')
        
        print(f"Participant: {participant_id}, Video: {video_id}, Snippet: {snippet_index}")
        print(f"Audio file type: {audio_file.content_type}")
        print(f"Audio filename: {audio_file.filename}")
        
        if not all([participant_id, video_id, snippet_index]):
            print("ERROR: Missing parameters")
            return jsonify({'error': 'Missing parameters'}), 400
        
        # accept pretty much any audio MIME type
        allowed_types = [
            'audio/webm',
            'audio/ogg',
            'audio/mpeg',
            'audio/mp3',
            'audio/wav',
            'audio/mp4',
            'audio/x-m4a'
        ]
        
        # check if content type starts with any allowed type (to handle codecs parameter)
        is_valid = any(audio_file.content_type.startswith(allowed) for allowed in allowed_types)
        
        if not is_valid:
            print(f"ERROR: Invalid file type: {audio_file.content_type}")
            return jsonify({'error': f'Invalid file type: {audio_file.content_type}'}), 400
        
        # create directory structure
        recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings')
        participant_dir = os.path.join(recordings_dir, participant_id, video_id)
        
        try:
            os.makedirs(participant_dir, exist_ok=True)
            print(f"Created/verified directory: {participant_dir}")
        except Exception as e:
            print(f"ERROR creating directory: {e}")
            return jsonify({'error': f'Could not create directory: {str(e)}'}), 500
        
        # save file with proper extension based on content type
        extension = 'webm'
        if 'ogg' in audio_file.content_type:
            extension = 'ogg'
        elif 'mp3' in audio_file.content_type or 'mpeg' in audio_file.content_type:
            extension = 'mp3'
        elif 'wav' in audio_file.content_type:
            extension = 'wav'
        elif 'mp4' in audio_file.content_type or 'm4a' in audio_file.content_type:
            extension = 'm4a'
        
        filename = f"snippet_{snippet_index}.{extension}"
        filepath = os.path.join(participant_dir, filename)
        
        try:
            audio_file.save(filepath)
            print(f"Saved file to: {filepath}")
            print(f"File size: {os.path.getsize(filepath)} bytes")
        except Exception as e:
            print(f"ERROR saving file: {e}")
            return jsonify({'error': f'Could not save file: {str(e)}'}), 500
        
        # return relative path for storage in DB
        relative_path = f"recordings/{participant_id}/{video_id}/{filename}"
        print(f"Returning path: {relative_path}")
        print("=== Upload Complete ===\n")
        
        return jsonify({'path': relative_path}), 200

    # serve React app and handle client-side routing
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        # log what's being requested
        print(f"Catch-all route hit: /{path}")
        
        # API routes should already be handled by blueprints
        if path.startswith('api/'):
            print(f"  -> API route not found: {path}")
            return jsonify({'error': 'API endpoint not found'}), 404
        
        # static files (videos, recordings) should be handled by specific routes above
        if path.startswith('videos/') or path.startswith('recordings/'):
            print(f"  -> File route not found: {path}")
            return jsonify({'error': 'File not found'}), 404
        
        # handle Vite build assets (CSS, JS files in /assets/)
        if path.startswith('assets/'):
            file_path = os.path.join(app.static_folder, path)
            if os.path.exists(file_path):
                print(f"  -> Serving asset: {path}")
                return send_from_directory(app.static_folder, path)
            else:
                print(f"  -> Asset not found: {path}")
                return jsonify({'error': 'Asset not found'}), 404
        
        # if the path has a file extension, try to serve it
        if path and '.' in os.path.basename(path):
            file_path = os.path.join(app.static_folder, path)
            if os.path.exists(file_path):
                print(f"  -> Serving static file: {path}")
                return send_from_directory(app.static_folder, path)
            else:
                print(f"  -> Static file not found: {path}")
                return jsonify({'error': 'File not found'}), 404
        
        # for all other routes (React Router paths), serve index.html
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            print(f"  -> Serving index.html for React Router path: {path}")
            return send_from_directory(app.static_folder, 'index.html')
        else:
            print(f"  -> index.html not found! Did you run 'make build'?")
            return jsonify({
                'error': 'Application not built',
                'message': 'Run: make build',
                'static_folder': app.static_folder
            }), 404
    
    # DEBUG: print all registered routes
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:50s} {rule.rule:50s} {','.join(rule.methods)}")
    print("=========================\n")
    
    return app

app = create_app()

if __name__ == '__main__':
    print(f"Starting server on port 3000...")
    print(f"Static folder: {app.static_folder}")
    print(f"Static folder exists: {os.path.exists(app.static_folder)}")
    if os.path.exists(app.static_folder):
        print(f"Static folder contents: {os.listdir(app.static_folder)}")
    app.run(debug=True, port=3000, host='0.0.0.0')