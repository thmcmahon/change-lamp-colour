import os
import sys
import argparse
from argparse import RawTextHelpFormatter
import asyncio
import logging
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

# same colour map
COLORS = {
    'green':  (0, 255, 0),
    'yellow': (255, 223, 120),
}

# read once at module load
DEVICE_UUID = os.environ.get("DEVICE_UUID", "default_uuid")

# top-level default logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------
# Suppress a noisy meross_iot warning about "become online while offline"
# We only filter out records whose message text contains that exact phrase.
class SuppressOfflineWarning(logging.Filter):
    def filter(self, record):
        # drop only the "has become online while we were offline" warning
        msg = record.getMessage()
        if "has become online while we were offline" in msg:
            return False
        return True
# Attach filter to the meross_iot.manager logger so that only this warning is suppressed
logging.getLogger("meross_iot.manager").addFilter(SuppressOfflineWarning())

async def list_devices(manager):
    devices = manager.find_devices()
    print("\nDiscovered Devices:")
    print("-" * 20)
    for d in devices:
        print(f"Device: {d.name}")
        print(f"UUID:   {d.uuid}")
        print("-" * 20)


async def set_device_color(manager, color, device_uuid):
    # locate the device by provided UUID
    devices = manager.find_devices()
    dev = next((d for d in devices if d.uuid == device_uuid), None)
    if not dev:
        logger.error(f"Device with UUID {device_uuid} not found.")
        return
    # refresh device state before inspecting or setting
    # refresh device state before inspecting or setting
    await dev.async_update()
    if dev.online_status == OnlineStatus.ONLINE:
        await dev.async_set_light_color(rgb=COLORS[color])
        print(f"Set device color to {color}")
    else:
        logger.error("Device is offline.")


async def main(args):
    try:
        # Authenticate
        http_client = await MerossHttpClient.async_from_user_password(
            email=os.environ.get("MEROSS_EMAIL"),
            password=os.environ.get("MEROSS_PASSWORD"),
            api_base_url="https://iotx-ap.meross.com"
        )

        manager = MerossManager(http_client=http_client)
        await manager.async_init()

        # one discovery for both commands
        await manager.async_device_discovery()

        if args.list_devices:
            await list_devices(manager)
        elif args.set_colour:
            # allow override via CLI uuid, otherwise use env DEVICE_UUID
            target_uuid = args.uuid if args.uuid else DEVICE_UUID
            await set_device_color(manager, args.set_colour, target_uuid)

        manager.close()
        await http_client.async_logout()
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Meross Lamp Control",
        formatter_class=RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python meross_lamp.py --list-devices\n"
            "  python meross_lamp.py --set-colour green\n"
        )
    )
    parser.add_argument(
        "-l", "--list-devices",
        action="store_true",
        help="List all devices"
    )
    parser.add_argument(
        "-s", "--set-colour",
        choices=list(COLORS.keys()),
        help="Set the color of a specific device.\nAvailable colors: %(choices)s"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable DEBUG logging output"
    )
    parser.add_argument(
        "-u", "--uuid",
        type=str,
        help="Override device UUID (default: DEVICE_UUID env var)"
    )
    args = parser.parse_args()

    # If no flags provided, show help and exit
    if not args.list_devices and args.set_colour is None:
        parser.print_help()
        sys.exit(0)

    # Configure logging based on debug flag
    level = logging.DEBUG if args.debug else logging.WARNING
    logging.getLogger().setLevel(level)
    logging.getLogger("meross_iot").setLevel(level)

    asyncio.run(main(args))
