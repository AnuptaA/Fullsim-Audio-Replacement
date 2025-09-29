from app import create_app
from models import db, Video, Snippet, Participant

def seed_database():
    app = create_app()
    
    with app.app_context():
        # clear existing data (probalby should change this later)
        print("Clearing existing data...")
        Snippet.query.delete()
        Video.query.delete()
        Participant.query.delete()
        db.session.commit()
        
        # create sample participant
        print("Creating sample participant...")
        participant = Participant(
            participant_code="DEMO001",
            native_language="English"
        )
        db.session.add(participant)
        
        # create sample videos
        print("Creating sample videos...")
        
        video1 = Video(
            video_id="script_001",
            title="Coffee Shop Conversation",
            description="A casual conversation ordering coffee",
            total_snippets=3,
            audio_type="balanced_simultaneous"
        )
        db.session.add(video1)
        db.session.flush()  # get video1.id
        
        # add snippets for video1
        snippets1 = [
            Snippet(
                video_id=video1.id,
                snippet_index=1,
                video_filename="snippet_1.mp4",
                audio_filename="snippet_1_audio.mp3",
                duration=8.5,
                transcript_original="Hola, ¿qué tal?",
                transcript_translated="Hello, how are you?"
            ),
            Snippet(
                video_id=video1.id,
                snippet_index=2,
                video_filename="snippet_2.mp4",
                audio_filename="snippet_2_audio.mp3",
                duration=12.3,
                transcript_original="Quiero un café con leche, por favor.",
                transcript_translated="I would like a coffee with milk, please."
            ),
            Snippet(
                video_id=video1.id,
                snippet_index=3,
                video_filename="snippet_3.mp4",
                audio_filename="snippet_3_audio.mp3",
                duration=6.8,
                transcript_original="Gracias, que tenga un buen día.",
                transcript_translated="Thank you, have a good day."
            ),
        ]
        
        for snippet in snippets1:
            db.session.add(snippet)
        
        video2 = Video(
            video_id="script_002",
            title="Restaurant Order",
            description="Ordering food at a restaurant",
            total_snippets=2,
            audio_type="full_replacement"
        )
        db.session.add(video2)
        db.session.flush()
        
        snippets2 = [
            Snippet(
                video_id=video2.id,
                snippet_index=1,
                video_filename="snippet_1.mp4",
                audio_filename="snippet_1_audio.mp3",
                duration=10.2,
                transcript_original="Buenas tardes, ¿tiene una mesa para dos?",
                transcript_translated="Good afternoon, do you have a table for two?"
            ),
            Snippet(
                video_id=video2.id,
                snippet_index=2,
                video_filename="snippet_2.mp4",
                audio_filename="snippet_2_audio.mp3",
                duration=15.7,
                transcript_original="Para mí, la paella de mariscos, por favor.",
                transcript_translated="For me, the seafood paella, please."
            ),
        ]
        
        for snippet in snippets2:
            db.session.add(snippet)
        
        video3 = Video(
            video_id="script_003",
            title="Asking for Directions",
            description="Getting directions to a location",
            total_snippets=2,
            audio_type="muffled_simultaneous"
        )
        db.session.add(video3)
        db.session.flush()
        
        snippets3 = [
            Snippet(
                video_id=video3.id,
                snippet_index=1,
                video_filename="snippet_1.mp4",
                audio_filename="snippet_1_audio.mp3",
                duration=9.4,
                transcript_original="Disculpe, ¿dónde está la estación de tren?",
                transcript_translated="Excuse me, where is the train station?"
            ),
            Snippet(
                video_id=video3.id,
                snippet_index=2,
                video_filename="snippet_2.mp4",
                audio_filename="snippet_2_audio.mp3",
                duration=11.1,
                transcript_original="Muchas gracias por su ayuda.",
                transcript_translated="Thank you very much for your help."
            ),
        ]
        
        for snippet in snippets3:
            db.session.add(snippet)
        
        db.session.commit()
        print("✓ Database seeded successfully!")
        print(f"  - Created 1 participant")
        print(f"  - Created 3 videos")
        print(f"  - Created 7 snippets")

if __name__ == '__main__':
    seed_database()