from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import pytz  # to make the datetime.now() timezone aware and get rid of the warning message from 'PytzUsageWarning'
import os
import logging
from datetime import datetime
from SoftriteAPI.settings import MEDIA_ROOT
from backups.utils import cleanup_incomplete_uploads, remove_empty_folders


logger = logging.getLogger(__name__)


class BackupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backups'

    def ready(self):
        from users.models import Profile

        def cleanup_media_folder():
            """
            I noticed that sometimes when a user uploads a gif as a profile pic, the old profile pic is not deleted.
            This function will delete all unreferenced images in the profile_pics folder. (its only temporary while I
            figure out why the old profile pic is not deleted)
            """
            referenced_images = [os.path.normpath(os.path.join(MEDIA_ROOT, profile.image.name)) for profile in
                                 Profile.objects.all()]

            media_folder = os.path.join(MEDIA_ROOT, 'profile_pics')  # Adjust the folder path as needed
            all_images = [os.path.normpath(os.path.join(media_folder, filename)) for filename in
                          os.listdir(media_folder)]

            log_text_path = f"{os.sep}".join(os.path.normpath(media_folder).split(os.sep)[-2:])

            # get the set difference to find unreferenced images
            unreferenced_images = set(all_images) - set(referenced_images)

            logger.info(f"Unreferenced Images in {log_text_path}: {len(unreferenced_images)}")
            logger.info(f"All Images in {log_text_path}:  {len(all_images)}")

            for image_path in unreferenced_images:
                logger.info(f"Deleting unreferenced image: {image_path}")
                os.remove(image_path)

        def clean_function():
            """container function to run one or more functions from the utils"""
            cleanup_media_folder()
            cleanup_incomplete_uploads()
            backups_path = os.path.join(MEDIA_ROOT, 'backups')
            remove_empty_folders(backups_path, False)
            # make sure to set remove root to false. It would suck to delete the backups dir by mistake!

        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        tz = pytz.timezone(settings.TIME_ZONE)
        # run every 2 hours
        scheduler.add_job(clean_function, 'interval', hours=2, id='clean_storage',
                          misfire_grace_time=60,  # if the job is missed within a 60-second window, it will still run
                          next_run_time=tz.localize(datetime.now()))
        scheduler.start()
