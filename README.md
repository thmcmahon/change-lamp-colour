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

This repository includes a GitHub Actions workflow (`.github/workflows/change-colour.yml`) that:
- Runs hourly at minute 45 UTC.
- Uses the Australia/Sydney timezone to gate exactly **06:45** (sets green) and **10:45** (sets yellow) local Canberra time.
- Can be manually triggered via the **Run workflow** button, with optional inputs:
  - `time`: override the local time for testing (format `HH:MM`).
  - `color`: manually choose `green` or `yellow` in one step.

To customize or inspect the schedule, see `.github/workflows/change-colour.yml`.

## Testing

```bash
pytest
```