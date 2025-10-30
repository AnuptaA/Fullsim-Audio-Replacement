"""Create dummy video and audio files for testing"""
import os
import subprocess

def create_dummy_files():
    videos_dir = 'videos'
    os.makedirs(videos_dir, exist_ok=True)
    
    print("Creating dummy media files...")
    
    for video_id in [1, 2, 3, 4, 5]:
        num_snippets = 3
        
        for snippet_idx in range(num_snippets):
            # CREATE 3 VIDEO FILES (each with audio baked in)
            video_file_full = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_full.mp4"
            video_file_muffled = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_muffled.mp4"
            video_file_balanced = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}_balanced.mp4"
            
            # create 3 video files with 2-second silent video + audio
            for video_file in [video_file_full, video_file_muffled, video_file_balanced]:
                subprocess.run([
                    'ffmpeg', '-y', 
                    '-f', 'lavfi', '-i', 'color=c=black:s=640x480:d=2',
                    '-f', 'lavfi', '-i', 'anullsrc=r=44100',
                    '-c:v', 'libx264', '-c:a', 'aac',
                    '-t', '2', '-pix_fmt', 'yuv420p',
                    video_file
                ], capture_output=True)
            
            print(f"Created 3 video variants for video {video_id}, snippet {snippet_idx}")
    
    print(f"\n Done! Created {len(os.listdir(videos_dir))} files")

if __name__ == '__main__':
    create_dummy_files()