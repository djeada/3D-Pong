"""Main entry point for the 3D Pong game."""

import logging
import os

from src.models.game import Game

# Configure logging at application level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main() -> None:
    """Initialize and start the 3D Pong game."""
    # Determine the correct path to the config file
    # This works both when running from the project root and from src directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config", "config.yaml")
    
    game = Game(config_path)
    game.initialize()
    game.start()


if __name__ == "__main__":
    main()
