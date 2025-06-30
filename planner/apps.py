
from django.apps import AppConfig
import sys
import os


class PlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planner'

    def ready(self):
        # Run scheduler only once when using runserver (avoid autoreloader duplicate)
        if sys.argv[0].endswith("manage.py") and 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true':
                from .scheduler import start_scheduler
                start_scheduler()




# 2nd code 

# from django.apps import AppConfig
# import sys  # Import this to check how the app was started


# class PlannerConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'planner'

#     def ready(self):
#         # Only start the scheduler when running the development server (not on migrations, shell, etc.)
#         if 'runserver' in sys.argv:
#             from .scheduler import start_scheduler
#             start_scheduler()












# 1 st code 

# from django.apps import AppConfig


# class PlannerConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'planner'


#     def ready(self):
#         from .scheduler import start_scheduler
#         start_scheduler()
