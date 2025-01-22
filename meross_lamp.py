import asyncio
import os
import logging
import argparse
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus

logging.basicConfig(level=logging.INFO)
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
    logger.info("Found devices:")
    for device in all_devices:
        logger.info(f"Name: {device.name}")
        logger.info(f"  Type: {device.type}")
        logger.info(f"  UUID: {device.uuid}")
        logger.info(f"  Hardware: {device.hardware_version}")
        logger.info(f"  Firmware: {device.firmware_version}")
        logger.info("---")

async def set_device_color(manager, color):
    await manager.async_device_discovery()
    all_devices = manager.find_devices()
    device = next((d for d in all_devices if d.uuid == DEVICE_UUID), None)

    if device and device.online_status == OnlineStatus.ONLINE:
        color_rgb = COLORS.get(color)
        if color_rgb:
            await device.async_set_light_color(rgb=color_rgb)
            logger.info(f"Set device color to {color}")
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
    parser = argparse.ArgumentParser(description="Meross Lamp Control")
    parser.add_argument('-l', '--list-devices', action='store_true', help="List all devices")
    parser.add_argument('-s', '--set-colour', type=str, help="Set the color of a specific device")
    args = parser.parse_args()

    asyncio.run(main(args))
