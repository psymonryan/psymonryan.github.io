---
title: "n8n OAuth2 'status: error, message: unauthorised' with Google Calendar [Solved]"
date: 2025-12-27 00:00:00 +0000
last_modified_at: 2025-12-27 00:00:00 +0000
categories:
  - n8n
  - OAuth2
  - Google Calendar
  - Troubleshooting
tags:
  - n8n
  - oauth2
  - google
  - calendar
  - authentication
  - workflow
  - debugging
---

## Introduction

After my n8n Docker container silently upgraded to version 2.1.4, I started receiving persistent OAuth2 authentication failures when connecting to Google Calendar. The error message `"status: error, message: unauthorised"` appeared consistently, despite the workflow having worked perfectly for months.

What made this particularly frustrating was that my setup differs from most n8n deployments, making solution finding by google search not so effective - I run n8n on an internal domain and proxy external requests through an existing website domain. This architecture is more secure than just exposing the service to the internet, but unfortunately, it creates specific challenges with OAuth callbacks, as I found out.

## My Homelab Setup

My n8n deployment uses:
- **Internal domain**: `n8n.local.lab` (accessible only on my internal network)
- **External proxy**: Requests from the internet go through `mypublicdomain.com` via Traefik on my swarm cluster.
- **No public exposure**: I don't expose n8n directly to the internet.

This setup works for most n8n features, but it causes issues with OAuth because:
- n8n assumes the domain you log in from is the same domain that receives OAuth callbacks
- Google OAuth requires `authorized` redirect URIs
- Internal domains with self-signed certificates cause browser security issues during OAuth redirects

## The Problem

When attempting to authenticate with Google Calendar using the OAuth2 credential, I received:
```
"status: error, message: unauthorised"
```

This prevented token renewal and made the Google Calendar node unusable.

## Troubleshooting Attempts

I systematically tried numerous approaches from the docs and various google and perplexity.ai searches:

### OAuth Credential Configuration
- Recreated the n8n Google Calendar credential
- Generated new OAuth client ID and secret
- Verified redirect URI matched exactly between Google Cloud Console and n8n

### Google Cloud Console Settings
- Changed OAuth app from "Testing" to "Production" mode
- Deleted and recreated the app
- Added required scopes (which had disappeared for some reason): `https://www.googleapis.com/auth/calendar`

### Version Testing
- Rolled back to version 2.0.1
- Tried version 2.1.2
- Tested current version 2.1.4
- (in hindsight, I should have rolled back <2.0) :laughing:

### Debugging
- Enabled debug logging (no useful information)
- Checked Traefik logs (nothing of interest there either)
- Tested callback URLs directly with wget
- Verified network connectivity from within the container

### Browser and Environment
- Tested in incognito mode
- Cleared cookies and cache
- Tried different browsers
- Checked for URL trailing slash issues

### Reverse Proxy Configuration
- Verified X-Forwarded headers
- Modified Traefik middleware multiple times (didnt seem to make any difference)
- Tested different N8N_HOST values and other Environment variable changes

### Workarounds (once I understood the root cause)
- **URL Shortener**: Tried *redirectmeto.com* - Google rejected it (as it classes this as a shortener and URL _shorteners_ are not allowed)
- **Internal Subdomain**: Created a public subdomain pointing to internal IP - this broke my external webhooks and caused certificate issues

## The Discovery

During testing, I noticed an important difference:
- Internal callback: `https://n8n.local.lab/rest/oauth2-credential/callback` returned HTML about missing parameters
- External callback: `https://mypublicdomain.com/rest/oauth2-credential/callback` returned the JSON error

This suggested that n8n was treating requests differently the endpoint I was browsing in from, and further exploration revealed that it was looking for a 'logged in session' on the callback URI.

Of course this was not happening as I'm only logging in from my internal address, not the external address that the callback is required for.

## Root Cause

Before n8n version 2.0 this was working fine, but:

Starting with n8n v2.0, the default behaviour changed:
- **Before v2.0**: `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` (default)
- **From v2.0**: `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=false` (default)

