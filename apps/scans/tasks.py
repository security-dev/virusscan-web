import uuid

import clamav_client
from celery import shared_task
from django.conf import settings
from django.db import transaction

from apps.scans.models import Scan
from apps.scans.utils import build_file_path


def map_scan_result_to_status(
    result_state: str,
) -> str:
    status_mapping = {
        "ERROR": Scan.Status.FAILED,
        "OK": Scan.Status.CLEAN,
        "FOUND": Scan.Status.FOUND,
    }
    return status_mapping.get(result_state, Scan.Status.FAILED)


@shared_task(
    autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5}
)
def scan_file_by_scan_id(scan_id: uuid.UUID):
    scan = Scan.objects.get(id=scan_id)
    if scan.status == Scan.Status.CLEAN or scan.status == Scan.Status.FOUND:
        return
    file_path = build_file_path(scan_id)
    scanner = clamav_client.get_scanner(settings.CLAMAV_CONFIG)

    scan.status = Scan.Status.SCANNING
    scan.save()

    result = scanner.scan(str(file_path))

    with transaction.atomic():
        scan.refresh_from_db()
        scan.result = result.details

        scan.status = map_scan_result_to_status(str(result.state))
        scan.save()
