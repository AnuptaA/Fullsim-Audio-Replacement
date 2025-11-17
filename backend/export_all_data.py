"""
Comprehensive export script for all participant data
Includes: audio assignments, session length, MCQ answers, Likert responses, and volume calibration
"""

import csv
import json
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

def get_read_only_session():
    """Create a read-only database session"""
    database_url = os.getenv('ACTUAL_DATABASE_URL')
    if not database_url:
        raise ValueError("ACTUAL_DATABASE_URL not found in environment variables")
    
    # create engine with read-only autocommit=False
    engine = create_engine(
        database_url,
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True
    )
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        session.execute("SET TRANSACTION READ ONLY")
    except:
        pass
    
    return session, engine


# old version of export_comprehensive_data for reference
# def export_comprehensive_data(output_file='comprehensive_participant_data.csv'):
#     """
#     Export all participant data in a single comprehensive spreadsheet
#     One row per snippet response with all associated data
#     """
#     print("Connecting to database...")
#     session, engine = get_read_only_session()
    
#     try:
#         query = text("""
#         SELECT 
#             -- Participant info
#             p.participant_id,
#             p.created_at as participant_created_at,
            
#             -- Video info
#             v.id as video_id,
#             v.title as video_title,
            
#             -- Snippet info
#             s.id as snippet_id,
#             s.snippet_index,
#             s.is_calibration,
            
#             -- Audio assignment
#             paa.audio_type as audio_type_assigned,
            
#             -- Response data
#             sr.mcq_answers,
#             sr.audio_duration as response_audio_duration,
#             sr.likert_mental_demand,
#             sr.likert_tone_difficulty,
#             sr.likert_confidence_conversation,
#             sr.likert_nonlexical_preserved,
#             sr.submitted_at as response_submitted_at,
            
#             -- Session data
#             vs.session_start as video_session_start,
#             vs.session_end as video_session_end,
#             vs.total_duration_seconds as video_session_duration_seconds,
            
#             -- Volume calibration
#             vc.optimal_volume,
#             vc.created_at as calibration_submitted_at
            
#         FROM snippet_responses sr
#         JOIN participants p ON sr.participant_id = p.id
#         JOIN snippets s ON sr.snippet_id = s.id
#         JOIN videos v ON s.video_id = v.id
#         LEFT JOIN participant_audio_assignments paa 
#             ON paa.participant_id = p.id AND paa.snippet_id = s.id
#         LEFT JOIN video_sessions vs 
#             ON vs.participant_id = p.id AND vs.video_id = v.id
#         LEFT JOIN volume_calibrations vc 
#             ON vc.participant_id = p.id AND vc.video_id = v.id
#         WHERE sr.submitted_at IS NOT NULL
#             AND p.created_at >= '2025-11-16 00:00:00'
#         ORDER BY p.participant_id, v.id, s.snippet_index
#         """)
        
#         result = session.execute(query)
#         results = result.fetchall()
        
#         if not results:
#             print("No data found to export")
#             return
        
#         print(f"Found {len(results)} responses to export")
        
#         with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
#             fieldnames = [
#                 'participant_id',
#                 'participant_created_at',
                
#                 'video_id',
#                 'video_title',
                
#                 'snippet_id',
#                 'snippet_number',
#                 'is_calibration',
                
#                 'audio_type_assigned',
                
#                 'mcq_answers',
#                 'response_audio_duration',
                
#                 'likert_mental_demand',
#                 'likert_tone_difficulty',
#                 'likert_confidence_conversation',
#                 'likert_nonlexical_preserved',
                
#                 'response_submitted_at',
                
#                 'video_session_start',
#                 'video_session_end',
#                 'video_session_duration_seconds',
#                 'video_session_duration_minutes',
                
#                 'optimal_volume',
#                 'optimal_volume_percent',
#                 'calibration_submitted_at'
#             ]
            
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
            
#             for row in results:
#                 duration_minutes = None
#                 if row.video_session_duration_seconds:
#                     duration_minutes = round(row.video_session_duration_seconds / 60, 2)
                
#                 volume_percent = None
#                 if row.optimal_volume is not None:
#                     volume_percent = round(row.optimal_volume * 100, 1)
                
#                 writer.writerow({
#                     'participant_id': row.participant_id,
#                     'participant_created_at': row.participant_created_at.isoformat() if row.participant_created_at else '',
                    
