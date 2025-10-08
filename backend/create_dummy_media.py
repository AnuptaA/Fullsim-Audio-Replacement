"""Create dummy video and audio files for testing"""
import os
import subprocess

def create_dummy_files():
    videos_dir = 'videos'
    os.makedirs(videos_dir, exist_ok=True)
    
    print("Creating dummy media files...")
    
    for video_id in [1, 2, 3]:
        num_snippets = 2
        
        for snippet_idx in range(num_snippets):
            video_file = f"{videos_dir}/video_{video_id}_snippet_{snippet_idx}.mp4"
            audio_file = f"{videos_dir}/audio_{video_id}_snippet_{snippet_idx}.mp3"
            
            # create 2-second silent video
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=640x480:d=2',
                '-f', 'lavfi', '-i', 'anullsrc',
                '-c:v', 'libx264', '-t', '2', '-pix_fmt', 'yuv420p',
                video_file
            ], capture_output=True)
            
            # create 2-second silent audio
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-t', '2', '-q:a', '9', '-acodec', 'libmp3lame',
                audio_file
            ], capture_output=True)
            
            print(f"Created {video_file} and {audio_file}")
    
    print(f"\n Done! Created {len(os.listdir(videos_dir))} files")

if __name__ == '__main__':
    create_dummy_files()