# Meross Lamp Controller

This is a lightweight Python CLI to list and control a Meross smart lamp via the Meross IoT HTTP API.

## What it does
- Discovers and lists all your Meross devices (`--list-devices`).
- Sets a lamp’s color to **green** or **yellow** (`--set-colour`).
- Allows overriding the target device UUID via `--uuid` (defaults to the `DEVICE_UUID` env var).
- Supports a `--debug` flag for verbose logging.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your environment variables:
   ```bash
   export MEROSS_EMAIL=you@example.com
   export MEROSS_PASSWORD=supersecret
   export DEVICE_UUID=<your-default-device-uuid>
   ```

3. Run the CLI:
   ```bash
   # List devices
   python meross_lamp.py --list-devices

   # Set default device to green
   python meross_lamp.py --set-colour green

   # Override UUID and set yellow
   python meross_lamp.py --set-colour yellow --uuid 1234-ABCD-5678-EFGH

   # Debug logging
   python meross_lamp.py --set-colour green --debug
   ```

## Scheduling

This repository includes a GitHub Actions workflow at `.github/workflows/change-colour.yml`:
- Scheduled runs in Canberra time (AEST/AEDT):
  - 06:45 local → triggers at `45 20 * * *` UTC (sets **green**)
  - 10:00 local → triggers at `0 0 * * *` UTC  (sets **yellow**)
- Manual runs via **Run workflow** (workflow_dispatch) with a required `color` input:
  - `color`: `green` or `yellow`

See `.github/workflows/change-colour.yml` for full details.

## Testing

```bash
pytest
```