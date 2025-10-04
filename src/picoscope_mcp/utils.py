"""Utility functions for PicoScope MCP server."""

from typing import Any
import numpy as np


def adc_to_mv(adc_values: np.ndarray, voltage_range: float, max_adc: int) -> np.ndarray:
    """Convert ADC counts to millivolts.

    Args:
        adc_values: Array of ADC values.
        voltage_range: Voltage range in volts.
        max_adc: Maximum ADC value for the device.

    Returns:
        Array of voltage values in millivolts.
    """
    return (adc_values / max_adc) * voltage_range * 1000


def mv_to_adc(mv_values: float | np.ndarray, voltage_range: float, max_adc: int) -> int | np.ndarray:
    """Convert millivolts to ADC counts.

    Args:
        mv_values: Voltage value(s) in millivolts.
        voltage_range: Voltage range in volts.
        max_adc: Maximum ADC value for the device.

    Returns:
        ADC count(s).
    """
    result = (mv_values / (voltage_range * 1000)) * max_adc
    if isinstance(mv_values, (int, float)):
        return int(result)
    return result.astype(int)


def calculate_frequency(time_values: np.ndarray, voltage_values: np.ndarray) -> float:
    """Calculate signal frequency using zero-crossing method.

    Args:
        time_values: Time array in seconds.
        voltage_values: Voltage array.

    Returns:
        Frequency in Hz.
    """
    # Find zero crossings
    zero_crossings = np.where(np.diff(np.sign(voltage_values - np.mean(voltage_values))))[0]

    if len(zero_crossings) < 2:
        return 0.0

    # Calculate period from zero crossings
    periods = []
    for i in range(len(zero_crossings) - 2):
        period = time_values[zero_crossings[i + 2]] - time_values[zero_crossings[i]]
        periods.append(period)

    if not periods:
        return 0.0

    avg_period = np.mean(periods)
    return 1.0 / avg_period if avg_period > 0 else 0.0


def calculate_rms(voltage_values: np.ndarray) -> float:
    """Calculate RMS voltage.

    Args:
        voltage_values: Voltage array in millivolts.

    Returns:
        RMS voltage in millivolts.
    """
    return float(np.sqrt(np.mean(voltage_values**2)))


def calculate_peak_to_peak(voltage_values: np.ndarray) -> float:
    """Calculate peak-to-peak voltage.

    Args:
        voltage_values: Voltage array in millivolts.

    Returns:
        Peak-to-peak voltage in millivolts.
    """
    return float(np.max(voltage_values) - np.min(voltage_values))


def get_available_voltage_ranges() -> list[float]:
    """Get list of standard voltage ranges in volts.

    Returns:
        List of available voltage ranges.
    """
    return [0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]


def validate_channel(channel: str, num_channels: int) -> bool:
    """Validate channel identifier.

    Args:
        channel: Channel identifier (A, B, C, D, etc.).
        num_channels: Number of available channels on device.

    Returns:
        True if channel is valid, False otherwise.
    """
    channel_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    return channel in channel_map and channel_map[channel] < num_channels
