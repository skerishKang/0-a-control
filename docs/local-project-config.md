# Local project config

`data/config/tracked_projects.json` is a local-only configuration file.

It can contain user-specific workspace values, so it must not be committed to Git.
The repository only tracks `data/config/tracked_projects.example.json`.

## Setup

1. Copy the example file to `data/config/tracked_projects.json`.
2. Edit the copied file on the current machine.
3. Keep the copied file local and untracked.

## Commit policy

- Commit the example file.
- Do not commit the real local config file.
- Do not commit runtime database files, generated session files, or generated queue artifacts.
