import importlib
from pathlib import Path
from django.urls import URLPattern, URLResolver
from typing import List, Union


WS_URLS_DIR = Path(__file__).parent

ws_url_files = [
    str(f) for f in Path(WS_URLS_DIR).rglob("*.py") if f.name != "__init__.py"
]

websocket_urlpatterns: List[Union[URLPattern, URLResolver]] = []

for file_path in ws_url_files:
    relative_path = Path(file_path).relative_to(WS_URLS_DIR).with_suffix("")
    module_name = f"ws_urls.{'.'.join(relative_path.parts)}"

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "websocket_urlpatterns"):
            websocket_urlpatterns.extend(module.websocket_urlpatterns)
    except Exception as e:
        print(f"Error importing WebSocket URL patterns from {module_name}: {e}")

__all__ = ["websocket_urlpatterns"]
