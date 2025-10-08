from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from models import db, Participant
from middleware.auth import require_client_secret
import os

#----------------------------------------------------------------------#

admin_bp = Blueprint('admin', __name__)

#----------------------------------------------------------------------#

@admin_bp.route('/login', methods=['POST'])
@require_client_secret
def admin_login():
    data = request.json
    password = data.get('password')
    
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if password == admin_password:
        access_token = create_access_token(identity='admin')
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'error': 'Invalid password'}), 401

@admin_bp.route('/participants', methods=['GET'])
@require_client_secret
@jwt_required()
def list_all_participants():
    participants = Participant.query.all()
    # Use the to_dict() method from the model
    return jsonify([p.to_dict() for p in participants]), 200

@admin_bp.route('/participants', methods=['POST'])
@require_client_secret
@jwt_required()
def create_participant():
    data = request.json
    
    # Validate required fields
    if not data or 'participant_id' not in data:
        return jsonify({'error': 'participant_id is required'}), 400
    
    if not data.get('email'):
        return jsonify({'error': 'email is required'}), 400
    
    # Check if participant already exists
    existing = Participant.query.filter_by(participant_id=data['participant_id']).first()
    if existing:
        return jsonify({'error': 'Participant already exists'}), 400
    
    # Check if email already exists
    existing_email = Participant.query.filter_by(email=data['email']).first()
    if existing_email:
        return jsonify({'error': 'Email already exists'}), 400
    
    participant = Participant(
        participant_id=data['participant_id'],
        email=data['email']
    )
    
    db.session.add(participant)
    
    try:
        db.session.commit()
        return jsonify(participant.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/participants/<int:participant_db_id>', methods=['DELETE'])
@require_client_secret
@jwt_required()
def delete_participant(participant_db_id):
    participant = Participant.query.get_or_404(participant_db_id)
    
    try:
        db.session.delete(participant)
        db.session.commit()
        return jsonify({'message': 'Participant deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
#----------------------------------------------------------------------#