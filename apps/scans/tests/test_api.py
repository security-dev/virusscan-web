import os
import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from apps.scans.models import Scan

pytestmark = pytest.mark.django_db
User = get_user_model()


# Fixtures
@pytest.fixture
def auth_user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def auth_token(auth_user):
    return auth_user.create_api_key("testkey")


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def authenticated_client(auth_token):
    return Client(headers={"X-API-Key": auth_token})


@pytest.fixture
def test_scan():
    return Scan.objects.create(
        filename="test_file.txt",
        sha256="test_sha256",
        sha512="test_sha512",
        status=Scan.Status.COMPLETED,
        result={"test": "result"},
    )


@pytest.fixture
def api_url():
    return "/api/scans"


@pytest.fixture
def test_file():
    return SimpleUploadedFile(
        "test.txt", b"test file content", content_type="text/plain"
    )


@pytest.fixture(autouse=True)
def cleanup_files():
    yield
    for scan in Scan.objects.all():
        file_path = os.path.join(settings.VIRUSSCAN_FILES_DIR, str(scan.id))
        if os.path.exists(file_path):
            os.remove(file_path)


@pytest.fixture
def mock_calculate_hashes(mocker):
    return mocker.patch(
        "apps.scans.api.calculate_hashes",
        return_value=("mocked_sha256", "mocked_sha512"),
    )


@pytest.fixture
def auth_not_required(settings):
    settings.REQUIRE_AUTH = False


@pytest.fixture
def auth_required(settings):
    settings.REQUIRE_AUTH = True


class TestApiUnauthorized:
    """Tests for API endpoints when authentication is required but not provided"""

    @pytest.mark.usefixtures("auth_required")
    class TestEndpoints:
        def test_upload_unauthorized(self, api_client, api_url, test_file):
            response = api_client.post(
                f"{api_url}/", {"file": test_file}, format="multipart"
            )
            assert response.status_code == 401

        def test_list_unauthorized(self, api_client, api_url):
            response = api_client.get(f"{api_url}/")
            assert response.status_code == 401

        def test_detail_unauthorized(self, api_client, api_url, test_scan):
            response = api_client.get(f"{api_url}/{test_scan.id}")
            assert response.status_code == 401


class TestApiEndpoints:
    """Tests for API endpoints in both authenticated and unauthenticated modes"""

    @pytest.mark.usefixtures("auth_not_required")
    class TestUnauthenticated:
        def test_upload(self, api_client, api_url, test_file):
            response = api_client.post(
                f"{api_url}/", {"file": test_file}, format="multipart"
            )
            assert response.status_code == 200
            assert Scan.objects.filter(filename="test.txt").exists()

        def test_upload_no_file(self, api_client, api_url):
            response = api_client.post(f"{api_url}/")
            assert response.status_code == 422

        def test_list_empty(self, api_client, api_url):
            response = api_client.get(f"{api_url}/")
            assert response.status_code == 200
            assert response.json() == []

        def test_list_with_data(self, api_client, api_url, test_scan):
            response = api_client.get(f"{api_url}/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["filename"] == "test_file.txt"

        def test_get_scan(self, api_client, api_url, test_scan):
            response = api_client.get(f"{api_url}/{test_scan.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == "test_file.txt"

        def test_get_scan_not_found(self, api_client, api_url):
            response = api_client.get(f"{api_url}/{str(uuid.uuid4())}")
            assert response.status_code == 404

        def test_get_scan_invalid_id_format(self, api_client, api_url):
            response = api_client.get(f"{api_url}/12345")
            assert response.status_code == 422

        def test_upload_and_retrieve(
            self, api_client, api_url, test_file, mock_calculate_hashes
        ):
            # Upload
            upload_response = api_client.post(
                f"{api_url}/", {"file": test_file}, format="multipart"
            )
            assert upload_response.status_code == 200

            # Retrieve
            scan = Scan.objects.get(filename="test.txt")
            detail_response = api_client.get(f"{api_url}/{scan.id}")
            assert detail_response.status_code == 200
            assert detail_response.json()["sha256"] == "mocked_sha256"

    @pytest.mark.usefixtures("auth_required")
    class TestAuthenticated:
        def test_upload(self, authenticated_client, api_url, test_file):
            response = authenticated_client.post(
                f"{api_url}/", {"file": test_file}, format="multipart"
            )
            assert response.status_code == 200
            assert Scan.objects.filter(filename="test.txt").exists()

        def test_upload_no_file(self, authenticated_client, api_url):
            response = authenticated_client.post(f"{api_url}/")
            assert response.status_code == 422

        def test_list_empty(self, authenticated_client, api_url):
            response = authenticated_client.get(f"{api_url}/")
            assert response.status_code == 200
            assert response.json() == []

        def test_list_with_data(self, authenticated_client, api_url, test_scan):
            response = authenticated_client.get(f"{api_url}/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["filename"] == "test_file.txt"

        def test_get_scan(self, authenticated_client, api_url, test_scan):
            response = authenticated_client.get(f"{api_url}/{test_scan.id}")
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == "test_file.txt"

        def test_get_scan_not_found(self, authenticated_client, api_url):
            response = authenticated_client.get(f"{api_url}/{str(uuid.uuid4())}")
            assert response.status_code == 404

        def test_get_scan_invalid_id_format(self, authenticated_client, api_url):
            response = authenticated_client.get(f"{api_url}/12345")
            assert response.status_code == 422

        def test_upload_and_retrieve(
            self, authenticated_client, api_url, test_file, mock_calculate_hashes
        ):
            # Upload
            upload_response = authenticated_client.post(
                f"{api_url}/", {"file": test_file}, format="multipart"
            )
            assert upload_response.status_code == 200

            # Retrieve
            scan = Scan.objects.get(filename="test.txt")
            detail_response = authenticated_client.get(f"{api_url}/{scan.id}")
            assert detail_response.status_code == 200
            assert detail_response.json()["sha256"] == "mocked_sha256"
