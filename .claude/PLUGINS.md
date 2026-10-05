# Claude Code plugins for this repository

`.claude/settings.json` registers three plugin marketplaces and enables one
plugin from each. Claude Code picks these up automatically when the repo is opened —
there is nothing to `npm install` for the registration itself.

| Plugin | Marketplace | Source | What it does |
| --- | --- | --- | --- |
| `superdesign@superdesign` | `superdesign` | [superdesigndev/superdesign-skill](https://github.com/superdesigndev/superdesign-skill) | Design skill: UI, presentations and graphics on the Superdesign canvas. |
| `claude-mem@thedotmack` | `thedotmack` | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | Persistent memory: compresses and recalls context across sessions. |
| `impeccable@impeccable` | `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Design fluency for frontend work: one skill, 23 `/impeccable ...` commands, anti-pattern detection. |

## Manual install (equivalent to the committed config)

`/plugin` is a user-typed slash command, so run these yourself in Claude Code if
you would rather not rely on the checked-in settings:

```
/plugin marketplace add superdesigndev/superdesign-skill
/plugin install superdesign@superdesign

/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem@thedotmack

/plugin marketplace add pbakaus/impeccable
/plugin install impeccable@impeccable
```

Update later with `/plugin update`.

## Runtime prerequisites

Registration is config-only, but the plugins need these to actually run:

- **superdesign** — the CLI it drives, plus a login:
  ```
  npm install -g @superdesign/cli@latest
  superdesign login
  ```
- **claude-mem** — Node >= 20, plus `bun` and `uv` (its installer fetches both
  if missing). The full setup, including the worker service, is:
  ```
  npx claude-mem install
  ```
  Note that plain `npm install -g claude-mem` installs the library only — it
  does not register hooks or start the worker.

- **impeccable** — Node 22 or newer on PATH. Its `PostToolUse` (Edit|Write) and
  `Stop` hooks no-op with a one-time notice if Node is older, so nothing breaks;
  the design checks just never run.

## Not installed here: task-observer

`rebelytics/one-skill-to-rule-them-all` ships the `task-observer` skill, which
is designed to invoke itself before the first tool call of every session and to
be reinforced by a `UserPromptSubmit` hook or a CLAUDE.md activation block. That
shape — standing instructions injected into the agent on every turn — is blocked
by this environment's auto-mode safety classifier, so it is deliberately absent
from this repo rather than half-installed.

Install it yourself if you want it: copy `SKILL.md`, `references/` and
`scripts/` from that repository into `.claude/skills/task-observer/`, then add
the activation block from its `references/environments.md` to your CLAUDE.md.
The repo's `scripts/validate-skill-bundle.py` checks the bundle is complete —
note it requires the directory be named `task-observer` exactly.

## Before you enable claude-mem for everyone

claude-mem registers `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
`PostToolUse` and `Stop` hooks. They run on every tool call and every turn, and
by default the hosted provider sends session content off-machine. That is a
per-team data-egress decision, not just a convenience setting.

To keep the marketplace registered but leave the plugin off, drop this entry
from `.claude/settings.json`:

```json
"claude-mem@thedotmack": true
```

Or opt out locally without touching the shared file, in `.claude/settings.local.json`:

```json
{ "enabledPlugins": { "claude-mem@thedotmack": false } }
```

`.claude/settings.local.json` is developer-local and should not be committed.
