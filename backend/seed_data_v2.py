"""Seed database with sample data for testing"""
from app import create_app
from models import db, Participant, Video, Snippet, SnippetResponse
from datetime import datetime
import random
import string

def generate_participant_id():
    """Generate a random participant ID like C205B201"""
    return f"C{''.join(random.choices(string.digits, k=3))}B{''.join(random.choices(string.digits, k=3))}"

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("Starting database seed...")
        
        # clear existing data
        print("Clearing existing data...")
        SnippetResponse.query.delete()
        Snippet.query.delete()
        Video.query.delete()
        Participant.query.delete()
        db.session.commit()
        
        # create sample participants
        print("Creating sample participants...")
        participants = []
        participant_ids = []
        for i in range(3):
            pid = generate_participant_id()
            participant_ids.append(pid)
            participant = Participant(
                participant_id=pid,
                email=f"participant{i+1}@test.com",
                created_at=datetime.utcnow()
            )
            participants.append(participant)
            db.session.add(participant)
        
        db.session.commit()
        print(f"Created {len(participants)} participants")
        for p in participants:
            print(f"  - ID: {p.id}, participant_id: {p.participant_id}")
        
        # create sample videos
        print("Creating sample videos...")
        videos_data = [
            {
                'video_id': 1,
                'title': 'Spanish Conversation - Restaurant',
                'description': 'Basic restaurant conversation in Spanish',
                'total_snippets': 4,
                'google_form_url': 'https://forms.google.com/example1'
            },
            {
                'video_id': 2,
                'title': 'Spanish Conversation - Shopping',
                'description': 'Shopping conversation in Spanish',
                'total_snippets': 4,
                'google_form_url': 'https://forms.google.com/example2'
            },
            {
                'video_id': 3,
                'title': 'Spanish Conversation - Hotel',
                'description': 'Hotel check-in conversation in Spanish',
                'total_snippets': 4,
                'google_form_url': 'https://forms.google.com/example3'
            },
            {
                'video_id': 4,
                'title': 'Spanish Conversation - Train Station',
                'description': 'Asking for directions at a train station in Spanish',
                'total_snippets': 4,
                'google_form_url': 'https://forms.google.com/example4'
            },
            {
                'video_id': 5,
                'title': 'Spanish Conversation - Market',
                'description': 'Shopping at a local market in Spanish',
                'total_snippets': 4,
                'google_form_url': 'https://forms.google.com/example5'
            }
        ]
        
        videos = []
        for video_data in videos_data:
            video = Video(**video_data)
            videos.append(video)
            db.session.add(video)
        
        db.session.commit()
        print(f"Created {len(videos)} videos")
        for v in videos:
            print(f"  - ID: {v.id}, video_id: {v.video_id}, title: {v.title}")
        
        # create snippets for each video
        print("Creating snippets...")
        snippet_count = 0
        
        for video in videos:
            for i in range(video.total_snippets):
                is_last_snippet = (i == video.total_snippets - 1)
                
                snippet = Snippet(
                    video_id=video.id,
                    snippet_index=i,
                    video_filename_full=f"video_{video.video_id}_snippet_{i}_full.mp4",
                    video_filename_muffled=f"video_{video.video_id}_snippet_{i}_muffled.mp4",
                    video_filename_balanced=f"video_{video.video_id}_snippet_{i}_balanced.mp4",
                    duration=5.0 + (i * 0.5),
                    transcript_original=f"Original: This is snippet {i} from {video.title}.",
                    transcript_translated=f"Translation: This is snippet {i} from {video.title}.",
                    is_calibration=is_last_snippet,
                    mcq_questions=[
                        {
                            'question': f'Sample question {j+1} for snippet {i}?',
                            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                            'correct_answer': j % 4
                        }
                        for j in range(3)
                    ] if not is_last_snippet else []
                )
                db.session.add(snippet)
                snippet_count += 1
        
        db.session.commit()
        print(f"Created {snippet_count} snippets")
        
        # refresh to get snippet IDs
        db.session.expire_all()
        
        # create some sample responses
        print("Creating sample responses...")
        response_count = 0
        
        # get all snippets from first video
        first_video_snippets = Snippet.query.filter_by(video_id=videos[0].id).order_by(Snippet.snippet_index).all()
        
        print(f"Found {len(first_video_snippets)} snippets for video {videos[0].video_id}")
        
        # first participant completes all snippets of first video
        for snippet in first_video_snippets:
            response = SnippetResponse(
                participant_id=participants[0].id,  # FK to participant.id
                snippet_id=snippet.id,  # FK to snippet.id
                audio_recording_path=f"recordings/{participants[0].participant_id}/{videos[0].video_id}/snippet_{snippet.snippet_index}.webm",
                audio_duration=5.2,
                mcq_answers=[0, 1],  # answers to both MCQ questions
                submitted_at=datetime.utcnow()
            )
            db.session.add(response)
            response_count += 1
            print(f"  - Response for participant {participants[0].participant_id}, snippet {snippet.snippet_index}")
        
        # second participant completes only first snippet of first video
        if first_video_snippets:
            first_snippet = first_video_snippets[0]
            response = SnippetResponse(
                participant_id=participants[1].id,
                snippet_id=first_snippet.id,
                audio_recording_path=f"recordings/{participants[1].participant_id}/{videos[0].video_id}/snippet_{first_snippet.snippet_index}.webm",
                audio_duration=5.0,
                mcq_answers=[1, 0],
                submitted_at=datetime.utcnow()
            )
            db.session.add(response)
            response_count += 1
            print(f"  - Response for participant {participants[1].participant_id}, snippet {first_snippet.snippet_index}")
        
        # third participant has no responses yet (brand new)
        
        db.session.commit()
        print("DATABASE SEEDED SUCCESSFULLY!")
        
        print(f"\nParticipants created:")
        for p in participants:
            responses = SnippetResponse.query.filter_by(participant_id=p.id).count()
            print(f"  - {p.participant_id} ({p.email}) - {responses} responses")
        
        print(f"\nVideos created:")
        for v in videos:
            snippets = Snippet.query.filter_by(video_id=v.id).count()
            print(f"  - Video {v.video_id}: {v.title} ({snippets} snippets)")
        

if __name__ == '__main__':
    seed_database()