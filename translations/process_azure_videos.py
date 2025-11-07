import os
import subprocess
import argparse
import shutil
from tqdm import tqdm

#----------------------------------------------------------------------#

def validate_video_file(video_path):
    """Check if video has audio stream"""
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', 
           '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return 'audio' in result.stdout

def get_video_duration(video_path):
    """Get video duration in seconds"""
    probe_cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    
    result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from video file as WAV"""
    result = subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error',
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        output_audio_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Audio extraction failed: {result.stderr}")

def create_video_with_audio_mix(original_video_path, translated_video_path, 
                                 output_path, original_volume, translated_volume):
    """
    Create video with mixed audio tracks
    Uses video from Azure translation, mixes audio from both
    """
    video_duration = get_video_duration(translated_video_path)
    
    cmd = [
        'ffmpeg', '-y', '-loglevel', 'error',
        '-i', translated_video_path,
        '-i', original_video_path,
        '-filter_complex',
        f'[1:a]volume={original_volume},apad=whole_dur={video_duration}[a1];'
        f'[0:a]volume={translated_volume},apad=whole_dur={video_duration}[a2];'
        f'[a1][a2]amix=inputs=2:duration=first[aout]',
        '-map', '0:v',
        '-map', '[aout]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-shortest',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Failed to create output video: {result.stderr}")

def process_video_pair(original_video, azure_video, translated_dir):
    """
    Process a pair of original and Azure-translated videos
    Creates muffled and balanced variants
    """
    base_name = os.path.splitext(os.path.basename(original_video))[0]
    
    print(f"\n  Processing: {base_name}")
    
    # validate both videos have audio
    if not validate_video_file(original_video):
        print(f"    WARNING: Original video has no audio, skipping...")
        return False
    
    if not validate_video_file(azure_video):
        print(f"    WARNING: Azure video has no audio, skipping...")
        return False
    
    # create variants
    variants = [
        ("muffled", 0.3, 1.0, "30% Spanish + 100% English"),
        ("balanced", 0.7, 1.0, "70% Spanish + 100% English")
    ]
    
    for variant_name, orig_vol, trans_vol, description in tqdm(variants, 
                                                                desc="    Creating variants", 
                                                                unit="variant", 
                                                                leave=False):
        output_path = os.path.join(translated_dir, f"{base_name}_{variant_name}.mp4")
        print(f"      Creating {variant_name} ({description})...")
        create_video_with_audio_mix(original_video, azure_video, 
                                    output_path, orig_vol, trans_vol)
    
    # copy Azure video as "full" variant
    full_output = os.path.join(translated_dir, f"{base_name}_full.mp4")
    print(f"      Copying full translation (100% English)...")
    shutil.copy2(azure_video, full_output)
    
    print(f"    > Created 3 variants for {base_name}")
    return True

def match_original_to_azure(original_dir, azure_dir):
    """
    Match original videos with their Azure-translated counterparts
    Normalizes filenames by removing underscores and converting to lowercase
    Returns list of (original_path, azure_path) tuples
    """
    
    def normalize_name(filename):
        """Remove underscores, convert to lowercase for matching"""
        base = os.path.splitext(filename)[0]
        # Remove all underscores and convert to lowercase
        normalized = base.replace('_', '').lower()
        return normalized
    
    # get all videos from original directory
    original_videos = {}
    for root, dirs, files in os.walk(original_dir):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                full_path = os.path.join(root, file)
                normalized = normalize_name(file)
                original_videos[normalized] = full_path
    
    # get all Azure videos
    azure_videos = {}
    for file in os.listdir(azure_dir):
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            full_path = os.path.join(azure_dir, file)
            normalized = normalize_name(file)
            azure_videos[normalized] = full_path
    
    # match pairs
    pairs = []
    unmatched_azure = []
    matched_originals = set()
    
    print("\n  Matching videos:")
    for azure_normalized, azure_path in azure_videos.items():
        if azure_normalized in original_videos:
            orig_path = original_videos[azure_normalized]
            if orig_path not in matched_originals:
                pairs.append((orig_path, azure_path))
                matched_originals.add(orig_path)
                print(f"    > {os.path.basename(orig_path)} <-> {os.path.basename(azure_path)}")
        else:
            unmatched_azure.append(os.path.basename(azure_path))
            print(f"      No match for Azure: {os.path.basename(azure_path)} (normalized: {azure_normalized})")
    
    # show unmatched originals
    unmatched_originals = []
    for normalized, orig_path in original_videos.items():
        if orig_path not in matched_originals:
            unmatched_originals.append(os.path.basename(orig_path))
    
    if unmatched_originals:
        print(f"\n  Unmatched original videos ({len(unmatched_originals)}):")
        for name in unmatched_originals:
            print(f"    - {name}")
    
    return pairs, unmatched_azure

def process_all_azure_videos(original_dir='original', azure_dir='azure', translated_dir='translated'):
    """
    Process all Azure-translated videos
    Creates muffled and balanced variants
    """
    os.makedirs(azure_dir, exist_ok=True)
    os.makedirs(translated_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"PROCESSING AZURE-TRANSLATED VIDEOS")
    print(f"{'='*60}")
    print(f"  Original videos: {original_dir}/")
    print(f"  Azure translations: {azure_dir}/")
    print(f"  Output: {translated_dir}/")
    
    # match original and Azure videos
    pairs, unmatched = match_original_to_azure(original_dir, azure_dir)
    
    if not pairs:
        print(f"\n  No matching video pairs found!")
        print(f"  Azure videos must have same filename as originals")
        return
    
    print(f"\n  Matched pairs: {len(pairs)}")
    print(f"  Variants per video: 3 (muffled, balanced, full)")
    print(f"  Total output videos: {len(pairs) * 3}")
    
    if unmatched:
        print(f"\n  Unmatched Azure videos ({len(unmatched)}):")
        for name in unmatched:
            print(f"    - {name}")
    
    print(f"\n  Variants to be created:")
    
    # process each pair
    successfully_processed = 0
    failed_videos = []
    
    for original_video, azure_video in tqdm(pairs, desc="Overall Progress", unit="pair"):
        try:
            if process_video_pair(original_video, azure_video, translated_dir):
                successfully_processed += 1
        except Exception as e:
            print(f"\n  ERROR processing {os.path.basename(original_video)}: {e}")
            import traceback
            traceback.print_exc()
            failed_videos.append(os.path.basename(original_video))
    
    # print summary
    print(f"\n{'='*60}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"  Successfully processed: {successfully_processed}/{len(pairs)} video pairs")
    print(f"  Total variants created: {successfully_processed * 3} videos")
    print(f"  Output directory: {translated_dir}/")
    
    if failed_videos:
        print(f"\n  Failed videos ({len(failed_videos)}):")
        for video in failed_videos:
            print(f"    - {video}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process Azure-translated videos to create audio mix variants',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('--original-dir', default='original',
                       help='Directory containing original Spanish videos (default: original)')
    parser.add_argument('--azure-dir', default='azure',
                       help='Directory containing Azure-translated videos (default: azure)')
    parser.add_argument('--translated-dir', default='translated',
                       help='Output directory for all variants (default: translated)')
    
    args = parser.parse_args()
    
    process_all_azure_videos(args.original_dir, args.azure_dir, args.translated_dir)