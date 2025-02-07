import os
import uuid

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.scans.models import Scan

# Mark all tests in this file as requiring database access
pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    """Fixture for API client"""
    from django.test import Client

    return Client()


@pytest.fixture
def test_scan():
    """Fixture for a test scan"""
    return Scan.objects.create(
        filename="test_file.txt",
        sha256="test_sha256",
        sha512="test_sha512",
        status=Scan.Status.COMPLETED,
        result={"test": "result"},
    )


@pytest.fixture
def api_url():
    """Base API URL"""
    return "/api/scans"


@pytest.fixture
def test_file():
    """Fixture for a test file"""
    return SimpleUploadedFile(
        "test.txt", b"test file content", content_type="text/plain"
    )


@pytest.fixture(autouse=True)
def cleanup_files():
    """Automatically clean up test files after each test"""
    yield
    for scan in Scan.objects.all():
        file_path = os.path.join(settings.VIRUSSCAN_FILES_DIR, str(scan.id))
        if os.path.exists(file_path):
            os.remove(file_path)


class TestScanUpload:
    def test_upload_success(self, api_client, api_url, test_file):
        response = api_client.post(
            f"{api_url}/", {"file": test_file}, format="multipart"
        )

        assert response.status_code == 200
        assert Scan.objects.filter(filename="test.txt").exists()

    def test_upload_no_file(self, api_client, api_url):
        response = api_client.post(f"{api_url}/")
        assert response.status_code == 422

    def test_upload_large_file(self, api_client, api_url):
        large_content = b"x" * (1024 * 1024 * 20)  # 20MB file
        large_file = SimpleUploadedFile(
            "large.txt", large_content, content_type="text/plain"
        )

        response = api_client.post(
            f"{api_url}/", {"file": large_file}, format="multipart"
        )

        assert response.status_code == 200
        assert Scan.objects.filter(filename="large.txt").exists()

    def test_upload_invalid_file_type(self, api_client, api_url):
        exe_file = SimpleUploadedFile(
            "malicious.exe",
            b"fake executable content",
            content_type="application/x-msdownload",
        )

        response = api_client.post(
            f"{api_url}/", {"file": exe_file}, format="multipart"
        )

        assert response.status_code == 200  # Currently accepts all files


class TestScanList:
    def test_list_scans_empty(self, api_client, api_url):
        response = api_client.get(f"{api_url}/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_scans_with_data(self, api_client, api_url, test_scan):
        response = api_client.get(f"{api_url}/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "test_file.txt"
        assert data[0]["sha256"] == "test_sha256"
        assert data[0]["status"] == "completed"


class TestScanDetail:
    def test_get_scan_success(self, api_client, api_url, test_scan):
        response = api_client.get(f"{api_url}/{test_scan.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["filename"] == "test_file.txt"
        assert data["sha256"] == "test_sha256"
        assert data["status"] == "completed"

    def test_get_scan_not_found(self, api_client, api_url):
        non_existent_id = uuid.uuid4()
        response = api_client.get(f"{api_url}/{non_existent_id}")
        assert response.status_code == 404


@pytest.fixture
def mock_calculate_hashes(mocker):
    """Mock the calculate_hashes function"""
    return mocker.patch(
        "apps.scans.api.calculate_hashes",
        return_value=("mocked_sha256", "mocked_sha512"),
    )


class TestScanIntegration:
    def test_upload_and_retrieve(
        self, api_client, api_url, test_file, mock_calculate_hashes
    ):
        # Test file upload
        upload_response = api_client.post(
            f"{api_url}/", {"file": test_file}, format="multipart"
        )
        assert upload_response.status_code == 200

        # Get the created scan
        scan = Scan.objects.get(filename="test.txt")

        # Test retrieval
        detail_response = api_client.get(f"{api_url}/{scan.id}")
        assert detail_response.status_code == 200

        data = detail_response.json()
        assert data["filename"] == "test.txt"
        assert data["sha256"] == "mocked_sha256"
        assert data["status"] == "pending"
