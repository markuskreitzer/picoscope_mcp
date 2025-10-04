"""Signal analysis and measurement tools."""

from typing import Any, Literal
import numpy as np
from ..device_manager import device_manager
from ..utils import calculate_frequency, calculate_rms, calculate_peak_to_peak


def register_analysis_tools(mcp: Any) -> None:
    """Register signal analysis tools with the MCP server."""

    @mcp.tool()
    def measure_frequency(channel: Literal["A", "B", "C", "D"]) -> dict[str, Any]:
        """Measure signal frequency on a channel.

        Note: This requires a recent capture. Call capture_block first.

        Args:
            channel: Channel to measure.

        Returns:
            Dictionary containing frequency in Hz and measurement details.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Check if channel is configured
            if channel not in device_manager.channel_configs:
                return {
                    "status": "error",
                    "error": f"Channel {channel} not configured. Configure and capture first.",
                }

            # For now, we need to guide the user to capture data first
            # In a real implementation, we might store the last capture
            return {
                "status": "info",
                "message": "To measure frequency: 1) Configure channel, 2) Set trigger, 3) Capture block, then extract frequency from captured data",
                "channel": channel,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "channel": channel,
            }

    @mcp.tool()
    def measure_amplitude(
        channel: Literal["A", "B", "C", "D"],
        measurement_type: Literal["peak_to_peak", "rms", "mean", "max", "min"] = "peak_to_peak",
    ) -> dict[str, Any]:
        """Measure signal amplitude on a channel.

        Note: This requires a recent capture. Call capture_block first.

        Args:
            channel: Channel to measure.
            measurement_type: Type of amplitude measurement.

        Returns:
            Dictionary containing amplitude in volts and measurement type.
        """
        try:
            if not device_manager.is_connected():
                return {
                    "status": "error",
                    "error": "No device connected",
                }

            # Check if channel is configured
            if channel not in device_manager.channel_configs:
                return {
                    "status": "error",
                    "error": f"Channel {channel} not configured. Configure and capture first.",
                }

            # For now, we need to guide the user to capture data first
            return {
                "status": "info",
                "message": "To measure amplitude: 1) Configure channel, 2) Set trigger, 3) Capture block, then extract measurements from captured data",
                "channel": channel,
                "measurement_type": measurement_type,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "channel": channel,
            }

    @mcp.tool()
    def measure_rise_time(
        channel: Literal["A", "B", "C", "D"],
        low_threshold_percent: float = 10.0,
        high_threshold_percent: float = 90.0,
    ) -> dict[str, Any]:
        """Measure signal rise time (10% to 90% by default).

        Args:
            channel: Channel to measure.
            low_threshold_percent: Lower threshold percentage (0-100).
            high_threshold_percent: Upper threshold percentage (0-100).

        Returns:
            Dictionary containing rise time in seconds.
        """
        # TODO: Implement rise time measurement
        return {
            "status": "not_implemented",
            "channel": channel,
            "low_threshold": low_threshold_percent,
            "high_threshold": high_threshold_percent,
        }

    @mcp.tool()
    def measure_pulse_width(
        channel: Literal["A", "B", "C", "D"], threshold_percent: float = 50.0
    ) -> dict[str, Any]:
        """Measure pulse width at specified threshold.

        Args:
            channel: Channel to measure.
            threshold_percent: Threshold percentage for pulse measurement (0-100).

        Returns:
            Dictionary containing pulse width in seconds.
        """
        # TODO: Implement pulse width measurement
        return {
            "status": "not_implemented",
            "channel": channel,
            "threshold": threshold_percent,
        }

    @mcp.tool()
    def compute_fft(
        channel: Literal["A", "B", "C", "D"],
        window: Literal["hann", "hamming", "blackman", "rectangular"] = "hann",
    ) -> dict[str, Any]:
        """Compute FFT (Fast Fourier Transform) for frequency domain analysis.

        Args:
            channel: Channel to analyze.
            window: Window function to apply.

        Returns:
            Dictionary containing frequency bins and magnitude spectrum.
        """
        # TODO: Implement FFT computation
        return {"status": "not_implemented", "channel": channel, "window": window}

    @mcp.tool()
    def get_statistics(
        channel: Literal["A", "B", "C", "D"], num_samples: int = 1000
    ) -> dict[str, Any]:
        """Get statistical analysis of signal.

        Args:
            channel: Channel to analyze.
            num_samples: Number of samples to analyze.

        Returns:
            Dictionary containing min, max, mean, std dev, etc.
        """
        # TODO: Implement statistics calculation
        return {"status": "not_implemented", "channel": channel, "num_samples": num_samples}

    @mcp.tool()
    def measure_thd(channel: Literal["A", "B", "C", "D"]) -> dict[str, Any]:
        """Measure Total Harmonic Distortion (THD).

        Args:
            channel: Channel to measure.

        Returns:
            Dictionary containing THD percentage and harmonic components.
        """
        # TODO: Implement THD measurement
        return {"status": "not_implemented", "channel": channel}
