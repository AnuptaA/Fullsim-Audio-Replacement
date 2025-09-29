from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON

db = SQLAlchemy()

class Participant(db.Model):
    """Store participant information"""
    __tablename__ = 'participants'
    
    # table stuff
    id = db.Column(db.Integer, primary_key=True)
    participant_code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    native_language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # relationships
    interactions = db.relationship('Interaction', backref='participant', lazy='dynamic', cascade='all, delete-orphan')
    comprehension_responses = db.relationship('ComprehensionResponse', backref='participant', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_code': self.participant_code,
            'native_language': self.native_language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Participant {self.participant_code}>'


class Video(db.Model):
    """Store video metadata"""
    __tablename__ = 'videos'
    
    # table stuff
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    total_snippets = db.Column(db.Integer, nullable=False, default=0)
    audio_type = db.Column(db.String(50), nullable=False)  # full_replacement, balanced_simultaneous, muffled_simultaneous
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # relationships
    snippets = db.relationship('Snippet', backref='video', lazy='dynamic', cascade='all, delete-orphan', order_by='Snippet.snippet_index')
    interactions = db.relationship('Interaction', backref='video', lazy='dynamic')
    
    def to_dict(self, include_snippets=False):
        data = {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'total_snippets': self.total_snippets,
            'audio_type': self.audio_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_snippets:
            data['snippets'] = [s.to_dict() for s in self.snippets.order_by(Snippet.snippet_index).all()]
        return data
    
    def __repr__(self):
        return f'<Video {self.video_id}>'


class Snippet(db.Model):
    """Store individual video snippet information"""
    __tablename__ = 'snippets'
    
    # table stuff
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False, index=True)
    snippet_index = db.Column(db.Integer, nullable=False)
    video_filename = db.Column(db.String(200), nullable=False)
    audio_filename = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # duration in seconds
    transcript_original = db.Column(db.Text)  # spanish transcript
    transcript_translated = db.Column(db.Text)  # english translation
    
    # need to ensure unique snippet index per video
    __table_args__ = (
        db.UniqueConstraint('video_id', 'snippet_index', name='unique_video_snippet'),
        db.Index('idx_video_snippet', 'video_id', 'snippet_index'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'snippet_index': self.snippet_index,
            'video_filename': self.video_filename,
            'audio_filename': self.audio_filename,
            'duration': self.duration,
            'transcript_original': self.transcript_original,
            'transcript_translated': self.transcript_translated
        }
    
    def __repr__(self):
        return f'<Snippet {self.video_id}-{self.snippet_index}>'


class Interaction(db.Model):
    """Store user interactions during video playback"""
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False, index=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False, index=True)
    snippet_index = db.Column(db.Integer, nullable=False)
    
    # keystroke data: [{key: 'A', timestamp: 1234567890, video_time: 5.2}, ...]
    keystroke_data = db.Column(JSON)
    
    # path to recorded audio response
    response_recording_path = db.Column(db.String(500))
    
    # timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'video_id': self.video_id,
            'snippet_index': self.snippet_index,
            'keystroke_data': self.keystroke_data,
            'response_recording_path': self.response_recording_path,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Interaction P{self.participant_id}-V{self.video_id}-S{self.snippet_index}>'


class ComprehensionResponse(db.Model):
    """Unsure if we need this but if we do, stores end-of-video comprehension task responses"""
    __tablename__ = 'comprehension_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False, index=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False, index=True)
    
    # custom quiz/Google Form data
    response_data = db.Column(JSON, nullable=False)
    
    # score/metrics if applicable
    score = db.Column(db.Float)
    
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'video_id': self.video_id,
            'response_data': self.response_data,
            'score': self.score,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<ComprehensionResponse P{self.participant_id}-V{self.video_id}>'