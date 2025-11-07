import unittest
import tempfile
from pathlib import Path
from configparser import ConfigParser

from mangohud import (
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

    def test_upsert_mangohud_preset_default_behavior(self):
        """Test that upsert_mangohud_preset creates a preset with default values."""
        # Call the method with all default parameters
        self.editor.upsert_mangohud_preset()

        # Verify the file was created
        self.assertTrue(self.test_config_path.exists())

        # Read the config file and verify the content
        config = ConfigParser(allow_no_value=True, interpolation=None, delimiters=("=",))
        config.optionxform = str  # case-sensitive keys
        with self.test_config_path.open("r", encoding="utf-8") as f:
            config.read_file(f)

        # Check that the default preset section exists
        preset_section = f"[preset {MANGOHUD_DEFAULT_PRESET_NUMBER}]"
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


if __name__ == "__main__":
    unittest.main()