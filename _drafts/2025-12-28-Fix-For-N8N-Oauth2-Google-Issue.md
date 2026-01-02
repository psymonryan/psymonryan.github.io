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

## A Clue is Found!

During testing, I noticed something interesting. When I removed the parameters from the callback URI:

- The internal local callback URI `https://n8n.local.lab/rest/oauth2-credential/callback` worked (as in gave me a nice HTML response about how the parameters were missing)
- The external Traefik proxied callback URI `https://n8n.smartblackbox.com/rest/oauth2-credential/callback` failed

![working local callback]({{ site.baseurl }}/assets/pimg/working local callback.png "Working local callback")

This suggested that n8n was treating internal and external requests differently based on the source IP.

In my case, requests from `outside` get proxied via Traefik and end up arriving with a 172.x.x.x source address, whereas my internal network (192.168.x.x) is considered "trusted".

## Understanding the Authentication Flow

Through DeepWiki's source code analysis, I gained a deeper understanding of how n8n handles OAuth callbacks with authentication:

### When `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=false`:
1. **Authentication middleware runs first**: The `createAuthMiddleware()` function in `auth.service.ts` checks for valid authentication cookies/tokens (lines 95-146)
2. **If authentication fails**: Returns JSON `{"status": "error", "message": "Unauthorized"}` and stops processing (line 145)
3. **If authentication succeeds**: Continues to OAuth callback handler, which then validates OAuth parameters

### When `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true`:
1. **Auth middleware is skipped**: The `skipAuth: skipAuthOnOAuthCallback` parameter in the `@Get` decorator bypasses authentication (`oauth2-credential.controller.ts:38`)
2. **OAuth handler runs directly**: Checks for required OAuth parameters (`code` and `state`) and returns "Insufficient parameters for OAuth2 callback" if missing (`oauth2-credential.controller.ts:41-48`)

### Why Endpoints Behave Differently

The difference between my endpoints when `skipAuthOnOAuthCallback=false`:
- **External endpoint (mydomain.com)**: No valid authentication cookie/token present → auth middleware fails → JSON error response
- **Internal endpoint (n8n.local.lan)**: Has valid authentication (or different cookie domain settings) → auth passes → reaches OAuth parameter validation

The "awareness" of different connection methods is simply the authentication middleware intercepting requests before they reach the OAuth callback logic.

### Validation of this Conclusion

- I Deleted the cookies for theinternal domain to confirm authentication was the root cause
- Verified that the issue occurred because authentication cookies were tied to the login domain (`n8n.local.lab`) but OAuth callbacks arrived from different domains
- ie: the root cause: not being logged in to the domain where the callback arrives

### 8. Workarounds Attempted

After discovering the authentication issue, I attempted several workarounds:

#### Attempt 1: URL Shortener
- Tried using `redirectmeto.com` as a redirect URI so I could give a 'real' domain to google, but end up on my internal (and authenticated) domain after the redirects
- Google rejected this: "Redirect URIs cannot contain URL shortener domains"

#### Attempt 2: Internal Subdomain
- Created a subdomain of my public domain with an A record pointing to internal IP (192.168.X.XX)
- This required changing `WEBHOOK_URL`, which broke all external webhooks needing the working external URI
- I tried the oauth redirect anyway but it ended up on my internal domain which of course has a self-signed certificate
- Browsers refused to accept this, including Chrome due to HSTS errors
- Decided this was getting too hacky and abandoned this approach

## The Solution

With this understanding, the root cause became clear. The authentication check happens before any OAuth-specific logic, and Google's OAuth flow doesn't support an additional authentication layer for the callback.

It turns out that n8n changed its default authentication behaviour for OAuth callbacks starting from version 2.0:

- **Before n8n v2.0**: The default was `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true`
- **From n8n v2.0 onwards**: The default is `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=false`

### Implementation

The fix seemed straightforward - add the environment variable to skip authentication on OAuth callbacks:

```bash
N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true
```

However, for some reason it was still not working and I was again getting the same `unauthorized` message for the redirect URI

After many many hours of going through the code, it turns out there is a bug in the Docker container packaging. While the n8n source code shows valid checks to skip authentication, the actual code in the Docker container still performs user authentication on the callback, even when this flag was set. This suggests there may be a discrepancy between the source and the packaged version.

