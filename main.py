import os

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code repo
# and add the `decky-loader/plugin/imports` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky
import asyncio

# For some reason I can't extract the Python code to other file and import it
# here - plugin breaks

from pathlib import Path
from configparser import ConfigParser
import shutil

MANGOHUD_CONFIG_PATH = Path.home() / ".config" / "MangoHud" / "presets.conf"
MANGOHUD_CONFIG_PRESET_TEMPLATE = """
[preset {f_preset_number}]
alpha={f_alpha}
background_alpha={f_background_alpha}
time
time_no_label
time_format={f_time_format}
legacy_layout=false
horizontal
offset_y={f_offset_y}
offset_x={f_offset_x}
position={f_position}
"""

MANGOHUD_DEFAULT_PRESET_NUMBER = 3
MANGOHUD_DEFAILT_PRESET_KEY_VALUES = {
    "alpha": 1.0,
    "background_alpha": 0.0,
    "time_format": "%H:%M",
    "offset_y": -5,
    "offset_x": 1212,
    "position": "top-right",
}
MANGOHUD_DEFAULT_PRESET_FLAGS = [
    "time",
    "time_no_label",
    "legacy_layout",
    "horizontal",
]

class MangoHudConfigEditor:
    def __init__(self, path: Path = MANGOHUD_CONFIG_PATH):
        self.path = Path(path).expanduser()
        self._create_config_parser()

    def _create_config_parser(self) -> None:
        self.config_parser = ConfigParser(
            allow_no_value=True,
            interpolation=None,
            delimiters=("=",),  # MangoHud uses "=" as delimiter
        )
        self.config_parser.optionxform = str  # make keys case-sensitive

    def _create_presets_conf_if_doesnt_exist(self) -> None:
        if not self.path.exists():
            self.path.touch()

    def _create_presets_conf_dirs_parents(self) -> None:
        p = Path(self.path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)

    def _backup_existing_mangohud_config(self):
        p = Path(self.path).expanduser()
        if p.exists():
            shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))

    def _read_with_config_parser(self) -> None:
        with self.path.open("r", encoding="utf-8") as f:
            self.config_parser.read_file(f)

    def _add_section_if_not_exists(
        self,
        section: str
    ) -> None:
        if not self.config_parser.has_section(section):
            self.config_parser.add_section(section)

    def _delete_keys_and_flags(
        self,
        section: str,
        keys_and_flags: list[str],
    ) -> None:
        for k in keys_and_flags:
            if self.config_parser.has_option(section, k):
                self.config_parser.remove_option(section, k)

    def _set_key_values(
        self,
        section: str,
        kv: dict[str, str | int | float]
    ) -> None:
        for k, v in kv.items():
            self.config_parser.set(section, k, str(v))

    def _clear_preset(
        self,
        section: str
    ) -> None:
        for k in list(self.config_parser[section].keys()):
            self.config_parser.remove_option(section, k)

    def _set_flags(
        self,
        section: str,
        flags: list[str]
    ) -> None:
        for fl in flags:
            self.config_parser.set(section, fl, None)

    def _write_presets_conf(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            self.config_parser.write(f)

    def upsert_mangohud_preset(
        self,
        preset: int = 3,
        kv: dict[str, str | int | float] | None = None,
        flags: list[str] | None = None,
        remove: list[str] | None = None,
        clear_preset_first: bool = False,
    ):
        """Change or add a MangoHud preset in the config file.

        Args:
            path: Path to the MangoHud config file.
            preset: Preset number to add or update.
            kv: Key-value pairs to set in the preset.
            flags: List of flags (keys without values) to set in the preset.
            remove: List of keys/flags to remove from the preset.
            clear_preset_first: If True, clears all existing keys/flags in the preset before applying changes.
        """
        if kv is None:
            kv = MANGOHUD_DEFAILT_PRESET_KEY_VALUES
        if flags is None:
            flags = MANGOHUD_DEFAULT_PRESET_FLAGS
        if remove is None:
            remove = []

        self._create_presets_conf_dirs_parents()
        self._backup_existing_mangohud_config()
        self._create_presets_conf_if_doesnt_exist()
        self._read_with_config_parser()

        preset_header = f"preset {preset}"
        self._add_section_if_not_exists(preset_header)

        if clear_preset_first:
            self._clear_preset(preset_header)

        self._set_key_values(preset_header, kv)
        self._set_flags(preset_header, flags)
        self._delete_keys_and_flags(preset_header, remove)

        self._write_presets_conf()

    def delete_preset(
        self,
        preset: int = 3,
    ):
        """Delete a MangoHud preset from the config file.

        Args:
            preset: Preset number to delete.
        """
        self._create_presets_conf_dirs_parents()
        self._backup_existing_mangohud_config()
        self._create_presets_conf_if_doesnt_exist()
        self._read_with_config_parser()

        preset_header = f"preset {preset}"
        if self.config_parser.has_section(preset_header):
            self.config_parser.remove_section(preset_header)

        self._write_presets_conf()

    def get_current_preset_data(
        self,
        preset: int = 3,
    ) -> dict[str, str | None]:
        """Get the current key-value pairs and flags of a MangoHud preset.

        Args:
            preset: Preset number to retrieve.
        """
        self._create_presets_conf_dirs_parents()
        self._create_presets_conf_if_doesnt_exist()
        self._read_with_config_parser()

        preset_header = f"preset {preset}"
        if not self.config_parser.has_section(preset_header):
            return {}

        preset_data: dict[str, str | None] = {}
        for k in self.config_parser[preset_header].keys():
            preset_data[k] = self.config_parser.get(preset_header, k)

        return preset_data

    def preset_data_is_empty(
        self,
        preset: int = 3,
    ) -> bool:
        """Check if a MangoHud preset is empty (has no keys or flags).

        Args:
            preset: Preset number to check.
        """
        self._create_presets_conf_dirs_parents()
        self._create_presets_conf_if_doesnt_exist()
        self._read_with_config_parser()

        preset_header = f"preset {preset}"
        if not self.config_parser.has_section(preset_header):
            return True

        return len(self.config_parser[preset_header].keys()) == 0


    def preset_data_is_only_plugin_data(
        self,
        preset: int = 3,
    ) -> bool:
        """Check if a MangoHud preset contains only the plugin's default keys and flags.

        Args:
            preset: Preset number to check.
        """
        self._create_presets_conf_dirs_parents()
        self._create_presets_conf_if_doesnt_exist()
        self._read_with_config_parser()

        preset_header = f"preset {preset}"
        if not self.config_parser.has_section(preset_header):
            return False

        inspected_keys_set = set(self.config_parser[preset_header].keys())

        plugin_keys_set = set(MANGOHUD_DEFAILT_PRESET_KEY_VALUES.keys())
        plugin_flags_set = set(MANGOHUD_DEFAULT_PRESET_FLAGS)

        return inspected_keys_set == plugin_keys_set.union(plugin_flags_set)

mangohud_editor = MangoHudConfigEditor()

class Plugin:
    async def mangohud_upsert_time_preset(
        self,
        preset_number: int,
        alpha: float,
        background_alpha: float,
        time_format: str,
        offset_y: int,
        offset_x: int,
        position: str,
    ) -> None:
        kv = MANGOHUD_DEFAILT_PRESET_KEY_VALUES
        kv.update({
            "alpha": alpha,
            "background_alpha": background_alpha,
            "time_format": time_format,
            "offset_y": offset_y,
            "offset_x": offset_x,
            "position": position,
        })
        mangohud_editor.upsert_mangohud_preset(
            preset=preset_number,
            kv=kv,
            flags=MANGOHUD_DEFAULT_PRESET_FLAGS,
        )

    async def mangohud_delete_preset(self, preset_number: int) -> None:
        mangohud_editor.delete_preset(preset=preset_number)

    async def mangohud_get_current_preset_data(self, preset_number: int) -> dict[str, str | None]:
        return mangohud_editor.get_current_preset_data(preset=preset_number)

    async def mangohud_preset_is_empty(self, preset_number: int) -> bool:
        return mangohud_editor.preset_data_is_empty(preset=preset_number)

    async def mangohud_preset_non_plugin_keys_inside(self, preset_number: int) -> bool:
        return not mangohud_editor.preset_data_is_only_plugin_data(preset=preset_number)

    # ==========================================================================
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        self.loop = asyncio.get_event_loop()
        decky.logger.info("Hello World!")

    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self):
        decky.logger.info("Goodnight World!")
        pass

    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self):
        decky.logger.info("Goodbye World!")
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky.decky_LOG_DIR/template.log`
        decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky.decky_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.decky_SETTINGS_DIR/`
        decky.migrate_settings(
            os.path.join(decky.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        decky.migrate_runtime(
            os.path.join(decky.DECKY_HOME, "template"),
            os.path.join(decky.DECKY_USER_HOME, ".local", "share", "decky-template"))
