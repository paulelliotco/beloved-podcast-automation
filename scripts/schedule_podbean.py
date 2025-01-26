#!/usr/bin/env python3
"""
Podbean Scheduler Script

This script takes a WhatsApp message containing podcast scheduling information
and prepares the uploads to Podbean with proper scheduling.

Example WhatsApp message format:
The Foundation part 1 & 2 December 4th, 2024
The Foundation part 3 & 4 December 11th, 2024
"""

import os
import re
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz
from groq import Groq
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Constants
PACIFIC_TZ = pytz.timezone('America/Los_Angeles')
SCHEDULE_TIME = "00:01"  # 12:01 AM Pacific Time
PODBEAN_API_BASE = "https://api.podbean.com/v1"

class PodBeanAPI:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        
    def get_access_token(self) -> str:
        """Get access token using client credentials grant type"""
        if self.access_token:
            return self.access_token
            
        auth_url = f"{PODBEAN_API_BASE}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "BelovedPodcastScheduler/1.0"
        }
        
        # Using client credentials grant type as specified in docs
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(
                auth_url,
                headers=headers,
                data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret)
            )
            
            print(f"Auth request URL: {auth_url}")
            print(f"Auth request headers: {headers}")
            print(f"Auth response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Auth error response: {response.text}")
                raise Exception(f"Failed to get access token: {response.text}")
                
            token_data = response.json()
            print(f"Auth success - token type: {token_data.get('token_type')}")
            
            self.access_token = token_data["access_token"]
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Network error during authentication: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error during authentication: {str(e)}")
            raise
        
    def upload_audio(self, file_path: str) -> str:
        """Upload audio file and get media key"""
        # First, get upload authorization
        auth_url = f"{PODBEAN_API_BASE}/files/uploadAuthorize"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "User-Agent": "BelovedPodcastScheduler/1.0"
        }
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Request upload URL
        params = {
            "filename": os.path.basename(file_path),
            "filesize": file_size,
            "content_type": "audio/mpeg"
        }
        
        auth_response = requests.get(auth_url, headers=headers, params=params)
        print(f"Upload auth request URL: {auth_url}")
        print(f"Upload auth headers: {headers}")
        print(f"Upload auth params: {params}")
        
        if auth_response.status_code != 200:
            print(f"Upload auth response: {auth_response.text}")
            raise Exception(f"Failed to get upload authorization: {auth_response.text}")
            
        upload_data = auth_response.json()
        print(f"Upload auth success - presigned URL received")
        
        # Now upload the file using the presigned URL
        with open(file_path, 'rb') as file:
            upload_response = requests.put(
                upload_data['presigned_url'],
                data=file
            )
            
        if upload_response.status_code != 200:
            print(f"Upload response: {upload_response.text}")
            raise Exception(f"Failed to upload file: {upload_response.text}")
            
        return upload_data['file_key']
        
    def schedule_episode(self, title: str, description: str, media_key: str, schedule_time: datetime) -> Dict:
        """Schedule an episode for future publishing"""
        episode_url = f"{PODBEAN_API_BASE}/episodes"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        data = {
            "title": title,
            "content": description,
            "status": "future",  # Changed from 'publish' to 'future' for scheduling
            "type": "public",
            "media_key": media_key,
            "publish_timestamp": int(schedule_time.timestamp())
        }
        
        response = requests.post(episode_url, headers=headers, data=data)
        if response.status_code != 200:
            print(f"Schedule response: {response.text}")
            raise Exception(f"Failed to schedule episode: {response.text}")
            
        return response.json()["episode"]

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")
groq_client = Groq(api_key=GROQ_API_KEY)

