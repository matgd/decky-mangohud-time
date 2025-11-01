import os

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code repo
# and add the `decky-loader/plugin/imports` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky
import asyncio
from pathlib import Path

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

class Plugin:
    async def mangohud_config_exists(self) -> bool:
        return MANGOHUD_CONFIG_PATH.exists()

    async def create_empty_mangohud_config(self):
        MANGOHUD_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANGOHUD_CONFIG_PATH.touch()

    async def mangohud_config_contents(self) -> str:
        if not MANGOHUD_CONFIG_PATH.exists():
            return ""
        return MANGOHUD_CONFIG_PATH.read_text()

    async def struct_mangohud_preset(self,
        preset_number: int = 3,
        alpha: float = 1.0,
        background_alpha: float = 0.0,
        time_format: str = "%H:%M",
        offset_y: int = -5,
        offset_x: int = 1212,
        position: str = "top-right"
    ) -> str:
        return MANGOHUD_CONFIG_PRESET_TEMPLATE.format(
            f_preset_number=preset_number,
            f_alpha=alpha,
            f_background_alpha=background_alpha,
            f_time_format=time_format,
            f_offset_y=offset_y,
            f_offset_x=offset_x,
            f_position=position
        )

    # TODO: First version - overwrite the whole file
    #       When disabling delete the file
    #       Add sliders, value inputs
    #
    # TODO: Second version - try to modify existing mangohud_config in place

    # ==========================================================================

    # A normal method. It can be called from the TypeScript side using @decky/api.
    async def add(self, left: int, right: int) -> int:
        return left + right

    async def long_running(self):
        await asyncio.sleep(15)
        # Passing through a bunch of random data, just as an example
        await decky.emit("timer_event", "Hello from the backend!", True, 2)

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

    async def start_timer(self):
        self.loop.create_task(self.long_running())

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
