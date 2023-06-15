from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User


def convert_size(size_bytes: int | bytes) -> str:
    """ Takes a file size in bytes and returns a string with the appropriate unit.
    E.g. 1024 bytes -> 1 KB  or 1024 MB -> 1 GB
    """
    if size_bytes == 0:
        return '0 bytes'
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f'{size_bytes:.2f} {unit}'
        size_bytes /= 1024


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

            # check file type before saving. only allow .zip files
            if not file.name.endswith('.zip'):
                return HttpResponse("Invalid file type. Only .zip files are allowed.", status=415)

            # get the user credentials from the request
            username = request.POST.get('username')
            password = request.POST.get('password')

            # authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is None:
                return HttpResponse("Invalid credentials", status=401)

            saveDir = os.path.join('backups/', user.username)
            """
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)  # makedirs creates all the directories in the path if they don't exist
            """
            savePath = os.path.join(saveDir, file.name)

            storage_left = user.profile.max_storage - user.profile.used_storage

            backup = Backup(user=user, file=file)
            backup.file.name = savePath
            backup.save()

            if backup.filesize > (user.profile.max_storage - user.profile.used_storage):
                response_str = f"Could not upload file {backup.basename}. " \
                               f"You cannot exceeded your storage limit of {convert_size(user.profile.max_storage)}. " \
                               f"Storage left: {convert_size(storage_left)}, " \
                               f"upload size: {convert_size(backup.filesize)}"
                backup.delete()
                return HttpResponse(response_str, status=413)

            else:
                return HttpResponse("File uploaded successfully", status=200)
        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse(f"Error: {e}")

    else:
        # return an error message
        return HttpResponse("GET requests not allowed for this endpoint. Please use a POST request to upload files.")


class BackupDeleteView(LoginRequiredMixin, DeleteView):
    model = Backup
    success_url = reverse_lazy('profile')
    context_object_name = 'backup'
    template_name = 'backups/backups_delete.html'

    def get_object(self, queryset=None):
        backup = super().get_object()
        if backup.user != self.request.user and not backup.user.is_superuser:
            raise PermissionError("You don't have permission to delete this backup.")
        return backup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Delete Backup"
        return context


@login_required
def admin_backups_page(request):
    all_users = User.objects.all()
    context = {
        'all_users': all_users,
        'title': 'Admin Backups',
    }
    return render(request, 'backups/backups_admin.html', context)


@login_required
def admin_backups_user_page(request, username):
    """
    View for the admin backups page. This page lists all the backups for a given user.
    The username is passed in as an argument.
    """
    user = User.objects.get(username=username)
    backups = Backup.objects.filter(user=user).order_by('-date_uploaded')

    context = {
        'backups': backups,
        'title': 'Admin Backups',
        'user': user,
    }
    return render(request, 'backups/backups_admin_user.html', context)


class BackupListView(LoginRequiredMixin, ListView):
    model = Backup
    template_name = 'backups/backups_list.html'
    context_object_name = 'backups'
    ordering = ['-date_uploaded']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Profile'
        context['search_form'] = BackupSearch(initial={'start_date': self.request.GET.get('start_date'),
                                                       'end_date': self.request.GET.get('end_date'),
                                                       'name': self.request.GET.get('name')})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        name = self.request.GET.get('name')
        if start_date and end_date and start_date <= end_date:
            queryset = queryset.filter(date_uploaded__range=[start_date, end_date])  # filter by date range.
            # __range is a django filter
        elif start_date and not end_date:
            queryset = queryset.filter(date_uploaded__gte=start_date)  # gte is greater than or equal to
        elif end_date and not start_date:
            queryset = queryset.filter(date_uploaded__lte=end_date)  # lte is less than or equal to
        if name:
            queryset = queryset.filter(file__icontains=name)
        # only show backups uploaded by the user
        return queryset.filter(user=self.request.user)
