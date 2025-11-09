import unittest
import tempfile
from pathlib import Path
from configparser import ConfigParser

# Mock the decky plugin, I don't need to test it
import sys
from unittest import mock
sys.modules['decky'] = mock.MagicMock()

from main import (
    MangoHudConfigEditor,
    MANGOHUD_DEFAULT_PRESET_NUMBER,
    MANGOHUD_DEFAILT_PRESET_KEY_VALUES,
    MANGOHUD_DEFAULT_PRESET_FLAGS,
)


class TestMangoHudConfigEditorDefault(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = Path(self.temp_dir) / "presets.conf"
        self.editor = MangoHudConfigEditor(path=self.test_config_path)

    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir)

    def _read_config(self):
        """Helper method to read and parse the config file."""
        config = ConfigParser(allow_no_value=True, interpolation=None, delimiters=("=",))
        config.optionxform = str  # case-sensitive keys
        with self.test_config_path.open("r", encoding="utf-8") as f:
            config.read_file(f)
        return config

    def test_upsert_mangohud_preset_default_behavior(self):
        """Test that upsert_mangohud_preset creates a preset with default values."""
        # Call the method with all default parameters
        self.editor.upsert_mangohud_preset()

        # Verify the file was created
        self.assertTrue(self.test_config_path.exists())

        # Read the config file and verify the content
        config = self._read_config()

        # Check that the default preset section exists
        preset_section = f"preset {MANGOHUD_DEFAULT_PRESET_NUMBER}"
        self.assertTrue(config.has_section(preset_section))

        # Verify all default key-value pairs
        for key, expected_value in MANGOHUD_DEFAILT_PRESET_KEY_VALUES.items():
            self.assertTrue(config.has_option(preset_section, key))
            actual_value = config.get(preset_section, key)
            self.assertEqual(actual_value, str(expected_value))

        # Verify all default flags (keys with no value)
        for flag in MANGOHUD_DEFAULT_PRESET_FLAGS:
            self.assertTrue(config.has_option(preset_section, flag))
            # Flags should have None as value
            self.assertIsNone(config.get(preset_section, flag))

    def test_upsert_mangohud_preset_custom_preset_number(self):
        """Test upsert with custom preset number."""
        self.editor.upsert_mangohud_preset(preset=2)

        config = self._read_config()
        preset_section = "preset 2"

        # Verify the correct preset section was created
        self.assertTrue(config.has_section(preset_section))

        # Verify default values are still used
        for key, expected_value in MANGOHUD_DEFAILT_PRESET_KEY_VALUES.items():
            self.assertEqual(config.get(preset_section, key), str(expected_value))

        for flag in MANGOHUD_DEFAULT_PRESET_FLAGS:
            self.assertTrue(config.has_option(preset_section, flag))

    def test_upsert_mangohud_preset_custom_kv(self):
        """Test upsert with custom key-value pairs."""
        custom_kv = {"custom_kv": 2137}
        self.editor.upsert_mangohud_preset(kv=custom_kv)

        config = self._read_config()
        preset_section = f"preset {MANGOHUD_DEFAULT_PRESET_NUMBER}"

        # Verify custom key-value is set
        self.assertTrue(config.has_option(preset_section, "custom_kv"))
        self.assertEqual(config.get(preset_section, "custom_kv"), "2137")

        # Verify default flags are still used
        for flag in MANGOHUD_DEFAULT_PRESET_FLAGS:
            self.assertTrue(config.has_option(preset_section, flag))

    def test_upsert_mangohud_preset_custom_flags(self):
        """Test upsert with custom flags."""
        custom_flags = ["custom_flag"]
        self.editor.upsert_mangohud_preset(flags=custom_flags)

        config = self._read_config()
        preset_section = f"preset {MANGOHUD_DEFAULT_PRESET_NUMBER}"

        # Verify custom flag is set
        self.assertTrue(config.has_option(preset_section, "custom_flag"))
        self.assertIsNone(config.get(preset_section, "custom_flag"))

        # Verify default key-values are still used
        for key, expected_value in MANGOHUD_DEFAILT_PRESET_KEY_VALUES.items():
            self.assertEqual(config.get(preset_section, key), str(expected_value))

    def test_upsert_mangohud_preset_remove_key(self):
        """Test upsert with remove parameter to remove a specific key."""
        # First create a preset with defaults
        self.editor.upsert_mangohud_preset()

        # Now remove the 'alpha' key
        self.editor.upsert_mangohud_preset(remove=["alpha"])

        config = self._read_config()
        preset_section = f"preset {MANGOHUD_DEFAULT_PRESET_NUMBER}"

        # Verify 'alpha' was removed
        self.assertFalse(config.has_option(preset_section, "alpha"))

        # Verify other default keys still exist
        self.assertTrue(config.has_option(preset_section, "background_alpha"))
        self.assertTrue(config.has_option(preset_section, "time_format"))

        # Verify flags still exist
        for flag in MANGOHUD_DEFAULT_PRESET_FLAGS:
            self.assertTrue(config.has_option(preset_section, flag))

    def test_upsert_mangohud_clear_preset_first(self):
        """Test upsert with clear_preset_first=True to clear all existing options."""
        # First create a preset with defaults
        self.editor.upsert_mangohud_preset()

        # Now remove all and add only custom values
        custom_kv = {"new_key": "new_value"}
        custom_flags = ["new_flag"]
        self.editor.upsert_mangohud_preset(
            kv=custom_kv,
            flags=custom_flags,
            clear_preset_first=True
        )

        config = self._read_config()
        preset_section = f"preset {MANGOHUD_DEFAULT_PRESET_NUMBER}"

        # Verify that only new things are present
        self.assertTrue(config.has_option(preset_section, "new_key"))
        self.assertEqual(config.get(preset_section, "new_key"), "new_value")
        self.assertTrue(config.has_option(preset_section, "new_flag"))

        # Verify old defaults don't exist
        self.assertFalse(config.has_option(preset_section, "alpha"))
        self.assertFalse(config.has_option(preset_section, "background_alpha"))
        self.assertFalse(config.has_option(preset_section, "time"))

    def test_upsert_mangohud_preset_combination(self):
        """Test upsert with combination of custom preset, kv, flags, and remove."""
        custom_preset = 5
        custom_kv = {"custom_kv": 2137, "another_key": 420}
        custom_flags = ["custom_flag", "another_flag"]

        # First create with defaults to have something to remove
        self.editor.upsert_mangohud_preset(preset=custom_preset)

        # Now update with custom values and remove alpha
        self.editor.upsert_mangohud_preset(
            preset=custom_preset,
            kv=custom_kv,
            flags=custom_flags,
            remove=["alpha"]
        )

        config = self._read_config()
        preset_section = f"preset {custom_preset}"

        # Verify custom preset number
        self.assertTrue(config.has_section(preset_section))

        # Verify custom key-values
        self.assertEqual(config.get(preset_section, "custom_kv"), "2137")
        self.assertEqual(config.get(preset_section, "another_key"), "420")

        # Verify custom flags
        self.assertTrue(config.has_option(preset_section, "custom_flag"))
        self.assertTrue(config.has_option(preset_section, "another_flag"))
        self.assertIsNone(config.get(preset_section, "custom_flag"))
        self.assertIsNone(config.get(preset_section, "another_flag"))

        # Verify 'alpha' was removed
        self.assertFalse(config.has_option(preset_section, "alpha"))

        # Verify other default values still exist (from first call)
        self.assertTrue(config.has_option(preset_section, "background_alpha"))


    def test_get_current_preset_data(self):
        """Test get_current_preset_data retrieves the correct data."""
        preset_number = 3
        # First create a preset with defaults
        self.editor.upsert_mangohud_preset(preset=preset_number)

        # Retrieve the preset data
        preset_data = self.editor.get_current_preset_data(preset=preset_number)

        # Verify all default key-value pairs are present
        for key, expected_value in MANGOHUD_DEFAILT_PRESET_KEY_VALUES.items():
            self.assertIn(key, preset_data)
            self.assertEqual(preset_data[key], str(expected_value))

        # Verify all default flags are present with None value
        for flag in MANGOHUD_DEFAULT_PRESET_FLAGS:
            self.assertIn(flag, preset_data)
            self.assertIsNone(preset_data[flag])


if __name__ == "__main__":
    unittest.main()