from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import pytz  # to make the datetime.now() timezone aware and get rid of the warning message from 'PytzUsageWarning'
from datetime import datetime


class PayrollInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payroll_info'

    def ready(self):
        import payroll_info.signals
        from payroll_info.views import update_rbz_rate
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        tz = pytz.timezone(settings.TIME_ZONE)
        # scheduler.add_job(update_rbz_rate, 'interval', hours=2, id='update_rbz_rate_job',
        #                   next_run_time=tz.localize(datetime.now()))

        # call the update_rbz_rate function at 08:30, 08:45, 09:00, 11:00, 13:00, 15:00, and 16:30 everyday
        scheduler.add_job(update_rbz_rate, 'cron', hour='8-9,11,13,15,16', minute='30,45,0', id='update_rbz_rate_job',
                          next_run_time=tz.localize(datetime.now()))

        scheduler.start()
