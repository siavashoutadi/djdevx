import importlib
from pathlib import Path

URLS_DIR = Path(__file__).parent

url_files = [str(f) for f in Path(URLS_DIR).rglob("*.py") if f.name != "__init__.py"]

urlpatterns = []

for file_path in url_files:
    relative_path = Path(file_path).relative_to(URLS_DIR).with_suffix("")
    module_name = f"urls.{'.'.join(relative_path.parts)}"

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "urlpatterns"):
            urlpatterns += module.urlpatterns
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
