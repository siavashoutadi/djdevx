"""Project task definitions.

Add ``@shared_task`` functions here or in each Django app's ``tasks.py`` —
Celery autodiscovers them via ``app.autodiscover_tasks()``.
"""

from celery import shared_task


@shared_task
def hello(name: str) -> str:
    """Minimal task used to verify the worker is processing jobs."""
    return f"Hello, {name}!"
