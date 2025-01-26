#!/usr/bin/env python3
"""
Podcast Processing Pipeline

Main script that orchestrates the entire podcast processing workflow:
1. Extract YouTube video metadata
2. Match with Spotify titles
3. Download and convert matched videos
4. Generate final podcast files

Dependencies:
- pandas: Data manipulation
- yt-dlp: YouTube video downloading
- FFmpeg: Audio processing
"""

import os
import sys
import pandas as pd
from typing import Optional

from scripts.url_extractor import get_videos
from scripts.podcast_processor import convert_video_to_audio
from scripts.url_matcher import match_podcast_urls


def ensure_metadata(metadata_path: str = 'output/video_metadata.csv') -> Optional[pd.DataFrame]:
    """
    Ensure YouTube video metadata exists, extract if needed.

    Args:
        metadata_path (str): Path to metadata CSV file

    Returns:
        Optional[pd.DataFrame]: DataFrame containing video metadata or None if extraction fails
    """
    try:
        # Extract metadata if file doesn't exist or is empty
        if not os.path.exists(metadata_path) or os.path.getsize(metadata_path) == 0:
            print("Extracting YouTube metadata...")
            return get_videos()
        
        print("Loading existing metadata...")
        return pd.read_csv(metadata_path)
    except Exception as e:
        print(f"Error with metadata: {str(e)}")
        return None


def process_video(video_url: str, date: str) -> bool:
    """
    Process a single video: download and convert to audio.

    Args:
        video_url (str): YouTube video URL
        date (str): Date for filename

    Returns:
        bool: True if processing successful, False otherwise
    """
    try:
        return convert_video_to_audio(video_url, date)
    except Exception as e:
        print(f"Error processing video {video_url}: {str(e)}")
        return False


def main() -> None:
    """
    Main pipeline execution.

    Workflow:
    1. Extract/load metadata
    2. Match URLs
    3. Process videos
    4. Generate report
    """
    # Create output directories if they don't exist
    os.makedirs('output/podcasts', exist_ok=True)

    print("1. Getting YouTube metadata...")
    metadata_df = ensure_metadata()
    if metadata_df is None:
        sys.exit(1)

    print("\n2. Loading Spotify titles...")
    try:
        spotify_df = pd.read_csv('input/spotifylist.csv')
        spotify_titles = spotify_df['title'].tolist()
    except FileNotFoundError:
        print("Error: spotifylist.csv not found in input directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading Spotify titles: {str(e)}")
        sys.exit(1)

    print("\n3. Matching titles...")
    matched_urls = match_podcast_urls(spotify_titles, metadata_df)
    
    if not matched_urls:
        print("No matches found!")
        sys.exit(1)

    print(f"\nFound {len(matched_urls)} matches")
    
    # Save matched URLs to CSV
    matched_df = pd.DataFrame(matched_urls)
    matched_df.to_csv('output/matched_urls.csv', index=False)
    print(f"Saved {len(matched_urls)} matches to output/matched_urls.csv")

    print("\n4. Processing videos...")
    success_count = 0
    total_videos = len(matched_urls)
    
    for i, match in enumerate(matched_urls, 1):
        if match['youtube_url']:
            print(f"\nProcessing video {i}/{total_videos}")
            print(f"Title: {match['youtube_title']}")
            print(f"URL: {match['youtube_url']}")
            if process_video(match['youtube_url'], match['upload_date']):
                success_count += 1
                print("✓ Success")
            else:
                print("✗ Failed")

    print(f"\nProcessing complete! Successfully processed {success_count}/{len(matched_urls)} videos")


if __name__ == "__main__":
    main()
