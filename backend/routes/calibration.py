from flask import Blueprint, request, jsonify
from models import db, VolumeCalibration, Participant, Video
from flask_jwt_extended import jwt_required, get_jwt_identity

calibration_bp = Blueprint('calibration', __name__)

@calibration_bp.route('/', methods=['POST'])
@jwt_required()
def submit_calibration():
    """Submit volume calibration for a video"""
    current_user = get_jwt_identity()
    
    participant = Participant.query.filter_by(participant_id=current_user).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    data = request.get_json()
    video_id = data.get('video_id')
    optimal_volume = data.get('optimal_volume')
    
    if not video_id or optimal_volume is None:
        return jsonify({'error': 'video_id and optimal_volume required'}), 400
    
    if not (0.0 <= optimal_volume <= 1.0):
        return jsonify({'error': 'optimal_volume must be between 0.0 and 1.0'}), 400
    
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    existing = VolumeCalibration.query.filter_by(
        participant_id=participant.id,
        video_id=video.id
    ).first()
    
    if existing:
        existing.optimal_volume = optimal_volume
    else:
        calibration = VolumeCalibration(
            participant_id=participant.id,
            video_id=video.id,
            optimal_volume=optimal_volume
        )
        db.session.add(calibration)
    
    db.session.commit()
    return jsonify({'message': 'Calibration saved successfully'}), 200

@calibration_bp.route('/video/<int:video_id>', methods=['GET'])
@jwt_required()
def get_calibration(video_id):
    """Get existing calibration for a video"""
    current_user = get_jwt_identity()
    
    participant = Participant.query.filter_by(participant_id=current_user).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    calibration = VolumeCalibration.query.filter_by(
        participant_id=participant.id,
        video_id=video.id
    ).first()
    
    if calibration:
        return jsonify(calibration.to_dict()), 200
    else:
        return jsonify({'optimal_volume': None}), 200