from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON

#----------------------------------------------------------------------#

db = SQLAlchemy()

#----------------------------------------------------------------------#

class Participant(db.Model):
    """Store participant information"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(16), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # relationships
    snippet_responses = db.relationship('SnippetResponse', backref='participant', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Participant {self.participant_id}>'

#----------------------------------------------------------------------#

class Video(db.Model):
    """Store video metadata"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    total_snippets = db.Column(db.Integer, nullable=False)
    google_form_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    snippets = db.relationship('Snippet', backref='video', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_snippets=False):
        data = {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'total_snippets': self.total_snippets,
            'google_form_url': self.google_form_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_snippets:
            # get snippets ordered by snippet_index
            ordered_snippets = Snippet.query.filter_by(video_id=self.id).order_by(Snippet.snippet_index).all()
            data['snippets'] = [s.to_dict() for s in ordered_snippets]
        return data
    
    def __repr__(self):
        return f'<Video {self.video_id}>'

#----------------------------------------------------------------------#

class Snippet(db.Model):
    """Store individual video snippet information"""
    __tablename__ = 'snippets'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    snippet_index = db.Column(db.Integer, nullable=False)
    video_filename_full = db.Column(db.String(500))
    video_filename_muffled = db.Column(db.String(500))
    video_filename_balanced = db.Column(db.String(500))
    duration = db.Column(db.Float)
    transcript_original = db.Column(db.Text)
    transcript_translated = db.Column(db.Text)
    mcq_questions = db.Column(JSON)
    is_calibration = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('video_id', 'snippet_index', name='unique_video_snippet'),
        db.Index('idx_video_snippet', 'video_id', 'snippet_index'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'snippet_index': self.snippet_index,
            'video_filename_full': self.video_filename_full,
            'video_filename_muffled': self.video_filename_muffled,
            'video_filename_balanced': self.video_filename_balanced,
            'duration': self.duration,
            'transcript_original': self.transcript_original,
            'transcript_translated': self.transcript_translated,
            'mcq_questions': self.mcq_questions or [],
            'is_calibration': self.is_calibration or False, 
        }
    
    def __repr__(self):
        return f'<Snippet {self.video_id}:{self.snippet_index}>'

#----------------------------------------------------------------------#

class SnippetResponse(db.Model):
    """Store participant responses for each snippet"""
    __tablename__ = 'snippet_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False, index=True)
    snippet_id = db.Column(db.Integer, db.ForeignKey('snippets.id'), nullable=False, index=True)
    audio_recording_path = db.Column(db.String(500)) # deprecated
    audio_recording_base64 = db.Column(db.Text)
    audio_mime_type = db.Column(db.String(50))
    audio_duration = db.Column(db.Float)
    mcq_answers = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=True, index=True)
    
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'snippet_id', name='unique_participant_snippet_response'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'snippet_id': self.snippet_id,
            'audio_recording_path': self.audio_recording_path,
            'audio_recording_base64': self.audio_recording_base64,
            'audio_mime_type': self.audio_mime_type,
            'audio_duration': self.audio_duration,
            'mcq_answers': self.mcq_answers or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
        }
    
    def __repr__(self):
        return f'<SnippetResponse participant:{self.participant_id} snippet:{self.snippet_id}>'
    
#----------------------------------------------------------------------#

class ParticipantAudioAssignment(db.Model):
    """Stores which audio type each participant hears for each snippet"""
    __tablename__ = 'participant_audio_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    snippet_id = db.Column(db.Integer, db.ForeignKey('snippets.id'), nullable=False)
    audio_type = db.Column(db.String(20), nullable=False)  # 'full', 'muffled', or 'balanced'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # unique constraint: one assignment per participant per snippet
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'snippet_id', name='unique_participant_snippet_audio'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'snippet_id': self.snippet_id,
            'audio_type': self.audio_type,
            'created_at': self.created_at.isoformat()
        }
    
#----------------------------------------------------------------------#

class VolumeCalibration(db.Model):
    """Store participant's optimal volume level for each video"""
    __tablename__ = 'volume_calibrations'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    optimal_volume = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'video_id', name='unique_participant_video_calibration'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'video_id': self.video_id,
            'optimal_volume': self.optimal_volume,
            'created_at': self.created_at.isoformat()
        }
    
#----------------------------------------------------------------------#

class VideoSession(db.Model):
    """Track time spent from opening video to completing calibration"""
    __tablename__ = 'video_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    session_start = db.Column(db.DateTime, nullable=False)  # when first snippet opened
    session_end = db.Column(db.DateTime, nullable=True)  # when calibration submitted
    total_duration_seconds = db.Column(db.Float, nullable=True)  # calculated on completion
    
    __table_args__ = (
        db.UniqueConstraint('participant_id', 'video_id', name='unique_participant_video_session'),
        db.Index('idx_participant_video_session', 'participant_id', 'video_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'video_id': self.video_id,
            'session_start': self.session_start.isoformat() if self.session_start else None,
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'total_duration_seconds': self.total_duration_seconds,
        }
    
    def __repr__(self):
        return f'<VideoSession participant:{self.participant_id} video:{self.video_id}>'

#----------------------------------------------------------------------#