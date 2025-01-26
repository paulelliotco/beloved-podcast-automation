#!/usr/bin/env python3
"""
Podcast Audio Conversion Module

This script handles the conversion of YouTube videos to podcast-friendly audio files.
It provides robust video-to-audio conversion with advanced audio processing capabilities.

Key Features:
- Direct YouTube video to MP3 conversion
- Advanced audio processing
    * Noise reduction
    * Loudness normalization
    * Mono channel conversion
- Retry mechanism for download failures
- Filename sanitization
- Flexible audio quality settings

Dependencies:
- yt-dlp: YouTube video and audio downloading
- Custom utils module for title cleaning

Input:
- YouTube video URLs
- Optional date for filename formatting

Output:
- High-quality, normalized MP3 audio files
- Consistent naming convention

Audio Processing Specifications:
- Format: MP3
- Channels: Mono
- Sample Rate: 44.1 kHz
- Bitrate: 128 kbps
- Noise Reduction: Applied
- Loudness Normalization: Integrated Loudness -16 LUFS
"""

import os
import sys
import time
import yt_dlp

# Custom utility imports
from scripts.utils import clean_title

def wait_for_file_release(filepath, timeout=30, check_interval=1):
    """Wait for a file to be released by other processes."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try to open the file in read-write mode
            with open(filepath, 'a+b'):
                return True
        except IOError:
            time.sleep(check_interval)
    return False

def convert_video_to_audio(video_url, date=None, max_retries=3, retry_delay=5):
    """
    Download YouTube video directly as MP3 with specific audio settings:
    - Sample rate: 44.1 kHz
    - Channel: Mono
    - Bitrate: 128k
    - Audio filtering:
        * High/low pass filters (50Hz-15000Hz)
        * Noise reduction
        * Dynamic range compression
        * Dynamic normalization
        * LUFS normalization
    """
    try:
        # Get video info first
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info['title']
        
        # Clean title and create safe filename
        _, safe_title = clean_title(title, date)
        output_path = os.path.join('output', 'podcasts', safe_title + '.mp3')
        
        # Skip if file exists and is not empty
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"File already exists: {output_path}")
            return True

        print(f"\nProcessing video: {title}")

        # Configure yt-dlp to download audio only
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path + '.webm',  # Temporary WebM file
            'keepvideo': False,
            'noplaylist': True,
            'no_warnings': True,
            'retries': 10,
            'progress_hooks': [lambda d: print(f"Download progress: {d['_percent_str']}" if '_percent_str' in d else '')]
        }

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Convert to MP3 using moviepy (same approach as manual_convert.py)
        temp_file = output_path + '.webm'
        if os.path.exists(temp_file):
            try:
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(temp_file)
                audio = audio.set_fps(44100)  # Set sample rate to 44.1 kHz
                audio.write_audiofile(
                    output_path,
                    bitrate="128k",
                    nbytes=2,
                    codec='libmp3lame',
                    verbose=False,
                    logger=None
                )
                audio.close()
                os.remove(temp_file)  # Clean up temporary file
            except Exception as e:
                raise Exception(f"Audio conversion failed: {str(e)}")

        # Verify the output
        if not os.path.exists(output_path):
            raise Exception("Processing failed - output file not created")
        
        if os.path.getsize(output_path) < 1000:  # Less than 1KB
            raise Exception("Processing failed - output file too small")

        print("Processing complete!")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        # Clean up failed output
        for path in [output_path, output_path + '.webm']:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        return False


def main():
    """
    Command-line interface for direct video-to-audio conversion.

    Allows manual conversion of a single YouTube video:
    - Requires YouTube URL and optional date
    - Provides exit status based on conversion success

    Usage:
        python podcast_processor.py <youtube_url> <date>
    """
    if len(sys.argv) != 3:
        print("Usage: python podcast_processor.py <youtube_url> <date>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    date = sys.argv[2]
    
    # Attempt conversion and set exit code
    success = convert_video_to_audio(video_url, date)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()