"""Channel and device configuration tools."""

from typing import Any, Literal
from ..device_manager import device_manager
from ..models import ChannelConfig, ChannelCoupling


def register_configuration_tools(mcp: Any) -> None:
    """Register configuration tools with the MCP server."""

    @mcp.tool()
    def configure_channel(
        channel: Literal["A", "B", "C", "D"],
        enabled: bool = True,
        coupling: Literal["AC", "DC"] = "DC",
        voltage_range: float = 5.0,
        analog_offset: float = 0.0,
    ) -> dict[str, Any]:
        """Configure a channel on the oscilloscope.

        Args:
            channel: Channel identifier (A, B, C, or D).
            enabled: Whether the channel is enabled.
            coupling: AC or DC coupling.
            voltage_range: Voltage range in volts (e.g., 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20).
            analog_offset: DC offset voltage in volts.

        Returns:
            Dictionary containing configuration status and applied settings.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Create channel config
            config = ChannelConfig(
                channel=channel,
                enabled=enabled,
                coupling=ChannelCoupling.AC if coupling == "AC" else ChannelCoupling.DC,
                voltage_range=voltage_range,
                analog_offset=analog_offset,
            )

            # Configure the channel
            success = device_manager.configure_channel(config)

            if success:
                return {
                    "status": "success",
                    "channel": channel,
                    "enabled": enabled,
                    "coupling": coupling,
                    "voltage_range": voltage_range,
                    "analog_offset": analog_offset,
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to configure channel",
                    "channel": channel,
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "channel": channel,
            }

    @mcp.tool()
    def get_channel_config(channel: Literal["A", "B", "C", "D"]) -> dict[str, Any]:
        """Get current configuration of a channel.

        Args:
            channel: Channel identifier (A, B, C, or D).

        Returns:
            Dictionary containing current channel settings.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Get channel config from device manager
            if channel in device_manager.channel_configs:
                config = device_manager.channel_configs[channel]
                return {
                    "status": "success",
                    "channel": channel,
                    "enabled": config.enabled,
                    "coupling": config.coupling.value,
                    "voltage_range": config.voltage_range,
                    "analog_offset": config.analog_offset,
                }
            else:
                return {
                    "status": "error",
                    "error": f"Channel {channel} not configured",
                    "channel": channel,
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "channel": channel,
            }

    @mcp.tool()
    def set_timebase(sample_interval_ns: int, num_samples: int) -> dict[str, Any]:
        """Set the timebase (sampling rate) for data acquisition.

        Note: The actual timebase is determined during block capture based on
        the requested number of samples. This tool is informational.

        Args:
            sample_interval_ns: Desired sample interval in nanoseconds.
            num_samples: Number of samples to capture.

        Returns:
            Dictionary containing timebase information.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Calculate approximate sample rate
            sample_rate_hz = 1_000_000_000 / sample_interval_ns if sample_interval_ns > 0 else 0

            return {
                "status": "success",
                "note": "Timebase will be set during capture based on device capabilities",
                "requested_interval_ns": sample_interval_ns,
                "requested_sample_rate_hz": sample_rate_hz,
                "num_samples": num_samples,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
