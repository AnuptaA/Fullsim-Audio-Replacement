from flask import Blueprint, request, jsonify
from models import db, Video, Snippet
from datetime import datetime
from flask_jwt_extended import jwt_required

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
        'audio_type': v.audio_type,
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
@jwt_required()
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