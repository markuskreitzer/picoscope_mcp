"""Discovery and connection tools for PicoScope devices."""

from typing import Any
from ..device_manager import device_manager


def register_discovery_tools(mcp: Any) -> None:
    """Register device discovery and connection tools with the MCP server."""

    @mcp.tool()
    def list_devices() -> dict[str, Any]:
        """List all connected PicoScope devices.

        Returns:
            Dictionary containing list of discovered devices with their info.
        """
        try:
            devices = device_manager.discover_devices()
            return {
                "status": "success",
                "devices": devices,
                "count": len(devices),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "devices": [],
                "count": 0,
            }

    @mcp.tool()
    def connect_device(serial: str = "") -> dict[str, Any]:
        """Connect to a specific PicoScope device.

        Args:
            serial: Device serial number. If empty, connects to first available device.

        Returns:
            Dictionary containing connection status and device information.
        """
        try:
            # Connect to device
            success = device_manager.connect(serial=serial if serial else None)

            if not success:
                return {
                    "status": "error",
                    "error": "Failed to connect to device",
                    "serial": serial,
                }

            # Get device info
            info = device_manager.get_info()
            if info:
                return {
                    "status": "success",
                    "connected": True,
                    "device": {
                        "model": info.model,
                        "serial": info.serial,
                        "variant": info.variant,
                        "num_channels": info.num_channels,
                        "max_adc_value": info.max_adc_value,
                    },
                }
            else:
                return {
                    "status": "error",
                    "error": "Connected but failed to retrieve device info",
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "serial": serial,
            }

    @mcp.tool()
    def get_device_info() -> dict[str, Any]:
        """Get detailed information about the currently connected device.

        Returns:
            Dictionary containing device model, serial, variant, capabilities, etc.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                    "connected": False,
                }

            info = device_manager.get_info()
            if info:
                return {
                    "status": "success",
                    "connected": True,
                    "device": {
                        "model": info.model,
                        "serial": info.serial,
                        "variant": info.variant,
                        "batch_and_serial": info.batch_and_serial,
                        "num_channels": info.num_channels,
                        "max_adc_value": info.max_adc_value,
                        "min_adc_value": info.min_adc_value,
                    },
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to retrieve device info",
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    @mcp.tool()
    def disconnect_device() -> dict[str, Any]:
        """Disconnect from the currently connected PicoScope device.

        Returns:
            Dictionary containing disconnection status.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "warning",
                    "message": "No device was connected",
                    "connected": False,
                }

            success = device_manager.disconnect()

            if success:
                return {
                    "status": "success",
                    "message": "Device disconnected successfully",
                    "connected": False,
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to disconnect device",
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
