from flask import Blueprint, request, jsonify
from models import db, Participant, Video, Snippet, SnippetResponse
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

#----------------------------------------------------------------------#

responses_bp = Blueprint('responses', __name__)

#----------------------------------------------------------------------#

@responses_bp.route('/', methods=['POST'])
@jwt_required()
def create_response():
    current_user = get_jwt_identity()
    data = request.json

    if data.get('participant_id') != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    participant = Participant.query.filter_by(participant_id=data['participant_id']).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    snippet = Snippet.query.get(data['snippet_id'])
    if not snippet:
        return jsonify({'error': 'Snippet not found'}), 404
    
    # check if response already exists
    existing = SnippetResponse.query.filter_by(
        participant_id=participant.id,
        snippet_id=snippet.id
    ).first()
    
    if existing:
        # update existing response
        existing.audio_recording_path = data.get('audio_recording_path')
        existing.audio_duration = data.get('audio_duration', 0.0)
        existing.mcq_answers = data.get('mcq_answers', [])
        existing.submitted_at = datetime.utcnow()
    else:
        # create new response
        response = SnippetResponse(
            participant_id=participant.id,
            snippet_id=snippet.id,
            audio_recording_path=data.get('audio_recording_path'),
            audio_duration=data.get('audio_duration', 0.0),
            mcq_answers=data.get('mcq_answers', []),
            submitted_at=datetime.utcnow()
        )
        db.session.add(response)
    
    db.session.commit()
    return jsonify({'success': True}), 201

@responses_bp.route('/<int:response_id>', methods=['GET'])
@jwt_required()
def get_response(response_id):
    response = SnippetResponse.query.get(response_id)
    if not response:
        return jsonify({'error': 'Response not found'}), 404
    
    return jsonify({
        'id': response.id,
        'participant_id': response.participant_id,
        'snippet_id': response.snippet_id,
        'audio_recording_path': response.audio_recording_path,
        'audio_duration': response.audio_duration,
        'mcq_answers': response.mcq_answers,
        'submitted_at': response.submitted_at.isoformat() if response.submitted_at else None
    })

@responses_bp.route('/participant/<participant_id>/video/<int:video_id>', methods=['GET'])
@jwt_required()
def get_participant_video_responses(participant_id, video_id):
    current_user = get_jwt_identity()
    
    if participant_id != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    snippets = Snippet.query.filter_by(video_id=video.id).all()
    snippet_ids = [s.id for s in snippets]
    
    responses = SnippetResponse.query.filter(
        SnippetResponse.participant_id == participant.id,
        SnippetResponse.snippet_id.in_(snippet_ids)
    ).all()
    
    return jsonify([{
        'id': r.id,
        'snippet_id': r.snippet_id,
        'audio_recording_path': r.audio_recording_path,
        'audio_duration': r.audio_duration,
        'mcq_answers': r.mcq_answers,
        'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None
    } for r in responses])

#----------------------------------------------------------------------#