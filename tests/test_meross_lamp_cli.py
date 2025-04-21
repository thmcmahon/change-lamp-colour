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