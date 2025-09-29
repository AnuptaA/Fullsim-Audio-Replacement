from flask import Blueprint, jsonify
from models import Video, Snippet

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/', methods=['GET'])
def list_videos():
    """List all videos"""
    videos = Video.query.all()
    return jsonify([v.to_dict() for v in videos])

@videos_bp.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Get video by ID with snippets"""
    video = Video.query.get_or_404(video_id)
    return jsonify(video.to_dict(include_snippets=True))

@videos_bp.route('/<int:video_id>/snippets', methods=['GET'])
def get_snippets(video_id):
    """Get all snippets for a video"""
    snippets = Snippet.query.filter_by(video_id=video_id).order_by(Snippet.snippet_index).all()
    return jsonify([s.to_dict() for s in snippets])