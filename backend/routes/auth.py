from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import Participant
from datetime import timedelta

#----------------------------------------------------------------------#

auth_bp = Blueprint('auth', __name__)

#----------------------------------------------------------------------#

@auth_bp.route('/participant-token', methods=['POST'])
def issue_participant_token():
    """
    Issue JWT token for validated participant.
    Public endpoint - called after participant validates their ID.
    Returns short-lived JWT for subsequent API calls.
    """
    data = request.get_json() or {}
    participant_id = data.get('participant_id')
    
    if not participant_id:
        return jsonify({'error': 'participant_id required'}), 400
    
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    # create JWT with participant identity and role
    token = create_access_token(
        identity=participant.participant_id,
        additional_claims={'role': 'participant'},
        expires_delta=timedelta(hours=3)
    )
    
    return jsonify({
        'token': token,
        'participant': participant.to_dict()
    }), 200

#----------------------------------------------------------------------#