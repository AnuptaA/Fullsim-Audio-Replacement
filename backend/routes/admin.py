import random
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from datetime import datetime, timedelta
from models import db, Participant
import os

#----------------------------------------------------------------------#

admin_bp = Blueprint('admin', __name__)

#----------------------------------------------------------------------#

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.json
    password = data.get('password')
    
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if password == admin_password:
        access_token = create_access_token(
            identity='admin',
            additional_claims={'role': 'admin'},
            expires_delta=timedelta(hours=8)
        )
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'error': 'Invalid password'}), 401

@admin_bp.route('/participants', methods=['GET'])
@jwt_required()
def list_all_participants():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    participants = Participant.query.all()
    return jsonify([p.to_dict() for p in participants]), 200

@admin_bp.route('/participants', methods=['POST'])
@jwt_required()
def admin_create_participant():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # check if email already exists
        existing = Participant.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': 'Email already exists'}), 400
        
        # generate unique participant ID
        while True:
            # format: C###L### (e.g., C205B201)
            participant_id = 'C' + ''.join(random.choices(string.digits, k=3)) + \
                           random.choice(string.ascii_uppercase) + \
                           ''.join(random.choices(string.digits, k=3))
            
            # check if this ID already exists
            if not Participant.query.filter_by(participant_id=participant_id).first():
                break
        
        participant = Participant(
            participant_id=participant_id,
            email=email,
            created_at=datetime.utcnow()
        )
        
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({
            'id': participant.id,
            'participant_id': participant.participant_id,
            'email': participant.email,
            'created_at': participant.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating participant: {e}")
        return jsonify({'error': str(e)}), 500
    

@admin_bp.route('/participants/<int:participant_db_id>', methods=['DELETE'])
@jwt_required()
def delete_participant(participant_db_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    participant = Participant.query.get_or_404(participant_db_id)
    
    try:
        db.session.delete(participant)
        db.session.commit()
        return jsonify({'message': 'Participant deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#----------------------------------------------------------------------#