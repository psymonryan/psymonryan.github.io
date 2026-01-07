# IndexNow Implementation for psymonryan.github.io

## What is IndexNow?

IndexNow is an open protocol developed by Microsoft and Bing that allows website owners to instantly notify search engines about new or updated content. This helps improve SEO and ensures your content is indexed quickly.

## Implementation

### 1. API Key File

The file `e845a0b6f0724cc0a8c2688f092ee917.txt` contains the API key that proves ownership of the domain. This file must be hosted at the root of your website.

### 2. Submission Script

The `submit_to_indexnow.py` script:
- Finds all blog posts in the `_posts` directory
- Generates proper URLs for each post
- Submits them to the IndexNow API
- Also includes important static pages (home, about, archives, categories, tags)

## Usage

To see what URLs will be submitted (dry run):

```bash
python3 submit_to_indexnow.py
```

To actually submit the URLs to IndexNow:

```bash
python3 submit_to_indexnow.py --submit
```

## How It Works

1. The script scans the `_posts` directory for all `.md` files
2. It converts filenames like `2025-04-23-Finding-The-Cursor-Position-In-ContentEditable.md` into URLs like `https://psymonryan.github.io/posts/Finding-The-Cursor-Position-In-ContentEditable/`
3. It sends a POST request to `https://api.indexnow.org/IndexNow` with:
   - Your domain name
   - The API key
   - The location of the key file
   - The list of URLs to index

## Requirements

- Python 3 (uses only built-in libraries)
- Internet connection to submit to IndexNow API

## Notes

- The script uses only built-in Python libraries (`os`, `json`, `http.client`)
- IndexNow returns HTTP 202 (Accepted) on successful submission
- You can run this script manually or automate it (e.g., via GitHub Actions after each deploy)
