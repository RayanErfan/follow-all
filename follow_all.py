#!/usr/bin/env python3
"""
follow_all.py — Follow everyone that a GitHub profile is following.

Made for the class assignment "follow everyone on the list".
Uses only the Python standard library — no pip install needed.

Usage:
    python3 follow_all.py <profile-username> [--dry-run]

Authentication (never put your token inside the script!):
    - macOS/Linux:  export GITHUB_TOKEN=ghp_xxxxx
    - Windows:      set GITHUB_TOKEN=ghp_xxxxx
    - or let the script ask you for it securely when it runs.

How to get a token:
    GitHub → Settings → Developer settings → Personal access tokens →
    Generate new token (classic) → check the "user:follow" scope only.

Notes:
    - Following is idempotent: people you already follow are simply skipped.
    - You cannot follow your own account; the script skips it automatically.
    - GitHub limits how fast you can follow; if you hit a limit (HTTP 429)
      the script waits and retries automatically.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from getpass import getpass

API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "follow-all-script"}


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def api(method, path, token=None, quiet_errors=()):
    """Make one GitHub API request. Returns (status_code, parsed_json_or_None)."""
    headers = dict(HEADERS)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        if e.code in quiet_errors:
            return e.code, None
        if e.code == 403 and e.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - time.time(), 5)
            print(f"  rate limit hit, waiting {int(wait)}s ...")
            time.sleep(wait)
            return api(method, path, token, quiet_errors)
        if e.code == 429:
            print("  slow down, waiting 60s ...")
            time.sleep(60)
            return api(method, path, token, quiet_errors)
        try:
            detail = json.loads(e.read()).get("message", "")
        except Exception:
            detail = ""
        return e.code, {"message": detail}


def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        token = getpass("Paste your GitHub token (input hidden): ").strip()
    if not token:
        fail("no token provided")
    status, me = api("GET", "/user", token)
    if status != 200:
        fail(f"token rejected by GitHub (HTTP {status}) — check it has the 'user:follow' scope")
    return token, me["login"]


def get_following(profile, token):
    """Fetch everyone `profile` is following, following pagination."""
    logins, page = [], 1
    while True:
        status, data = api("GET", f"/users/{profile}/following?per_page=100&page={page}", token)
        if status != 200:
            fail(f"could not read '{profile}' (HTTP {status}) — double-check the username")
        if not data:
            break
        logins += [u["login"] for u in data]
        if len(data) < 100:
            break
        page += 1
    return logins


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry_run = "--dry-run" in sys.argv[1:]

    if len(args) != 1:
        print(__doc__.strip())
        sys.exit(1)
    profile = args[0].lstrip("@").rstrip("/")

    token, me = get_token()
    print(f"logged in as: {me}")

    targets = get_following(profile, token)
    # remove duplicates (case-insensitive) and yourself
    seen, unique = set(), []
    for login in targets:
        key = login.lower()
        if key in seen or key == me.lower():
            continue
        seen.add(key)
        unique.append(login)
    print(f"'{profile}' is following {len(unique)} accounts")

    if dry_run:
        for login in unique:
            print(f"  would follow: {login}")
        print("dry run — nothing was followed")
        return

    ok = failed = 0
    failures = []
    for i, login in enumerate(unique, 1):
        status, _ = api("PUT", f"/user/following/{login}", token, quiet_errors=(429,))
        if status == 204:
            ok += 1
        else:
            failed += 1
            failures.append((login, status))
        if i % 25 == 0 or i == len(unique):
            print(f"  progress {i}/{len(unique)}  (followed {ok}, failed {failed})")
        time.sleep(0.2)  # stay well under GitHub's speed limits

    print(f"\ndone: followed {ok}, failed {failed}")
    for login, status in failures[:20]:
        print(f"  HTTP {status}: {login}")
    if len(failures) > 20:
        print(f"  ...and {len(failures) - 20} more")
    print("\nreminder: delete your token when you're finished — "
          "GitHub → Settings → Developer settings → Personal access tokens")


if __name__ == "__main__":
    main()
