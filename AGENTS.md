# AGENTS.md

This file provides guidance for AI agents working with this repository.

## Repository Overview

This is Simon Ryan's technical blog built with Jekyll and hosted on GitHub Pages. The blog focuses on topics including Artificial Intelligence & Machine Learning, Linux Systems, Cloud Technologies, Software Development, DevOps & Automation, and Web Development.

## File Structure

```
/
├── _config.yml                  # Jekyll configuration
├── _posts/                      # Blog posts (Markdown files)
├── _drafts/                     # Draft blog posts
├── _tabs/                       # Navigation tabs
├── assets/                      # Images and static assets
├── _plugins/                    # Custom Jekyll plugins
├── Gemfile                      # Ruby dependencies
├── Gemfile.lock                 # Ruby dependency versions
├── README.md                    # Project documentation
├── AGENTS.md                    # AI agent guidance (this file)
└── ...                         # Other configuration files
```

## Key Files and Directories

### `_config.yml`
- Main Jekyll configuration file
- Contains site metadata, theme settings, and plugin configurations
- **Important settings**: `title`, `tagline`, `url`, `theme`, `plugins`

### `_posts/`
- Contains published blog posts in Markdown format
- Filename format: `YYYY-MM-DD-Title.md`
- Front matter includes: `title`, `date`, `categories`, `tags`, `layout`

### `_drafts/`
- Contains unpublished blog post drafts
- Same format as `_posts/` but not included in site builds by default

### `_tabs/`
- Navigation tabs for the blog
- Files: `about.md`, `archives.md`, `categories.md`, `tags.md`

### `assets/`
- `img/`: Blog post images
- `pimg/`: Processed images (optimized for web)
- `lib/`: CSS, JavaScript, and other assets

## Blog Post Format

All blog posts use Markdown with YAML front matter:

```yaml
---
title: "Post Title"
description: A consise description of the page that will become the meta description
date: YYYY-MM-DD HH:MM:SS +/-TTTT
tags: [tag1, tag2, tag3]
categories: [category1, category2]
layout: post
---

Content in Markdown format...
```

## Common Tasks

### Creating a New Blog Post

1. Create a new file in `_posts/` with format: `YYYY-MM-DD-Title.md`
2. Add YAML front matter with title, date, tags, and categories
3. Write content in Markdown
4. Add images to `assets/img/` and reference them in the post

### Running the Blog Locally

```bash
bundle install
bundle exec jekyll serve --livereload --drafts --host=0.0.0.0
```

The blog will be available at `http://localhost:4000`

### Building the Site

```bash
bundle exec jekyll build
```

### Publishing

Commit changes to the `main` branch. GitHub Actions will automatically:
1. Build the site
2. Deploy to GitHub Pages
3. Run the ./submit_to_indexnow.py script

## Development Environment

### Required Tools

- Ruby 3.1.3 or later
- Bundler
- Jekyll
- Node.js (for some theme features)

### Installing Dependencies

```bash
bundle install
```

## Theme Information

This blog uses the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme.

### Theme Features

- Responsive design
- Dark/light mode toggle
- Math support (LaTeX)
- Mermaid diagrams
- Code highlighting
- Table of contents
- SEO optimization

### Theme Configuration

Key theme settings in `_config.yml`:
- `theme_mode`: `[light|dark]`
- `avatar`: Profile image
- `toc`: Table of contents settings
- `assets`: CSS/JS customization

## Writing Guidelines

### Post Structure

1. **Title**: Clear and descriptive
2. **Introduction**: Hook readers and explain what the post covers
3. **Body**: Well-organized sections with clear headings
4. **Conclusion**: Summary and key takeaways
5. **Tags**: 3-5 relevant tags
6. **Categories**: 1-2 broad categories

### Markdown Features

- Use ` ``` ` for code blocks with language specification
- Use `> ` for blockquotes
- Use `[link text](url)` for links
- Use `![alt text](image.png)` for images
- Use `**bold**` and '*italic*' for emphasis

### Image Handling

1. Place images in `assets/img/`
2. Reference with relative paths: `/assets/img/filename.png`
3. For blog post images, also place in `assets/pimg/` for optimized versions

## Automation

### GitHub Actions

The `.github/workflows/pages-deploy.yml` file handles:
- Building the Jekyll site
- Deploying to GitHub Pages on push to `main`

### Custom Plugins

- `_plugins/posts-lastmod-hook.rb`: Updates post modification dates

## Tips for AI Agents

### When Adding/Editing Posts

1. Always check `_drafts/` for existing drafts before creating new posts
2. Maintain consistent front matter format
3. Use existing tags and categories where appropriate
4. Follow the 30-minute rule: only document solutions that took significant time

### When Modifying Configuration

1. Test changes locally before committing
2. Check for theme compatibility
3. Document configuration changes in the README

### When Working with Images

1. Provide both original and optimized versions
2. Use descriptive filenames
3. Add alt text for accessibility

## Links

- **Website**: [https://psymonryan.github.io](https://psymonryan.github.io)
- **GitHub**: [https://github.com/psymonryan](https://github.com/psymonryan)
