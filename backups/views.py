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
from django.utils.crypto import get_random_string
from backups.utils import *


def delete_chunks(uploader_id: str):
    """
    Delete all chunks for a given uploader ID.
    """
    destination = os.path.join(MEDIA_ROOT, 'uploads')
    for file in os.listdir(destination):
        if file.startswith(uploader_id):
            print(f"Deleting {file}")
            os.remove(os.path.join(destination, file))


@csrf_exempt
def upload(request):
    """
    Handle the chunked upload process for chunked file uploads.
    """
    if not request.method == 'POST':
        return HttpResponse("Only POST requests are allowed", status=405)

    # Get or set the uploader ID cookie
    uploader_id = request.COOKIES.get('uploader_id')
    if not uploader_id or uploader_id is None:
        uploader_id = get_random_string(length=32)
        request.COOKIES['uploader_id'] = uploader_id

    # Get the chunk index, total number of chunks, and chunk data
    total_chunks = int(request.POST.get('total_chunks'))
    chunk_index = int(request.POST.get('chunk_index'))
    file_data = request.FILES.get('file')

    # Authenticate the user
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is None:
        delete_chunks(uploader_id)
        return HttpResponse("Invalid credentials", status=401)

    try:
        # Define the destination directory where the file chunks will be saved
        destination = os.path.join(MEDIA_ROOT, 'uploads')

        # Create a FileSystemStorage instance and set the destination directory
        fs = FileSystemStorage(location=destination)

        # Create a temporary file name using the session ID, original file name, and chunk index
        tmp_filename = f"{uploader_id}_chunk_{chunk_index}.part"

        # Save the chunk to the temporary file
        fs.save(tmp_filename, file_data)

        # Check if all chunks have been received
        if chunk_index == total_chunks - 1:
            filename = request.POST.get('filename')
            checksum = request.POST.get('checksum')

            saveDir = os.path.join('backups/', user.profile.company.name)
            final_filename = f"{filename}"
            final_file_path = os.path.join(saveDir, final_filename)
            final_file_path = os.path.join(MEDIA_ROOT, final_file_path)
            final_file_path = get_available_name(final_file_path)

            if not os.path.exists(os.path.dirname(final_file_path)):
                os.makedirs(os.path.dirname(final_file_path))

            if not final_file_path.endswith('.zip'):
                delete_chunks(uploader_id)
                return HttpResponse("Invalid file type. Only .zip files are allowed.", status=415)

            with open(final_file_path, 'wb') as final_file:
                for i in range(total_chunks):
                    chunk_filename = f"{uploader_id}_chunk_{i}.part"
                    chunk_path = os.path.join(destination, chunk_filename)

                    with open(chunk_path, 'rb') as chunk:
                        final_file.write(chunk.read())

                    # Delete the temporary chunk file
                    fs.delete(chunk_path)

            storage_left = user.profile.company.max_storage - user.profile.company.used_storage

            backup = Backup(user=user, company=user.profile.company, file=final_file_path)
            backup.save()

            # Verify checksum if provided
            calculated_checksum = calculate_checksum(final_file_path)
            if checksum and checksum != calculated_checksum:
                backup.delete()  # Delete the backup  AND  the backup file if the checksums don't match
                return HttpResponse("Invalid checksum", status=400)

            if backup.filesize > (user.profile.company.max_storage - user.profile.company.used_storage):
                response_str = f"Could not upload file {backup.basename}. " \
                               f"You cannot exceeded your storage limit of {convert_size(user.profile.company.max_storage)}. " \
                               f"Storage left: {convert_size(storage_left)}, " \
                               f"upload size: {convert_size(backup.filesize)}"
                backup.delete()
                delete_chunks(uploader_id)
                return HttpResponse(response_str, status=413)

            response = HttpResponse("File uploaded successfully", status=200)
            response.set_cookie('uploader_id', uploader_id)
            print(response.content)
            return response

        else:
            response = HttpResponse("Chunk uploaded successfully", status=200)
            response.set_cookie('uploader_id', uploader_id)
            return response
    except Exception as e:
        delete_chunks(uploader_id)
        print(f'Error: {e}')
        return HttpResponse(f"Server error: {e}", status=500)


class BackupDeleteView(LoginRequiredMixin, DeleteView):
    model = Backup
    success_url = reverse_lazy('profile')
    context_object_name = 'backup'
    template_name = 'backups/backups_delete.html'

    def get_object(self, queryset=None):
        backup = super().get_object()
        # if backup.user != self.request.user and not backup.user.is_superuser:
        #     raise PermissionError("You don't have permission to delete this backup.")
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


class CompanyBackupListView(LoginRequiredMixin, ListView):
    model = Backup
    template_name = 'backups/backups_list.html'
    context_object_name = 'backups'
    ordering = ['-date_uploaded']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Company Backups'
        context['company'] = Company.objects.get(id=int(self.kwargs['company_id']))
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
        # # only show backups by company
        # company = Company.objects.get(id=int(self.kwargs['company_id']))
        # return queryset.filter(company=company)
        return queryset
