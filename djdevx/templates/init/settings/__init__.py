from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_DIR = BASE_DIR / "settings"

DJANGO_SETTINGS_DIR = SETTINGS_DIR / "django"
PACKAGES_SETTINGS_DIR = SETTINGS_DIR / "packages"
APPS_SETTINGS_DIR = SETTINGS_DIR / "apps"

setting_files = []

setting_files += [
    str(f) for f in Path(DJANGO_SETTINGS_DIR).rglob("*.py") if f.name != "__init__.py"
]
setting_files += [
    str(f) for f in Path(PACKAGES_SETTINGS_DIR).rglob("*.py") if f.name != "__init__.py"
]
setting_files += [
    str(f) for f in Path(APPS_SETTINGS_DIR).rglob("*.py") if f.name != "__init__.py"
]


for setting_file in setting_files:
    with open(setting_file) as f:
        code = compile(f.read(), setting_file, "exec")
        exec(code)
