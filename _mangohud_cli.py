#!python3
from mangohud import MangoHudConfigEditor

DEFAULT_TEST_FILE = ".test_presets.conf"

# MangoHudConfigEditor(DEFAULT_TEST_FILE).upsert_mangohud_preset()
# MangoHudConfigEditor(DEFAULT_TEST_FILE).upsert_mangohud_preset(remove=["alpha"])
# MangoHudConfigEditor(DEFAULT_TEST_FILE).delete_preset(3)

# print the file
with open(DEFAULT_TEST_FILE, "r", encoding="utf-8") as f:
    print(DEFAULT_TEST_FILE)
    print('---')
    print(f.read())