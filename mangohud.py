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
        remove_all: bool = False,
    ) -> None:
        if remove_all:
            keys_and_flags = self.config_parser.options(section)

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
        remove_all: bool = False,
    ):
        """Change or add a MangoHud preset in the config file.

        Args:
            path: Path to the MangoHud config file.
            preset: Preset number to add or update.
            kv: Key-value pairs to set in the preset.
            flags: List of flags (keys without values) to set in the preset.
            remove: List of keys/flags to remove from the preset.
        """
        kv = kv or MANGOHUD_DEFAILT_PRESET_KEY_VALUES
        flags = flags or MANGOHUD_DEFAULT_PRESET_FLAGS
        remove = remove or []

        self._create_presets_conf_dirs_parents()
        self._backup_existing_mangohud_config()
        self._create_presets_conf_if_doesnt_exist()
        self._read_with_config_parser()

        preset_header = f"[preset {preset}]"
        self._add_section_if_not_exists(preset_header)

        self._delete_keys_and_flags(preset_header, remove, remove_all)
        self._set_key_values(preset_header, kv)
        self._set_flags(preset_header, flags)

        self._write_presets_conf()

mangohud_editor = MangoHudConfigEditor()