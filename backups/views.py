import os
from datetime import datetime

from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from .models import Backup
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User


@csrf_exempt
def upload(request):
    """
    View for uploading a backup file from Adaski via http.
    This view takes a POST request with a file and saves it to the server's filesystem.
    Each backup file is saved with a unique name based on the user's/company's profile name and
    the date and time of upload. A backup record is also created in the database.
    """
    print(request.FILES)
    if request.method == 'POST':
        try:
            file = request.FILES['file']

            # for backup in Backup.objects.all():
            #     print(f'Deleting {backup.file}')
            #     os.remove(backup.file.path)
            #     backup.delete()

            # get the user credentials from the request
            username = request.POST.get('username')
            password = request.POST.get('password')

            # authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is None:
                return HttpResponse("Invalid credentials")

            saveDir = os.path.join('backups', user.username)
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)  # makedirs creates all the directories in the path if they don't exist
            savePath = os.path.join(saveDir, file.name)

            backup = Backup(user=user, file=file)
            backup.file.name = savePath

            # for old_bc in Backup.objects.filter(user=user):
            #     print(os.path.normpath(old_bc.file.name))
            #     if os.path.normpath(old_bc.file.name) == os.path.normpath(savePath):
            #         print(f"Deleting old backup {old_bc.file.path}")
            #         old_bc.delete()  # delete the old backup record from the database

            backup.save()
            return HttpResponse("File uploaded successfully")
        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse(f"Error: {e}")

    else:
        # return an error message
        return HttpResponse("GET requests not allowed for this endpoint. Please use a POST request to upload files.")
