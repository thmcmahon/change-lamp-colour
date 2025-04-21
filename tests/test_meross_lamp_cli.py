import os
import sys
import subprocess
import pytest

# Path to the meross_lamp.py script under test
SCRIPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'meross_lamp.py')
)

def run_cli(args, env=None):
    """
    Run the meross_lamp.py script with given args.
    Returns a CompletedProcess-like object with stdout, stderr, and returncode.
    """
    cmd = [sys.executable, SCRIPT_PATH] + args
    env_vars = os.environ.copy() if env is None else env
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env_vars,
        text=True,
    )
    return result

def test_help_shows_usage():
    """The help flag should exit 0 and print usage info to stdout."""
    res = run_cli(['-h'])
    assert res.returncode == 0
    assert 'usage:' in res.stdout.lower()

@pytest.mark.skipif(
    not all(os.environ.get(v) for v in ['MEROSS_EMAIL', 'MEROSS_PASSWORD']),
    reason='MEROSS_EMAIL and MEROSS_PASSWORD must be set'
)
def test_list_devices_live():
    """Integration: --list-devices against live Meross API."""
    res = run_cli(['--list-devices'])
    assert res.returncode == 0
    assert 'Discovered Devices:' in res.stdout

@pytest.mark.skipif(
    not all(os.environ.get(v) for v in ['MEROSS_EMAIL', 'MEROSS_PASSWORD', 'DEVICE_UUID']),
    reason='MEROSS_EMAIL, MEROSS_PASSWORD, and DEVICE_UUID must be set'
)
def test_set_colour_live():
    """Integration: --set-colour against live Meross API."""
    color = 'yellow'
    res = run_cli(['--set-colour', color])
    assert res.returncode == 0
    assert f'Set device color to {color}' in res.stdout

@pytest.mark.skipif(
    not all(os.environ.get(v) for v in ['MEROSS_EMAIL', 'MEROSS_PASSWORD', 'DEVICE_UUID']),
    reason='MEROSS_EMAIL, MEROSS_PASSWORD, and DEVICE_UUID must be set'
)
def test_set_colour_with_uuid_override_live():
    """Integration: --set-colour with explicit --uuid override."""
    color = 'yellow'
    uuid = os.environ['DEVICE_UUID']
    # Should succeed when overriding with the same UUID
    res = run_cli(['--set-colour', color, '--uuid', uuid])
    assert res.returncode == 0
    assert f'Set device color to {color}' in res.stdout

@pytest.mark.skipif(
    not all(os.environ.get(v) for v in ['MEROSS_EMAIL', 'MEROSS_PASSWORD']),
    reason='MEROSS_EMAIL and MEROSS_PASSWORD must be set'
)
def test_set_colour_with_uuid_invalid_live():
    """Integration: --set-colour with explicit invalid --uuid should log error."""
    color = 'yellow'
    invalid_uuid = '00000000-0000-0000-0000-000000000000'
    res = run_cli(['--set-colour', color, '--uuid', invalid_uuid])
    # CLI logs an error but exit code remains 0
    assert res.returncode == 0
    # Expect error message in stderr mentioning not found
    # The error message may appear in stdout or stderr
    combined = (res.stdout + res.stderr).lower()
    assert 'not found' in combined and invalid_uuid.lower() in combined

def test_missing_credentials_list_devices():
    """
    The script should exit 1 and print a helpful error if credentials are missing when listing devices.
    """
    # Run with empty env -> no MEROSS_EMAIL/PASSWORD
    res = run_cli(['--list-devices'], env={})
    assert res.returncode == 1
    out = (res.stdout + res.stderr).lower()
    assert 'meross_email' in out and 'meross_password' in out

def test_missing_credentials_set_colour():
    """
    The script should exit 1 and print a helpful error if credentials are missing when setting colour.
    """
    res = run_cli(['--set-colour', 'green'], env={})
    assert res.returncode == 1
    out = (res.stdout + res.stderr).lower()
    assert 'meross_email' in out and 'meross_password' in out