"""Configuration module for loading and managing game settings."""

import logging
import os
from typing import Any, Dict

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

DEFAULT_CONFIG: Dict[str, Dict[str, Any]] = {
    "window": {
        "width": 800,
        "height": 600,
    },
    "ball": {
        "radius": 0.02,
        "phi_resolution": 20,
        "theta_resolution": 20,
    },
    "paddle": {
        "x_length": 0.02,
        "y_length": 0.4,
        "z_length": 0.02,
    },
    "game": {
        "speed_increase_interval": 500,
        "speed_multiplier": 1.1,
    },
}


def create_default_config(config_file: str) -> None:
    """
    Create a default configuration file.

    Args:
        config_file: Path where the configuration file will be created.
    """
    with open(config_file, "w") as file:
        yaml.safe_dump(DEFAULT_CONFIG, file)
    logging.info(f"Default configuration file created at {config_file}")


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    If the configuration file doesn't exist, creates a default one.

    Args:
        config_file: Path to the configuration file.

    Returns:
        A dictionary containing the configuration settings.
    """
    if not os.path.exists(config_file):
        logging.warning(
            f"Configuration file {config_file} not found. Creating default configuration."
        )
        create_default_config(config_file)
        return DEFAULT_CONFIG

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
        logging.info(f"Configuration file {config_file} loaded successfully.")
        return config
