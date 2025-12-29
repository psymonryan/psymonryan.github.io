---
title: "n8n OAuth2 'status: error, message: unauthorised' with Google Calendar Credential [Solved]"
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

I just learned that always using `:latest` on my docker images may not be such a good idea :smile:

When my swarm stack recently restarted, it silently upgraded n8n to version 2.1.4, after which I encountered persistent OAuth2 authentication failures when trying to connect to Google Calendar. Despite trying numerous troubleshooting steps, the issue remained unresolved until I discovered a critical change in n8n's authentication behaviour starting from version 2.0.

This post documents my frustrating journey ruling out every suggestion I could find using [Google](https://www.google.com/), [Bing](https://www.bing.com/), [Perplexity](https://www.perplexity.ai/), and even [ChatGPT](https://chat.openai.com/).

Finally, by chance I noticed some weird behaviour that allowed me to query the source code via [DeepWiki](https://deepwiki.com/), which led me to the solution.

Of course, the solution was clearly documented in the [n8n release notes](https://docs.n8n.io/release-notes/), but it was completely "unfindable" when searching for the symptoms of the issue.

## The Problem

When attempting to authenticate with Google Calendar in n8n using the OAuth2 credential, I consistently received a `"status: error, message: unauthorised"` response in the authentication popup. This prevented me from renewing the OAuth token, which had been working without issues for a long time.


![Attempt to fix Google Calendar OAuth2]({{ site.baseurl }}/assets/pimg/attempt to fix Google Calendar Oauth2.png "Attempting various fixes")

## Troubleshooting Attempts

I tried numerous approaches to resolve the issue:

### 1. Re-creating OAuth Credentials

- Recreated the n8n Google Calendar credential using the existing Client ID
- Generated new OAuth client ID and secret in Google Cloud Console
- Verified the redirect URI matched exactly between Google Cloud Console and n8n

### 2. Google Cloud Console Configuration

- Changed the Google OAuth app from "Testing" to "Production" mode

![Google App in Production]({{ site.baseurl }}/assets/pimg/google app - in production.png "Google OAuth app configuration")

- Deleted and recreated the app with a new name ("NEW N8N")
- Added missing scopes back (they were empty in the console)
- Verified required scopes: `https://www.googleapis.com/auth/calendar`

![Correct Google Scopes]({{ site.baseurl }}/assets/pimg/correct google scopes.png "Correct Google Calendar scopes")

### 3. n8n Version Rollback (and forward)

- Rolled back to version 2.0.1 (I presumed this was the previously working version, where as it must have been < v2)
- I also tried version 2.1.2
- Reverted back to 2.1.4

### 4. Debugging and Logging

- Enabled debug logging in n8n - this provided no useful information at the instant of the callback issue
- Checked Traefik logs for anything unusual
- Tested direct access to callback URL using wget
- Verified container network connectivity

### 5. Browser and Environment Issues

- Tested in incognito mode
- Cleared cookies and cache
- Tried different browsers
- Verified there were no trailing slash issues in URLs

### 6. Reverse Proxy Configuration

- Checked X-Forwarded headers
- Modified Traefik middleware to ensure proper header forwarding
- Tried different N8N_HOST values

## The Clue

During testing, I noticed something interesting. When I removed the parameters from the callback URI:

- The internal local callback URI `https://n8n.local.lab/rest/oauth2-credential/callback` worked (as in gave me a nice HTML response about how the parameters were missing)
- The external Traefik proxied callback URI `https://n8n.smartblackbox.com/rest/oauth2-credential/callback` failed

![working local callback]({{ site.baseurl }}/assets/pimg/working local callback.png "Working local callback")

This suggested that n8n was treating internal and external requests differently based on the source IP.

In my case, requests from `outside` get proxied via Traefik and end up arriving with a 172.x.x.x source address, whereas my internal network (192.168.x.x) is considered "trusted".

## The Solution

With this specific observation, I was able to query the n8n source code via [DeepWiki](https://deepwiki.com/) and immediately found the root cause. I discovered that n8n changed its default authentication behaviour for OAuth callbacks starting from version 2.0:

- **Before n8n v2.0**: The default was `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true`, meaning no authentication was required for OAuth callback endpoints
- **From n8n v2.0 onwards**: The default is `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=false`, requiring authentication by default

This security improvement makes sense, but it can break existing OAuth integrations when n8n is protected by an authentication layer. Unfortunately, Google's OAuth flow doesn't provide a way to supply an additional authentication layer for the callback (as of December 2025).

### Implementation

The fix was simple - add the environment variable to skip authentication on OAuth callbacks:

```bash
N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true
```

## Conclusion

This issue highlights several important lessons:

1. **Always check release notes** for breaking changes before upgrading software
2. **Avoid using `:latest` tags** in production - pin to specific versions
3. **Methodically eliminate possibilities** ("The Process of Elimination") when troubleshooting complex issues
4. **Understand your authentication flow** when using reverse proxies
5. **The Source is the Authoritative document** DeepWiki really shines in cases where documentation is lacking or the internet is flooded with AI Slop articles

In the end, the solution required just a single environment variable change, but the debugging process involved many hours of testing various configurations. The key was recognising the pattern of internal vs. external callback behaviour.

## References

1. [n8n Google OAuth2 Single Service Documentation](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service/)
2. [n8n Release Notes](https://docs.n8n.io/release-notes/)
3. [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
4. [Traefik Documentation](https://doc.traefik.io/traefik/)
5. [DeepWiki - Source Code Search](https://deepwiki.com/)
6. [Perplexity AI](https://www.perplexity.ai/)
7. [ChatGPT](https://chat.openai.com/)

## Final Thoughts

This experience highlights an important consideration when implementing breaking changes in software: how to ensure users are aware of and properly handle the change. The n8n team made a sensible security improvement by requiring authentication on OAuth callbacks, but the way this change was introduced could have been better.

When making breaking changes, especially in widely-used tools, it's worth considering whether to force users to explicitly acknowledge the change. One approach could be to require users to explicitly set the new environment variable before the application starts. If the variable is undefined, the application could refuse to start with a clear error message explaining what needs to be changed.

This approach has several benefits:

1. **Explicit awareness**: Users must actively engage with the change rather than discovering it through silent failures
2. **Clear documentation**: The error message serves as immediate, actionable documentation
3. **Reduced risk**: Production systems won't silently break with different behavior (since they will fail during staging)

Of course, this approach has trade-offs - it creates more friction for users. However, for critical infrastructure tools like n8n, where silent failures can have significant consequences, this friction might well be justified.
