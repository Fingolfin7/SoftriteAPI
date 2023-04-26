"""
WSGI config for SoftriteAPI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import pytz # to make the datetime.now() timezone aware and get rid of the warning message from 'PytzUsageWarning'
from datetime import datetime
from django.conf import settings
from payroll_info.views import update_rbz_rate
from django.core.wsgi import get_wsgi_application
from apscheduler.schedulers.background import BackgroundScheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SoftriteAPI.settings')

application = get_wsgi_application()

# call the update_rbz_rate function every 5 minutes in the background
scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)

# timezone configuration
tz = pytz.timezone(settings.TIME_ZONE)

scheduler.add_job(update_rbz_rate, 'interval', hours=2, id='update_rbz_rate_job',
                  next_run_time=tz.localize(datetime.now()))  # Run update_rbz_rate every 2 hours

scheduler.start()
