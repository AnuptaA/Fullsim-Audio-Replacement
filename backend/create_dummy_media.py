import os
import subprocess

def create_dummy_files():
    videos_dir = 'videos'
    os.makedirs(videos_dir, exist_ok=True)
    
    print("Creating dummy media files...")
    
    for video_id in [1, 2, 3, 4, 5]:
        num_snippets = 4
        
        for snippet_idx in range(num_snippets):
            # for calibration snippet (last one), create special files
            is_calibration = (snippet_idx == 3)
            
            if is_calibration:
                print(f"Creating CALIBRATION snippet for video {video_id}, snippet {snippet_idx}")
                
                # for calibration: 
                # - "full" = translated video with translated audio (this is what plays as video)
                # - "muffled" and "balanced" = original audio tracks (these are overlaid)
                
                # translated video plays as main video
                video_file_full = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_full.mp4"
                subprocess.run([
                    'ffmpeg', '-y', 
                    '-f', 'lavfi', '-i', 'color=c=blue:s=640x480:d=5',
                    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=5',
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-t', '5', '-pix_fmt', 'yuv420p',
                    video_file_full
                ], capture_output=True)
                
                # original audio tracks (muffled and balanced)
                video_file_muffled = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_muffled.mp4"
                video_file_balanced = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_balanced.mp4"
                
                for video_file in [video_file_muffled, video_file_balanced]:
                    subprocess.run([
                        'ffmpeg', '-y', 
                        '-f', 'lavfi', '-i', 'anullsrc=r=44100:d=5',
                        '-f', 'lavfi', '-i', 'sine=frequency=220:duration=5',
                        '-c:v', 'libx264', '-c:a', 'aac',
                        '-t', '5', '-pix_fmt', 'yuv420p',
                        video_file
                    ], capture_output=True)
                
                print(f"    Created calibration videos (full=translated, muffled/balanced=original)")
            else:
                video_file_full = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_full.mp4"
                video_file_muffled = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_muffled.mp4"
                video_file_balanced = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_balanced.mp4"
                
                for video_file in [video_file_full, video_file_muffled, video_file_balanced]:
                    subprocess.run([
                        'ffmpeg', '-y', 
                        '-f', 'lavfi', '-i', 'color=c=black:s=640x480:d=2',
                        '-f', 'lavfi', '-i', 'anullsrc=r=44100',
                        '-c:v', 'libx264', '-c:a', 'aac',
                        '-t', '2', '-pix_fmt', 'yuv420p',
                        video_file
                    ], capture_output=True)
                
                print(f"    Created 3 video variants for video {video_id}, snippet {snippet_idx}")
    
    print(f"\nDone! Created {len(os.listdir(videos_dir))} files")

if __name__ == '__main__':
    create_dummy_files()