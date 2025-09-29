from flask import Blueprint, request, jsonify
from models import db, Interaction
from datetime import datetime

interactions_bp = Blueprint('interactions', __name__)

@interactions_bp.route('/', methods=['POST'])
def create_interaction():
    """Log a new interaction"""
    try:
        data = request.json
        interaction = Interaction(
            participant_id=data['participant_id'],
            video_id=data['video_id'],
            snippet_index=data['snippet_index'],
            keystroke_data=data.get('keystroke_data'),
            response_recording_path=data.get('response_recording_path')
        )
        db.session.add(interaction)
        db.session.commit()
        return jsonify(interaction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@interactions_bp.route('/<int:interaction_id>/complete', methods=['PUT'])
def complete_interaction(interaction_id):
    """Mark interaction as completed"""
    interaction = Interaction.query.get_or_404(interaction_id)
    interaction.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(interaction.to_dict())

@interactions_bp.route('/participant/<int:participant_id>', methods=['GET'])
def get_participant_interactions(participant_id):
    """Get all interactions for a participant"""
    interactions = Interaction.query.filter_by(participant_id=participant_id).all()
    return jsonify([i.to_dict() for i in interactions])