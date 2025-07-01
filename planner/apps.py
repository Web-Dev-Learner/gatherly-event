
from django.apps import AppConfig
import sys
import os


class PlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planner'

    def ready(self):
        
        if sys.argv[0].endswith("manage.py") and 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true':
                from .scheduler import start_scheduler
                start_scheduler()








