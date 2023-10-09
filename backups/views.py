import uuid
import os.path

from django.utils import timezone

from .forms import *
from backups.utils import *
from backups.emails import *
from urllib.parse import unquote
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

HTTP_STATUS_METHOD_NOT_ALLOWED = 405
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_STATUS_SERVER_ERROR = 500

logger = logging.getLogger(__name__)


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


def send_backup_complete_email(users_list: list | set, backup: Backup):
    # Make sure backup.date_uploaded is timezone aware
    backup_date_uploaded = timezone.localtime(backup.date_uploaded)

    formatted_date = backup_date_uploaded.strftime("%A %d %B, %Y at %H:%M")

    # get the first comment if it exists
    comment = backup.comment_set.first().body if backup.comment_set.exists() else ""

    mailMan = Mailer(my_email=EMAIL_HOST_USER, my_password=EMAIL_HOST_PASSWORD, smtp_server=EMAIL_HOST, port=EMAIL_PORT)
    mailMan.sendHtmlEmail(to_email=[user.email for user in users_list], subject='Backup Complete',
                          html_content=f'''
                           <!DOCTYPE html>
                           <html>
                               <head>
                                   <title>Backup Upload Complete</title>
                                   <style>
                                       body {{
                                           font-family: Arial, sans-serif;
                                       }}
                                       .container {{
                                           margin: 0 auto;
                                           max-width: 600px;
                                           padding: 20px;
                                           background-color: #fff;
                                           border-radius: 10px;
                                           box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                                       }}
                                       h1 {{
                                           color: #0072c6;
                                           font-size: 36px;
                                           margin-bottom: 20px;
                                       }}
                                       img {{
                                           max-width: 100%;
                                           height: auto;
                                           margin-bottom: 20px;
                                       }}
                                       .center-img {{
                                           display: block;
                                           margin-left: auto;
                                           margin-right: auto;
                                       }}
                                   </style>

                               </head> 
                               <body> 
                                   <div class="container"> 
                                       <img src="https://adaski.co.zw/static/payroll_info/images/logo-transparent.png" alt="Adaski Logo" class="center-img">
                                       <h1>Backup Upload Complete</h1> 
                                       <p>Your backup upload is complete. You can view your backup on the <a href="https://adaski.co.zw/">Adaski</a> website.</p> 
                                       <p>Backup Name: <b>{backup.basename}</b></p>
                                       <p>Backup Date: <b>{formatted_date}</b></p>
                                       <p>Uploaded by: <b>{backup.user.username}</b></p>

                                       {"<p>Backup Comment: <b>" + comment + "</b>" if comment != "" else ""}

                                       <p>Thank you for using Softrite.</p>
                                   </div>
                               </body>
                           </html>
                           '''
                          )

    # close the mailer connection
    mailMan.close_connection()

    log_message = "Sent backup complete email to "
    for i, to_user in enumerate(users_list):
        if i != len(users_list) - 1:
            log_message += f"{to_user.email} ({to_user.username})"
            log_message += ", "
        else:
            log_message += f"and {to_user.email} ({to_user.username})"
            log_message += f" from {to_user.profile.company.name} for backup '{backup.basename}' successfully."

    logger.info(log_message)


def handle_uploaded_file(request, uploader_id, total_chunks, user):
    destination = os.path.join(MEDIA_ROOT, 'uploads')
    final_file_path = process_final_file_path(user, request)

    if not final_file_path.endswith('.zip'):
        delete_chunks(uploader_id)
        return HttpResponse("Invalid file type. Only .zip files are allowed.",
                            status=HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE)

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

    # get comment and create a comment object
    comment = request.POST.get('comment')
    if comment and comment != '':
        comment = Comment(user=user, backup=backup, body=unquote(comment.strip()))
        comment.save()

    response = HttpResponse("File uploaded successfully", status=200)
    response.set_cookie('uploader_id', uploader_id, httponly=True)
    logger.info(f"User '{user.username}' ({user.profile.company.name}) uploaded file '{backup.basename}' successfully.")

    # send backup complete email
    users_list = [user] if user.profile.get_backup_emails else []
    users_list += list(User.objects.filter(profile__is_company_admin=True,  # include company admins
                                           profile__get_backup_emails=True,  # don't include profiles that have False
                                           profile__company=user.profile.company))
    users_list = set(users_list)  # remove duplicates (if any)

    send_backup_complete_email(users_list, backup)

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
    filesize = int(request.POST.get('filesize'))
    filename = request.POST.get('filename')
    file_data = request.FILES.get('file')

    user = request.user

    if not user.profile.company:
        delete_chunks(uploader_id)
        return HttpResponse(f"User '{user.username}' is not associated with a company.",
                            status=HTTP_STATUS_UNAUTHORIZED)

    storage_left = user.profile.company.max_storage - user.profile.company.used_storage
    if int(filesize) > storage_left:
        response_str = f"Could not upload file {filename}. " \
                       f"You cannot exceed your storage limit of " \
                       f"{convert_size(user.profile.company.max_storage)}. " \
                       f"Storage left: {convert_size(storage_left)}, " \
                       f"upload size: {convert_size(int(filesize))}"
        delete_chunks(uploader_id)
        return HttpResponse(response_str, status=HTTP_STATUS_REQUEST_ENTITY_TOO_LARGE)

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
        logger.error(f'Error uploading file. Error: {e}')
        return HttpResponse(f"Server error: {e}", status=HTTP_STATUS_SERVER_ERROR)