# Add custom datetime JSON encoder
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def parse_with_groq(message: str) -> List[Dict[str, Any]]:
    """Use Groq to parse WhatsApp message into structured data."""
    prompt = """Parse the following WhatsApp message into structured data. Each line starts with an asterisk (*) and contains a podcast title and date.
    If a title contains multiple parts (e.g., "part 1 & 2"), create separate entries for each part.
    Return a list of objects with 'title' and 'schedule_date' fields. Convert MM/DD dates to YYYY-MM-DD format assuming year 2024.
    
    Example message:
    *Title One part 1 & 2 12/23
    *Title Two 12/24
    
    Example output:
    {
        "entries": [
            {
                "title": "Title One part 1",
                "schedule_date": "2024-12-23"
            },
            {
                "title": "Title One part 2",
                "schedule_date": "2024-12-23"
            },
            {
                "title": "Title Two",
                "schedule_date": "2024-12-24"
            }
        ]
    }"""
    
    try:
        # Create chat completion with JSON mode
        completion = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system",
                    "content": """You are a WhatsApp message parser that outputs JSON. 
                    If a title contains multiple parts (e.g., "part 1 & 2"), create separate entries for each part.
                    The JSON schema must be:
                    {
                        "entries": [
                            {
                                "title": "string",
                                "schedule_date": "string (YYYY-MM-DD)"
                            }
                        ]
                    }"""
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nMessage to parse:\n{message}"
                }
            ],
            temperature=0.0,  # Use 0 temperature for deterministic output
            response_format={"type": "json_object"}  # Enable JSON mode
        )
        
        # Extract the JSON response
        response_text = completion.choices[0].message.content
        print(f"\nRaw Groq response:\n{response_text}\n")  # Debug output
        
        # Parse the JSON response
        response_json = json.loads(response_text)
        entries = response_json.get("entries", [])
        
        # Print parsed entries
        print("\nGroq parsing result:")
        print(json.dumps(entries, indent=4))
        print()
        
        # Convert dates to datetime objects
        for entry in entries:
            entry['schedule_date'] = datetime.strptime(entry['schedule_date'], '%Y-%m-%d')
            print(f"Parsed entry: {{'title': '{entry['title']}', 'schedule_date': '{entry['schedule_date'].strftime('%Y-%m-%d')}'}}")
            
        return entries
        
    except Exception as e:
        print(f"Error parsing with Groq: {str(e)}")
        return []

def parse_whatsapp_message(message: str) -> List[Dict[str, Any]]:
    """
    Parse WhatsApp message into structured data.
    
    Args:
        message: Raw WhatsApp message text
        
    Returns:
        List of dictionaries containing parsed information
    """
    parsed_entries = []
    
    # Split message into lines and process each line
    for line in message.strip().split('\n'):
        if not line.strip():
            continue
            
        # Extract date using regex
        date_match = re.search(r'(\w+ \d+(?:st|nd|rd|th)?,? \d{4})', line)
        if not date_match:
            continue
            
        date_str = date_match.group(1)
        # Convert date string to datetime
        schedule_date = datetime.strptime(date_str, "%B %d%S, %Y")
        
        # Extract title and parts
        title_parts = line[:date_match.start()].strip()
        parts_match = re.search(r'part (\d+)(?: & |, & |, )(\d+)(?: & |, & |, )?(\d+)?', title_parts, re.IGNORECASE)
        
        if parts_match:
            base_title = title_parts[:parts_match.start()].strip()
            parts = [int(p) for p in parts_match.groups() if p]
            
            # Create entry for each part
            for part_num in parts:
                parsed_entries.append({
                    "title": f"{base_title} part {part_num}",
                    "schedule_date": schedule_date,
                })
    
    return parsed_entries

def find_matching_files(entries: List[Dict[str, Any]], metadata_path: str, audio_dir: str) -> List[Dict[str, Any]]:
    """Match parsed entries with audio files and metadata."""
    from fuzzywuzzy import fuzz
    matched_entries = []
    
    # Read metadata
    metadata_df = pd.read_csv(metadata_path)
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    
    def normalize_text(text):
        """Normalize text for matching"""
        text = text.lower()
        text = text.replace('_', ' ').replace('-', ' ')
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return ' '.join(text.split())
    
    def extract_part_number(text):
        """Extract part number from text, returns None if no part number found"""
        patterns = [
            r'part\s*[-_]?\s*(\d+)',  # part 1, part-1, part_1
            r'part(\d+)',             # part1
            r'[-_]part[-_]\s*(\d+)',  # -part-1, _part_1
        ]
        
        text = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return None
    
    print("\nMatching files with audio and metadata...")
    for entry in entries:
        print(f"\nProcessing: {entry['title']}")
        search_title = normalize_text(entry['title'])
        search_part = extract_part_number(entry['title'])
        
        # First try to find exact metadata match
        metadata_match = None
        for _, row in metadata_df.iterrows():
            meta_title = row['title']
            if normalize_text(meta_title) == search_title:
                metadata_match = row
                print(f"Found exact metadata match: {meta_title}")
                break
            
            # Check if both have matching part numbers
            meta_part = extract_part_number(meta_title)
            if search_part and meta_part and search_part == meta_part:
                if fuzz.token_set_ratio(search_title, normalize_text(meta_title)) >= 90:
                    metadata_match = row
                    print(f"Found metadata match with part number: {meta_title}")
                    break
        
        if metadata_match is not None:
            # Now find matching audio file for this metadata
            matching_file = None
            highest_ratio = 0
            meta_title_normalized = normalize_text(metadata_match['title'])
            
            for audio_file in audio_files:
                audio_title = normalize_text(os.path.splitext(audio_file)[0])
                ratio = fuzz.token_set_ratio(meta_title_normalized, audio_title)
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    matching_file = audio_file
            
            if matching_file and highest_ratio >= 90:
                audio_path = os.path.join(audio_dir, matching_file)
                entry['audio_file'] = audio_path
                entry['podbean_title'] = metadata_match['title']  # Use exact metadata title
                entry['description'] = metadata_match.get('description', '')
                print(f"Found matching audio file: {matching_file}")
                matched_entries.append(entry)
            else:
                print(f"No matching audio file found for metadata: {metadata_match['title']}")
        else:
            print(f"No metadata match found for: {entry['title']}")
    
    return matched_entries

