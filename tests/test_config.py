"""Unit tests for configuration module."""

import os
import tempfile
import unittest

from src.config.config import DEFAULT_CONFIG, create_default_config, load_config


class TestConfig(unittest.TestCase):
    """Tests for configuration loading and defaults."""

    def test_default_config_structure(self) -> None:
        """Test that default config has required sections."""
        self.assertIn("window", DEFAULT_CONFIG)
        self.assertIn("ball", DEFAULT_CONFIG)
        self.assertIn("paddle", DEFAULT_CONFIG)
        self.assertIn("game", DEFAULT_CONFIG)

    def test_default_config_window_values(self) -> None:
        """Test default window configuration values."""
        self.assertEqual(DEFAULT_CONFIG["window"]["width"], 800)
        self.assertEqual(DEFAULT_CONFIG["window"]["height"], 600)

    def test_default_config_ball_values(self) -> None:
        """Test default ball configuration values."""
        self.assertEqual(DEFAULT_CONFIG["ball"]["radius"], 0.02)
        self.assertEqual(DEFAULT_CONFIG["ball"]["phi_resolution"], 20)
        self.assertEqual(DEFAULT_CONFIG["ball"]["theta_resolution"], 20)

    def test_default_config_paddle_values(self) -> None:
        """Test default paddle configuration values."""
        self.assertEqual(DEFAULT_CONFIG["paddle"]["x_length"], 0.02)
        self.assertEqual(DEFAULT_CONFIG["paddle"]["y_length"], 0.4)
        self.assertEqual(DEFAULT_CONFIG["paddle"]["z_length"], 0.02)

    def test_default_config_game_values(self) -> None:
        """Test default game configuration values."""
        self.assertEqual(DEFAULT_CONFIG["game"]["speed_increase_interval"], 500)
        self.assertEqual(DEFAULT_CONFIG["game"]["speed_multiplier"], 1.1)
        self.assertEqual(DEFAULT_CONFIG["game"]["win_score"], 11)
        self.assertFalse(DEFAULT_CONFIG["game"]["ai_enabled"])
        self.assertEqual(DEFAULT_CONFIG["game"]["default_difficulty"], "medium")

    def test_load_config_creates_default_when_missing(self) -> None:
        """Test that load_config creates default config when file is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test_config.yaml")
            config = load_config(config_path)

            self.assertTrue(os.path.exists(config_path))
            self.assertEqual(config, DEFAULT_CONFIG)

    def test_create_default_config_creates_file(self) -> None:
        """Test that create_default_config creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "new_config.yaml")
            create_default_config(config_path)

            self.assertTrue(os.path.exists(config_path))


if __name__ == "__main__":
    unittest.main()
