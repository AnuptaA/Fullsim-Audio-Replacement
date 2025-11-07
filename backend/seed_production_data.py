from app import create_app
from models import db, Participant, Video, Snippet
from dotenv import load_dotenv
import os
import sys

def seed_production_data():
    """Seed database with real videos and snippets from R2 CDN"""
    
    app = create_app()
    load_dotenv()

    with app.app_context():
        print("Starting production data seeding...")

        BASE_URL = os.getenv('R2_BASE_URL')

        # Define videos data
        videos_data = [
            # Script 1 - Shopkeeper
            {
                'video_id': 1,
                'title': 'Buying a Product',
                'description': 'A conversation with a craftsman shopkeeper.',
                'total_snippets': 4,
                'google_form_url': 'https://forms.gle/GuYU5Cr5gbnwtxf76',
                'snippets': [
                    {
                        'snippet_index': 0,
                        'video_filename_full': f'{BASE_URL}/script_1_snippet_1_enthusiastic_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_1_snippet_1_enthusiastic_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_1_snippet_1_enthusiastic_balanced.mp4',
                        'duration': 30.0,
                        'transcript_original': 'Spanish conversation about handcrafted trinkets',
                        'transcript_translated': 'English: Discussion about mugs and handcrafted items',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What objects does the shopkeeper show to the customer?',
                                'options': ['Mugs', 'Plates', 'Bowls', 'Phones'],
                                'correct_answer': 0
                            },
                            {
                                'question': 'What does the shop specialize in?',
                                'options': ['Second-hand clothing', 'Electronics', 'Hand crafted trinkets', 'Home-cooked dishes'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of confidence?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of annoyance?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of deception?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 1,
                        'video_filename_full': f'{BASE_URL}/script_1_snippet_2_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_1_snippet_2_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_1_snippet_2_balanced.mp4',
                        'duration': 28.5,
                        'transcript_original': 'Spanish: Discussion about flawed red mug',
                        'transcript_translated': 'English: The apprentice and social media influence',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'Who made the flawed red mug the shopkeeper was talking about?',
                                'options': ['His wife', 'His apprentice', 'His son', 'He did'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'Who does the shopkeeper blame for introducing strange techniques and methods?',
                                'options': ['A rival shopkeeper', 'A book', 'Himself', 'Social Media'],
                                'correct_answer': 3
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of confidence?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of annoyance?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of deception?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 2,
                        'video_filename_full': f'{BASE_URL}/script_1_snippet_3_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_1_snippet_3_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_1_snippet_3_balanced.mp4',
                        'duration': 32.0,
                        'transcript_original': 'Spanish: Discount and techniques discussion',
                        'transcript_translated': 'English: No discount and secretive techniques',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'How much of a discount is the shopkeeper willing to give?',
                                'options': ['None', '10%', '20%', '30%'],
                                'correct_answer': 0
                            },
                            {
                                'question': 'How does the shopkeeper describe his techniques?',
                                'options': ['He wants to share them with as many people as possible', "He doesn't particularly care", "He's extremely secretive about them", 'He only shares with family and friends'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of confidence?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of annoyance?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of deception?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 3,
                        'video_filename_full': f'{BASE_URL}/script_1_snippet_1_enthusiastic_full.mp4',   # full translation
                        'video_filename_muffled': f'{BASE_URL}/script_1_snippet_1.MOV',     # original Spanish (hacked as "muffled")
                        'video_filename_balanced': f'{BASE_URL}/script_1_snippet_1.MOV',    # original Spanish (used as "original audio")
                        'duration': 30.0,
                        'transcript_original': 'Calibration snippet - Original Spanish',
                        'transcript_translated': 'Calibration snippet - English translation',
                        'is_calibration': True,
                        'mcq_questions': []
                    },
                ]
            },
            
            # Script 2 - Friends' Life Changes
            {
                'video_id': 2,
                'title': "Two Friends Gossiping",
                'description': 'Friends talk about their lives.',
                'total_snippets': 4,
                'google_form_url': 'https://forms.gle/1HAd32K7ux67sLd97',
                'snippets': [
                    {
                        'snippet_index': 0,
                        'video_filename_full': f'{BASE_URL}/script_2_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_2_snippet_1_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_2_snippet_1_balanced.mp4',
                        'duration': 30.0,
                        'transcript_original': 'Spanish: Tom becoming a poet',
                        'transcript_translated': "English: Tom's new career and wedding",
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What profession did Tom just start?',
                                'options': ['A poet', 'A taxi driver', 'An artist', 'A social media influencer'],
                                'correct_answer': 0
                            },
                            {
                                'question': 'What did Tom invite the speaker to?',
                                'options': ['An unveiling of his newest work', 'His wedding', 'A high school reunion', 'A dinner'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness/sarcasm?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of admiration and respect?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of judgment and envy?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 1,
                        'video_filename_full': f'{BASE_URL}/script_2_snippet_2_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_2_snippet_2_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_2_snippet_2_balanced.mp4',
                        'duration': 28.5,
                        'transcript_original': 'Spanish: Mark becoming a paramedic',
                        'transcript_translated': "English: Mark's career change motivation",
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What profession did Mark just start?',
                                'options': ['A firefighter', 'Stock broker', 'A paramedic', 'A waiter'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'Why did Mark quit his old job?',
                                'options': ['He got tired of doing the same thing', "He wasn't being paid enough", 'He was actually fired', "He didn't meet performance standards"],
                                'correct_answer': 0
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness/sarcasm?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of admiration and respect?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of judgment and envy?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 2,
                        'video_filename_full': f'{BASE_URL}/script_2_snippet_3_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_2_snippet_3_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_2_snippet_3_balanced.mp4',
                        'duration': 32.0,
                        'transcript_original': "Spanish: Speaker's brother moving out",
                        'transcript_translated': "English: Brother's new independent life",
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': "What did the speaker's brother do?",
                                'options': ['He moved out to be on his own path with his girlfriend', 'He just got an official job selling pictures at local markets', 'He sold his car', 'He complained about being too boring'],
                                'correct_answer': 0
                            },
                            {
                                'question': "How does the speaker's brother feel about his new life?",
                                'options': ['Happy, since he feels he figured it out', 'Uncertain about the future', 'Ambivalent', 'Bitter about having to leave his old life behind'],
                                'correct_answer': 0
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness/sarcasm?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of admiration and respect?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of judgment and envy?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 3,
                        'video_filename_full': f'{BASE_URL}/script_2_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_2_snippet_1.mov',
                        'video_filename_balanced': f'{BASE_URL}/script_2_snippet_1.mov',
                        'duration': 30.0,
                        'transcript_original': 'Calibration snippet - Original Spanish',
                        'transcript_translated': 'Calibration snippet - English translation',
                        'is_calibration': True,
                        'mcq_questions': []
                    }
                ]
            },
            
            # Script 3 - Taxi Driver
            {
                'video_id': 3,
                'title': 'Taxi Driver Conversation',
                'description': 'A taxi driver shares local knowledge and opinions.',
                'total_snippets': 4,
                'google_form_url': 'https://forms.gle/EsxDU8Gabk2X1DNT9',
                'snippets': [
                    {
                        'snippet_index': 0,
                        'video_filename_full': f'{BASE_URL}/script_3_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_3_snippet_1_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_3_snippet_1_balanced.mp4',
                        'duration': 30.0,
                        'transcript_original': 'Spanish: Taking back streets',
                        'transcript_translated': 'English: Route choice and stress reduction',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What route does the driver plan to take?',
                                'options': ['The main road through downtown', 'The highway to avoid traffic', 'The back streets', 'Whatever route is fastest'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'What does the driver mean when he says the back streets are "cheaper"?',
                                'options': ['The meter fare will cost less', 'It causes less stress', 'There are fewer tolls to pay', 'The distance is shorter'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of fondness and pride?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of exasperation and annoyance?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 1,
                        'video_filename_full': f'{BASE_URL}/script_3_snippet_2_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_3_snippet_2_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_3_snippet_2_balanced.mp4',
                        'duration': 28.5,
                        'transcript_original': 'Spanish: Neighborhood changes',
                        'transcript_translated': 'English: Hotel construction and tourism',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What changed the neighborhood according to the driver?',
                                'options': ['A new cathedral was built', 'A hotel was constructed', 'A billboard was put up', 'The mountain became popular'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'What does the driver think tourists should do instead of seeing everything from the car?',
                                'options': ['Stay longer than two hours', 'Hire a tour guide', 'Visit during the week', 'Walk around'],
                                'correct_answer': 3
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of fondness and pride?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of exasperation and annoyance?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 2,
                        'video_filename_full': f'{BASE_URL}/script_3_snippet_3_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_3_snippet_3_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_3_snippet_3_balanced.mp4',
                        'duration': 32.0,
                        'transcript_original': 'Spanish: Construction delays',
                        'transcript_translated': 'English: Long-term construction frustration',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': "Why can't the driver turn left?",
                                'options': ["It's a one-way street", "There's construction blocking it", 'Traffic is too heavy', 'His daughter told him not to'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'How long does the driver say the construction has been going on?',
                                'options': ['About five years', 'Since last month', 'Around nineteen years', 'Two weeks'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of fondness and pride?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of exasperation and annoyance?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 3,
                        'video_filename_full': f'{BASE_URL}/script_3_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_3_snippet_1.mov',
                        'video_filename_balanced': f'{BASE_URL}/script_3_snippet_1.mov',
                        'duration': 30.0,
                        'transcript_original': 'Calibration snippet - Original Spanish',
                        'transcript_translated': 'Calibration snippet - English translation',
                        'is_calibration': True,
                        'mcq_questions': []
                    }
                ]
            },
            
            # Script 4 - Town Festival
            {
                'video_id': 4,
                'title': 'A Night Out',
                'description': 'Recounting a memorable night out experience.',
                'total_snippets': 4,
                'google_form_url': 'https://forms.gle/P1TxF9hM9eHqvLWc7',
                'snippets': [
                    {
                        'snippet_index': 0,
                        'video_filename_full': f'{BASE_URL}/script_4_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_4_snippet_1_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_4_snippet_1_balanced.mp4',
                        'duration': 30.0,
                        'transcript_original': 'Spanish: Festival and mayor dancing',
                        'transcript_translated': "English: Mayor's dancing at town festival",
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What event did the speaker attend last night?',
                                'options': ["A concert at the mayor's house", 'A town festival', 'A dance competition', 'A restaurant opening'],
                                'correct_answer': 1
                            },
                            {
                                'question': "How does the speaker describe the mayor's dancing?",
                                'options': ['Professional and smooth', 'Better than expected', 'Like he was fighting bees', 'The worst part of the night'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of happiness and fondness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of confusion?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 1,
                        'video_filename_full': f'{BASE_URL}/script_4_snippet_2_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_4_snippet_2_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_4_snippet_2_balanced.mp4',
                        'duration': 28.5,
                        'transcript_original': 'Spanish: Fireworks and lantern fire',
                        'transcript_translated': 'English: Late fireworks and lantern incident',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'When did the fireworks start?',
                                'options': ['Around 9 PM', 'Exactly at midnight', 'Around midnight or 1 AM', 'Right after sunset'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'What happened to one of the giant lanterns?',
                                'options': ['It caught fire', 'It floated away', 'It fell on someone', 'It was the most beautiful one'],
                                'correct_answer': 0
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of happiness and fondness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of confusion?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 2,
                        'video_filename_full': f'{BASE_URL}/script_4_snippet_3_bitter_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_4_snippet_3_bitter_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_4_snippet_3_bitter_balanced.mp4',
                        'duration': 32.0,
                        'transcript_original': "Spanish: Next year's festival and wife situation",
                        'transcript_translated': 'English: Planning ahead and personal troubles',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What does the speaker offer to do for the listener next year?',
                                'options': ['Buy them festival tickets', 'Save them a spot at the festival', 'Introduce them to his wife', 'Show them around town'],
                                'correct_answer': 1
                            },
                            {
                                'question': "What is happening with the speaker's wife?",
                                'options': ["She's planning a surprise party", 'She wants to move back home', 'She wants some space', "She's excited about next year"],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of happiness and fondness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of confusion?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 3,
                        'video_filename_full': f'{BASE_URL}/script_4_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_4_snippet_1.mov',
                        'video_filename_balanced': f'{BASE_URL}/script_4_snippet_1.mov',
                        'duration': 30.0,
                        'transcript_original': 'Calibration snippet - Original Spanish',
                        'transcript_translated': 'Calibration snippet - English translation',
                        'is_calibration': True,
                        'mcq_questions': []
                    }
                ]
            },
            
            # Script 5 - Book Artist
            {
                'video_id': 5,
                'title': 'The Passion Project',
                'description': 'An artist discusses working on a new passion project.',
                'total_snippets': 4,
                'google_form_url': 'https://forms.gle/R3JiGsEmzycDxN2d7',
                'snippets': [
                    {
                        'snippet_index': 0,
                        'video_filename_full': f'{BASE_URL}/script_5_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_5_snippet_1_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_5_snippet_1_balanced.mp4',
                        'duration': 30.0,
                        'transcript_original': 'Spanish: Creating book art',
                        'transcript_translated': 'English: Tiny worlds inside hollowed books',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'What does the speaker create?',
                                'options': ['LED lights for libraries', 'Tiny worlds inside hollowed-out books', 'Forest paths in his backyard', 'Online tutorials about books'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'How many items has the speaker sold so far?',
                                'options': ['Five', 'Ten', 'Twenty', 'None yet'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of excitement and passion?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of hope?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 1,
                        'video_filename_full': f'{BASE_URL}/script_5_snippet_2_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_5_snippet_2_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_5_snippet_2_balanced.mp4',
                        'duration': 28.5,
                        'transcript_original': 'Spanish: Design theft by company',
                        'transcript_translated': 'English: Company mass-producing stolen designs',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': 'Where did the speaker first share his designs?',
                                'options': ['On social media', 'At an art gallery', 'In an email to the company', 'On a forum'],
                                'correct_answer': 3
                            },
                            {
                                'question': "What did the company do with the speaker's designs?",
                                'options': ['Offered to buy them for a high price', 'Asked permission to use them', 'Mass-produced and sold them', 'Rejected them as too expensive'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of excitement and passion?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of hope?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 2,
                        'video_filename_full': f'{BASE_URL}/script_5_snippet_3_resilient_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_5_snippet_3_resilient_muffled.mp4',
                        'video_filename_balanced': f'{BASE_URL}/script_5_snippet_3_resilient_balanced.mp4',
                        'duration': 32.0,
                        'transcript_original': 'Spanish: New custom commission business',
                        'transcript_translated': 'English: Personal custom book art commissions',
                        'is_calibration': False,
                        'mcq_questions': [
                            {
                                'question': "What is the speaker's new business idea?",
                                'options': ['Selling books online', "Creating custom commissions based on customers' favorite books", 'Teaching others how to make book art', 'Opening a physical store'],
                                'correct_answer': 1
                            },
                            {
                                'question': 'How does the speaker feel about this new direction?',
                                'options': ['Uncertain and worried', 'Ready to give up', 'Like it feels right and personal', 'Angry at the company'],
                                'correct_answer': 2
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of excitement and passion?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of bitterness?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            },
                            {
                                'question': 'To what extent does the speaker speak with a tone of hope?',
                                'options': ['Not at all', 'Little', 'Somewhat', 'To a large extent', 'To a great extent'],
                                'correct_answer': None
                            }
                        ]
                    },
                    {
                        'snippet_index': 3,
                        'video_filename_full': f'{BASE_URL}/script_5_snippet_1_full.mp4',
                        'video_filename_muffled': f'{BASE_URL}/script_5_snippet_1.mov',
                        'video_filename_balanced': f'{BASE_URL}/script_5_snippet_1.mov',
                        'duration': 30.0,
                        'transcript_original': 'Calibration snippet - Original Spanish',
                        'transcript_translated': 'Calibration snippet - English translation',
                        'is_calibration': True,
                        'mcq_questions': []
                    },
                ]
            }
        ]
        
        print("Creating videos and snippets...")
        for video_data in videos_data:
            snippets_data = video_data.pop('snippets')
            
            video = Video(**video_data)
            db.session.add(video)
            db.session.flush()
            
            for snippet_data in snippets_data:
                snippet = Snippet(
                    video_id=video.id,
                    **snippet_data
                )
                db.session.add(snippet)
            
            print(f"  > Created video {video.video_id}: {video.title} with {len(snippets_data)} snippets")
        
        db.session.commit()
        print(f"\n  Successfully seeded {len(videos_data)} videos!")
        print("\nDatabase statistics:")
        print(f"  - Videos: {Video.query.count()}")
        print(f"  - Snippets: {Snippet.query.count()}")
        print(f"  - Regular snippets: {Snippet.query.filter_by(is_calibration=False).count()}")

if __name__ == '__main__':
    try:
        seed_production_data()
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)