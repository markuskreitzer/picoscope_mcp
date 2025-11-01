# PicoScope MCP Server

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.x-green.svg)](https://github.com/jlowin/fastmcp)

A STDIO MCP server that enables LLMs like Claude to interact with PicoScope oscilloscopes for signal acquisition, measurement, and analysis. Built with FastMCP and the official PicoSDK Python bindings.

<a href="https://glama.ai/mcp/servers/@markuskreitzer/picoscope_mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@markuskreitzer/picoscope_mcp/badge" alt="PicoScope Server MCP server" />
</a>

## Features

- **Device Management**: Auto-discover and connect to PicoScope devices
- **Channel Configuration**: Set voltage ranges, coupling, and offsets
- **Data Acquisition**: Block capture and streaming modes
- **Triggering**: Simple and advanced trigger configurations
- **Measurements**: Frequency, amplitude, rise time, FFT, THD, and more
- **Signal Generation**: Control built-in arbitrary waveform generator
- **AI-Native**: Designed for natural language control via Claude and other LLMs

## Quick Start

```bash
# Clone the repository
git clone https://github.com/markuskreitzer/picoscope_mcp.git
cd picoscope_mcp

# Install dependencies (requires uv package manager)
uv sync

# Run the MCP server
uv run picoscope-mcp
```

The server runs in STDIO mode and is ready to communicate with MCP clients like Claude Desktop.

## Installation

### Prerequisites

1. **PicoSDK C Libraries** (required for hardware operation)
   - **Windows**: Download from [PicoTech Downloads](https://www.picotech.com/downloads)
   - **macOS**: Download PicoScope software package
   - **Linux**: Install via package manager:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install libps5000a libps4000a libps3000a libps2000a
     ```

2. **Python 3.11+** with uv package manager

### Install Dependencies

```bash
# Clone or navigate to the project directory
cd picoscope_mcp

# Install dependencies
uv sync
```

## Usage

### Running the Server

```bash
uv run picoscope-mcp
```

The server runs in STDIO mode, communicating via standard input/output for use with MCP-compatible clients.

### Using with Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "picoscope": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/picoscope_mcp",
        "run",
        "picoscope-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop, and you'll see the PicoScope tools available in the MCP menu.

### Testing Without Hardware

The server will run even without PicoScope hardware connected, though device operations will fail until:
1. PicoSDK C libraries are installed
2. A PicoScope device is connected

## MCP Tools

### Discovery & Connection

| Tool | Description |
|------|-------------|
| `list_devices` | Find all connected PicoScope devices |
| `connect_device` | Connect to a specific device (by serial) or first available |
| `get_device_info` | Get details about connected device |
| `disconnect_device` | Disconnect from current device |

### Channel Configuration

| Tool | Description |
|------|-------------|
| `configure_channel` | Set channel parameters (range, coupling, offset) |
| `get_channel_config` | Query current channel settings |
| `set_timebase` | Configure sampling rate (informational) |

### Triggering

| Tool | Description |
|------|-------------|
| `set_simple_trigger` | Configure edge trigger (rising/falling/both) |

### Data Acquisition

| Tool | Description |
|------|-------------|
| `capture_block` | Single snapshot capture with pre/post trigger samples |
| `start_streaming` | Begin continuous data capture |
| `stop_streaming` | End streaming mode |
| `get_streaming_data` | Retrieve latest streaming data |

### Analysis

| Tool | Description |
|------|-------------|
| `measure_frequency` | Calculate signal frequency |
| `measure_amplitude` | Measure voltage (pk-pk, RMS, etc.) |
| `measure_rise_time` | Edge timing analysis |
| `measure_pulse_width` | Pulse characteristics |
| `compute_fft` | Frequency domain analysis |
| `get_statistics` | Signal statistics (min/max/mean/std) |
| `measure_thd` | Total Harmonic Distortion |

### Advanced

| Tool | Description |
|------|-------------|
| `set_signal_generator` | Configure AWG output |
| `stop_signal_generator` | Disable signal generator |
| `configure_math_channel` | Channel operations (A+B, A-B, etc.) |
| `export_waveform` | Save data to file (CSV/JSON/NumPy) |
| `configure_downsampling` | Set downsampling mode |

## Example Usage with Claude

```
User: "Connect to the first PicoScope and measure the frequency on channel A"

Claude calls:
1. list_devices() -> finds available devices
2. connect_device() -> connects to first device
3. configure_channel(channel="A", enabled=true, voltage_range=5.0) -> enables channel A
4. set_simple_trigger(source="A", threshold_mv=0) -> sets auto-trigger
5. capture_block(pre_trigger_samples=1000, post_trigger_samples=1000) -> captures waveform
6. Returns captured data with time and voltage values

User can then analyze the returned data for frequency, or request additional captures.
```

## Configuration

### Typical Workflow

1. **Connect**: `connect_device()`
2. **Configure Channels**: `configure_channel()` for each channel
3. **Set Trigger**: `set_simple_trigger()`
4. **Capture**: `capture_block()` or `start_streaming()`
5. **Analyze**: Use measurement tools on captured data

### Supported Hardware

- **PS5000A Series** (primary support)
- **PS2000/3000/4000/6000 Series** (planned)

Currently optimized for PS5000A. Other series will require device-specific implementations.

## Development

### Project Structure

```
picoscope_mcp/
├── src/picoscope_mcp/
│   ├── server.py          # FastMCP server
│   ├── device_manager.py  # Device abstraction
│   ├── models.py          # Data structures
│   ├── utils.py           # Helper functions
│   └── tools/             # MCP tool implementations
│       ├── discovery.py
│       ├── configuration.py
│       ├── acquisition.py
│       ├── analysis.py
│       └── advanced.py
└── tests/
    └── test_tools.py
```

### Running Tests

```bash
uv run pytest
```

### Adding Support for New Device Series

1. Update `device_manager.py` to detect device series
2. Import appropriate picosdk module (e.g., `ps3000a`)
3. Map device-specific constants and API calls
4. Handle series-specific capabilities

## Troubleshooting

### "PicoSDK not found" Error

Install PicoSDK C libraries for your platform (see Prerequisites).

### "No device connected" Errors

1. Ensure PicoScope is connected via USB
2. Check device appears in system (Windows Device Manager, macOS System Information, Linux `lsusb`)
3. Verify PicoSDK drivers are installed
4. Try reconnecting the device

### Channel Configuration Fails

- Check voltage range is supported: 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20V
- Verify channel exists (A-D for 4-channel models)

### Capture Timeout

- Ensure trigger settings are appropriate for signal
- Try increasing auto-trigger timeout
- Check signal is within configured voltage range

## Roadmap

- [x] **Phase 1**: Foundation - Device discovery, connection, PS5000A support
- [ ] **Phase 2**: Advanced acquisition - Streaming mode, advanced triggers
- [ ] **Phase 3**: Multi-device support - PS2000/3000/4000/6000 series
- [ ] **Phase 4**: Enhanced analysis - Real-time FFT, automated characterization
- [ ] **Phase 5**: Visualization - Web dashboard for waveform viewing

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed architecture and development plans.

## Contributing

Contributions are welcome! This project is in active development.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/picoscope_mcp.git
cd picoscope_mcp

# Install dependencies including dev tools
uv sync

# Run tests
uv run pytest
```

### Areas for Contribution

- Support for additional PicoScope series (PS2000, PS3000, PS4000, PS6000)
- Streaming mode implementation
- Advanced trigger modes (pulse width, window, logic)
- Additional measurement algorithms
- Documentation and examples
- Test coverage
- Bug reports and fixes

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**Note**: This license allows commercial use but requires derivative works to remain open source under GPLv3.

## Acknowledgments

- **Pico Technology** for the [PicoSDK Python wrappers](https://github.com/picotech/picosdk-python-wrappers)
- **Anthropic** for the [Model Context Protocol](https://modelcontextprotocol.io/)
- **Jeff Lowin** for [FastMCP](https://github.com/jlowin/fastmcp)
- The open source community

## References

- [PicoScope Programmers Guides](https://www.picotech.com/library/oscilloscopes)
- [picosdk-python-wrappers](https://github.com/picotech/picosdk-python-wrappers)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Setup](https://docs.claude.com/en/docs/model-context-protocol)

## Contact

- **Issues**: [GitHub Issues](https://github.com/markuskreitzer/picoscope_mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/markuskreitzer/picoscope_mcp/discussions)