def prepare_podbean_schedule(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare scheduling information for each entry.
    """
    print("\nPreparing schedule times...")
    scheduled_entries = []
    
    for entry in entries:
        if 'audio_file' not in entry or 'podbean_title' not in entry:
            print(f"Skipping entry - missing required fields: {entry}")
            continue
            
        # Handle both string and datetime schedule_date
        if isinstance(entry['schedule_date'], str):
            schedule_date = datetime.strptime(entry['schedule_date'], '%Y-%m-%d').date()
        else:
            schedule_date = entry['schedule_date'].date()
            
        schedule_time = datetime.strptime(SCHEDULE_TIME, '%H:%M').time()
        schedule_datetime = PACIFIC_TZ.localize(datetime.combine(schedule_date, schedule_time))
        
        entry['schedule_datetime'] = schedule_datetime
        scheduled_entries.append(entry)
    
    return scheduled_entries

def schedule_to_podbean(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Schedule entries to Podbean.
    """
    # Initialize Podbean client
    client_id = os.getenv('PODBEAN_CLIENT_ID')
    client_secret = os.getenv('PODBEAN_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("Podbean credentials not found in .env file")
        
    podbean = PodBeanAPI(client_id, client_secret)
    results = []
    
    for entry in entries:
        try:
            print(f"\nProcessing: {entry['podbean_title']}")
            
            # 1. Upload the audio file
            print("Uploading audio file...")
            media_key = podbean.upload_audio(entry['audio_file'])
            
            # 2. Schedule the episode
            print("Scheduling episode...")
            response = podbean.schedule_episode(
                title=entry['podbean_title'],
                description=entry['description'],
                media_key=media_key,
                schedule_time=entry['schedule_datetime']
            )
            
            print(f"Successfully scheduled: {entry['podbean_title']}")
            results.append({
                'title': entry['podbean_title'],
                'status': 'success',
                'podbean_id': response['id'],
                'schedule_time': entry['schedule_datetime'].isoformat(),
                'permalink_url': response.get('permalink_url')
            })
            
        except Exception as e:
            print(f"Error scheduling {entry['podbean_title']}: {str(e)}")
            results.append({
                'title': entry['podbean_title'],
                'status': 'error',
                'error': str(e)
            })
    
    return results

def main():
    """
    Main execution function.
    """
    # Get the script's directory and project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Parent directory of scripts
    
    # Read WhatsApp message from file using absolute path
    message_path = os.path.join(project_root, "input", "whatsapp_message.txt")
    try:
        with open(message_path, 'r') as f:
            message = f.read()
    except FileNotFoundError:
        print(f"Error: WhatsApp message file not found at {message_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading WhatsApp message: {str(e)}")
        sys.exit(1)
        
    print("\nParsing WhatsApp message with Groq...")
    entries = parse_with_groq(message)
    
    if not entries:
        print("Failed to parse message. Exiting.")
        sys.exit(1)
    
    print("\nMatching files and metadata...")
    # Get project root directory
    project_root = "d:/Cascade Projects/beloved-podcast"
    
    # Use absolute paths
    metadata_path = os.path.join(project_root, "output/video_metadata.csv")
    audio_dir = os.path.join(project_root, "output/podcasts")
    
    # Match files and metadata
    matched_entries = find_matching_files(entries, metadata_path, audio_dir)
    
    if not matched_entries:
        print("No entries were matched with audio files. Exiting.")
        sys.exit(1)
        
    print("\nPreparing schedule times...")
    scheduled_entries = prepare_podbean_schedule(matched_entries)
    
    print("\nScheduling to Podbean...")
    schedule_to_podbean(scheduled_entries)

if __name__ == "__main__":
    main()
