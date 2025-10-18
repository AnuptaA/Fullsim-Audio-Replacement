from flask import Blueprint, request, jsonify
from models import db, Participant
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

#----------------------------------------------------------------------#

participants_bp = Blueprint('participants', __name__)

#----------------------------------------------------------------------#

@participants_bp.route('/validate', methods=['POST'])
def validate_participant():
    data = request.get_json()
    participant_id = data.get('participant_id')

    if not participant_id:
        return jsonify({'error': 'participant_id required'}), 400
    
    participant = Participant.query.filter_by(participant_id=participant_id).first()

    if participant:
        return jsonify({
            'valid': True,
            'participant': {
                'id': participant.id,
                'participant_id': participant.participant_id,
                'email': participant.email,
                'created_at': participant.created_at.isoformat()
            }
        }), 200
    else:
        return jsonify({'valid': False}), 404

@participants_bp.route('/<participant_id>', methods=['GET'])
@jwt_required()
def get_participant(participant_id):
    current_user = get_jwt_identity()
    if current_user != participant_id:
        return jsonify({'error': 'Unauthorized'}), 403

    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    return jsonify({
        'id': participant.id,
        'participant_id': participant.participant_id,
        'email': participant.email,
        'created_at': participant.created_at.isoformat()
    })


#----------------------------------------------------------------------#
