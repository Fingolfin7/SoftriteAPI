from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import pytz  # to make the datetime.now() timezone aware and get rid of the warning message from 'PytzUsageWarning'
from datetime import datetime


class BackupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backups'

    def ready(self):
        from backups.utils import cleanup_incomplete_uploads
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        tz = pytz.timezone(settings.TIME_ZONE)
        # run every 2 hours
        scheduler.add_job(cleanup_incomplete_uploads, 'interval', hours=2, id='cleanup_incomplete_uploads_job',
                          misfire_grace_time=60,  # if the job is missed by 60 seconds, it will still run
                          next_run_time=tz.localize(datetime.now()))
        scheduler.start()
