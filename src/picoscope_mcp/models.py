"""Data models and type definitions for PicoScope MCP server."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ChannelCoupling(str, Enum):
    """Channel coupling types."""

    AC = "AC"
    DC = "DC"


class TriggerDirection(str, Enum):
    """Trigger direction options."""

    RISING = "Rising"
    FALLING = "Falling"
    RISING_OR_FALLING = "Rising_Or_Falling"


class DownsamplingMode(str, Enum):
    """Downsampling mode options."""

    NONE = "none"
    AGGREGATE = "aggregate"
    DECIMATE = "decimate"
    AVERAGE = "average"


@dataclass
class DeviceInfo:
    """Information about a PicoScope device."""

    handle: int
    model: str
    serial: str
    variant: str
    batch_and_serial: str
    max_adc_value: int
    min_adc_value: int
    num_channels: int


@dataclass
class ChannelConfig:
    """Channel configuration settings."""

    channel: str
    enabled: bool
    coupling: ChannelCoupling
    voltage_range: float
    analog_offset: float


@dataclass
class TriggerConfig:
    """Trigger configuration settings."""

    source: str
    threshold_mv: float
    direction: TriggerDirection
    auto_trigger_ms: int


@dataclass
class CaptureData:
    """Captured waveform data."""

    channel: str
    time_values: list[float]
    voltage_values: list[float]
    sample_interval_ns: int
    num_samples: int
