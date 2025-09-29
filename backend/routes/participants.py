from flask import Blueprint, request, jsonify
from models import db, Participant
from sqlalchemy.exc import IntegrityError

participants_bp = Blueprint('participants', __name__)

@participants_bp.route('/', methods=['POST'])
def create_participant():
    """Create a new participant"""
    try:
        data = request.json
        participant = Participant(
            participant_code=data['participant_code'],
            native_language=data.get('native_language')
        )
        db.session.add(participant)
        db.session.commit()
        return jsonify(participant.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Participant code already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@participants_bp.route('/<int:participant_id>', methods=['GET'])
def get_participant(participant_id):
    """Get participant by ID"""
    participant = Participant.query.get_or_404(participant_id)
    return jsonify(participant.to_dict())

@participants_bp.route('/', methods=['GET'])
def list_participants():
    """List all participants"""
    participants = Participant.query.all()
    return jsonify([p.to_dict() for p in participants])