import os
import uuid
from typing import List

from django.conf import settings
from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File, ModelSchema

from .models import Scan
from .utils import calculate_hashes

router = Router()


class ScanSchema(ModelSchema):
    class Meta:
        model = Scan
        fields = ("id", "filename", "sha256", "status", "result", "created_at")


@router.post("/")
def upload(request, file: UploadedFile = File(...)):
    # Create Scan object
    scan = Scan.objects.create(
        filename=file.name,  # Store original filename
        status=Scan.Status.PENDING,
        result=None,
    )

    file_path = os.path.join(settings.VIRUSSCAN_FILES_DIR, str(scan.id))
    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # Calculate file hashes
    sha256, sha512 = calculate_hashes(file_path)
    scan.sha256 = sha256
    scan.sha512 = sha512
    scan.save()


@router.get("/", response=List[ScanSchema])
def list_scans(request):
    scans = Scan.objects.order_by("-created_at")
    return list(scans)


@router.get("/{scan_id}", response=ScanSchema)
def get_scan(request, scan_id: uuid.UUID):
    return get_object_or_404(Scan, id=scan_id)
