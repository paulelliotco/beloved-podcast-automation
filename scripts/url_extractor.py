#!/usr/bin/env python3
"""
YouTube Video Metadata Extraction Module

This script is responsible for extracting metadata from a specified YouTube channel
using the YouTube Data API v3. It retrieves video information and saves it to a CSV file.

Key Features:
- Fetch all videos from a specified YouTube channel
- Clean and standardize video titles
- Save metadata with consistent formatting
- Support for pagination of YouTube API results

Dependencies:
- google-api-python-client
- pandas
- python-dotenv
- Custom utils module for title cleaning

Usage:
    python url_extractor.py
    
Environment:
    Requires YOUTUBE_API_KEY in .env file

Output:
    Saves video metadata to output/video_metadata.csv
"""

import os
import html
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Custom utility imports
from scripts.utils import clean_title

# Load environment variables
load_dotenv()

# Validate and retrieve YouTube API key
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("YouTube API key not found in environment variables. "
                     "Please set YOUTUBE_API_KEY in .env file.")

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_videos(channel_name='belovedsonsofgod', output_dir='output', max_results=1000):
    """
    Extract video metadata from a specified YouTube channel.

    This function performs a comprehensive retrieval of video metadata:
    - Finds the channel ID based on the channel name
    - Retrieves video details using YouTube Data API
    - Handles API pagination to get all videos
    - Cleans and standardizes video titles
    - Saves metadata to a CSV file

    Args:
        channel_name (str, optional): Name of the YouTube channel to extract videos from.
            Defaults to 'belovedsonsofgod'.
        output_dir (str, optional): Directory to save the output CSV. 
            Defaults to 'output'.
        max_results (int, optional): Maximum number of videos to retrieve. 
            Defaults to 1000.

    Returns:
        pd.DataFrame: A DataFrame containing video metadata

    Raises:
        ValueError: If the channel is not found
        Exception: For any API or processing errors
    """
    try:
        # Step 1: Find the channel ID
        channel_response = youtube.search().list(
            part="snippet",
            q=channel_name,
            type="channel",
            maxResults=1
        ).execute()

        if not channel_response.get('items'):
            raise ValueError(f"No channel found with name: {channel_name}")

        channel_id = channel_response['items'][0]['id']['channelId']
        print(f"Found channel: {channel_id}")

        # Step 2: Retrieve all videos from the channel
        videos = []
        next_page_token = None
        total_retrieved = 0

        while total_retrieved < max_results:
            # Fetch a batch of videos
            response = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50,  # YouTube API max per request
                type="video",
                pageToken=next_page_token,
                order="date"  # Get newest videos first
            ).execute()

            # Get video IDs for detailed info
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            
            if video_ids:
                # Get detailed video information
                video_response = youtube.videos().list(
                    part="snippet,contentDetails,statistics,status",
                    id=','.join(video_ids),
                    maxResults=50
                ).execute()
                
                # Process each video in the batch
                for video in video_response.get('items', []):
                    if total_retrieved >= max_results:
                        break

                    # Extract and clean metadata
                    snippet = video['snippet']
                    date = snippet['publishedAt'][:10]  # YYYY-MM-DD format
                    
                    # Clean title using utility function
                    title, _ = clean_title(snippet['title'])

                    # Get full description
                    try:
                        # Get individual video details to ensure full description
                        full_video = youtube.videos().list(
                            part="snippet",
                            id=video['id']
                        ).execute()
                        description = full_video['items'][0]['snippet']['description']
                    except Exception as e:
                        print(f"\nError getting full description for {title}: {e}")
                        description = snippet.get('description', '')

                    if not description:
                        description = f"Episode: {title}"

                    video_entry = {
                        'title': title,
                        'video_id': video['id'],
                        'url': f"https://www.youtube.com/watch?v={video['id']}",
                        'description': description,
                        'duration': video['contentDetails'].get('duration', ''),
                        'view_count': video['statistics'].get('viewCount', '0'),
                        'upload_date': f"{int(date[5:7]):02d}-{int(date[8:10]):02d}-{date[2:4]}"  # MM-DD-YY
                    }
                    videos.append(video_entry)
                    total_retrieved += 1

                    print(f"\rRetrieved {total_retrieved} videos...", end='', flush=True)

            # Check for more pages of results
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        # Step 3: Save metadata to CSV
        if videos:
            df = pd.DataFrame(videos)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save to CSV
            output_path = os.path.join(output_dir, 'video_metadata.csv')
            df.to_csv(output_path, index=False)
            
            print(f"\nSaved {len(videos)} videos to {output_path}")
            return df
        else:
            print("No videos found for the specified channel.")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error extracting videos: {e}")
        raise


def main():
    """
    Main function to run video metadata extraction.
    
    This serves as an entry point when the script is run directly.
    It calls get_videos() with default parameters.
    """
    get_videos()


if __name__ == "__main__":
    main()
