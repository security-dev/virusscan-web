import uuid
from typing import Dict, Optional, Literal

import clamav_client
from celery import shared_task
from django.conf import settings
from django.db import transaction

from apps.scans.models import Scan
from apps.scans.utils import build_file_path


def _build_result(
    state: Optional[Literal["ERROR", "OK", "FOUND"]],
    details: str,
) -> Dict:
    """Helper function to build the scan result dictionary."""
    return {"infected": state == "FOUND", "details": details}


@shared_task
def scan_file_by_scan_id(scan_id: uuid.UUID):
    scan = Scan.objects.get(id=scan_id)
    file_path = build_file_path(scan_id)
    scanner = clamav_client.get_scanner(settings.CLAMAV_CONFIG)

    scan.status = Scan.Status.SCANNING
    scan.save()

    result = scanner.scan(str(file_path))

    with transaction.atomic():
        scan.refresh_from_db()
        scan.result = _build_result(result.state, result.details)

        scan.status = (
            Scan.Status.FAILED if result.state == "ERROR" else Scan.Status.COMPLETED
        )
        scan.save()