#                     'video_id': row.video_id,
#                     'video_title': row.video_title,
                    
#                     'snippet_id': row.snippet_id,
#                     'snippet_number': row.snippet_index,
#                     'is_calibration': row.is_calibration,
                    
#                     'audio_type_assigned': row.audio_type_assigned or 'N/A',
                    
#                     'mcq_answers': str(row.mcq_answers) if row.mcq_answers else '[]',
#                     'response_audio_duration': row.response_audio_duration or '',
                    
#                     'likert_mental_demand': row.likert_mental_demand or '',
#                     'likert_tone_difficulty': row.likert_tone_difficulty or '',
#                     'likert_confidence_conversation': row.likert_confidence_conversation or '',
#                     'likert_nonlexical_preserved': row.likert_nonlexical_preserved or '',
                    
#                     'response_submitted_at': row.response_submitted_at.isoformat() if row.response_submitted_at else '',
                    
#                     'video_session_start': row.video_session_start.isoformat() if row.video_session_start else '',
#                     'video_session_end': row.video_session_end.isoformat() if row.video_session_end else '',
#                     'video_session_duration_seconds': row.video_session_duration_seconds or '',
#                     'video_session_duration_minutes': duration_minutes or '',
                    
#                     'optimal_volume': row.optimal_volume if row.optimal_volume is not None else '',
#                     'optimal_volume_percent': volume_percent if volume_percent is not None else '',
#                     'calibration_submitted_at': row.calibration_submitted_at.isoformat() if row.calibration_submitted_at else ''
#                 })
        
#         print(f"Exported {len(results)} responses to {output_file}")
        
#         print_summary_statistics(results)
        
#     finally:
#         session.close()
#         engine.dispose()
#         print("\nDatabase connection closed (no writes performed)")


