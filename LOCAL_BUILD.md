# Local custom branch

This branch is a snapshot of the local Hoshimi server customization.

- Base commit: `7c09ef5268ef1210b44d78cbb84ef82ac54c9806` (2026-11-21 17:01, Merge PR #15)
- Branch: `local/hoshimi-custom-20261123`
- Upstream latest at snapshot time: `0b2b2d09` (not merged into this branch)

## Scope

Relative to the base commit, this branch contains:

- 19 modified server modules
- 4 new modules: achievement story, fragment exchange, equipment recommendation data, save compatibility
- Local multi-dimensional variable logic, shop fixes, black-zone and seizure handling, achievement story, fragment exchange, and local protocol extensions

The branch intentionally keeps the local behavior instead of replacing it with the newer upstream implementation. Upstream changes after `7c09ef52` can be merged in a separate sync branch.

## Not included

- `data/` (user saves, chat, UIDs)
- `logs/` and `python-server-*.log*`
- `config_local.py` (machine-specific paths and ports)
- `*.bak`, `*.pem`, `*.pfx`, certificates and keys
- probe binaries, screenshots, temporary scripts

Create `config_local.py` locally when running this branch; it is intentionally ignored.

## Test-only setting

`agl_server/polyhedron_game.py` currently has:

```python
SPECIAL_GATE_CHANCE = 1.0
```

This is a local test setting that makes every eligible node spawn a special gate. For normal play or shared builds, change it back to `0.25` or make it configurable.
