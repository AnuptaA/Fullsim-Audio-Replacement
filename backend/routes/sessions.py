from flask import Blueprint, request, jsonify
from models import db, Participant, Video, VideoSession
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

#----------------------------------------------------------------------#

sessions_bp = Blueprint('sessions', __name__)

#----------------------------------------------------------------------#

@sessions_bp.route('/start', methods=['POST'])
@jwt_required()
def start_session():
    """Record when participant starts a video"""
    current_user = get_jwt_identity()
    data = request.json
    
    if data.get('participant_id') != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    participant = Participant.query.filter_by(participant_id=data['participant_id']).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    video = Video.query.filter_by(video_id=data['video_id']).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # check if session already exists
    existing = VideoSession.query.filter_by(
        participant_id=participant.id,
        video_id=video.id
    ).first()
    
    if existing:
        # session already started, return existing
        return jsonify(existing.to_dict()), 200
    
    # otherwise create new session
    session = VideoSession(
        participant_id=participant.id,
        video_id=video.id,
        session_start=datetime.utcnow()
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201

@sessions_bp.route('/end', methods=['POST'])
@jwt_required()
def end_session():
    """Record when participant completes calibration"""
    current_user = get_jwt_identity()
    data = request.json
    
    if data.get('participant_id') != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    participant = Participant.query.filter_by(participant_id=data['participant_id']).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    video = Video.query.filter_by(video_id=data['video_id']).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    session = VideoSession.query.filter_by(
        participant_id=participant.id,
        video_id=video.id
    ).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # update session end time and calculate duration
    session.session_end = datetime.utcnow()
    session.total_duration_seconds = (session.session_end - session.session_start).total_seconds()
    
    db.session.commit()
    
    return jsonify(session.to_dict()), 200

@sessions_bp.route('/participant/<participant_id>/video/<int:video_id>', methods=['GET'])
@jwt_required()
def get_session(participant_id, video_id):
    """Get session info for a participant and video"""
    current_user = get_jwt_identity()
    
    if participant_id != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    session = VideoSession.query.filter_by(
        participant_id=participant.id,
        video_id=video.id
    ).first()
    
    if not session:
        return jsonify({'session': None}), 200
    
    return jsonify(session.to_dict()), 200

#----------------------------------------------------------------------#