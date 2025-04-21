import asyncio
import os
import logging
import traceback
import argparse
import sys
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

logging.basicConfig(
    level=logging.WARNING,  # Default to WARNING level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


COLORS = {
    'green': (0, 255, 0),
    'yellow': (255, 223, 120)
}

# Load sensitive information from environment variables
DEVICE_UUID = os.environ.get("DEVICE_UUID", "default_uuid")

async def list_devices(manager):
    await manager.async_device_discovery()
    all_devices = manager.find_devices()
    print("\nDiscovered Devices:")
    print("-" * 20)
    for device in all_devices:
        print(f"Device: {device.name}")
        print(f"UUID: {device.uuid}")
        print("-" * 20)

async def set_device_color(manager, color):
    await manager.async_device_discovery()
    all_devices = manager.find_devices()
    device = next((d for d in all_devices if d.uuid == DEVICE_UUID), None)

    if device and device.online_status == OnlineStatus.ONLINE:
        color_rgb = COLORS.get(color)
        if color_rgb:
            await device.async_set_light_color(rgb=color_rgb)
            print(f"Set device color to {color}")
        else:
            logger.error(f"Color {color} not recognized. Available colors: {list(COLORS.keys())}")
    else:
        logger.error("Device not found or offline.")

async def main(args):
    try:
        http_api_client = await MerossHttpClient.async_from_user_password(
            email=os.environ.get("MEROSS_EMAIL"),
            password=os.environ.get("MEROSS_PASSWORD"),
            api_base_url="https://iotx-ap.meross.com"
        )

        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()

        if args.list_devices:
            await list_devices(manager)
        elif args.set_colour:
            await set_device_color(manager, args.set_colour)

        manager.close()
        await http_api_client.async_logout()

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Meross Lamp Control",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python meross_lamp.py --list-devices\n"
            "  python meross_lamp.py --set-colour green\n"
        )
    )
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help="List all devices"
    )
    parser.add_argument(
        '-s', '--set-colour', type=str,
        choices=list(COLORS.keys()),
        help=(
            "Set the color of a specific device.\n"
            "Available colors: %(choices)s"
        )
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable DEBUG logging output"
    )
    args = parser.parse_args()

    # Configure logging levels based on debug flag
    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.getLogger().setLevel(log_level)
    logging.getLogger('meross_iot').setLevel(log_level)

    # If no flags provided, show help and exit
    if not args.list_devices and args.set_colour is None:
        parser.print_help()
        sys.exit(0)

    asyncio.run(main(args))
