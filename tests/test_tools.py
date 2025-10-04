"""Tests for PicoScope MCP tools."""

import pytest
from picoscope_mcp.device_manager import PicoScopeManager


def test_device_manager_initialization():
    """Test device manager can be initialized."""
    manager = PicoScopeManager()
    assert manager is not None
    assert not manager.is_connected()


def test_discover_devices():
    """Test device discovery (may return empty list if no devices)."""
    manager = PicoScopeManager()
    devices = manager.discover_devices()
    assert isinstance(devices, list)


# Note: Most tests will require actual hardware to be connected
# These are just basic structure tests
