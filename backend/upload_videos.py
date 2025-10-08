import os
import sys
from models import db, Video, Snippet
from app import create_app

#----------------------------------------------------------------------#

##
## THIS FILE IS DEPRECATED, NEEDS TO BE UPDATED BEFORE USE IN PROD   ##
##

#----------------------------------------------------------------------#

def upload_video_metadata(video_id, title, description, audio_type, snippets_data):
    """
    Upload video and snippet metadata to database
    
    snippets_data format:
    [
        {
            'video_filename': 'snippet_1.mp4',
            'audio_filename': 'snippet_1_audio.mp3',
            'duration': 8.5,
            'transcript_original': 'Spanish text',
            'transcript_translated': 'English text'
        },
        ...
    ]
    """
    flask_env = os.getenv('FLASK_ENV', 'development')
    app = create_app(flask_env)
    
    with app.app_context():
        # check existence
        existing = Video.query.filter_by(video_id=video_id).first()
        if existing:
            print(f"Video {video_id} already exists. Updating...")
            video = existing
            # delete
            Snippet.query.filter_by(video_id=video.id).delete()
        else:
            print(f"Creating new video {video_id}...")
            video = Video(video_id=video_id)
            db.session.add(video)

        # metadata update
        video.title = title
        video.description = description
        video.audio_type = audio_type
        video.total_snippets = len(snippets_data)
        
        db.session.flush()
        
        # create snippets
        for idx, snippet_data in enumerate(snippets_data):
            snippet = Snippet(
                video_id=video.id,
                snippet_index=idx + 1,
                **snippet_data
            )
            db.session.add(snippet)
        
        db.session.commit()
        print(f"Successfully uploaded {video_id} with {len(snippets_data)} snippets")

#----------------------------------------------------------------------#

if __name__ == '__main__':
    # Example usage
    snippets = [
        {
            'video_filename': 'snippet_1.mp4',
            'audio_filename': 'snippet_1_audio.mp3',
            'duration': 10.5,
            'transcript_original': '¿Hola, cómo estás?',
            'transcript_translated': 'Hello, how are you?'
        },
        {
            'video_filename': 'snippet_2.mp4',
            'audio_filename': 'snippet_2_audio.mp3',
            'duration': 12.3,
            'transcript_original': 'Muy bien, gracias. ¿Y tú?',
            'transcript_translated': 'Very well, thanks. And you?'
        }
    ]
    
    upload_video_metadata(
        video_id='test_real_video',
        title='Real Test Video',
        description='First real conversation',
        audio_type='balanced_simultaneous',
        snippets_data=snippets
    )