## Conclusion

This issue highlights several important lessons:

1. **Always check release notes** for breaking changes before upgrading software
2. **Avoid using `:latest` tags** in production - pin to specific versions
3. **Methodically eliminate possibilities** ("The Process of Elimination") when troubleshooting complex issues
4. **Understand your authentication flow** when using reverse proxies
5. **The Source is the Authoritative document** DeepWiki really shines in cases where documentation is lacking or the internet is flooded with AI Slop articles
6. **n8n is designed for same-domain authentication** - The architecture assumes you log in and use OAuth callbacks from the same domain

In the end, the solution required just a single environment variable change, but the debugging process involved many hours of testing various configurations. The key was recognising the authentication middleware's role in intercepting OAuth callbacks.

## Architectural Implications

This experience revealed an important architectural consideration: **n8n is fundamentally designed to have the callback on the same site where you log in**. This makes sense from a security perspective, as it maintains consistent authentication state across the OAuth flow.

For organizations that want to keep n8n accessible only on internal networks, this creates challenges:

- **Google won't allow internal domains** in authorized redirect URIs
- **Self-signed certificates** on internal domains cause browser security issues
- **URL shorteners are prohibited** by Google's OAuth policies
- **Changing WEBHOOK_URL** breaks external integrations

The `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` workaround solves the immediate problem but may not be ideal from a security perspective, as it bypasses authentication entirely for OAuth callbacks.

## References

1. [n8n Google OAuth2 Single Service Documentation](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service/)
2. [n8n Release Notes](https://docs.n8n.io/release-notes/)
3. [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
4. [Traefik Documentation](https://doc.traefik.io/traefik/)
5. [DeepWiki - Source Code Search](https://deepwiki.com/)
6. [Perplexity AI](https://www.perplexity.ai/)
7. [ChatGPT](https://chat.openai.com/)

## Final Thoughts

This experience highlights several important considerations:

### 1. Breaking Changes and User Awareness

The n8n team made a sensible security improvement by requiring authentication on OAuth callbacks starting from version 2.0. However, the way this change was introduced could have been better. When making breaking changes in widely-used tools, it's worth considering ways to force users to explicitly acknowledge the change.

One approach could be to require users to explicitly set the new environment variable before the application starts. If the variable is undefined, the application could refuse to start with a clear error message explaining what needs to be changed.

**Benefits of this approach:**
- **Explicit awareness**: Users must actively engage with the change rather than discovering it through silent failures
- **Clear documentation**: The error message serves as immediate, actionable documentation
- **Reduced risk**: Production systems won't silently break with different behavior

**Trade-offs:** This creates more friction for users, but for critical infrastructure tools like n8n, this friction might be justified.

### 2. The Importance of Source Code Analysis

While traditional troubleshooting methods (checking logs, testing configurations, searching documentation) are essential, this case demonstrates the value of **direct source code analysis**. Tools like DeepWiki that provide immediate access to the actual implementation can be invaluable when:

- Documentation is incomplete or outdated
- Search engines return AI-generated content that doesn't address the actual issue
- The problem involves complex interactions between components

In this case, understanding the exact flow of authentication middleware and OAuth callback handlers was crucial to identifying the root cause.

### 3. Architectural Constraints

This issue revealed that n8n's architecture assumes same-domain authentication for OAuth flows. While this is secure and makes sense for many deployment scenarios, it creates challenges for organizations with specific security requirements:

- Need to keep n8n accessible only on internal networks
- Use of internal domains with self-signed certificates
- Strict Google OAuth policies that prohibit workarounds

For such organizations, the `N8N_SKIP_AUTH_ON_OAUTH_CALLBACK=true` setting provides a workaround, but it's important to understand the security implications of bypassing authentication on OAuth callbacks.

### 4. Potential Packaging Bug

During my investigation, I noticed a potential discrepancy between the n8n source code and the Docker container packaging. While the source clearly shows checks to skip authentication when the flag is set, the actual behaviour in the Docker container suggested that user authentication was still being performed on callbacks. This could indicate:

- A bug in the packaging process
- Outdated code in the container
- Different build configurations