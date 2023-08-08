import os.path
import uuid
from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from backups.utils import *


HTTP_STATUS_METHOD_NOT_ALLOWED = 405
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_STATUS_SERVER_ERROR = 500


def save_chunk_to_temp_file(uploader_id, chunk_index, file_data):
    destination = os.path.join(MEDIA_ROOT, 'uploads')
    fs = FileSystemStorage(location=destination)
    tmp_filename = f"{uploader_id}_chunk_{chunk_index}.part"
    fs.save(tmp_filename, file_data)
    return os.path.join(destination, tmp_filename)


def delete_chunks(uploader_id: str):
    """
    Delete all chunks for a given uploader ID.
    """
    destination = os.path.join(MEDIA_ROOT, 'uploads')
    for file in os.listdir(destination):
        if file.startswith(uploader_id):
            os.remove(os.path.join(destination, file))


def process_final_file_path(user, request):
    saveDir = os.path.join('backups', user.profile.company.name)
    adaski_file_path = request.POST.get('save_dir')

    if adaski_file_path:
        adaski_file_path = os.path.normpath(adaski_file_path)
        adaski_file_path = os.path.dirname(adaski_file_path) if os.path.isfile(adaski_file_path) else adaski_file_path
        adaski_file_path, before_after_gen_folder = os.path.split(adaski_file_path)
        adaski_file_path, month_folder = os.path.split(adaski_file_path)
        adaski_file_path, year_folder = os.path.split(adaski_file_path)
        _, company_code_folder = os.path.split(adaski_file_path)

        saveDir = os.path.join(saveDir, company_code_folder, year_folder, month_folder, before_after_gen_folder)

    filename = request.POST.get('filename')
    final_filename = f"{filename}"
    final_file_path = os.path.join(saveDir, final_filename)
    final_file_path = os.path.join(MEDIA_ROOT, final_file_path)
    os.makedirs(os.path.dirname(final_file_path), exist_ok=True)  # Create the directory if it doesn't exist
    return get_available_name(final_file_path)


def handle_uploaded_file(request, uploader_id, total_chunks, user):
    destination = os.path.join(MEDIA_ROOT, 'uploads')
    final_file_path = process_final_file_path(user, request)

    if not final_file_path.endswith('.zip'):
        delete_chunks(uploader_id)
        return HttpResponse("Invalid file type. Only .zip files are allowed.", status=HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE)

    with open(final_file_path, 'wb') as final_file:
        for i in range(total_chunks):
            chunk_filename = f"{uploader_id}_chunk_{i}.part"
            chunk_path = os.path.join(destination, chunk_filename)

            with open(chunk_path, 'rb') as chunk:
                final_file.write(chunk.read())

            # Delete the temporary chunk file
            fs = FileSystemStorage(location=destination)
            fs.delete(chunk_path)

    storage_left = user.profile.company.max_storage - user.profile.company.used_storage

    backup = Backup(user=user, company=user.profile.company, file=final_file_path)
    backup.save()

    # Verify checksum if provided
    checksum = request.POST.get('checksum')
    calculated_checksum = calculate_checksum(final_file_path)
    if checksum and checksum != calculated_checksum:
        backup.delete()  # Deletes the backup  AND  the backup file if the checksums don't match
        return HttpResponse("Invalid checksum", status=HTTP_STATUS_BAD_REQUEST)

    if int(backup.filesize) > storage_left:
        response_str = f"Could not upload file {backup.basename}. " \
                       f"You cannot exceed your storage limit of " \
                       f"{convert_size(user.profile.company.max_storage)}. " \
                       f"Storage left: {convert_size(storage_left)}, " \
                       f"upload size: {convert_size(int(backup.filesize))}"
        backup.delete()
        delete_chunks(uploader_id)
        return HttpResponse(response_str, status=HTTP_STATUS_REQUEST_ENTITY_TOO_LARGE)

    response = HttpResponse("File uploaded successfully", status=200)
    response.set_cookie('uploader_id', uploader_id, httponly=True)
    print(response.content)
    return response


# @csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload(request):
    """
    Handle the chunked upload process for chunked file uploads.
    """
    if not request.method == 'POST':
        return HttpResponse("Only POST requests are allowed", status=HTTP_STATUS_METHOD_NOT_ALLOWED)

    uploader_id = request.COOKIES.get('uploader_id')
    if not uploader_id:
        uploader_id = str(uuid.uuid4())  # Generate a unique ID for this upload using UUID4
        request.COOKIES['uploader_id'] = uploader_id

    total_chunks = int(request.POST.get('total_chunks'))
    chunk_index = int(request.POST.get('chunk_index'))
    file_data = request.FILES.get('file')

    # username = request.POST.get('username')
    # password = request.POST.get('password')
    # if username and password:
    #     user = authenticate(request, username=username, password=password)
    #
    #     if user is None:
    #         delete_chunks(uploader_id)
    #         return HttpResponse("Invalid credentials", status=HTTP_STATUS_UNAUTHORIZED)
    # else:
    #     user = request.user

    user = request.user

    if not user.profile.company:
        delete_chunks(uploader_id)
        return HttpResponse(f"User '{user.username}' is not associated with a company.", status=HTTP_STATUS_UNAUTHORIZED)

    try:
        save_chunk_to_temp_file(uploader_id, chunk_index, file_data)

        if chunk_index == total_chunks - 1:
            return handle_uploaded_file(request, uploader_id, total_chunks, user)
        else:
            response = HttpResponse("Chunk uploaded successfully", status=200)
            response.set_cookie('uploader_id', uploader_id, httponly=True)
            return response
    except Exception as e:
        delete_chunks(uploader_id)
        print(f'Error: {e}')
        return HttpResponse(f"Server error: {e}", status=HTTP_STATUS_SERVER_ERROR)


def manual_upload(request):
    form = UploadBackupForm()
    return render(request, 'backups/manual_upload.html', {'upload_backup_form': form})


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


class BackupListView(LoginRequiredMixin, ListView):
    model = Backup
    template_name = 'backups/backups_list.html'
    context_object_name = 'backups'
    ordering = ['-date_uploaded']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'User Backups'
        context['show_manual_backups'] = True
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
        company = Company.objects.get(id=int(self.kwargs['company_id']))
        context['title'] = 'Company Backups'
        context['company'] = company
        context['show_manual_backups'] = (company == self.request.user.profile.company)
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
        # only show backups by company
        return queryset.filter(company_id=int(self.kwargs['company_id']))
