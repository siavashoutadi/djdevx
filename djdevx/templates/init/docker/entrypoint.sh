#!/bin/bash -euo pipefail

python manage.py showmigrations | grep '\[ \]' && python manage.py migrate

python -m uvicorn applications.asgi:application --host 0.0.0.0 --port 8000 --reload