def manual_upload(request):
    form = UploadBackupForm()
    return render(request, 'backups/manual_upload.html', {'upload_backup_form': form})


def file_browser_view(request):
    """
    view that lists all the files in the user's company's backup folder. If the user is a staff member or superuser,
    they can view the backups for all the companies (i.e. the backup root folder).
    """
    if request.method == 'POST':
        path = request.POST.get('path', '')
    else:
        path = request.GET.get('path', '')

    if request.user.is_staff or request.user.is_superuser:
        base_path = os.path.join(MEDIA_ROOT, 'backups')
        backups = Backup.objects.all().order_by('-date_uploaded')
    else:
        company = request.user.profile.company
        base_path = os.path.join(MEDIA_ROOT, 'backups', company.name)  # media_root/backups/company_name/
        backups = Backup.objects.filter(company=company).order_by('-date_uploaded')

    # if this is the root folder then go ahead and run remove_empty_folders() to remove any empty subdirectories
    # before the user sees them
    if path == '':
        remove_empty_folders(base_path, removeRoot=False)  # removeRoot=False means don't delete the root 'base' folder

    path = os.path.normpath(os.path.join(base_path, path))
    subdirectories = []
    files = []

    if os.path.isdir(path):
        items = os.listdir(path)
        subdirectories = [item for item in items if os.path.isdir(os.path.join(path, item))]
        # filter backup files to show only the backups in this current directory
        files = [backup for backup in backups if backup.file.path in
                 [os.path.join(path, item) for item in items]
                 ]

    path_segments = [segment for segment in path.split(os.sep) if segment]  # os.sep is the path separator for the OS

    one_level_up = os.path.normpath(f"{os.sep}".join(path_segments[:-1])) if len(path_segments) > 1 else None
    # ensure the new path stays within the intended base path
    # if the length of one_level_up is less than or equal to the length of the base path then
    # it is no longer within the limits of the intended base path
    if one_level_up and len(one_level_up) < len(base_path):
        one_level_up = None

    clickable_path_segments = []
    for i, segment in enumerate(path_segments):
        segment_path = os.path.normpath(f"{os.sep}".join(path_segments[:i + 1]))
        clickable_path_segments.append((segment, segment_path))

    clickable_path_segments = [seg_tuple for seg_tuple in clickable_path_segments if seg_tuple[0] not in MEDIA_ROOT]

    if not (request.user.is_staff or request.user.is_superuser):  # if the user is not a staff member or superuser
        clickable_path_segments = clickable_path_segments[1:]  # remove the 'backups' folder from the clickable path

    context = {
        'files': files,
        'current_path': path,
        'title': 'Browse Files',
        'subdirectories': subdirectories,
        'one_level_up': one_level_up,
        'clickable_path_segments': clickable_path_segments,
    }

    return render(request, "backups/file_browser.html", context)


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


def tally_used_storage(company: Company):
    """
    Tally the total storage used by the company and update the company's used_storage field if it is not correct.
    """
    associated_backups = Backup.objects.filter(company=company)
    tally = sum(backup.filesize for backup in associated_backups)
    if tally != company.used_storage:
        logger.info(f"Updating company '{company.name}' used storage from {convert_size(company.used_storage)} "
                    f"to {convert_size(tally)}, after tally.")
        company.used_storage = tally
        company.save()


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
        queryset = super().get_queryset().filter(company_id=int(self.kwargs['company_id']))

        # while doing this, check if the total storage used by the company is correct and if not, fix it
        company = Company.objects.get(id=int(self.kwargs['company_id']))
        tally_used_storage(company=company)

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
        return queryset


class BackupDetailView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'backups/backups_detail.html'
    context_object_name = 'comments'
    ordering = ['created']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        backup = get_object_or_404(Backup, id=self.kwargs['pk'])
        context['title'] = 'Backup Details'
        context['backup'] = backup
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        backup_id = int(self.kwargs['pk'])
        parent_id = request.POST.get('parent_id')

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.backup_id = backup_id

            if parent_id:
                comment.parent_id = int(parent_id)
                message = 'Reply added successfully'
            else:
                message = 'Comment added successfully'

            try:
                comment.save()
                messages.success(request, message)
            except IntegrityError:
                messages.error(request, 'Error adding comment. Please try again.')

        else:
            messages.error(request, 'Error adding comment. Please try again.')

        return redirect(self.get_success_url())

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(backup_id=int(self.kwargs['pk']), parent=None)

    def get_success_url(self):
        return reverse_lazy('backups:backup_details', kwargs={'pk': self.kwargs['pk']})
