#!/usr/bin/env python3
"""
Script to submit URLs to IndexNow for psymonryan.github.io
Uses only built-in Python libraries

Usage:
    python3 submit_to_indexnow.py [--submit]

    Without --submit: Shows what URLs will be submitted
    With --submit: Actually submits the URLs to IndexNow
"""

import os
import json
import http.client
import sys

# Configuration
HOST = "psymonryan.github.io"
KEY = "4f1f1160dc1c435988263c1b5a43b63b"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
API_HOST = "api.indexnow.org"
API_PATH = "/IndexNow"

POSTS_DIR = "_posts"


def find_blog_posts():
    """Find all blog post markdown files and generate their URLs"""
    url_list = []

    # Add important static pages
    static_pages = [
        "",  # Home page
        "about",
        "archives",
        "categories",
        "tags"
    ]

    for page in static_pages:
        if page:
            url = f"https://{HOST}/{page}/"
        else:
            url = f"https://{HOST}/"
        url_list.append(url)

    # Walk through the _posts directory for blog posts
    for root, dirs, files in os.walk(POSTS_DIR):
        for file in files:
            if file.endswith('.md'):
                # Get the full path
                file_path = os.path.join(root, file)

                # Skip the .placeholder file
                if file == '.placeholder':
                    continue

                # Convert markdown filename to URL format
                # Example: 2025-04-23-Finding-The-Cursor-Position-In-ContentEditable.md
                # becomes: /posts/Finding-The-Cursor-Position-In-ContentEditable/

                # Remove the directory path and .md extension
                filename = os.path.basename(file_path)
                if filename == '.placeholder':
                    continue

                # Remove date prefix and .md extension
                # The date format is YYYY-MM-DD, so we skip 11 characters
                name_part = filename[11:]  # Skip "YYYY-MM-DD-" (11 chars)
                name_part = name_part.replace('.md', '')

                # Create the URL
                url = f"https://{HOST}/posts/{name_part}/"
                url_list.append(url)

    return url_list


def submit_to_indexnow(url_list):
    """Submit URLs to IndexNow API"""

    # Prepare the JSON payload
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": url_list
    }

    json_payload = json.dumps(payload).encode('utf-8')

    # Create HTTP connection and submit
    conn = http.client.HTTPSConnection(API_HOST)

    try:
        conn.request(
            "POST",
            API_PATH,
            body=json_payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Content-Length": len(json_payload)
            }
        )

        # Get the response
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')

        print(f"Response Status: {response.status}")
        print(f"Response Body: {response_data}")

        # IndexNow returns 202 (Accepted) on success
        return response.status == 202

    except Exception as e:
        print(f"Error submitting to IndexNow: {e}")
        return False
    finally:
        conn.close()


def main():
    # Check if --submit flag is present
    should_submit = "--submit" in sys.argv

    print("Finding blog posts...")
    url_list = find_blog_posts()

    if should_submit:
        print("\nSubmitting to IndexNow...")
        success = submit_to_indexnow(url_list)

        if success:
            print("\nSuccessfully submitted URLs to IndexNow!")
        else:
            print("\nFailed to submit URLs to IndexNow.")
    else:
        # Display a readable version of what will be posted
        print("\n=== PREVIEW OF WHAT WILL BE SUBMITTED ===")
        print(f"\nHost: {HOST}")
        print(f"Key: {KEY}")
        print(f"Key Location: {KEY_LOCATION}")
        print(f"\nNumber of URLs: {len(url_list)}")
        print("\nURLs:")
        for i, url in enumerate(url_list, 1):
            print(f"  {i}. {url}")

        print("\n" + "=" * 50)
        print("JSON Payload:")
        print("=" * 50)

        # Prepare the JSON payload (same as in submit_to_indexnow function)
        payload = {
            "host": HOST,
            "key": KEY,
            "keyLocation": KEY_LOCATION,
            "urlList": url_list
        }

        # Pretty print the JSON
        print(json.dumps(payload, indent=2))

        print("\n" + "=" * 50)
        print("\nUse --submit flag to actually submit this data to IndexNow.")
        print("Example: python3 submit_to_indexnow.py --submit")


if __name__ == "__main__":
    main()
