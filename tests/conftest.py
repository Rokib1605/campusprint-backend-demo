import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.storage import MemoryStore


@pytest.fixture
def client():
    with TestClient(create_app(MemoryStore.seeded())) as api:
        yield api


@pytest.fixture
def admin():
    return {"x-user-id": "admin-01"}


@pytest.fixture
def student():
    return {"x-user-id": "student-1605"}


@pytest.fixture
def other_student():
    return {"x-user-id": "student-1609"}


@pytest.fixture
def staff():
    return {"x-user-id": "staff-01"}


@pytest.fixture
def sample_option():
    return {"code": "COLOR_A4", "name": "Color A4", "category": "PRINT", "unit_price_bdt": 8, "available": True}


@pytest.fixture
def sample_order():
    return {"document_name": "assignment.pdf", "pages": 20, "copies": 2, "print_option_id": 1, "binding_option_id": 2}
