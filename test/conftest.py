import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core import database as db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Overriding database path variables during tests to point to a temporary test JSON file.
    This guarantees that unit tests never overwrite or pollute real development data.
    """
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_db_dir = os.path.join(test_dir, "data_test")
    test_db_path = os.path.join(test_db_dir, "users_test.json")
    
    # Store original paths
    orig_db_dir = db.DB_DIR
    orig_db_path = db.DB_PATH
    
    # Apply override paths
    db.DB_DIR = test_db_dir
    db.DB_PATH = test_db_path
    
    # Initialize testing database
    if not os.path.exists(test_db_dir):
        os.makedirs(test_db_dir, exist_ok=True)
    db.save_users([])
    
    yield
    
    # Clean up test database directory and files after all tests run
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass
    if os.path.exists(test_db_dir):
        try:
            os.rmdir(test_db_dir)
        except OSError:
            pass
            
    # Restore original database configurations
    db.DB_DIR = orig_db_dir
    db.DB_PATH = orig_db_path


@pytest.fixture(name="client")
def client_fixture():
    """
    FastAPI TestClient fixture. Resets database user array back to empty
    before starting each individual test case.
    """
    db.save_users([])
    with TestClient(app) as client:
        yield client
