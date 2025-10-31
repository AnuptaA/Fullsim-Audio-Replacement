from flask import Blueprint, request, jsonify
from models import db, Video, Snippet, ParticipantAudioAssignment, Participant
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import random

#----------------------------------------------------------------------#

videos_bp = Blueprint('videos', __name__)

#----------------------------------------------------------------------#

@videos_bp.route('/', methods=['GET'])
@jwt_required()
def list_videos():
    videos = Video.query.all()
    return jsonify([{
        'id': v.id,
        'video_id': v.video_id,
        'title': v.title,
        'description': v.description,
        'total_snippets': v.total_snippets,
        'google_form_url': v.google_form_url
    } for v in videos])

@videos_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    video = Video.query.filter_by(video_id=video_id).first()
    
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    snippets = Snippet.query.filter_by(video_id=video.id).order_by(Snippet.snippet_index).all()
    
    return jsonify({
        **video.to_dict(),
        'snippets': [s.to_dict() for s in snippets]
    }), 200

@videos_bp.route('/<int:video_id>/snippets', methods=['GET'])
@jwt_required()
def get_snippets(video_id):
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    snippets = Snippet.query.filter_by(video_id=video.id).order_by(Snippet.snippet_index).all()
    return jsonify([{
        'id': s.id,
        'snippet_index': s.snippet_index,
        'video_filename_full': s.video_filename_full,
        'video_filename_muffled': s.video_filename_muffled,
        'video_filename_balanced': s.video_filename_balanced,
        'duration': s.duration,
        'transcript_original': s.transcript_original,
        'transcript_translated': s.transcript_translated,
        'mcq_questions': s.mcq_questions
    } for s in snippets])

@videos_bp.route('/<int:video_id>/audio-assignments', methods=['GET'])
@jwt_required()
def get_audio_assignments(video_id):
    """
    Get or create audio type assignments for a participant for a specific video.
    Only assigns audio types to NON-calibration snippets.
    Returns: { snippet_id: 'full'|'muffled'|'balanced', ... }
    """
    current_user = get_jwt_identity()
    
    # get participant
    participant = Participant.query.filter_by(participant_id=current_user).first()
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    # get video and its snippets
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    snippets = Snippet.query.filter_by(video_id=video.id).order_by(Snippet.snippet_index).all()
    
    # ffilter out calibration snippets
    regular_snippets = [s for s in snippets if not s.is_calibration]
    
    # check that regular snippets are a multiple of 3
    if len(regular_snippets) % 3 != 0:
        return jsonify({'error': 'Invalid video configuration: regular snippet count must be multiple of 3'}), 500
    
    # check if assignments already exist for regular snippets
    existing_assignments = ParticipantAudioAssignment.query.filter_by(
        participant_id=participant.id
    ).filter(
        ParticipantAudioAssignment.snippet_id.in_([s.id for s in regular_snippets])
    ).all()
    
    if len(existing_assignments) == len(regular_snippets):
        # return existing assignments (only for regular snippets)
        result = {str(a.snippet_id): a.audio_type for a in existing_assignments}
        return jsonify(result), 200
    
    # create new randomized assignments for regular snippets only
    audio_types = ['full', 'muffled', 'balanced']
    
    # shuffle audio types for this participant (deterministic based on participant ID + video ID)
    seed_value = hash(f"{participant.participant_id}_{video.video_id}")
    random.seed(seed_value)
    shuffled_types = audio_types * (len(regular_snippets) // 3)
    random.shuffle(shuffled_types)
    random.seed()  # reset seed
    
    # create assignments for regular snippets
    assignments = {}
    for snippet, audio_type in zip(regular_snippets, shuffled_types):
        assignment = ParticipantAudioAssignment(
            participant_id=participant.id,
            snippet_id=snippet.id,
            audio_type=audio_type
        )
        db.session.add(assignment)
        assignments[str(snippet.id)] = audio_type
    
    db.session.commit()
    return jsonify(assignments), 200

#----------------------------------------------------------------------#