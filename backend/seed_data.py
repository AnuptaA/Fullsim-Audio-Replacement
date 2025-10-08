from app import create_app
from models import db, Video, Snippet, Participant
import os

#----------------------------------------------------------------------#

def seed_database():
    flask_env = os.getenv('FLASK_ENV', 'development')
    app = create_app(flask_env)
    
    with app.app_context():
        print("Starting database seed...")
        
        # # clear existing data (optional, comment out in production!)
        # otherwise we are doomed

        # print("Clearing existing data...")
        # Snippet.query.delete()
        # Video.query.delete()
        # Participant.query.delete()
        # db.session.commit()
        
        # xreate sample participant
        print("Creating sample participant...")
        participant = Participant(
            participant_code="DEMO001",
            native_language="English"
        )
        db.session.add(participant)
        
        # 15 dummy scripts
        videos_data = [
            {
                'video_id': 'script_001',
                'title': 'Coffee Shop Order',
                'description': 'Ordering coffee in a casual café setting',
                'audio_type': 'balanced_simultaneous',
                'snippets': 3
            },
            {
                'video_id': 'script_002',
                'title': 'Restaurant Reservation',
                'description': 'Making a dinner reservation over the phone',
                'audio_type': 'full_replacement',
                'snippets': 4
            },
            {
                'video_id': 'script_003',
                'title': 'Asking for Directions',
                'description': 'Getting directions to a local landmark',
                'audio_type': 'muffled_simultaneous',
                'snippets': 3
            },
            {
                'video_id': 'script_004',
                'title': 'Shopping for Groceries',
                'description': 'Buying produce at a market',
                'audio_type': 'balanced_simultaneous',
                'snippets': 5
            },
            {
                'video_id': 'script_005',
                'title': 'Hotel Check-in',
                'description': 'Checking into a hotel and asking about amenities',
                'audio_type': 'full_replacement',
                'snippets': 4
            },
            {
                'video_id': 'script_006',
                'title': 'Doctor Appointment',
                'description': 'Describing symptoms to a doctor',
                'audio_type': 'muffled_simultaneous',
                'snippets': 4
            },
            {
                'video_id': 'script_007',
                'title': 'Public Transportation',
                'description': 'Buying a bus ticket and asking about routes',
                'audio_type': 'balanced_simultaneous',
                'snippets': 3
            },
            {
                'video_id': 'script_008',
                'title': 'Job Interview',
                'description': 'Formal interview conversation with hesitation',
                'audio_type': 'full_replacement',
                'snippets': 5
            },
            {
                'video_id': 'script_009',
                'title': 'Meeting a Friend',
                'description': 'Casual conversation with humor and emotion',
                'audio_type': 'muffled_simultaneous',
                'snippets': 4
            },
            {
                'video_id': 'script_010',
                'title': 'Bank Transaction',
                'description': 'Opening a bank account with formal language',
                'audio_type': 'balanced_simultaneous',
                'snippets': 4
            },
            {
                'video_id': 'script_011',
                'title': 'Pharmacy Visit',
                'description': 'Asking for medication advice',
                'audio_type': 'full_replacement',
                'snippets': 3
            },
            {
                'video_id': 'script_012',
                'title': 'Sports Discussion',
                'description': 'Enthusiastic conversation about a football match',
                'audio_type': 'muffled_simultaneous',
                'snippets': 4
            },
            {
                'video_id': 'script_013',
                'title': 'Home Repair',
                'description': 'Explaining a plumbing problem to a technician',
                'audio_type': 'balanced_simultaneous',
                'snippets': 4
            },
            {
                'video_id': 'script_014',
                'title': 'Movie Discussion',
                'description': 'Persuasive conversation about film preferences',
                'audio_type': 'full_replacement',
                'snippets': 5
            },
            {
                'video_id': 'script_015',
                'title': 'Party Planning',
                'description': 'Planning a celebration with varied intonation',
                'audio_type': 'muffled_simultaneous',
                'snippets': 4
            }
        ]
        
        # sample Spanish phrases for different scenarios
        spanish_phrases = {
            'greeting': ['Hola, ¿qué tal?', 'Buenos días', '¿Cómo está usted?'],
            'request': ['Quiero...', '¿Me puede ayudar?', '¿Tiene...?'],
            'question': ['¿Dónde está...?', '¿Cuánto cuesta?', '¿A qué hora...?'],
            'thanks': ['Gracias', 'Muchas gracias', 'Muy amable'],
            'response': ['Sí, claro', 'No, lo siento', 'Por supuesto']
        }
        
        english_phrases = {
            'greeting': ['Hello, how are you?', 'Good morning', 'How are you doing?'],
            'request': ['I want...', 'Can you help me?', 'Do you have...?'],
            'question': ['Where is...?', 'How much does it cost?', 'What time...?'],
            'thanks': ['Thank you', 'Thank you very much', 'Very kind'],
            'response': ['Yes, of course', 'No, I\'m sorry', 'Of course']
        }
        
        print("Creating videos and snippets...")
        for vid_data in videos_data:
            video = Video(
                video_id=vid_data['video_id'],
                title=vid_data['title'],
                description=vid_data['description'],
                total_snippets=vid_data['snippets'],
                audio_type=vid_data['audio_type']
            )
            db.session.add(video)
            db.session.flush()
            
            # create snippets for each video
            for i in range(vid_data['snippets']):
                # rotate through phrase types
                phrase_types = list(spanish_phrases.keys())
                phrase_type = phrase_types[i % len(phrase_types)]
                
                snippet = Snippet(
                    video_id=video.id,
                    snippet_index=i + 1,
                    video_filename=f"snippet_{i+1}.mp4",
                    audio_filename=f"snippet_{i+1}_audio.mp3",
                    duration=8.0 + (i * 2.5),
                    transcript_original=spanish_phrases[phrase_type][i % len(spanish_phrases[phrase_type])],
                    transcript_translated=english_phrases[phrase_type][i % len(english_phrases[phrase_type])]
                )
                db.session.add(snippet)
        
        db.session.commit()
        print(f"Database seeded successfully!")
        print(f"  - Created 1 participant")
        print(f"  - Created {len(videos_data)} videos")
        print(f"  - Created {sum(v['snippets'] for v in videos_data)} snippets")

#----------------------------------------------------------------------#

if __name__ == '__main__':
    seed_database()