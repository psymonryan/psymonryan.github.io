# Simon's Blog

A personal technical blog built with [Jekyll](https://jekyllrb.com/) and hosted on GitHub Pages.

## About

This is Simon Ryan's technical blog where I share insights, tips, and tutorials on topics including:

- **Artificial Intelligence & Machine Learning**
- **Linux Systems**
- **Cloud Technologies**
- **Software Development**
- **DevOps & Automation**
- **Web Development**

The blog follows the philosophy: *"If it takes longer than 30 minutes to figure out, share it!"*

## Technology Stack for this Blog

- **Static Site Generator**: [Jekyll](https://jekyllrb.com/)
- **Theme**: [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions (automated build and deploy on push to main)

## Setup and Configuration

### Installing Ruby
To avoid using the old macOS Ruby version, install a newer version:

```bash
sudo port install chruby ruby-install
ruby-install ruby 3.1.3
```

Add these to your `~/.bashrc`:
```bash
source /opt/local/share/chruby/chruby.sh
source /opt/local/share/chruby/auto.sh
```

Then activate the new Ruby version:
```bash
chruby ruby-3.1.3
chruby  # Shows the current version
# or: ruby --version (should show 3.1.3, not macOS 2.6)
```

### Installing Jekyll
```bash
gem install jekyll
```

### Cloning the Blog
```bash
git clone https://github.com/cotes2020/chirpy-starter psymonryan.github.io
cd psymonryan.github.io
bundle  # Pulls in gem dependencies
```

### Running Locally
```bash
bundle install  # Install Ruby dependencies if needed
bundle exec jekyll serve --livereload --drafts --host=0.0.0.0
```

The blog will be available at `http://localhost:4000`

### Adding Images
Drag images to the appropriate folder in the sidebar, then drag them from the folder into your Markdown file - it will auto-link them for you.

### Upgrading Chirpy
See the [Chirpy Upgrade Guide](https://github.com/cotes2020/jekyll-theme-chirpy/wiki/Upgrade-Guide) for upgrade instructions.

### Extras Added

#### Emoji Support
Add to `Gemfile`, then run `bundle`:
```ruby
gem "jemoji"
```

Add to `_config.yml`:
```yaml
plugins:
  - jemoji
```

#### Meta Description
The first heading becomes the meta description when published, so make it long and keyword-rich for search engines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The Chirpy theme is licensed under MIT - see [Chirpy License](https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/LICENSE) for details.

## Links

- **Website**: [https://psymonryan.github.io](https://psymonryan.github.io)
- **GitHub**: [https://github.com/psymonryan](https://github.com/psymonryan)
- **Twitter**: [https://twitter.com/psymonryan](https://twitter.com/psymonryan)

## Writing Workflow

My writing process involves:

1. **Mind Mapping**: Using iThoughtsX to organize ideas
2. **Documentation**: Keeping a knowledge base of solutions that take >30 minutes to figure out
3. **Exporting**: Converting mind maps to Markdown
4. **Publishing**: Committing to GitHub triggers automated deployment via GitHub Actions

## Philosophy

> "If it is still in my head, it messes with my thinking. If it is in a storage system, then it is permanently searchable (and publishable)."

This blog is part of my broader documentation system that includes:

- **Daily Journal**: Chronological tracking of work and ideas
- **Projects Map**: Contextual organization of project-related information
- **Knowledge Base**: Solutions to problems that took significant time to resolve

By documenting and sharing this knowledge, I aim to:

- Help others avoid similar pitfalls
- Create a searchable archive of solutions
- Foster a community of learning and growth

---

*Built with Jekyll and the Chirpy Theme*
