import os
import hashlib
from datetime import datetime
from SoftriteAPI.settings import MEDIA_ROOT


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


def calculate_checksum(filepath: str) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_available_name(name: str) -> str:
    if os.path.exists(name):
        now = datetime.now().strftime('%m-%d-%Y at %H.%M.%S')
        name, ext = os.path.splitext(name)
        return f"{name} ({now}){ext}"
    return name


def cleanup_incomplete_uploads():
    destination = os.path.join(MEDIA_ROOT, 'uploads')
    for file in os.listdir(destination):
        file_path = os.path.join(destination, file)
        # check if file is older than 3 hours old, if so, delete it
        if os.stat(file_path).st_mtime < datetime.now().timestamp() - 10800:  # 10800 seconds = 3 hours
            if os.path.isfile(file_path):
                os.remove(file_path)
