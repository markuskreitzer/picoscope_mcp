"""Data acquisition tools for block and streaming modes."""

from typing import Any, Literal
from ..device_manager import device_manager
from ..models import TriggerConfig, TriggerDirection


def register_acquisition_tools(mcp: Any) -> None:
    """Register data acquisition tools with the MCP server."""

    @mcp.tool()
    def set_simple_trigger(
        source: Literal["A", "B", "C", "D", "External"],
        threshold_mv: float,
        direction: Literal["Rising", "Falling", "Rising_Or_Falling"] = "Rising",
        auto_trigger_ms: int = 1000,
    ) -> dict[str, Any]:
        """Set up a simple edge trigger.

        Args:
            source: Trigger source channel or external.
            threshold_mv: Trigger threshold in millivolts.
            direction: Trigger on rising, falling, or either edge.
            auto_trigger_ms: Auto-trigger timeout in milliseconds (0 = disabled).

        Returns:
            Dictionary containing trigger configuration status.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Map direction string to enum
            direction_map = {
                "Rising": TriggerDirection.RISING,
                "Falling": TriggerDirection.FALLING,
                "Rising_Or_Falling": TriggerDirection.RISING_OR_FALLING,
            }

            # Create trigger config
            config = TriggerConfig(
                source=source,
                threshold_mv=threshold_mv,
                direction=direction_map[direction],
                auto_trigger_ms=auto_trigger_ms,
            )

            # Set trigger
            success = device_manager.set_trigger(config)

            if success:
                return {
                    "status": "success",
                    "source": source,
                    "threshold_mv": threshold_mv,
                    "direction": direction,
                    "auto_trigger_ms": auto_trigger_ms,
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to set trigger",
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    @mcp.tool()
    def capture_block(
        pre_trigger_samples: int = 1000, post_trigger_samples: int = 1000
    ) -> dict[str, Any]:
        """Capture a single block of data.

        Args:
            pre_trigger_samples: Number of samples before trigger.
            post_trigger_samples: Number of samples after trigger.

        Returns:
            Dictionary containing captured waveform data for all enabled channels.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Capture block
            result = device_manager.capture_block(pre_trigger_samples, post_trigger_samples)

            if result is None:
                return {
                    "status": "error",
                    "error": "Failed to capture data",
                }

            # Format the response
            channels_data = {}
            for channel, data in result.items():
                channels_data[channel] = {
                    "time_values": data.time_values,
                    "voltage_values": data.voltage_values,
                    "sample_interval_ns": data.sample_interval_ns,
                    "num_samples": data.num_samples,
                }

            return {
                "status": "success",
                "total_samples": pre_trigger_samples + post_trigger_samples,
                "pre_trigger_samples": pre_trigger_samples,
                "post_trigger_samples": post_trigger_samples,
                "channels": channels_data,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    @mcp.tool()
    def start_streaming(
        sample_interval_ns: int,
        buffer_size: int = 100000,
        auto_stop: bool = False,
        max_samples: int = 0,
    ) -> dict[str, Any]:
        """Start streaming data acquisition.

        Args:
            sample_interval_ns: Sample interval in nanoseconds.
            buffer_size: Size of streaming buffer.
            auto_stop: Whether to automatically stop after max_samples.
            max_samples: Maximum samples to capture (0 = continuous).

        Returns:
            Dictionary containing streaming status and configuration.
        """
        # TODO: Implement streaming mode
        return {
            "status": "not_implemented",
            "sample_interval_ns": sample_interval_ns,
            "buffer_size": buffer_size,
        }

    @mcp.tool()
    def stop_streaming() -> dict[str, Any]:
        """Stop streaming data acquisition.

        Returns:
            Dictionary containing stop status and summary of captured data.
        """
        # TODO: Implement streaming stop
        return {"status": "not_implemented"}

    @mcp.tool()
    def get_streaming_data(max_samples: int = 1000) -> dict[str, Any]:
        """Get latest streaming data.

        Args:
            max_samples: Maximum number of samples to retrieve.

        Returns:
            Dictionary containing latest streaming data for enabled channels.
        """
        # TODO: Implement streaming data retrieval
        return {"status": "not_implemented", "max_samples": max_samples}