The authentication middleware now runs before OAuth callback handling. When I logged in to the internal domain but OAuth callbacks arrived externally, the authentication check failed because:
- Authentication cookies were tied to `n8n.local.lab`
- External callbacks arrived without valid authentication
- The middleware returned `{"status": "error", "message": "Unauthorized"}` before reaching OAuth logic

## The Solution

The fix should have been simple - set the environment variable: (and this is what it says in the documentation)
```bash
N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true
```

However, this didn't work. After extensive code analysis (and digging into the code), I discovered that the Docker container packaging had a discrepancy - it was still performing some of the user authentication checks on callbacks even when the flag was set. Specifically, it was expecting the user id to be defined, which, since there is no authentication, was not available.

How to fix this? I'm hoping this is just a packaging error made when the official docker container was built. (the wrong oauth2 code ends up in the container, as I see good code without this bug in the repo)

For now I'll take a _quick fix_ approach and hope that the next version has this fixed... If not I'll raise a ticket.
### Docker Container Patch

Since the official Docker image didn't properly respect the `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` flag, I created a custom Docker image with a patched version of the OAuth service. Here's how to replicate this fix:

#### 1. Create a custom Dockerfile

```dockerfile
FROM docker.n8n.io/n8nio/n8n:2.1.4

# Copy the 'fixed' code into place
COPY oauth.service.js /usr/local/lib/node_modules/n8n/dist/oauth/oauth.service.js

# Use the existing entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
```

#### 2. Create a patched oauth.service.js

The key change is in the `decodeCsrfState` method around line 150. The original code throws an `AuthError` when the user ID doesn't match, but we need to skip this check when `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true`:

But for now I'll just comment out the _throw_ and do something more elegant if I put in a PR.

```javascript
if (decryptedState.userId !== req.user?.id) {
    this.logger.debug('throwing since req.user?.id is wrong:', req.user?.id);
    // SDR: this should not trigger when N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true
    // throw new auth_error_1.AuthError('Unauthorized');
}
```

The commented-out line is the original code that was causing the issue. By commenting it out, the user id check no longer causes an exception.

With this patched version, the OAuth callback will work correctly even when authentication cookies are absent.

## Key Lessons

1. **Check release notes** for breaking changes before upgrading
2. **Avoid `:latest` tags** in production - pin to specific versions
3. **Carefully consider authentication flows** when using reverse proxies
4. **n8n assumes same-domain authentication** - callbacks should come from the same domain you log in from so all these issues would not have been there if I had done a _standard_ standalone installation
5. **Source code analysis** is invaluable when documentation is lacking and debug messages are few and far between. (Thank-you DeepWiki)

## Architectural Implications

This issue reveals that n8n's architecture assumes:
- You log in and use OAuth from the same domain
- Authentication state is maintained across the OAuth flow

For internal-only deployments, this creates challenges:
- Google won't allow internal domains in redirect URIs
- Self-signed certificates cause browser security issues
- URL shorteners are prohibited
- Changing `WEBHOOK_URL` breaks external integrations

The `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` setting works as a workaround but bypasses authentication for callbacks.

## References

- [n8n Google OAuth2 Documentation](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service/)
- [n8n Release Notes](https://docs.n8n.io/release-notes/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [DeepWiki - Source Code Search](https://deepwiki.com/)

## Final Thoughts

This experience highlights the importance of:

### Explicit Breaking Changes
The n8n team made a sensible security improvement, but the change could have been better communicated. Requiring users to explicitly acknowledge breaking changes (e.g., by refusing to start without the new variable set) would reduce silent failures.

### Source Code Analysis
When traditional troubleshooting fails, direct source code analysis becomes essential. Tools like DeepWiki provide immediate access to implementation details that can uncover issues not documented elsewhere.

### Architectural Awareness
Understanding a tool's architectural assumptions is crucial. n8n works best when authentication and OAuth callbacks share the same domain. For internal deployments, this requires careful planning.

For others facing similar issues with internal n8n deployments, the `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` environment variable is the key, though you may need to verify your Docker container properly implements this feature.