def export_comprehensive_data(output_file='comprehensive_participant_data.csv'):
    """
    Export all participant data in a single comprehensive spreadsheet
    One row per snippet response with all associated data
    READ-ONLY OPERATION
    """
    print("Connecting to database...")
    session, engine = get_read_only_session()
    
    try:
        query = text("""
        SELECT 
            -- Participant info
            p.participant_id,
            p.created_at as participant_created_at,
            
            -- Video info
            v.id as video_id,
            v.title as video_title,
            
            -- Snippet info
            s.id as snippet_id,
            s.snippet_index,
            s.is_calibration,
            s.mcq_questions,
            
            -- Audio assignment
            paa.audio_type as audio_type_assigned,
            
            -- Response data
            sr.mcq_answers,
            sr.audio_duration as response_audio_duration,
            sr.likert_mental_demand,
            sr.likert_tone_difficulty,
            sr.likert_confidence_conversation,
            sr.likert_nonlexical_preserved,
            sr.submitted_at as response_submitted_at,
            
            -- Session data
            vs.session_start as video_session_start,
            vs.session_end as video_session_end,
            vs.total_duration_seconds as video_session_duration_seconds,
            
            -- Volume calibration
            vc.optimal_volume,
            vc.created_at as calibration_submitted_at
            
        FROM snippet_responses sr
        JOIN participants p ON sr.participant_id = p.id
        JOIN snippets s ON sr.snippet_id = s.id
        JOIN videos v ON s.video_id = v.id
        LEFT JOIN participant_audio_assignments paa 
            ON paa.participant_id = p.id AND paa.snippet_id = s.id
        LEFT JOIN video_sessions vs 
            ON vs.participant_id = p.id AND vs.video_id = v.id
        LEFT JOIN volume_calibrations vc 
            ON vc.participant_id = p.id AND vc.video_id = v.id
        WHERE sr.submitted_at IS NOT NULL
            AND p.created_at >= '2025-11-16 00:00:00'
        ORDER BY p.participant_id, v.id, s.snippet_index
        """)
        
        result = session.execute(query)
        results = result.fetchall()
        
        if not results:
            print("No data found to export")
            return
        
        print(f"Found {len(results)} responses to export")
        
        # check completion status for each participant
        participant_completion = {}
        for row in results:
            pid = row.participant_id
            vid = row.video_id
            
            if pid not in participant_completion:
                participant_completion[pid] = {}
            
            if vid not in participant_completion[pid]:
                participant_completion[pid][vid] = False
            
            # mark video as complete if calibration is submitted
            if row.calibration_submitted_at:
                participant_completion[pid][vid] = True
        
        # find incomplete participants
        incomplete_participants = []
        complete_participants = []
        
        for pid, videos in participant_completion.items():
            # check if all 5 videos are complete
            all_complete = all(videos.get(vid, False) for vid in [1, 2, 3, 4, 5])
            
            if all_complete:
                complete_participants.append(pid)
            else:
                incomplete_participants.append(pid)
                missing_videos = [vid for vid in [1, 2, 3, 4, 5] if not videos.get(vid, False)]
                print(f"  -  {pid}: Missing videos {missing_videos}")
        
        print(f"\n{'='*60}")
        print(f"COMPLETION STATUS")
        print(f"{'='*60}")
        print(f"Complete participants: {len(complete_participants)}")
        print(f"Incomplete participants: {len(incomplete_participants)}")
        
        if incomplete_participants:
            print(f"\nIncomplete participant IDs:")
            for pid in sorted(incomplete_participants):
                print(f"  - {pid}")
        
        # filter results to only complete participants
        filtered_results = [row for row in results if row.participant_id in complete_participants]
        
        print(f"\n{'='*60}")
        print(f"Exporting {len(filtered_results)} responses from {len(complete_participants)} complete participants...")
        
        # write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                # participant
                'participant_id',
                'participant_created_at',
                
                # video
                'video_id',
                'video_title',
                
                # snippet
                'snippet_id',
                'snippet_number',
                'is_calibration',
                
                # audio assignment
                'audio_type_assigned',
                
                # MCQ responses
                'mcq_answers',
                'mcq_correct_answers',
                'response_audio_duration',
                
                # Likert questions (1-5 scale)
                'likert_mental_demand',
                'likert_tone_difficulty',
                'likert_confidence_conversation',
                'likert_nonlexical_preserved',
                
                # response timing
                'response_submitted_at',
                
                # video session
                'video_session_start',
                'video_session_end',
                'video_session_duration_seconds',
                'video_session_duration_minutes',
                
                # volume calibration
                'optimal_volume',
                'optimal_volume_percent',
                'calibration_submitted_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in filtered_results:
                # calculate duration in minutes
                duration_minutes = None
                if row.video_session_duration_seconds:
                    duration_minutes = round(row.video_session_duration_seconds / 60, 2)
                
                # convert volume to percentage
                volume_percent = None
                if row.optimal_volume is not None:
                    volume_percent = round(row.optimal_volume * 100, 1)
                
                # extract correct answers from MCQ questions
                mcq_correct_answers = []
                if row.mcq_questions:
                    try:
                        questions = json.loads(row.mcq_questions) if isinstance(row.mcq_questions, str) else row.mcq_questions
                        mcq_correct_answers = [q.get('correct_answer', -1) for q in questions]
                    except:
                        mcq_correct_answers = []
                
                writer.writerow({
                    'participant_id': row.participant_id,
                    'participant_created_at': row.participant_created_at.isoformat() if row.participant_created_at else '',
                    
                    'video_id': row.video_id,
                    'video_title': row.video_title,
                    
                    'snippet_id': row.snippet_id,
                    'snippet_number': row.snippet_index,
                    'is_calibration': row.is_calibration,
                    
                    'audio_type_assigned': row.audio_type_assigned or 'N/A',
                    
                    'mcq_answers': str(row.mcq_answers) if row.mcq_answers else '[]',
                    'mcq_correct_answers': str(mcq_correct_answers),
                    'response_audio_duration': row.response_audio_duration or '',
                    
                    'likert_mental_demand': row.likert_mental_demand or '',
                    'likert_tone_difficulty': row.likert_tone_difficulty or '',
                    'likert_confidence_conversation': row.likert_confidence_conversation or '',
                    'likert_nonlexical_preserved': row.likert_nonlexical_preserved or '',
                    
                    'response_submitted_at': row.response_submitted_at.isoformat() if row.response_submitted_at else '',
                    
                    'video_session_start': row.video_session_start.isoformat() if row.video_session_start else '',
                    'video_session_end': row.video_session_end.isoformat() if row.video_session_end else '',
                    'video_session_duration_seconds': row.video_session_duration_seconds or '',
                    'video_session_duration_minutes': duration_minutes or '',
                    
                    'optimal_volume': row.optimal_volume if row.optimal_volume is not None else '',
                    'optimal_volume_percent': volume_percent if volume_percent is not None else '',
                    'calibration_submitted_at': row.calibration_submitted_at.isoformat() if row.calibration_submitted_at else ''
                })
        
        print(f"✓ Exported {len(filtered_results)} responses to {output_file}")
        
        # print summary statistics (only for complete participants)
        print_summary_statistics(filtered_results)
        
    finally:
        session.close()
        engine.dispose()
        print("\nDatabase connection closed (no writes performed)")


