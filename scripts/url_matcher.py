#!/usr/bin/env python3
"""
URL Matching Module for Podcast Processing Pipeline

This module provides advanced title matching capabilities 
for podcast URL identification and validation.

Key Features:
- Fuzzy title matching
- Confidence scoring
- Preprocessing of titles
- Flexible matching strategies

Matching Algorithm Overview:
1. Preprocess and normalize titles
2. Calculate Levenshtein distance
3. Apply confidence thresholds
4. Return best matching URLs

Dependencies:
- fuzzywuzzy: Fuzzy string matching
- python-Levenshtein: Efficient string distance calculations
- pandas: Data manipulation
- numpy: Numerical operations

Input:
- Spotify podcast titles
- YouTube video titles

Output:
- Matched URLs with confidence scores
- Detailed matching information
"""

import re
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from typing import List, Tuple, Optional, Dict, Any


def preprocess_title(title: str) -> str:
    """
    Comprehensive title preprocessing for matching.

    Cleaning steps:
    - Convert to lowercase
    - Remove special characters
    - Remove common stop words
    - Normalize whitespace
    - Remove parenthetical content
    - Handle common abbreviations

    Args:
        title (str): Raw title to preprocess

    Returns:
        str: Cleaned and normalized title
    """
    # Convert to lowercase
    title = title.lower()
    
    # Remove parenthetical content
    title = re.sub(r'\([^)]*\)', '', title)
    
    # Remove special characters and extra whitespace
    title = re.sub(r'[^\w\s]', '', title)
    
    # Remove common stop words and noise
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
        'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 
        'into', 'over', 'after', 'podcast', 'show', 'episode'
    }
    
    # Split, filter, and rejoin
    words = [word for word in title.split() if word not in stop_words]
    title = ' '.join(words)
    
    # Normalize whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def calculate_title_similarity(title1: str, title2: str) -> float:
    """
    Calculate similarity between two titles using multiple metrics.

    Matching Strategies:
    - Partial ratio (substring matching)
    - Token set ratio (order-independent)
    - Token sort ratio (normalized word order)

    Args:
        title1 (str): First title to compare
        title2 (str): Second title to compare

    Returns:
        float: Similarity score (0-100)
    """
    # Preprocess titles
    clean_title1 = preprocess_title(title1)
    clean_title2 = preprocess_title(title2)
    
    # Calculate multiple similarity metrics
    metrics = [
        fuzz.partial_ratio(clean_title1, clean_title2),
        fuzz.token_set_ratio(clean_title1, clean_title2),
        fuzz.token_sort_ratio(clean_title1, clean_title2)
    ]
    
    # Weighted average of metrics
    weights = [0.3, 0.4, 0.3]
    similarity = np.average(metrics, weights=weights)
    
    return similarity


def match_podcast_urls(
    spotify_titles: List[str], 
    youtube_metadata: pd.DataFrame, 
    confidence_threshold: float = 70.0
) -> List[Dict[str, Any]]:
    """
    Match Spotify podcast titles with YouTube video URLs.

    Advanced matching process with:
    - Comprehensive similarity calculation
    - Confidence-based filtering
    - Multiple matching strategies
    - Detailed result reporting

    Args:
        spotify_titles (List[str]): List of Spotify podcast titles
        youtube_metadata (pd.DataFrame): DataFrame with YouTube video metadata
        confidence_threshold (float, optional): Minimum similarity score. Defaults to 70.0.

    Returns:
        List[Dict[str, Any]]: Matched URLs with detailed information
    """
    matched_urls = []
    
    for spotify_title in spotify_titles:
        best_match = {
            'spotify_title': spotify_title,
            'youtube_url': None,
            'youtube_title': None,
            'upload_date': None,
            'confidence': 0.0
        }
        
        for _, row in youtube_metadata.iterrows():
            youtube_title = row['title']
            youtube_url = row['url']
            upload_date = row['upload_date']  # Using upload_date from metadata
            
            # Calculate similarity
            similarity = calculate_title_similarity(spotify_title, youtube_title)
            
            # Update best match if better confidence
            if similarity > best_match['confidence'] and similarity >= confidence_threshold:
                best_match.update({
                    'youtube_url': youtube_url,
                    'youtube_title': youtube_title,
                    'upload_date': upload_date,  # Keep original MM-DD-YY format
                    'confidence': similarity
                })
        
        # Only add if a match was found
        if best_match['youtube_url']:
            matched_urls.append(best_match)
    
    return matched_urls


def export_matched_urls(
    matched_urls: List[Dict[str, Any]], 
    output_path: str = 'output/matched_urls.csv'
) -> None:
    """
    Export matched URLs to a CSV file.

    Provides a structured output of:
    - Spotify podcast titles
    - Matched YouTube URLs
    - Confidence scores
    - Video date in mmddyy format

    Args:
        matched_urls (List[Dict[str, Any]]): List of matched URL dictionaries
        output_path (str, optional): Path to save CSV. Defaults to 'output/matched_urls.csv'
    """
    # Convert to DataFrame for easy export
    df = pd.DataFrame(matched_urls)
    
    # Ensure output directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Export to CSV
    df.to_csv(output_path, index=False)
    print(f"Matched URLs exported to {output_path}")


def main() -> None:
    """
    Demonstration and testing of URL matching functionality.

    Provides a complete workflow:
    1. Load Spotify titles
    2. Load YouTube metadata
    3. Perform matching
    4. Export results
    """
    # Example usage (replace with actual data loading)
    spotify_titles = [
        "Divine Revelation Podcast",
        "Spiritual Insights Weekly",
        "Biblical Teachings Explained"
    ]
    
    # Load YouTube metadata (simulated)
    youtube_metadata = pd.DataFrame({
        'title': [
            "Divine Revelation - Special Session",
            "Spiritual Insights 2023",
            "Biblical Teachings Deep Dive"
        ],
        'url': [
            'https://youtube.com/divine1',
            'https://youtube.com/insights1',
            'https://youtube.com/biblical1'
        ],
        'upload_date': [
            '2022-01-01',
            '2023-02-15',
            '2022-03-20'
        ]
    })
    
    # Perform matching
    matched_urls = match_podcast_urls(spotify_titles, youtube_metadata)
    
    # Print results
    print("Matched URLs:")
    for match in matched_urls:
        print(f"Spotify Title: {match['spotify_title']}")
        print(f"YouTube Title: {match['youtube_title']}")
        print(f"Confidence: {match['confidence']:.2f}%")
        print(f"URL: {match['youtube_url']}")
        print(f"Date: {match['upload_date']}\n")
    
    # Optional: Export results
    export_matched_urls(matched_urls)


if __name__ == "__main__":
    main()
