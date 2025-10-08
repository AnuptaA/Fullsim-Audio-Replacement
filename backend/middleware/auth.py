from functools import wraps
from flask import request, jsonify
import os

#----------------------------------------------------------------------#

def require_client_secret(f):
    """Decorator to require client secret for API access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_secret = request.headers.get('X-API-Secret')
        expected_secret = os.getenv('API_CLIENT_SECRET')
        
        if not expected_secret:
            return jsonify({'error': 'Server configuration error'}), 500
        
        if not client_secret:
            return jsonify({'error': 'Missing API credentials'}), 401
        
        if client_secret != expected_secret:
            return jsonify({'error': 'Invalid API credentials'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

#----------------------------------------------------------------------#