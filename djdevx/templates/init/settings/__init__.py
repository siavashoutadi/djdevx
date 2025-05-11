import glob
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_DIR = BASE_DIR / "settings"

DJANGO_SETTINGS_DIR = SETTINGS_DIR / "django"
PACKAGES_SETTINGS_DIR = SETTINGS_DIR / "packages"
APPS_SETTINGS_DIR = SETTINGS_DIR / "apps"

setting_files = []

setting_files += glob.glob(str(DJANGO_SETTINGS_DIR / "[!__init__]*.py"))
setting_files += glob.glob(str(PACKAGES_SETTINGS_DIR / "[!__init__]*.py"))
setting_files += glob.glob(str(APPS_SETTINGS_DIR / "[!__init__]*.py"))

for setting_file in setting_files:
    with open(setting_file) as f:
        code = compile(f.read(), setting_file, "exec")
        exec(code)
