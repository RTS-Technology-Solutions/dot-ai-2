"""
configs/__init__.py — Config Singleton
======================================
Provides a module-level config object shared across all core systems.

Usage:
    # In main.py (before starting simulation):
    from configs import set_config
    from configs.profiles import PROFILES
    set_config(PROFILES["default"])

    # In any core module:
    from configs import get_config
    cfg = get_config()
    speed = cfg.behavior.movement_speed_base
"""

from .simulation_config import SimulationConfig

_config: SimulationConfig = SimulationConfig()


def get_config() -> SimulationConfig:
    """Return the active simulation configuration."""
    return _config


def set_config(config: SimulationConfig) -> None:
    """
    Replace the active configuration.

    Call this once in main.py before the simulation starts.
    Changes take effect on the next frame — supports live profile swapping.
    """
    global _config
    if not isinstance(config, SimulationConfig):
        raise TypeError(f"set_config expects a SimulationConfig, got {type(config)}")
    _config = config
