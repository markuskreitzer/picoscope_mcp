"""Device manager for PicoScope oscilloscopes."""

from typing import Optional, Any
import ctypes
import numpy as np

# Try to import PicoSDK, but handle gracefully if not installed
try:
    from picosdk.discover import find_all_units
    from picosdk.ps5000a import ps5000a as ps
    from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
    PICOSDK_AVAILABLE = True
except Exception as e:
    PICOSDK_AVAILABLE = False
    print(f"Warning: PicoSDK not available: {e}")
    print("Server will run but device operations will fail until PicoSDK is installed.")

from .models import DeviceInfo, ChannelConfig, TriggerConfig, CaptureData


class PicoScopeManager:
    """Manager for PicoScope device operations."""

    def __init__(self):
        """Initialize the device manager."""
        self.current_device: Optional[Any] = None
        self.device_info: Optional[DeviceInfo] = None
        self.channel_configs: dict[str, ChannelConfig] = {}
        self.chandle: Optional[ctypes.c_int16] = None
        self.status: dict[str, Any] = {}

    def discover_devices(self) -> list[dict[str, Any]]:
        """Discover all connected PicoScope devices.

        Returns:
            List of discovered devices with their information.
        """
        if not PICOSDK_AVAILABLE:
            return []

        try:
            devices = find_all_units()
            device_list = []

            for scope in devices:
                device_list.append(
                    {
                        "info": str(scope.info),
                        "variant": getattr(scope, "variant", "unknown"),
                    }
                )
                scope.close()

            return device_list
        except Exception as e:
            return []

    def connect(self, device_index: int = 0, serial: Optional[str] = None) -> bool:
        """Connect to a PicoScope 5000A device.

        Args:
            device_index: Index of device to connect to (0 for first device).
            serial: Optional serial number string for specific device.

        Returns:
            True if connection successful, False otherwise.
        """
        if not PICOSDK_AVAILABLE:
            return False

        try:
            # Create handle for PS5000A
            self.chandle = ctypes.c_int16()

            # Set resolution (12-bit default)
            resolution = ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]

            # Convert serial to bytes if provided
            serial_bytes = serial.encode() if serial else None

            # Open the device
            self.status["openunit"] = ps.ps5000aOpenUnit(
                ctypes.byref(self.chandle), serial_bytes, resolution
            )

            # Handle power status issues
            try:
                assert_pico_ok(self.status["openunit"])
            except:
                power_status = self.status["openunit"]
                # Power status codes: 286 = USB3.0 powered, 282 = needs external power
                if power_status in [286, 282]:
                    self.status["changePowerSource"] = ps.ps5000aChangePowerSource(
                        self.chandle, power_status
                    )
                    assert_pico_ok(self.status["changePowerSource"])
                else:
                    raise

            # Get device info
            info_string = ctypes.create_string_buffer(256)
            required_size = ctypes.c_int16(256)

            # Get variant info
            self.status["getUnitInfo"] = ps.ps5000aGetUnitInfo(
                self.chandle,
                ctypes.byref(info_string),
                ctypes.c_int16(256),
                ctypes.byref(required_size),
                ps.PICO_INFO["PICO_VARIANT_INFO"]
            )
            variant = info_string.value.decode('utf-8')

            # Get batch and serial
            self.status["getUnitInfo"] = ps.ps5000aGetUnitInfo(
                self.chandle,
                ctypes.byref(info_string),
                ctypes.c_int16(256),
                ctypes.byref(required_size),
                ps.PICO_INFO["PICO_BATCH_AND_SERIAL"]
            )
            batch_serial = info_string.value.decode('utf-8')

            # Store device information
            self.device_info = DeviceInfo(
                handle=self.chandle.value,
                model="PS5000A",
                serial=batch_serial,
                variant=variant,
                batch_and_serial=batch_serial,
                max_adc_value=32767,  # 15-bit for PS5000A
                min_adc_value=-32767,
                num_channels=4,  # PS5000A has 4 channels
            )

            return True
        except Exception as e:
            self.chandle = None
            self.device_info = None
            return False

    def disconnect(self) -> bool:
        """Disconnect from current device.

        Returns:
            True if disconnection successful, False otherwise.
        """
        try:
            if self.chandle:
                # Stop any running capture
                ps.ps5000aStop(self.chandle)
                # Close the unit
                ps.ps5000aCloseUnit(self.chandle)
                self.chandle = None
                self.current_device = None
                self.device_info = None
                self.channel_configs.clear()
                self.status.clear()
            return True
        except Exception as e:
            return False

    def is_connected(self) -> bool:
        """Check if a device is currently connected.

        Returns:
            True if connected, False otherwise.
        """
        return self.current_device is not None

    def get_info(self) -> Optional[DeviceInfo]:
        """Get information about the current device.

        Returns:
            DeviceInfo object or None if not connected.
        """
        return self.device_info

    def configure_channel(self, config: ChannelConfig) -> bool:
        """Configure a channel.

        Args:
            config: Channel configuration.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_connected():
            return False

        try:
            # Map channel letter to PS5000A channel constant
            channel_map = {
                "A": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                "B": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"],
                "C": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_C"],
                "D": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_D"],
            }

            if config.channel not in channel_map:
                return False

            # Map coupling type
            coupling = (
                ps.PS5000A_COUPLING["PS5000A_AC"]
                if config.coupling.value == "AC"
                else ps.PS5000A_COUPLING["PS5000A_DC"]
            )

            # Map voltage range to closest available range
            range_map = {
                0.02: "PS5000A_20MV",
                0.05: "PS5000A_50MV",
                0.1: "PS5000A_100MV",
                0.2: "PS5000A_200MV",
                0.5: "PS5000A_500MV",
                1.0: "PS5000A_1V",
                2.0: "PS5000A_2V",
                5.0: "PS5000A_5V",
                10.0: "PS5000A_10V",
                20.0: "PS5000A_20V",
            }

            # Find closest range
            closest_range = min(range_map.keys(), key=lambda x: abs(x - config.voltage_range))
            voltage_range = ps.PS5000A_RANGE[range_map[closest_range]]

            # Convert analog offset to ADC counts
            if self.device_info:
                analog_offset_adc = mV2adc(
                    config.analog_offset * 1000,  # V to mV
                    voltage_range,
                    self.device_info.max_adc_value
                )
            else:
                analog_offset_adc = 0

            # Set the channel
            self.status[f"setCh{config.channel}"] = ps.ps5000aSetChannel(
                self.chandle,
                channel_map[config.channel],
                1 if config.enabled else 0,
                coupling,
                voltage_range,
                analog_offset_adc
            )

            assert_pico_ok(self.status[f"setCh{config.channel}"])

            # Store configuration
            self.channel_configs[config.channel] = config
            return True

        except Exception as e:
            return False

    def set_trigger(self, config: TriggerConfig) -> bool:
        """Set up trigger.

        Args:
            config: Trigger configuration.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_connected():
            return False

        try:
            # Map source to channel
            source_map = {
                "A": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                "B": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"],
                "C": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_C"],
                "D": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_D"],
                "External": ps.PS5000A_CHANNEL["PS5000A_EXTERNAL"],
            }

            if config.source not in source_map:
                return False

            # Map trigger direction
            direction_map = {
                "Rising": ps.PS5000A_THRESHOLD_DIRECTION["PS5000A_RISING"],
                "Falling": ps.PS5000A_THRESHOLD_DIRECTION["PS5000A_FALLING"],
                "Rising_Or_Falling": ps.PS5000A_THRESHOLD_DIRECTION[
                    "PS5000A_RISING_OR_FALLING"
                ],
            }

            direction = direction_map[config.direction.value]

            # Convert threshold from mV to ADC counts
            # Use the configured range for the source channel if available
            if config.source in self.channel_configs:
                ch_config = self.channel_configs[config.source]
                range_map = {
                    0.02: "PS5000A_20MV",
                    0.05: "PS5000A_50MV",
                    0.1: "PS5000A_100MV",
                    0.2: "PS5000A_200MV",
                    0.5: "PS5000A_500MV",
                    1.0: "PS5000A_1V",
                    2.0: "PS5000A_2V",
                    5.0: "PS5000A_5V",
                    10.0: "PS5000A_10V",
                    20.0: "PS5000A_20V",
                }
                closest_range = min(
                    range_map.keys(), key=lambda x: abs(x - ch_config.voltage_range)
                )
                voltage_range = ps.PS5000A_RANGE[range_map[closest_range]]
            else:
                voltage_range = ps.PS5000A_RANGE["PS5000A_2V"]  # Default

            threshold_adc = mV2adc(
                config.threshold_mv,
                voltage_range,
                self.device_info.max_adc_value if self.device_info else 32767,
            )

            # Set simple trigger
            self.status["trigger"] = ps.ps5000aSetSimpleTrigger(
                self.chandle,
                1,  # Enable trigger
                source_map[config.source],
                threshold_adc,
                direction,
                0,  # Delay (samples)
                config.auto_trigger_ms,  # Auto-trigger timeout
            )

            assert_pico_ok(self.status["trigger"])
            return True

        except Exception as e:
            return False

    def capture_block(
        self, pre_trigger: int, post_trigger: int
    ) -> Optional[dict[str, CaptureData]]:
        """Capture a block of data.

        Args:
            pre_trigger: Number of samples before trigger.
            post_trigger: Number of samples after trigger.

        Returns:
            Dictionary of channel data or None if failed.
        """
        if not self.is_connected():
            return None

        try:
            total_samples = pre_trigger + post_trigger

            # Set up buffers for enabled channels
            buffers = {}
            channel_map = {
                "A": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                "B": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"],
                "C": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_C"],
                "D": ps.PS5000A_CHANNEL["PS5000A_CHANNEL_D"],
            }

            for ch_name, ch_config in self.channel_configs.items():
                if ch_config.enabled:
                    # Create buffer
                    buffer = (ctypes.c_int16 * total_samples)()
                    buffers[ch_name] = buffer

                    # Set data buffer
                    self.status[f"setDataBuffer{ch_name}"] = ps.ps5000aSetDataBuffer(
                        self.chandle,
                        channel_map[ch_name],
                        ctypes.byref(buffer),
                        total_samples,
                        0,  # Segment index
                        ps.PS5000A_RATIO_MODE["PS5000A_RATIO_MODE_NONE"],
                    )
                    assert_pico_ok(self.status[f"setDataBuffer{ch_name}"])

            # Get timebase - using timebase 0 for fastest sampling
            timebase = 0
            time_interval_ns = ctypes.c_float()
            max_samples = ctypes.c_int32()

            self.status["getTimebase"] = ps.ps5000aGetTimebase2(
                self.chandle,
                timebase,
                total_samples,
                ctypes.byref(time_interval_ns),
                ctypes.byref(max_samples),
                0,  # Segment index
            )

            # If timebase 0 doesn't work, try higher values
            while self.status["getTimebase"] != 0 and timebase < 100:
                timebase += 1
                self.status["getTimebase"] = ps.ps5000aGetTimebase2(
                    self.chandle,
                    timebase,
                    total_samples,
                    ctypes.byref(time_interval_ns),
                    ctypes.byref(max_samples),
                    0,
                )

            assert_pico_ok(self.status["getTimebase"])

            # Run block capture
            self.status["runBlock"] = ps.ps5000aRunBlock(
                self.chandle,
                pre_trigger,
                post_trigger,
                timebase,
                None,  # Time indisposed (not used)
                0,  # Segment index
                None,  # Callback (not used, we'll poll)
                None,  # Callback parameter
            )
            assert_pico_ok(self.status["runBlock"])

            # Wait for capture to complete
            ready = ctypes.c_int16(0)
            check = ctypes.c_int16(0)
            while ready.value == check.value:
                self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(ready))

            # Get values
            overflow = ctypes.c_int16()
            c_total_samples = ctypes.c_int32(total_samples)

            self.status["getValues"] = ps.ps5000aGetValues(
                self.chandle,
                0,  # Start index
                ctypes.byref(c_total_samples),
                1,  # Downsampling ratio
                ps.PS5000A_RATIO_MODE["PS5000A_RATIO_MODE_NONE"],
                0,  # Segment index
                ctypes.byref(overflow),
            )
            assert_pico_ok(self.status["getValues"])

            # Convert ADC values to mV and create CaptureData objects
            result = {}
            time_values = np.arange(total_samples) * (time_interval_ns.value / 1e9)  # Convert to seconds

            for ch_name, buffer in buffers.items():
                ch_config = self.channel_configs[ch_name]

                # Get voltage range
                range_map = {
                    0.02: "PS5000A_20MV", 0.05: "PS5000A_50MV", 0.1: "PS5000A_100MV",
                    0.2: "PS5000A_200MV", 0.5: "PS5000A_500MV", 1.0: "PS5000A_1V",
                    2.0: "PS5000A_2V", 5.0: "PS5000A_5V", 10.0: "PS5000A_10V",
                    20.0: "PS5000A_20V",
                }
                closest_range = min(range_map.keys(), key=lambda x: abs(x - ch_config.voltage_range))
                voltage_range = ps.PS5000A_RANGE[range_map[closest_range]]

                # Convert to numpy array
                adc_array = np.array(buffer)

                # Convert ADC to mV
                voltage_mv = adc2mV(
                    adc_array,
                    voltage_range,
                    self.device_info.max_adc_value if self.device_info else 32767,
                )

                result[ch_name] = CaptureData(
                    channel=ch_name,
                    time_values=time_values.tolist(),
                    voltage_values=voltage_mv.tolist(),
                    sample_interval_ns=int(time_interval_ns.value),
                    num_samples=total_samples,
                )

            return result

        except Exception as e:
            return None

    def start_streaming(
        self, sample_interval_ns: int, buffer_size: int
    ) -> bool:
        """Start streaming mode.

        Args:
            sample_interval_ns: Sample interval in nanoseconds.
            buffer_size: Buffer size for streaming.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_connected():
            return False

        # TODO: Implement streaming mode
        # This will need to set up buffers and call ps*RunStreaming

        return True

    def stop_streaming(self) -> bool:
        """Stop streaming mode.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_connected():
            return False

        # TODO: Implement streaming stop
        # Call ps*Stop

        return True


# Global instance of the device manager
device_manager = PicoScopeManager()
