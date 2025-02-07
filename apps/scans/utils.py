import hashlib
import os
import uuid

from django.conf import settings


def calculate_hashes(file_path):
    sha256_hash = hashlib.sha256()
    sha512_hash = hashlib.sha512()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
            sha512_hash.update(chunk)

    return sha256_hash.hexdigest(), sha512_hash.hexdigest()


def build_file_path(scan_id: uuid.UUID):
    if not isinstance(scan_id, uuid.UUID):
        raise ValueError("scan_id must be a UUID")
    return os.path.join(settings.VIRUSSCAN_FILES_DIR, str(scan_id))
