import asyncio
import os
from pathlib import Path
from moviepy.editor import AudioFileClip
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Source and destination directories
source_dir = Path(r"D:\Cascade Projects\beloved-podcast\output\other")
dest_dir = source_dir.parent / "converted_mp3"

# Create the destination directory if it doesn't exist
dest_dir.mkdir(exist_ok=True)

# Determine the number of workers based on CPU count
max_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave one core free for system tasks

async def convert_to_mp3(input_file, output_file):
    try:
        def conversion():
            # Ensure output file has .mp3 extension
            output_path = str(output_file).rsplit('.', 1)[0] + '.mp3'
            
            audio = AudioFileClip(str(input_file))
            audio = audio.set_fps(48000)  # Set sample rate to 44.1 kHz
            try:
                audio.write_audiofile(
                    output_path,
                    bitrate="256k",
                    nbytes=2,
                    codec='libmp3lame',
                    verbose=False,
                    logger=None
                )
            finally:
                # Ensure cleanup happens
                audio.close()

        # Run the conversion in a separate thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, conversion)
        print(f"Successfully converted: {input_file.name}")
    except Exception as e:
        print(f"Error converting {input_file.name}: {str(e)}")
        
async def main():
    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {dest_dir}")
    print(f"Using {max_workers} worker(s) for conversion")
    
    if not source_dir.exists():
        print(f"Error: The source directory does not exist.")
        return

    # Look for common audio formats instead of just MP3
    audio_extensions = ('*.wav', '*.m4a', '*.aac', '*.wma', '*.ogg', '*.flac', '*.webm')  # Add .webm here
    files = []
    for ext in audio_extensions:
        files.extend(source_dir.glob(ext))
    
    print(f"Found {len(files)} audio files in the directory.")

    # Create a semaphore to limit concurrent tasks
    semaphore = asyncio.Semaphore(max_workers)

    async def limited_convert(file, output_file):
        async with semaphore:
            await convert_to_mp3(file, output_file)

    # Create tasks for each file conversion
    tasks = []
    for file in files:
        # Ensure output filename has .mp3 extension
        output_file = dest_dir / (file.stem + '.mp3')
        task = asyncio.create_task(limited_convert(file, output_file))
        tasks.append(task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())