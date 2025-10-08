from flask import Blueprint, request, jsonify
from models import db, Participant, Video, Snippet, SnippetResponse
from datetime import datetime
from middleware.auth import require_client_secret

#----------------------------------------------------------------------#

participants_bp = Blueprint('participants', __name__)
videos_bp = Blueprint('videos', __name__)
responses_bp = Blueprint('responses', __name__)

#----------------------------------------------------------------------#

# participant routes
@participants_bp.route('/', methods=['GET'])
@require_client_secret
def list_participants():
    participants = Participant.query.all()
    return jsonify([{
        'id': p.id,
        'participant_id': p.participant_id,
        'email': p.email,
        'created_at': p.created_at.isoformat()
    } for p in participants])

@participants_bp.route('/<participant_id>', methods=['GET'])
@require_client_secret
def get_participant(participant_id):
    participant = Participant.query.filter_by(participant_id=participant_id).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    return jsonify({
        'id': participant.id,
        'participant_id': participant.participant_id,
        'email': participant.email,
        'created_at': participant.created_at.isoformat()
    })

@participants_bp.route('/', methods=['POST'])
@require_client_secret
def create_participant():
    data = request.json
    participant = Participant(
        participant_id=data['participant_id'],
        email=data.get('email', ''),
        created_at=datetime.utcnow()
    )
    db.session.add(participant)
    db.session.commit()
    return jsonify({'id': participant.id}), 201

#----------------------------------------------------------------------#

# video routes
@videos_bp.route('/', methods=['GET'])
@require_client_secret
def list_videos():
    videos = Video.query.all()
    return jsonify([{
        'id': v.id,
        'video_id': v.video_id,
        'title': v.title,
        'description': v.description,
        'total_snippets': v.total_snippets,
        'audio_type': v.audio_type,
        'google_form_url': v.google_form_url
    } for v in videos])

@videos_bp.route('/<int:video_id>', methods=['GET'])
@require_client_secret
def get_video(video_id):
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    snippets = Snippet.query.filter_by(video_id=video.id).order_by(Snippet.snippet_index).all()
    
    return jsonify({
        'id': video.id,
        'video_id': video.video_id,
        'title': video.title,
        'description': video.description,
        'total_snippets': video.total_snippets,
        'audio_type': video.audio_type,
        'google_form_url': video.google_form_url,
        'snippets': [{
            'id': s.id,
            'snippet_index': s.snippet_index,
            'video_filename': s.video_filename,
            'audio_filename': s.audio_filename,
            'duration': s.duration,
            'transcript_original': s.transcript_original,
            'transcript_translated': s.transcript_translated,
            'mcq_questions': s.mcq_questions
        } for s in snippets]
    })

@videos_bp.route('/<int:video_id>/snippets', methods=['GET'])
@require_client_secret
def get_snippets(video_id):
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    snippets = Snippet.query.filter_by(video_id=video.id).order_by(Snippet.snippet_index).all()
    return jsonify([{
        'id': s.id,
        'snippet_index': s.snippet_index,
        'video_filename': s.video_filename,
        'audio_filename': s.audio_filename,
        'duration': s.duration,
        'transcript_original': s.transcript_original,
        'transcript_translated': s.transcript_translated,
        'mcq_questions': s.mcq_questions
    } for s in snippets])

#----------------------------------------------------------------------#

# response routes
@responses_bp.route('/', methods=['POST'])
@require_client_secret
def create_response():
    data = request.json
    
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
@require_client_secret
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
@require_client_secret
def get_participant_video_responses(participant_id, video_id):
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