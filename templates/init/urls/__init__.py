import importlib
import glob
from pathlib import Path

URLS_DIR = Path(__file__).parent

url_files = glob.glob(str(URLS_DIR / "**/[!__init__]*.py"), recursive=True)

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
