#!/usr/bin/env python3
"""
Utility Functions Module

Provides common utility functions for the Beloved Podcast Processing Pipeline.
Focuses on text processing, cleaning, and standardization.

Key Utilities:
- Title cleaning and sanitization
- HTML entity decoding
- Special character removal
- Filename generation

Use Cases:
- Podcast title normalization
- Filename generation for audio files
- Preprocessing text for matching and storage

Dependencies:
- html: HTML entity decoding
- re: Regular expression operations
- datetime: Date handling (optional)
"""

import html
import re
from datetime import datetime


def clean_title(title, date=None):
    """
    Clean and standardize a title for display and filename purposes.

    Comprehensive title cleaning process:
    - Decode HTML entities
    - Remove extra spaces
    - Remove parenthetical content
    - Normalize special characters
    - Standardize Q&A formatting
    - Generate safe filename

    Args:
        title (str): Original title to clean
        date (str, optional): Date in MM-DD-YY format to append to filename

    Returns:
        tuple: 
            - Cleaned display title (with spaces)
            - Cleaned filename title (with underscores)
    """
    # Decode HTML entities first
    title = html.unescape(title)
    
    # Remove extra spaces and unwanted characters
    title = ' '.join(title.split())
    
    # Remove date patterns
    if '(' in title and ')' in title:
        title = title[:title.rfind('(')].strip()
    
    # Comprehensive character replacements
    replacements = {
        '&amp;': '&',      # Normalize ampersand
        '&quot;': '',       # Remove quotation entities
        ' - Part': ' Part', # Standardize part notation
        '|': '',            # Remove pipe characters
        '🩸': '',           # Remove blood drop emoji
        '❤️': '',           # Remove heart emoji
        '–': '-',           # Normalize dashes
        '"': '',            # Remove various quote types
        '"': '',
        '"': '',
        '?': '',            # Remove question marks
        ' V/S ': ' vs ',    # Normalize versus notation
        ' V/s ': ' vs ',
        ' v/s ': ' vs ',
        "''": "",           # Remove double quotes
        '`': '',            # Remove backticks
        '!': '',            # Remove exclamation marks
        '...': '',          # Remove ellipses
        ':': '',            # Remove colons
        ';': '',            # Remove semicolons
        ',': '',            # Remove commas
        '#': '',            # Remove hash symbols
        '@': '',            # Remove at symbols
        '$': '',            # Remove dollar signs
        '%': '',            # Remove percent signs
        '^': '',            # Remove carets
        '*': '',            # Remove asterisks
        '+': '',            # Remove plus signs
        '=': '',            # Remove equal signs
        '{': '',            # Remove curly braces
        '}': '',
        '[': '',            # Remove square brackets
        ']': '',
        '<': '',            # Remove angle brackets
        '>': '',
        '/': '',            # Remove forward slashes
        '\\': ''            # Remove backslashes
    }
    
    # Apply replacements
    for old, new in replacements.items():
        title = title.replace(old, new)
    
    # Standardize Q&A format with optional spaces and &
    title = re.sub(r'Q\s*&\s*A\s*[-–—_]?\s*(\d+)', r'Q&A \1', title, flags=re.IGNORECASE)
    title = re.sub(r'Q\s*&\s*A', 'Q&A', title, flags=re.IGNORECASE)
    
    # Remove any remaining special characters EXCEPT & and -
    title = re.sub(r'[^\w\s\&-]', '', title)
    
    # Remove multiple spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Create filename version (replace spaces with underscores)
    filename = title.replace(' ', '_')
    
    # Add date if provided
    if date:
        filename = f"{filename}_{date}"
    
    return title, filename


def main():
    """
    Demonstration and testing of utility functions.

    Provides examples of title cleaning and transformation.
    Useful for manual testing and understanding function behavior.
    """
    test_titles = [
        "Understanding Divine Love (Part 1)",
        "Q&A - Special Session 42",
        "Podcast with Special Characters: @#$%^&*()!",
        "Ishmael & Isaac – Sons of Flesh (Natural) V/S Son of Promise"
    ]

    print("Title Cleaning Demonstration:")
    for raw_title in test_titles:
        display_title, filename_title = clean_title(raw_title)
        print(f"\nOriginal: {raw_title}")
        print(f"Display Title: {display_title}")
        print(f"Filename: {filename_title}")


if __name__ == "__main__":
    main()
