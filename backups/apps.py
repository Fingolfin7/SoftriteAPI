from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import pytz  # to make the datetime.now() timezone aware and get rid of the warning message from 'PytzUsageWarning'
import os
from datetime import datetime
from SoftriteAPI.settings import MEDIA_ROOT
from backups.utils import cleanup_incomplete_uploads, remove_empty_folders


def clean_function():
    """container function to run one or more functions from the utils"""
    cleanup_incomplete_uploads()
    backups_path = os.path.join(MEDIA_ROOT, 'backups')
    remove_empty_folders(backups_path, False)
    # make sure to set remove root to false. It would suck to delete the backups dir by mistake!


class BackupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backups'

    def ready(self):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        tz = pytz.timezone(settings.TIME_ZONE)
        # run every 2 hours
        scheduler.add_job(clean_function, 'interval', hours=2, id='clean_storage',
                          misfire_grace_time=60,  # if the job is missed within a 60-second window, it will still run
                          next_run_time=tz.localize(datetime.now()))
        scheduler.start()
