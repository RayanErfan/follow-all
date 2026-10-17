# follow-all

Follows everyone that a given GitHub profile is following — built for our
college assignment where we all need to follow the same list of classmates.

Works on Windows / macOS / Linux. Needs only Python 3 — no `pip install`.

## Usage

```bash
python3 follow_all.py <profile-username>
```

Example:

```bash
python3 follow_all.py mlimyy1385-dot
```

Want to see what it would do without following anyone?

```bash
python3 follow_all.py mlimyy1385-dot --dry-run
```

## Setup — get a token (2 minutes)

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. **Generate new token (classic)**
3. Give it **only** the `user:follow` scope
4. Copy the `ghp_...` value

Then tell the script about it:

**macOS / Linux**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Windows (Command Prompt)**
```bat
set GITHUB_TOKEN=ghp_your_token_here
```

Or just run the script — it will ask you for the token with hidden input.

## Important — token safety

- **Never** paste your token into a script, a screenshot, a chat, or commit it
  to GitHub. Anyone with your token acts as you.
- Only grant the `user:follow` scope — nothing else.
- When you're done with the assignment, delete the token:
  **Settings → Developer settings → Personal access tokens → Delete**.
- If you ever accidentally share a token, delete it immediately and generate a
  new one.

## Notes

- Already following someone? They're just skipped — safe to run more than once.
- The script can't follow your own account; it skips it automatically.
- GitHub rate-limits how fast you can follow. If that happens the script waits
  and retries on its own, so just let it run.
