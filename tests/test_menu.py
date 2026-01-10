"""Unit tests for MainMenu."""

import unittest
from unittest.mock import MagicMock

from src.models.menu import MainMenu


class TestMainMenu(unittest.TestCase):
    """Tests for the MainMenu class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.renderer = MagicMock()
        self.window_config = {"width": 800, "height": 600}
        self.menu = MainMenu(self.renderer, self.window_config)

    def test_initial_visibility(self) -> None:
        """Test that menu is visible by default."""
        self.assertTrue(self.menu.is_visible())

    def test_initial_selection(self) -> None:
        """Test that first option is selected by default."""
        self.assertEqual(self.menu.get_selected_option(), 0)

    def test_navigate_down(self) -> None:
        """Test navigating down through menu options."""
        self.menu.handle_key("Down")
        self.assertEqual(self.menu.get_selected_option(), 1)

    def test_navigate_up(self) -> None:
        """Test navigating up through menu options."""
        self.menu.handle_key("Down")  # Go to option 1
        self.menu.handle_key("Up")  # Go back to option 0
        self.assertEqual(self.menu.get_selected_option(), 0)

    def test_wrap_around_down(self) -> None:
        """Test that navigation wraps around at the bottom."""
        self.menu.handle_key("Down")  # Go to option 1
        self.menu.handle_key("Down")  # Wrap to option 0
        self.assertEqual(self.menu.get_selected_option(), 0)

    def test_wrap_around_up(self) -> None:
        """Test that navigation wraps around at the top."""
        self.menu.handle_key("Up")  # Wrap to last option
        self.assertEqual(self.menu.get_selected_option(), 1)

    def test_select_option_hides_menu(self) -> None:
        """Test that selecting an option hides the menu."""
        self.menu.handle_key("Return")
        self.assertFalse(self.menu.is_visible())

    def test_selection_callback_called(self) -> None:
        """Test that selection callback is called when option is selected."""
        callback = MagicMock()
        self.menu.on_selection = callback
        self.menu.handle_key("Return")
        callback.assert_called_once_with(0)

    def test_hide_show(self) -> None:
        """Test hide and show methods."""
        self.menu.hide()
        self.assertFalse(self.menu.is_visible())
        self.menu.show()
        self.assertTrue(self.menu.is_visible())

    def test_handle_key_returns_true_on_selection(self) -> None:
        """Test that handle_key returns True when selection is made."""
        result = self.menu.handle_key("Return")
        self.assertTrue(result)

    def test_handle_key_returns_false_on_navigation(self) -> None:
        """Test that handle_key returns False on navigation."""
        result = self.menu.handle_key("Down")
        self.assertFalse(result)

    def test_handle_key_with_none(self) -> None:
        """Test that handle_key handles None gracefully."""
        result = self.menu.handle_key(None)
        self.assertFalse(result)

    def test_handle_key_with_empty_string(self) -> None:
        """Test that handle_key handles empty string gracefully."""
        result = self.menu.handle_key("")
        self.assertFalse(result)

    def test_handle_key_when_not_visible(self) -> None:
        """Test that handle_key does nothing when menu is hidden."""
        self.menu.hide()
        result = self.menu.handle_key("Return")
        self.assertFalse(result)

    def test_handle_unknown_key(self) -> None:
        """Test that unknown keys don't crash or change selection."""
        initial_selection = self.menu.get_selected_option()
        result = self.menu.handle_key("x")
        self.assertEqual(self.menu.get_selected_option(), initial_selection)
        self.assertFalse(result)

    def test_menu_options_count(self) -> None:
        """Test that menu has two options (single and two player)."""
        self.assertEqual(len(self.menu.menu_options), 2)

    def test_menu_constants(self) -> None:
        """Test menu option constants."""
        self.assertEqual(MainMenu.MENU_SINGLE_PLAYER, 0)
        self.assertEqual(MainMenu.MENU_TWO_PLAYER, 1)


if __name__ == "__main__":
    unittest.main()
