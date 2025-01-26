import os
from pathlib import Path
from moviepy.editor import AudioFileClip
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Source and destination directories
source_dir = Path(r"C:\Users\paule\OneDrive\Desktop\mp3")
dest_dir = source_dir.parent / "cut_mp3"

# Create the destination directory if it doesn't exist
dest_dir.mkdir(exist_ok=True)

# Determine the number of workers based on CPU count
max_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave one core free for system tasks

def cut_audio(input_file, output_file):
    try:
        audio = AudioFileClip(str(input_file))
        # Cut the first 4 seconds
        cut_audio = audio.subclip(4)
        
        # Ensure output file has .mp3 extension
        output_path = str(output_file).rsplit('.', 1)[0] + '.mp3'
        
        cut_audio.write_audiofile(
            output_path,
            bitrate="196k",
            nbytes=2,
            codec='libmp3lame',
            verbose=False,
            logger=None
        )
        
        audio.close()
        cut_audio.close()
        print(f"Successfully cut: {input_file.name}")
    except Exception as e:
        print(f"Error cutting {input_file.name}: {str(e)}")

def main():
    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {dest_dir}")
    print(f"Using {max_workers} worker(s) for cutting")
    
    if not source_dir.exists():
        print(f"Error: The source directory does not exist.")
        return

    # Look for common audio formats
    audio_extensions = ('*.wav', '*.m4a', '*.aac', '*.wma', '*.ogg', '*.flac', '*.mp3')
    files = []
    for ext in audio_extensions:
        files.extend(source_dir.glob(ext))
    
    print(f"Found {len(files)} audio files in the directory.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for file in files:
            output_file = dest_dir / (file.stem + '.mp3')
            executor.submit(cut_audio, file, output_file)

if __name__ == "__main__":
    main()