def print_summary_statistics(results):
    """Print summary statistics about the exported data"""
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    # unique participants
    unique_participants = set(row.participant_id for row in results)
    print(f"\nTotal unique participants: {len(unique_participants)}")
    
    # responses by audio type
    audio_type_counts = {}
    for row in results:
        audio_type = row.audio_type_assigned or 'Unknown'
        audio_type_counts[audio_type] = audio_type_counts.get(audio_type, 0) + 1
    
    print("\nResponses by audio type:")
    for audio_type, count in sorted(audio_type_counts.items()):
        print(f"  {audio_type}: {count}")
    
    # calibration vs non-calibration
    calibration_count = sum(1 for row in results if row.is_calibration)
    non_calibration_count = len(results) - calibration_count
    print(f"\nCalibration snippets: {calibration_count}")
    print(f"Non-calibration snippets: {non_calibration_count}")
    
    # average Likert scores by audio type
    likert_by_type = {}
    for row in results:
        if row.is_calibration:
            continue
        
        audio_type = row.audio_type_assigned or 'Unknown'
        if audio_type not in likert_by_type:
            likert_by_type[audio_type] = {
                'mental_demand': [],
                'tone_difficulty': [],
                'confidence': [],
                'nonlexical': []
            }
        
        if row.likert_mental_demand:
            likert_by_type[audio_type]['mental_demand'].append(row.likert_mental_demand)
        if row.likert_tone_difficulty:
            likert_by_type[audio_type]['tone_difficulty'].append(row.likert_tone_difficulty)
        if row.likert_confidence_conversation:
            likert_by_type[audio_type]['confidence'].append(row.likert_confidence_conversation)
        if row.likert_nonlexical_preserved:
            likert_by_type[audio_type]['nonlexical'].append(row.likert_nonlexical_preserved)
    
    print("\nAverage Likert scores by audio type (1-5 scale):")
    for audio_type in sorted(likert_by_type.keys()):
        scores = likert_by_type[audio_type]
        print(f"\n  {audio_type}:")
        if scores['mental_demand']:
            avg = sum(scores['mental_demand']) / len(scores['mental_demand'])
            print(f"    Mental Demand: {avg:.2f} (n={len(scores['mental_demand'])})")
        if scores['tone_difficulty']:
            avg = sum(scores['tone_difficulty']) / len(scores['tone_difficulty'])
            print(f"    Tone Difficulty: {avg:.2f} (n={len(scores['tone_difficulty'])})")
        if scores['confidence']:
            avg = sum(scores['confidence']) / len(scores['confidence'])
            print(f"    Confidence: {avg:.2f} (n={len(scores['confidence'])})")
        if scores['nonlexical']:
            avg = sum(scores['nonlexical']) / len(scores['nonlexical'])
            print(f"    Non-lexical Preserved: {avg:.2f} (n={len(scores['nonlexical'])})")
    
    # average session duration
    session_durations = [row.video_session_duration_seconds for row in results if row.video_session_duration_seconds]
    if session_durations:
        avg_duration = sum(session_durations) / len(session_durations)
        print(f"\nAverage video session duration: {avg_duration:.1f} seconds ({avg_duration/60:.1f} minutes)")
    
    # average optimal volume
    volumes = [row.optimal_volume for row in results if row.optimal_volume is not None]
    if volumes:
        avg_volume = sum(volumes) / len(volumes)
        print(f"\nAverage optimal volume: {avg_volume:.2f} ({avg_volume*100:.1f}%)")
        print(f"  Range: {min(volumes):.2f} - {max(volumes):.2f} ({min(volumes)*100:.1f}% - {max(volumes)*100:.1f}%)")


if __name__ == '__main__':
    print("=" * 60)
    print("COMPREHENSIVE PARTICIPANT DATA EXPORT")
    print("READ-ONLY MODE - No database modifications")
    print("=" * 60)
    print()
    
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'comprehensive_participant_data.csv'
    
    print(f"Exporting all participant data to {output_file}...")
    print()
    
    try:
        export_comprehensive_data(output_file)
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Export complete!")
    print("=" * 60)