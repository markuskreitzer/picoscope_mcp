# PicoScope MCP Server - Project Plan

## Overview

This project implements a STDIO MCP (Model Context Protocol) server for controlling PicoScope oscilloscopes. It enables AI assistants to interact with PicoScope devices for signal acquisition, measurement, and analysis tasks.

## Technology Stack

- **Language**: Python 3.11+
- **Package Manager**: uv
- **MCP Framework**: FastMCP 2.x
- **Hardware SDK**: picosdk-python-wrappers (official Pico Technology bindings)
- **Signal Processing**: NumPy
- **Transport**: STDIO (Standard Input/Output)

## Architecture

### Layered Design

```
┌─────────────────────────────────────┐
│   MCP Tools (FastMCP decorators)    │
│  - Discovery, Config, Acquisition   │
│  - Analysis, Advanced operations    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Device Manager Layer           │
│  - Abstract PicoScope operations    │
│  - Handle device-specific APIs      │
│  - Manage connection lifecycle      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     PicoSDK Python Wrappers         │
│  - ps2000a, ps3000a, ps4000a, etc.  │
│  - Low-level ctypes bindings        │
└─────────────────────────────────────┘
```

### Core Components

1. **server.py** - FastMCP server initialization and tool registration
2. **device_manager.py** - Device abstraction layer
3. **tools/** - MCP tool implementations organized by category
4. **models.py** - Data structures and type definitions
5. **utils.py** - Helper functions for signal processing

## MCP Tools Design

### 1. Discovery & Connection Tools

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `list_devices` | Find connected PicoScopes | None | List of devices with info |
| `connect_device` | Open device connection | device_id (optional) | Connection status |
| `get_device_info` | Get device details | device_id (optional) | Model, serial, capabilities |
| `disconnect_device` | Close connection | device_id (optional) | Disconnection status |

### 2. Channel Configuration Tools

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `configure_channel` | Set channel parameters | channel, enabled, coupling, range, offset | Config status |
| `get_channel_config` | Query channel settings | channel | Current configuration |
| `set_timebase` | Configure sampling rate | sample_interval_ns, num_samples | Actual timebase applied |

### 3. Triggering Tools

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `set_simple_trigger` | Basic edge trigger | source, threshold, direction, auto_trigger | Trigger config status |
| `set_advanced_trigger` | Complex triggers | (future: pulse, window, logic) | Trigger config status |

### 4. Data Acquisition Tools

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `capture_block` | Single snapshot capture | pre_trigger, post_trigger samples | Waveform data |
| `start_streaming` | Begin continuous capture | interval, buffer_size, auto_stop | Streaming status |
| `stop_streaming` | End streaming | None | Stop status + summary |
| `get_streaming_data` | Retrieve stream data | max_samples | Latest waveform data |

### 5. Measurement & Analysis Tools

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `measure_frequency` | Calculate signal frequency | channel | Frequency in Hz |
| `measure_amplitude` | Voltage measurements | channel, type (pk-pk/rms/etc) | Voltage in mV |
| `measure_rise_time` | Edge timing | channel, thresholds | Rise time in seconds |
| `measure_pulse_width` | Pulse characteristics | channel, threshold | Pulse width in seconds |
| `compute_fft` | Frequency domain analysis | channel, window | Frequency spectrum |
| `get_statistics` | Signal statistics | channel, num_samples | Min/max/mean/std dev |
| `measure_thd` | Harmonic distortion | channel | THD percentage |

### 6. Advanced Operations

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `set_signal_generator` | Configure AWG output | waveform, freq, amplitude, offset | Generator status |
| `stop_signal_generator` | Disable AWG | None | Stop status |
| `configure_math_channel` | Channel math operations | operation, channel_a, channel_b | Math config |
| `export_waveform` | Save data to file | format, channels, filename | Export status |
| `configure_downsampling` | Set downsampling | mode, ratio | Downsample config |

## Implementation Phases

### Phase 1: Foundation ✓ (Current)
- [x] Project initialization with uv
- [x] FastMCP server setup with STDIO transport
- [x] Project structure and file organization
- [x] Basic data models and utilities
- [ ] Device discovery and connection management
- [ ] Single device support (PS5000A as reference)

### Phase 2: Basic Acquisition
- [ ] Channel configuration implementation
- [ ] Simple trigger setup
- [ ] Block mode capture with data conversion
- [ ] Basic measurements (voltage, frequency)
- [ ] Error handling and validation

### Phase 3: Advanced Acquisition
- [ ] Streaming mode implementation
- [ ] Advanced trigger modes
- [ ] FFT and frequency domain analysis
- [ ] Comprehensive measurements (rise time, THD, etc.)
- [ ] Signal statistics

### Phase 4: Multi-Device & Production
- [ ] Support for all PicoScope series (2000-6000)
- [ ] Series-specific API handling (ps2000a, ps3000a, etc.)
- [ ] Signal generator control
- [ ] Data export capabilities
- [ ] Production-ready error handling
- [ ] Documentation and examples

## PicoScope SDK Integration

### Supported Device Series

| Series | API | Typical Channels | Max Sample Rate | Notes |
|--------|-----|------------------|-----------------|-------|
| PS2000 | ps2000/ps2000a | 2-4 | 100-500 MS/s | Entry level |
| PS3000 | ps3000a | 2-4 | 200 MS/s - 1 GS/s | Mid-range |
| PS4000 | ps4000a | 4-8 | 80-500 MS/s | High resolution |
| PS5000 | ps5000a | 2-4 | 250 MS/s - 1 GS/s | Flexible resolution |
| PS6000 | ps6000a | 2-4 | 5 GS/s | High performance |

### API Pattern

All PicoScope series follow a similar API pattern:

1. **Device Discovery**: `find_all_units()` from picosdk.discover
2. **Open Device**: `ps[series]OpenUnit()`
3. **Configure Channels**: `ps[series]SetChannel()`
4. **Set Trigger**: `ps[series]SetSimpleTrigger()` or advanced variants
5. **Capture Data**:
   - Block: `ps[series]RunBlock()` + `ps[series]GetValues()`
   - Streaming: `ps[series]RunStreaming()` + `ps[series]GetStreamingLatestValues()`
6. **Close Device**: `ps[series]CloseUnit()`

### Data Flow

1. **Capture**: Device captures analog signal → ADC conversion → driver buffer
2. **Transfer**: Driver buffer → Python ctypes buffer → NumPy array
3. **Conversion**: ADC counts → Voltage (using range and max ADC value)
4. **Processing**: Apply measurements, FFT, statistics
5. **Return**: Structured data to LLM via MCP

## Error Handling Strategy

### Input Validation
- Use Pydantic models or type hints for parameter validation
- Validate channel identifiers against device capabilities
- Check voltage ranges against supported values
- Verify sample rates are achievable

### Device State Management
- Check connection status before operations
- Handle power source issues (USB vs. external power)
- Manage buffer allocation/deallocation
- Graceful cleanup on errors

### Error Communication
- Return structured error responses to LLM
- Include actionable error messages
- Suggest corrective actions when possible
- Log detailed errors for debugging

## Testing Strategy

### Unit Tests
- Device manager initialization
- Tool parameter validation
- Utility function correctness (ADC conversion, frequency calculation)
- Mock device operations

### Integration Tests
- Full capture workflow with real hardware
- Multi-channel acquisition
- Trigger functionality
- Streaming mode stability

### Hardware Requirements
- At least one PicoScope device for testing
- Signal generator for input signals
- Known test signals for measurement validation

## Configuration Management

### Device Capabilities Detection
```python
{
    "model": "PS5244D",
    "channels": 4,
    "max_sample_rate": 1_000_000_000,  # 1 GS/s
    "resolution_bits": [8, 12, 14, 15, 16],
    "voltage_ranges": [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20],
    "has_awg": true,
    "has_ets": true,  # Equivalent Time Sampling
    "max_buffer_size": 128_000_000
}
```

### Default Settings
- **Voltage Range**: Auto-select based on expected signal
- **Coupling**: DC (most common use case)
- **Trigger**: Auto-trigger at 1000ms timeout
- **Sample Rate**: Maximum sustainable rate for buffer size

## File Structure

```
picoscope_mcp/
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock file
├── README.md                   # Usage instructions
├── PROJECT_PLAN.md            # This document
├── src/
│   └── picoscope_mcp/
│       ├── __init__.py         # Package initialization
│       ├── server.py           # FastMCP server entry point
│       ├── device_manager.py   # Device abstraction layer
│       ├── models.py           # Data models
│       ├── utils.py            # Helper functions
│       └── tools/              # MCP tool implementations
│           ├── __init__.py
│           ├── discovery.py    # Connection tools
│           ├── configuration.py # Setup tools
│           ├── acquisition.py  # Capture tools
│           ├── analysis.py     # Measurement tools
│           └── advanced.py     # Signal gen, export, etc.
└── tests/
    └── test_tools.py          # Test suite
```

## Usage Example

### Starting the Server
```bash
# Install dependencies
uv sync

# Run the MCP server
uv run picoscope-mcp
```

### Example LLM Interaction
```
User: "Connect to the first available PicoScope and measure the frequency of the signal on channel A"

LLM calls:
1. list_devices() → finds devices
2. connect_device() → connects to first device
3. configure_channel(channel="A", enabled=true) → enables channel A
4. set_simple_trigger(source="A", threshold_mv=0) → sets auto-trigger
5. capture_block() → captures waveform
6. measure_frequency(channel="A") → returns 1000.5 Hz
```

## Development Roadmap

### Immediate Next Steps
1. Implement device discovery with picosdk.discover
2. Create device connection logic for PS5000A series
3. Implement basic channel configuration
4. Add simple trigger setup
5. Implement block mode capture with ADC→mV conversion

### Future Enhancements
- Web dashboard for visualization
- Real-time streaming display
- Advanced trigger patterns (pulse width, logic, serial)
- Multi-device simultaneous capture
- Automated signal characterization
- Machine learning-based signal classification

## Dependencies

### Required
- **fastmcp** (≥2.12.4): MCP server framework
- **picosdk** (≥1.1): Official PicoScope Python bindings
- **numpy** (≥2.3.3): Signal processing and array operations

### Development
- **pytest** (≥8.0.0): Testing framework

### System Requirements
- **PicoSDK C Libraries**: Platform-specific drivers
  - Windows: PicoSDK installer
  - Linux: libps* packages
  - macOS: PicoSDK frameworks

## Known Limitations

### Current Implementation
- Focus on PS5000A series initially
- Other series require device-specific adaptations
- Streaming mode uses simplified callback approach
- Limited to basic trigger modes initially

### Hardware Limitations
- Some older models lack certain features (AWG, advanced triggers)
- Maximum sample rate varies by model and channel count
- Buffer size constraints affect long captures
- USB bandwidth limits streaming throughput

### SDK Constraints
- Different API versions across series
- Some models have deprecated or unsupported features
- Platform-specific C library requirements

## Contributing Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints for all functions
- Document all MCP tools with clear descriptions
- Include parameter units in docstrings

### Testing Requirements
- Add tests for new tools
- Verify with real hardware when possible
- Include error case testing
- Document test setup requirements

### Documentation
- Update PROJECT_PLAN.md for architectural changes
- Keep README.md usage instructions current
- Document device-specific quirks
- Provide example interactions

## References

### Documentation
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [PicoSDK Python Wrappers](https://github.com/picotech/picosdk-python-wrappers)
- [PicoScope Programmer's Guides](https://www.picotech.com/library/oscilloscopes)

### Resources
- PicoScope API reference for each series
- Example code in picosdk-python-wrappers repository
- Community forums and support channels
- Signal processing fundamentals for measurements

---

**Status**: Phase 1 in progress
**Last Updated**: 2025-10-03
**Maintainer**: Markus Kreitzer
